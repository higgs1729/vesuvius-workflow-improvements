# Data and attribution

Source dataset: Giorgio Angelotti et al., *Vesuvius Challenge – CT Scans of Herculaneum Papyri*, Vesuvius Challenge. See the official [data citation and license information](https://scrollprize.org/data). This is the newer Vesuvius Challenge dataset, rather than the pre-2025 DLS EduceLab-Scrolls collection.

The official data page specifies [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) unless an asset states otherwise. The CT-derived images, geometry, input metadata and measurements here retain the applicable data conditions. Code licensing does not replace those conditions. No endorsement by the data authors or organizers is claimed.

The two public PHerc0814 surface inputs and their original hashes/URLs are listed in [flatboi/inputs.json](flatboi/inputs.json). The CT comparison uses the first input and volume [`20250804134230-9.362um-1.2m-113keV-masked.zarr`](https://vesuvius-challenge-open-data.s3.amazonaws.com/PHerc0814/volumes/20250804134230-9.362um-1.2m-113keV-masked.zarr/.zattrs), level 0 at 9.362 µm per voxel. [Selected CT objects](ct/chunks.json) include hashes and original URLs.

Changes to data for these figures: flattening with the existing SLIM settings, component translations for the after case, native XYZ rasterization, linear surface and trilinear CT interpolation, cropping, a common intensity display window, enlargement for viewing, and explanatory masks/annotations. No text or letter labels were inserted into the scan images. The source-component image is a diagnostic label map, not a CT or ink image.

The earlier initial-UV stride issue is credited to [alpaltian, villa issue #2500](https://github.com/ScrollPrize/villa/issues/2500). That code change is not part of this component-packing patch. The patch uses the existing libigl component finder; the CT comparison uses Volume Cartographer's existing interpolation and TIFF output code.
