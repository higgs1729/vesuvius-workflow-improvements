# Verification scope

Prepared on 13 November 2026 (Japan time). The implementer and independent verifier were separate AI agents. The source, build commands, compiler dependency files, linked objects, executable hashes and saved output files were checked. These are local experiments, not human review or upstream acceptance.

## Native resume behavior

The original renderer completed level 0 but exited with an error for missing level 1 in two cases: a new output path with `--resume`, and an output containing only level 0. The fix uses the existing level geometry calculation and writer to initialize missing arrays before the existing pyramid pixel writer runs.

| Resume-fix case | Result |
|---|---|
| Normal output to a new path | 14 files identical to the original normal control |
| First-use `--resume` | Same 14 files |
| Level-0-only partial output | Same 14 files; existing L0 hashes and modification times retained |
| Level 0 plus level-1 metadata | Same 14 files; existing metadata retained |
| Already complete output | Same 14 files |
| `--pre`, followed by the tested part 0 | Same 14 files |
| Prepared mixture of gzip/dot L0, raw/slash L1 and Blosc L3 | Missing levels 2, 4 and 5 initialized using L0's format; all decoded pixels matched the normal control |

The independent verifier repeated the mixed-format partial case once in a new output directory, leaving level 2 as an empty directory. All 15 resulting files matched the saved mixed-format control. Existing L0 files and level-1/level-3 array metadata retained both their hashes and modification times. The native run took 6.56 seconds with peak RSS 65,696 KiB. The existing renderer still regenerates lower-level pixels and root OME attributes; preservation of every lower-level chunk's modification time is not claimed.

## OME references and the combined renderer

The original `--pyramid false` output had only array 0 while OME listed arrays 0–5. In the combined crop-guard/resume/OME build, normal pyramid-disabled output and metadata-only `--pre` both reference only array 0. The normal L0 metadata and chunk bytes match the original normal control. Root attributes match the control with only datasets 1–5 removed.

The combined renderer's normal output and first-use resume match the 14-file control. Its 18 saved crop-guard CLI cases passed. The verifier checked the exact executable used by those cases and the correspondence between the three product patches, compiled source, modified header and reused resume-fix object. Applying the patches in the checked alternate order produced the same source.

One new `--pre --num-parts 2 --pyramid false` invocation took 2.18 seconds with peak RSS 59,776 KiB. It produced 1,654 bytes in exactly three metadata files and no chunks, as expected for `--pre`. Each file matched the implementation's saved control. An initial read-only audit failed because it compared different temporary paths in a merge diagnostic; correcting that verifier condition required no additional rendering.

## Python boundary

The Python patch extends the existing thin binding and wrapper, and its default keeps the existing native entry point. The real changed `bindings.cpp` was compiled with nanobind 2.10.2 for Ubuntu CPython 3.12.3. The real `_catalog` extension required during `_reader` initialization was also built, using existing native libraries. The check imports the real writer module and dependencies while supplying package search paths instead of executing the two unrelated package initializers.

On tiny Zarr v2 uint8 arrays, preservation mode retained all L0/L1 metadata, chunks and modification times, including gzip/slash and raw/dot formats, and created missing L2 with L0's format. The existing public default and four-argument native call passed. The added regression function was extracted as its original AST and executed with the real writer/reader classes; this was not a pytest-runner invocation.

The lead, who did not implement the Python change, reviewed the check and repeated it in a new directory. A separate standard-library check decoded all four gzip chunks (64 pixels equal to 17) and inspected the raw chunk (16 pixels equal to 9), checked file hashes/modification times, and checked the missing level's metadata. That replay took 3.764 seconds with peak RSS 122,699,776 bytes. No extra build or download was needed.

The targeted build required 344.444 seconds across incremental attempts and 22,742,845 downloaded bytes including dependencies, metadata and source attempts. Missing include/transitive-library/catalog dependencies were resolved without rebuilding the whole project or modifying the restored system environment. Full package initialization, a wheel, pytest itself, other Python versions and other operating systems remain untested.

## Boundaries

- The real-CT fixture is one fixed 128 × 128 crop with 101 output layers, Zarr v2, uint8, bicubic sampling and mean accumulation at 0.5-step sampling.
- Partial states were constructed from saved outputs. An actual forced interruption and simultaneous multi-part rendering were not tested.
- The combined renderer was not separately rerun on every partial state; the shared resume implementation was checked in the earlier resume-only build.
- Zarr v3, all dtype/codec combinations, downstream viewers, general throughput, text readability and external adoption are outside the demonstrated scope.
- No new CT data or paid cloud computation was used. Build dependencies, if obtained for the Python check, are tracked separately from CT data.

Public patches and portable evidence are accompanied by hashes in the candidate manifest. The detailed private study identifiers are 120–125. They identify the experiment sequence without implying six separate contributions.
