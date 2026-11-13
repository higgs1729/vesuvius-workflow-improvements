# Recover missing Zarr pyramid levels and describe the levels actually written

Verified local candidate for the combined November 2026 Progress Prizes submission. Not published or submitted. The CLI changes and the targeted Python entry have implementation and independent checks. See the [verification scope](VERIFICATION.md).

The existing `vc_render_tifxyz --resume` can fail after completing level 0 when a single-part output has no lower-resolution arrays. This also occurs when `--resume` is used on a new output path. The renderer attempts to write level 1 without initializing its array metadata.

The fix extends the existing pyramid initializer with a mode that retains existing array metadata and creates missing levels using the saved level-0 format. Single-part rendering uses this mode when resuming with pyramids enabled. Existing levels must have the expected shape, chunk shape and dtype. The existing lower-level pixel calculation still runs; this is not a promise to retain lower-level chunk modification times or to avoid all recomputation.

A related fix makes OME `datasets` follow the pyramid flag. With `--pyramid false`, both normal rendering and `--pre` describe only level 0. Previously they also referenced levels 1–5, which were not created. These changes form one Zarr output improvement in the monthly bundle.

## Evidence and limits

On a fixed 128 × 128 crop with 101 output layers from the public PHerc0814 scan, the original renderer failed for a new `--resume` output and a level-0-only output. The changed renderer completed these cases and normal, partially initialized, already complete, and pre-initialized part-0 cases. The six resulting outputs each matched all 14 files of the original normal control.

A separate check resumed a prepared mixture of gzip, uncompressed and Blosc levels with missing intermediate levels. Existing level-0 files and array metadata retained their hashes and modification times. Missing arrays inherited level 0's format; the resulting decoded pixels matched the normal control. This was a constructed partial state, not a forced process-kill experiment.

The combined crop-guard, resume and OME patches were compiled into one renderer. Normal output and first-use resume each matched the 14-file control. Pyramid-disabled normal output retained the same level-0 array metadata and chunk bytes. A fresh metadata-only `--pre --pyramid false` check wrote exactly the three expected metadata files, with OME referencing level 0 and no pixel chunks. The crop-guard's 18 saved CLI checks also passed against this combined executable.

These results concern a fixed Zarr v2 uint8 fixture. They do not establish every dtype, codec, Zarr v3 case, simultaneous multi-part rendering, downstream viewer behavior, real-user adoption or improved text readability. No new CT data or paid cloud computation was used. Local electricity and model usage costs have not been calculated.

## Apply the patches

The native changes target [villa revision `0080fa393724575d4f19059d91402757f9351b28`](https://github.com/ScrollPrize/villa/tree/0080fa393724575d4f19059d91402757f9351b28). From that repository's root, apply the native initializer/renderer patch, its Python exposure, and the OME metadata patch in this order:

```sh
git apply --check /path/to/resume-pyramid.patch
git apply /path/to/resume-pyramid.patch
git apply --check /path/to/resume-pyramid-python.patch
git apply /path/to/resume-pyramid-python.patch
git apply --check /path/to/pyramid-metadata.patch
git apply /path/to/pyramid-metadata.patch
```

Build `vc_render_tifxyz` in an existing configured Volume Cartographer build and rebuild the Python extension if using the Python entry point. Our native tests compiled the changed translation units and linked existing dependencies on Ubuntu 24.04 with GCC 13. A fresh full-repository build was not tested. The crop-guard patch in the sibling candidate is compatible; both application orders were checked, and the combined renderer was exercised.

The thin Python API adds `preserve_existing=False` to `create_pyramid_levels`. Explicit `True` selects the native preservation mode and takes precedence over `overwrite`. This initializes array metadata only; call the existing pyramid writer to compute pixels. The public patch's README context matches the fixed main revision; its executable changes are identical to those exercised in the experiments.

## Check the Python entry without CT data

With a patched vc_reader installation and NumPy available, run:

```sh
python -B verify_python.py
```

The script creates tiny temporary Zarr arrays. It checks that gzip level 0 and uncompressed level 1 retain their metadata, data and modification times while a missing level 2 inherits level 0's format. It also exercises the public function with the new argument omitted and the existing four-argument native call.

Our runtime check used the real writer module and real compiled `_reader` and `_catalog` extensions in an isolated import. To use that mode, supply the actual source and extension paths; put `_catalog` alongside `_reader`, and make NumPy importable:

```sh
python -B verify_python.py \
  --writer /path/to/vc_reader/src/vc_reader/reader/writer.py \
  --extension /path/to/_reader.cpython-312-x86_64-linux-gnu.so \
  --upstream-test /path/to/vc_reader/tests/test_zarr_writer.py \
  --work /path/to/new-output
```

This mode supplies package search paths but does not execute the two top-level package initializers. `--upstream-test` executes the unchanged AST of the added test function with the real classes and function. The pytest runner, full package installation, wheel and ordinary package initialization were not validated. The isolated check passed on Ubuntu CPython 3.12.3, nanobind 2.10.2 and NumPy 2.2.6; the lead independently replayed it and decoded the preserved gzip/raw bytes with Python's standard library.

[Machine-readable results](RESULTS.json) and [source provenance](PROVENANCE.json) identify the native experiments and Python check. Native implementation and partial-state verification are studies 120–122; OME and combined-renderer verification are 123–124; Python build/runtime validation is 125, followed by the lead's independent replay. These are evidence stages for one contribution.

Prepared with AI agents. Independent verification means a separate AI agent, not human or upstream-maintainer review.

## Source and license scope

The renderer changes retain upstream Volume Cartographer's [GPLv3 license](LICENSE-volume-cartographer.txt). The vc_reader changes retain the upstream villa [root MIT license](LICENSE-villa-root.txt) and applicable notices. Newly authored contributions and this original explanatory material are also offered under [MIT](LICENSE-original-contributions.txt). These permissions do not relicense upstream context, remove conditions from the combined program, or cover dependency implementations.

Raw CT, surface files, third-party build dependencies and compiled binaries are not distributed here. The experimental volume was `20250804134230-9.362um-1.2m-113keV-masked.zarr`, paired with the PHerc0814 surface derived from `20250929040153-auto_grown_20250929040153260`; source dataset rights are unchanged. See the [Vesuvius data overview](https://scrollprize.org/data).
