"""Measure a diagnostic flatboi run on its original tifxyz input.

Requires numpy, scipy and tifffile. The diagnostic patches in this package
record original-face ownership; ordinary flatboi output alone lacks that map.
"""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import tifffile
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree
from mesh_quality import measure


def assess(source, run):
    probe = json.loads((run / 'output.obj_uv_diagnostics.json').read_text())
    trace = json.loads((run / 'raster_trace.json').read_text())
    cells = np.asarray(probe['fine_cells_yx'], int)
    faces = np.asarray(probe['fine_faces'], int)
    uv_valid = np.asarray(probe['fine_valid'], bool)
    uv = np.asarray([p if p is not None else [np.nan, np.nan]
                     for p in probe['fine_uvs']], float)
    raw = np.stack([tifffile.imread(source / f'{axis}.tif') for axis in 'xyz'], -1)
    vertices = raw[tuple(cells.T)].astype(float)
    if 'fine_positions' in probe:
        assert np.array_equal(vertices, probe['fine_positions'])
    qrc = cells[faces[::2]].min(1)
    assert len(faces) == 2 * len(qrc)
    assert np.array_equal(cells[faces[::2]], qrc[:, None] + [[1, 0], [0, 0], [0, 1]])
    assert np.array_equal(cells[faces[1::2]], qrc[:, None] + [[1, 0], [0, 1], [1, 1]])
    mask = np.isfinite(raw).all(-1) & (raw != -1).all(-1) & (raw[..., 2] > 0)
    quads = mask[:-1, :-1] & mask[1:, :-1] & mask[:-1, 1:] & mask[1:, 1:]
    assert np.array_equal(qrc, np.argwhere(quads))
    edges = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    graph = coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])),
                       shape=(len(vertices), len(vertices))).tocsr()
    count, labels = connected_components(graph, directed=False)
    quad_components = labels[faces[::2, 0]]
    centres = (vertices[faces[::2, 0]] + vertices[faces[::2, 1]]
               + vertices[faces[::2, 2]] + vertices[faces[1::2, 2]]) / 4
    mapping = np.flatnonzero(uv_valid[faces].all(1))
    assert trace['face_count'] == len(mapping)
    owners = np.asarray(trace['owners_row_major'], int).reshape(trace['grid_shape_yx'])
    present = owners >= 0
    xyz = np.stack([tifffile.imread(run / 'output' / f'{axis}.tif') for axis in 'xyz'], -1)
    assert np.array_equal(present, np.isfinite(xyz).all(-1) & (xyz != -1).all(-1) & (xyz[..., 2] > 0))
    out_labels = np.full(owners.shape, -1, int)
    out_labels[present] = labels[faces[mapping[owners[present]], 0]]
    distances = np.full(len(centres), np.inf)
    for label in range(count):
        samples = xyz[out_labels == label].astype(float)
        selected = quad_components == label
        if len(samples):
            distances[selected] = cKDTree(samples).query(centres[selected], workers=1)[0]
    samples_per_face = np.bincount(mapping[owners[present]], minlength=len(faces))
    samples_per_quad = samples_per_face.reshape(-1, 2).sum(1)
    rejected = np.asarray(trace['overlap_xy_owner_rejected'], int).reshape(-1, 4)
    cross_rejected = labels[faces[mapping[rejected[:, 2]], 0]] != labels[faces[mapping[rejected[:, 3]], 0]]
    cross_edges = int(((present[:-1] & present[1:]) & (out_labels[:-1] != out_labels[1:])).sum()
                      + ((present[:, :-1] & present[:, 1:]) & (out_labels[:, :-1] != out_labels[:, 1:])).sum())
    quality, _ = measure(vertices, faces, uv)
    return {
        'grid_yx': list(owners.shape), 'source_vertices': len(vertices),
        'source_faces': len(faces), 'input_quads': len(qrc), 'source_components': count,
        'invalid_uv_vertices': int((~uv_valid).sum()), 'filtered_triangles': len(faces) - len(mapping),
        'output_points': int(present.sum()), 'rejected_events': len(rejected),
        'cross_component_rejected': int(cross_rejected.sum()),
        'cross_component_grid_edges': cross_edges,
        'no_owned_sample_quads': int((samples_per_quad == 0).sum()),
        'gt20': int((distances > 20).sum()), 'gt40': int((distances > 40).sum()),
        'max_finite_distance': float(distances[np.isfinite(distances)].max()) if np.isfinite(distances).any() else None,
        'quads_without_component_samples': int((~np.isfinite(distances)).sum()),
        'quality': quality,
        'input_sha256': {name: hashlib.sha256((source / name).read_bytes()).hexdigest()
                         for name in ['meta.json', 'x.tif', 'y.tif', 'z.tif']},
        'scope': 'Original quad centres to samples of the same source component. '
                 'Raster rejections are events, not an exhaustive continuous-overlap count. '
                 'This does not measure ink readability.'
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--run', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    result = assess(args.input, args.run)
    with args.out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
