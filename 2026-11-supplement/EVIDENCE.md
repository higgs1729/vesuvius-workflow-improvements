# Evidence and scope

RESULTS.json contains compact extracts of frozen experiment records, with each original record's SHA-256 and study ID. Native runtime, independent checks and the later integrated smoke tests are distinct runs. Independent checking was performed by a separate AI agent or by the research lead using separate code. The experiments establish behavior on the stated inputs. Human adoption, upstream acceptance and improved readability remain unverified. [Result extracts](RESULTS.json)

## R005 · Grid-preserving surface packing

The rasterizer keeps the original UV-to-grid transform. It shifts snapped vertices and raster bounds by whole X cells and keeps triangle order, edge tests and interpolation arithmetic. Source XYZ and face connectivity stay unchanged. Grid width may increase. The existing default and legacy pack modes remain available. On the first surface, their outputs matched the respective saved controls. The two original PHerc0814 surfaces at keep100 and five iterations gave these results.

| Measurement | First surface | Second surface |
| --- | ---: | ---: |
| Original owners retaining source face and XYZ bits | 40,944 | 254,263 |
| New owner cells exposed | 189 | 399 |
| Cross-component rejections | 189 → 0 | 399 → 0 |
| Same-component rejections | 1 → 1 | 358 → 358 |
| Grid height × width | 172×553 → 172×683 | 252×2637 → 252×3033 |

R151 independently enumerated all source triangles and checked every packed owner's weights and XYZ. Product and observation builds agreed on the three XYZ TIFF files. In the separate R153 single-component PHerc0139 w035 control, the two product modes had identical XYZ files and all decoded float32 values, grid size, scale and SLIM energy. The only generated metadata difference was output UUID.

R155 used the first PHerc0814 surface at keep1.5, stride 8 and five iterations. All 21,350 original owners retained their source face, XYZ and weights. Cross-component rejections fell from 1,848 to zero, with 1,671 distinct owners exposed. The other 177 rejected claims became visible as same-component conflicts after separation, increasing the recorded same-component count from 11,340 to 11,517. The test covers that low-retention case and leaves other settings and object-store use untested.

R152 tracked original faces 53045 and 63364 in one fixed 64×64 PHerc0814 CT window. Crop XYWH was (7428,2378,64,64) before placement and (7388,2378,64,64) and (8608,2378,64,64) after shifts of −2 and +59 source-grid cells. For the linear surface path and offsets −2 to +2 voxels, each component retained 1,408 pure-support pixels and 7,040 bit-identical sample positions, float32 intensities and uint8 pixels. The 1,280 mixed-support positions had no valid sample in either translated crop. The figure uses the saved center-layer output and labels invalid support. The result leaves physical sheet correspondence, other CT windows, bicubic equivalence and legibility unverified. [Comparison figure](images/ct-preservation-center.png)

## R007 · Crop validation

The separate saved real CT control verified a complete crop of 128×128 pixels across three layers, with the decoded output matching its reference. An earlier observation with a missing crop height reached the full bounds selection, where the observation was stopped. The tested guard rejects the incomplete crop before opening the input. The 18-case CLI suite covers the argument paths without CT and passed in the integrated build, including nine early rejections and five valid crop paths that reached the expected input-open error. [Original R007 evidence](https://github.com/higgs1729/vesuvius-workflow-improvements/blob/a35e2d49124758bc28e7fcf499bd656387e74f5c/2026-11/crop-guard/README.md)

## R009 · Zarr restart and OME metadata

- **R131/R132 · Missing arrays after an actual stop.** With a single L0 chunk, the baseline resumed an output with L0 metadata only, wrote L0 pixels and exited 1 when it reached missing L1. The candidate created the missing arrays and matched the normal output. Across two debugger-stopped states, both resumed results matched all 14 normal files, six arrays and OME. Existing files were retained.
- **R157 · Two L0 chunks after an actual stop.** The first L0 writer had returned success before the debugger stopped the renderer. The saved state contained the first L0 chunk and array metadata for all six levels. Resume kept all eight existing files by SHA, mtime and inode, wrote the second L0 chunk and matched the 15-file normal output. The original renderer already had an L0 existence check. This trial measures retention and completion across two chunks. The missing-array rescue is evidenced by the prior case.
- **R160 · Integrated build.** The 1×129×28 w035 render matched R157. A fresh resume and resume from a separately prepared L0-only copy both matched the integrated normal output. The L0-only copy kept all four existing files by SHA, mtime and inode. That prepared state was built from a completed normal render.
- **OME and Python.** In earlier combined-renderer checks, ordinary output and metadata-only --pre with the pyramid disabled listed just L0. The separate isolated Python test exercised real _reader, _catalog and the actual writer wrapper on small local Zarr v2 data. The normal package initialization, wheel and full pytest run remain untested.

The product's OS termination signal was unresolved in the debugger experiments. The results leave torn chunk repair, power loss, simultaneous multi-part writers, Zarr v3 and arbitrary codec or dtype combinations untested. Lower pyramid pixel values can be recomputed on resume.

## Build boundaries

R159 built three native targets with the R005 changes at older base 7ad02f4f6e306b744ef6d2742dfe31fd55713ee5. R160 applied all four packaged patches at 14d4e725df8b569e6fc8ceb3c04d130f705c1565 and built flatboi, vc_core, vc_obj2tifxyz and vc_render_tifxyz on Ubuntu with the available dependencies. The independently checked first PHerc0814 grid was 172×683. Its three XYZ files matched the earlier trials, including all 117,476 float32 values per file. The R007 and R009 integration results above come from the same fixed build.

The recorded build used Linux symlinks and matching headers, callers and shared libraries. It does not establish fresh operating-system setup, full application or GUI builds, or an ABI-compatible replacement of an old shared library. R150 used an earlier isolated executable with the same patched header in both translation units. A misencoded existing comment was restored in the packaged source, and the before/after preprocessing output without comments matched in both historical variants. [Source hashes](SOURCE_HASHES.json) · [Build and reproduction](REPRODUCE.md)
