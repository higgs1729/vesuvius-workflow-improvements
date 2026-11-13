# Verification scope

On 13 November 2026 (Japan time), an AI agent other than the implementer independently checked the saved source, binaries, process records and output files. This was not human review or upstream acceptance.

The original source matched Git blob `3c0d4250ea484c616f4f8e2c260f7ce2a07f99d6`. Applying the product patch and the separate observation patch reconstructed all three actual compilation sources byte for byte. The normal product source contains no observation hook; crop geometry, sampling and output code remain unchanged.

The verifier ran the 18 data-free CLI cases once against the saved product binary, with new output paths. All passed. Nine invalid cases rejected the request with the crop diagnostic before input opening. The remaining cases exercised valid crop options, help, pre-existing argument failures and the empty merge branch. The replay took 5.40 seconds.

Saved real-surface observation logs showed identical selection for six valid conditions. Omitting height in the old version selected 46,784,000 pixels per layer instead of 16,384. No full-canvas render was performed. The difference is 46,767,616 selected pixels per layer; it is not measured download, running-time or monetary savings.

All three actual 128 × 128 TIFF files matched the original controls by SHA-256, and a separate TIFF/LZW decoder confirmed the pixels. The small merge output also matched the middle control. No new rendering, build, CT download or paid cloud computation was needed for independent verification.

The verifier's initial offline audit expected the help description on one line, while Boost wrapped it across lines. The checker was corrected to normalize whitespace; the initial failure was preserved. The product and experiment were not changed, and the CLI replay was not repeated.

This establishes the small guard's behavior in the tested CLI and local PHerc0814 setup. Other data types, GPU rendering and a fresh full build were not exercised. No external user incident or adoption has been established. The general regression script is included as `check_cli.py`; full local research evidence remains in studies 116 and 117 of the research workspace.
