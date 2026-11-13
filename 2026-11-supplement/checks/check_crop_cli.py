"""Run crop argument regressions against a real renderer without a volume."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile


CROP_ERROR = '--crop-width and --crop-height must both be positive for a manual crop'


def check(binary, root, invoke):
    absent_volume = root / 'absent.zarr'
    absent_segment = root / 'absent.tifxyz'
    assert not absent_volume.exists() and not absent_segment.exists()
    required = ['--scale', '1', '--group-idx', '0']
    input_args = required + ['--volume', str(absent_volume), '--segmentation', str(absent_segment)]
    invalid = {
        'missing-height': ['--crop-x', '7356', '--crop-y', '2272', '--crop-width', '128'],
        'missing-width': ['--crop-height', '128'],
        'negative-width': ['--crop-width=-128', '--crop-height', '128'],
        'negative-height': ['--crop-width', '128', '--crop-height=-128'],
        'zero-height': ['--crop-width', '128', '--crop-height', '0'],
        'position-only': ['--crop-x=-1', '--crop-y', '5'],
        'position-with-explicit-zero-sizes': ['--crop-x', '1', '--crop-width', '0', '--crop-height', '0'],
        'auto-with-partial': ['--auto-crop', '--crop-height', '128'],
    }
    valid = {
        'default-crop': [],
        'all-zero': ['--crop-x', '0', '--crop-y', '0', '--crop-width', '0', '--crop-height', '0'],
        'default-origin': ['--crop-width', '128', '--crop-height', '128'],
        'negative-origin': ['--crop-x=-1', '--crop-y=-2', '--crop-width', '128', '--crop-height', '128'],
        'auto-crop': ['--auto-crop'],
    }
    for name, args in (invalid | valid).items():
        output = root / f'{name}.zarr'
        message = CROP_ERROR if name in invalid else 'Error opening local zarr:'
        log = invoke(name, [str(binary), *input_args, '--zarr-output', str(output), *args], 1, message)
        if name in invalid:
            assert 'Error opening local zarr:' not in log and 'Error loading:' not in log
        else:
            assert CROP_ERROR not in log
        assert not output.exists(), name
    tif_output = root / 'tiff-invalid'
    invoke('tiff-invalid', [str(binary), *input_args, '--tif-output', str(tif_output),
                           '--crop-width', '128'], 1, CROP_ERROR)
    assert not tif_output.exists()
    help_log = invoke('help', [str(binary), '--help', '--crop-width', '128'], 0, 'Show this help message')
    assert all(flag in help_log for flag in ('--crop-width', '--crop-height', '--auto-crop', '--merge-tiff-parts'))
    assert CROP_ERROR not in help_log
    output = root / 'invalid-part'
    invoke('invalid-part', [str(binary), *input_args, '--tif-output', str(output), '--num-parts', '0'],
           1, 'need 0 <= part-id < num-parts')
    assert not output.exists()
    output = root / 'missing-segmentation'
    invoke('missing-segmentation', [str(binary), *required, '--volume', str(absent_volume), '--tif-output', str(output)],
           1, 'give --segmentation, or --store with one --surface')
    assert not output.exists()
    merge_path = root / 'empty-merge'
    merge_path.mkdir()
    invoke('merge-empty', [str(binary), *required, '--tif-output', str(merge_path), '--num-parts', '2',
                           '--merge-tiff-parts', '--crop-width', '128'], 1, 'No .partN.tif files found')
    assert not any(merge_path.iterdir())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('renderer', type=Path)
    args = parser.parse_args()

    def invoke(label, argv, exit_code, message):
        run = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
        print(json.dumps(dict(case=label, argv=argv, exit_code=run.returncode, log=run.stdout)))
        assert run.returncode == exit_code and message in run.stdout, label
        return run.stdout

    with tempfile.TemporaryDirectory(prefix='vc-crop-') as temp:
        check(args.renderer.resolve(strict=True), Path(temp), invoke)


if __name__ == '__main__':
    main()
