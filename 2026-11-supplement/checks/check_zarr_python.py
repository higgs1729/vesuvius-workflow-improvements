"""Smoke-test the real public create_pyramid_levels entry on a tiny Zarr v2 fixture."""
import argparse
import ast
import hashlib
import importlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types


def manifest(root):
    return {str(path.relative_to(root)): {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                          'mtime_ns': path.stat().st_mtime_ns}
            for path in root.rglob('*') if path.is_file()}


def array_metadata(root, level):
    return json.loads((root / str(level) / '.zarray').read_text())


def require_level(root, level, shape, chunks, compressor, separator):
    meta = array_metadata(root, level)
    assert meta['shape'] == list(shape) and meta['chunks'] == list(chunks)
    assert meta['compressor'] == compressor and meta['dimension_separator'] == separator
    assert meta['dtype'] == '|u1'


def test_public(root, writer):
    factors = (1, 2, 2)
    gzip7 = {'id': 'gzip', 'level': 7}

    def base(directory):
        return writer.ZarrWriter.create(directory / '0', shape=(1, 8, 8), chunks=(1, 4, 4), dtype='u1',
                                        compressor='gzip', level=7, separator='/')

    keep = root / 'preserve.zarr'
    base(keep)[...] = 17
    lower = writer.ZarrWriter.create(keep / '1', shape=(1, 4, 4), chunks=(1, 4, 4), dtype='u1',
                                     compressor=None, separator='.')
    lower[...] = 9
    before = {str(i): manifest(keep / str(i)) for i in (0, 1)}
    writer.create_pyramid_levels(keep, 2, factors=factors, preserve_existing=True)
    assert {str(i): manifest(keep / str(i)) for i in (0, 1)} == before
    assert (writer.ZarrReader.open(keep / '0', threads=1)[...] == 17).all()
    assert (writer.ZarrReader.open(keep / '1', threads=1)[...] == 9).all()
    require_level(keep, 0, (1, 8, 8), (1, 4, 4), gzip7, '/')
    require_level(keep, 1, (1, 4, 4), (1, 4, 4), None, '.')
    require_level(keep, 2, (1, 2, 2), (1, 2, 2), gzip7, '/')

    default = root / 'default.zarr'
    base(default)[...] = 17
    writer.ZarrWriter.create(default / '1', shape=(1, 4, 4), chunks=(1, 4, 4), dtype='u1',
                             compressor=None, separator='.')
    default_l0 = manifest(default / '0')
    writer.create_pyramid_levels(default, 2, factors=factors)
    assert manifest(default / '0') == default_l0
    require_level(default, 1, (1, 4, 4), (1, 4, 4), gzip7, '/')
    require_level(default, 2, (1, 2, 2), (1, 2, 2), gzip7, '/')
    writer._reader.create_pyramid_levels(str(default), 2, list(factors), False)
    assert manifest(default / '0') == default_l0
    require_level(default, 2, (1, 2, 2), (1, 2, 2), gzip7, '/')

    return {'preserved_level_file_manifests': before, 'preserved_pixels': {'0': 17, '1': 9},
            'preserve_true_created_level': array_metadata(keep, 2),
            'default_reinitialized_level': array_metadata(default, 1), 'default_created_level': array_metadata(default, 2),
            'native_original_four_argument_call_passed': True}


def import_isolated(writer_path, extension):
    # Supply only package paths, leaving unrelated package initializers unexecuted.
    source = writer_path.parent.parent
    for name, path in (('vc_reader', source), ('vc_reader.reader', source / 'reader')):
        module = types.ModuleType(name)
        module.__path__ = [str(path)]
        if name == 'vc_reader':
            module.__path__.append(str(extension.parent))
        module.__spec__ = importlib.machinery.ModuleSpec(name, None, is_package=True)
        module.__spec__.submodule_search_locations = module.__path__
        sys.modules[name] = module
    name = 'vc_reader._reader'
    spec = importlib.util.spec_from_file_location(name, extension)
    native = importlib.util.module_from_spec(spec)
    sys.modules[name] = native
    spec.loader.exec_module(native)
    writer = importlib.import_module('vc_reader.reader.writer')
    assert Path(writer.__file__).resolve() == writer_path.resolve()
    assert writer._reader is native and Path(native.__file__).resolve() == extension.resolve()
    return writer


def run_upstream_test(path, root, writer):
    name = 'test_create_pyramid_levels_preserves_existing_arrays'
    tree = ast.parse(path.read_text(), filename=str(path))
    function, = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
    scope = {key: getattr(writer, key) for key in ('ZarrWriter', 'ZarrReader', 'create_pyramid_levels')}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), 'exec'), scope)
    scope[name](root)
    return {'function': name, 'ast_sha256': hashlib.sha256(ast.dump(function).encode()).hexdigest(),
            'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--writer', type=Path, help='path to vc_reader/reader/writer.py for isolated import')
    parser.add_argument('--extension', type=Path, help='real compiled _reader extension for isolated import')
    parser.add_argument('--upstream-test', type=Path, help='run the named regression from the patched test source')
    parser.add_argument('--work', type=Path, help='new directory to retain fixtures')
    parser.add_argument('--report', type=Path, help='write the JSON report to a new file')
    args = parser.parse_args()
    if bool(args.writer) != bool(args.extension):
        parser.error('--writer and --extension go together')
    if args.writer:
        writer = import_isolated(args.writer, args.extension)
    else:
        writer = importlib.import_module('vc_reader.reader.writer')

    def verify(root):
        result = test_public(root, writer)
        if args.upstream_test:
            result['upstream_test_function_passed'] = run_upstream_test(args.upstream_test, root / 'regression.zarr', writer)
        catalog = sys.modules.get('vc_reader._catalog')
        result.update(writer_module=writer.__file__, native_module=writer._reader.__file__,
                      native_sha256=hashlib.sha256(Path(writer._reader.__file__).read_bytes()).hexdigest(),
                      catalog_module=catalog.__file__ if catalog else None,
                      catalog_sha256=hashlib.sha256(Path(catalog.__file__).read_bytes()).hexdigest() if catalog else None,
                      numpy_version=writer.np.__version__, import_isolated=bool(args.writer))
        content = json.dumps(result, indent=2) + '\n'
        if args.report:
            with args.report.open('x', encoding='utf-8') as stream:
                stream.write(content)
        print(content, end='')

    if args.work:
        args.work.mkdir()
        verify(args.work)
    else:
        with tempfile.TemporaryDirectory(prefix='r009-python-') as directory:
            verify(Path(directory))


if __name__ == '__main__':
    main()
