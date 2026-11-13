# Data and attribution

The surface and CT inputs derive from Giorgio Angelotti et al., Vesuvius Challenge – CT Scans of Herculaneum Papyri. The official data page gives the citation and CC BY-NC 4.0 terms unless an asset states otherwise. The archive contains source manifests and small CT metadata files. Use the original URLs, byte lengths and SHA-256 in the manifests to assemble local inputs. [Data terms](https://scrollprize.org/data) · [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)

- **PHerc0814 surfaces** are the two original TIFXYZ meshes of segments 20250929040153-auto_grown_20250929040153260 and 20250928235953-auto_grown_20250928235953722. Keep each manifest's four files in a separate input folder. [PHerc0814 surface files](data/surface-inputs-pherc0814.json)
- **PHerc0814 CT** for the fixed comparison is level 0 of 20250804134230-9.362um-1.2m-113keV-masked.zarr. The ten uncompressed chunks total 20 MiB. [PHerc0814 CT keys and hashes](data/pherc0814-ct-chunks.json) · [Cache array metadata](data/pherc0814-ct-metadata/0/.zarray)
- **PHerc0139 w035 surface** is segment 20260317000000-w035_2026031718 in scan coordinates 20250728140407 at 9.362 µm. [W035 surface files](data/surface-inputs-w035.json)
- **PHerc0139 CT** is level 0 of 20250728140407-9.362um-1.2m-113keV-masked.zarr. The two chunks used in the R009 test total 4 MiB. [PHerc0139 CT keys and hashes](data/pherc0139-ct-chunks.json) · [Cache array metadata](data/pherc0139-ct-metadata/0/.zarray)

For either sparse local Zarr cache, start with the contents of its pherc0814-ct-metadata or pherc0139-ct-metadata folder, including the hidden dotfiles. Store each fetched payload under its exact slash-separated key and check its length and SHA-256. The array shape in the metadata is the original full volume. The cache contains the selected source chunks for the stated crops. Check the interpolation footprint before using the sparse cache for other coordinates.

The PHerc0814 figure was generated from the center CT layer with common grayscale values and overlays for support. The center image uses the same fixed data and figure bytes as the recorded trial. The earlier low-keep initial-UV issue was reported by alpaltian. [CT figure](images/ct-preservation-center.png) · [Initial-UV issue](https://github.com/ScrollPrize/villa/issues/2500)
