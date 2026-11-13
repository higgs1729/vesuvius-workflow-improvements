# Reject incomplete manual crops before opening render inputs

Prepared locally for a combined November 2026 Progress Prizes submission. Not published or submitted. Implementation tests and a separate agent's [independent verification](VERIFICATION.md) passed.

`vc_render_tifxyz` currently uses the whole surface when either manual crop dimension is absent or nonpositive. A command intended to render a 128 × 128 region can therefore select the entire canvas if `--crop-height` is accidentally omitted. This small patch returns a clear error before opening the volume or surface.

The change preserves full-canvas rendering with no crop options or four zero values, crops with omitted origins, valid negative origins clipped to the canvas, and automatic cropping. Help and TIFF-part merging retain their existing early branches. The image sampling and conversion code is unchanged.

## Apply and check

The patch targets [this exact renderer revision](https://github.com/ScrollPrize/villa/blob/0080fa393724575d4f19059d91402757f9351b28/volume-cartographer/apps/src/vc_render_tifxyz.cpp), Git blob `3c0d4250ea484c616f4f8e2c260f7ce2a07f99d6`. From the villa repository root:

```sh
git apply --check /path/to/crop-guard.patch
git apply /path/to/crop-guard.patch
```

Build the existing `vc_render_tifxyz` target in your configured Volume Cartographer build. Our experiment compiled the renderer translation unit and linked existing dependencies on Ubuntu 24.04 with GCC 13; it did not validate a fresh full-repository build.

Run the data-free regression checks against the resulting executable:

```sh
python3 /path/to/check_cli.py /path/to/vc_render_tifxyz
```

The check drives the real CLI with nonexistent local inputs. Invalid crops must fail with the crop diagnostic and create no output. Valid options must reach the existing input diagnostic. It also checks help and existing argument/merge branches. Python 3.9 or newer is required. Each subprocess has a 30-second limit.

## Observed behavior and limits

On one PHerc0814 surface, a missing height selected a 13,600 × 3,440 canvas (46,784,000 pixels per layer) instead of 128 × 128 (16,384). A separate observation build exited immediately after choosing the crop, before output creation or sampling. We did not render that full canvas. These are selected pixel counts, not measured time, download or cost savings.

The implementation run rejected eight invalid Zarr cases and one invalid TIFF case before input opening. Six valid crop selections matched the old version. Three 128 × 128 TIFF layers from the patched normal CLI matched the original controls byte for byte; a small TIFF merge also matched its control. No new CT data or paid cloud computation was used.

This is a reproduced input-handling defect, not a claim of a reported real-world accident, downstream reading improvement, human review, or upstream adoption. The data-free checks are reusable, but do not replace the real-surface and image comparisons.

## Provenance and license scope

Prepared with AI agents on 13 November 2026 (Japan time). The experiments used a packed surface derived from the public PHerc0814 mesh `20250929040153-auto_grown_20250929040153260` and the public `20250804134230-9.362um-1.2m-113keV-masked.zarr` CT volume. See the [Vesuvius data overview](https://scrollprize.org/data). Raw CT, surface data and binaries are not included here; dataset rights are unchanged.

The patch modifies Volume Cartographer, whose [GPLv3 license](LICENSE-volume-cartographer.txt) continues to apply to the modified upstream work. Newly authored additions, `check_cli.py`, and this explanatory text are also offered under [MIT](LICENSE-original-contributions.txt); that permission does not relicense upstream context or the combined program. Dependencies retain their existing licenses.
