# Preparation changes

These changes make the supplied notebooks easier to follow and reuse. The monthly/annual calculations and principal indicator definitions and thresholds are retained unless an explicit data-handling correction is listed below.

## Documentation and packaging

- Replaced blank sections and incorrect State/Sentinel-2 headings with step-specific background, prerequisites, outputs, adaptation guidance, and interpretation.
- Added explanatory markdown between logical function groups and code comments at consequential operations.
- Retained all eight notebook filenames and historical output names where possible.
- Added shared configuration, data/method documentation, example inputs, environment specification, and validation scripts.
- Removed saved execution outputs, images, stale test-date displays, and execution counts so GitHub receives clean notebooks. The captured dates/package versions in the supplied files are not used as proof of revised-run compatibility.
- Retained the supplied notebooks' Apache 2.0 code declaration and Digital Earth Africa attribution. No author identity, publication DOI, or repository URL has been invented.

## Reuse and data-handling corrections

- Centralized study label, paths, inclusive years, grid, annual metric, reporting settings, thresholds, and final input selection.
- Aligned phenology processing years with the MVC and acquisition ranges. The original phenology loop began in 2017 while MVC requested 2000 onward.
- Read and combine all AOI polygon features, with explicit geometry/CRS validation, rather than implicitly taking the first feature.
- Added missing-file, duplicate-month/year, complete-rule-table, and exact-grid checks.
- Stopped failed monthly/phenology/MVC runs from appearing to complete successfully.
- Rebuilt combined CSVs from explicit configured-year inputs, avoiding accidental inclusion of an earlier combined CSV.
- Kept phenology durations numeric when writing CSV; only date fields are converted to timestamps.
- Read monthly and vPOS rasters with nodata masks. Wrote explicit NaN nodata to monthly NDVI/MVC/vPOS outputs so valid zero NDVI is distinguishable from missing pixels.
- Recorded the successful MVC observation window and count in the comparison CSV. Plot axes now correctly identify pixel row/column indexes.
- Used valid tile dimensions for small raster extents; GeoTIFF tile size remains a multiple of 16 even when the image is smaller.
- Required all requested trajectory files before skipping an existing window. Distinguished valid zero significance/direction from nodata.
- Initialized the trajectory direction intermediate when requesting p-values without a direction raster, avoiding an unbound-variable error in that output combination.
- Matched WorldCover to the annual NDVI pixel grid using nearest-neighbour reprojection; required every requested baseline/reporting year to exist.
- Made baseline/window output labels respond to configured dates rather than retaining hard-coded 2000–2015/16-year labels.
- Passed the configured annual NDVI scale and land-cover nodata class into the performance function.
- Used complete eight-scenario Y/N criteria validation and valid-binary input membership during integration. Missing input classes remain nodata.
- Required projected metre units for area reporting and used the affine-transform determinant for pixel area.

These corrections can change results when the original inputs contained missing values, shifted grids, multiple polygon features, missing annual years, malformed rules, or ambiguous nodata. Fresh output directories are recommended. No claim is made that the revised results numerically match an earlier thesis run without a complete original-data rerun.

## Method choices deliberately documented

The inherited simple Mann–Kendall variance, state denominator with configured recent length, WorldCover-only performance groups, observed maximum reference, NDVI clipping in MVC, mixed POS/MVC spatial summaries, and original class cutpoints remain visible. Their limitations are explained in METHODS rather than silently replaced with a different research method.
