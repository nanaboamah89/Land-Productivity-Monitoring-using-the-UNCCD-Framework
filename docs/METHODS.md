# Methods implemented in these notebooks

This document describes the calculations present in the supplied code and the preparation changes documented in `CHANGES.md`. It does not establish equivalence with a particular version of an external reporting standard.

## Monthly rolling NDVI — notebook 01

1. Load Landsat Collection 2 surface reflectance red/NIR through `load_ard`, with quality-mask opening and dilation filters of size 3.
2. Mask to the study polygon and place observations on the shared output grid.
3. Resample into calendar months and compute the multivariate geometric median of red and NIR for each month using `xr_geomedian`.
4. Apply a centered three-month median to each resulting band with `min_periods=1`.
5. Calculate `NDVI = (NIR − red) / (NIR + red)` from those rolling band values.
6. Write target-year months separately, using adjacent December and January observations to support the boundary windows.

This differs from computing one geomedian across all raw observations in a rolling three-month window, and from rolling an already-calculated NDVI series. No median absolute deviation layers are generated. The procedure can improve usable temporal coverage, but does not guarantee complete gap filling. No per-pixel observation-count layer is exported. Monthly timestamps denote the first day of the month; they are not exact acquisition dates of the composite values.

## Phenology and peak-window MVC — notebooks 02–03

The monthly rasters form an annual xarray time series. `xr_phenology` is applied both to the spatial-median NDVI curve and to each pixel. The original `method_sos='first'` and `method_eos='last'` choices are retained.

| Metric | Meaning | Units |
| --- | --- | --- |
| SOS, POS, EOS | Start, peak, end of season | Date in the table; day of year in the spatial panels |
| vSOS, vPOS, vEOS | NDVI at those dates | NDVI units |
| Trough | Minimum seasonal NDVI | NDVI units |
| LOS | Length of season | Days |
| AOS | Seasonal amplitude | NDVI units |
| ROG, ROS | Greening and senescence rates | NDVI change per day under the temporal-tool convention |

The historical `_POS_YYYY.tif` filename contains vPOS, a magnitude. AOI table magnitudes retain the original three-decimal rounding. A spatial-median curve and pixelwise peak map have different statistical meanings. Monthly resolution and rolling smoothing limit seasonal-date accuracy. Multiple growing seasons and seasons crossing December/January require a suitable alternative seasonal design.

MVC uses raw-observation NDVI in an interval around the AOI POS date. It tries ±1 month, then ±2 and ±3 on load failure, and uses the first successful load. That retry scheme does not automatically widen merely because pixel coverage is incomplete. NDVI is clipped to [0,1], then maximized over time per pixel. The output table records the successful interval and loaded observation count.

`POS_NDVI` is peak magnitude of the AOI spatial-median curve; `MVC_NDVI` is mean pixelwise MVC. `MVC_DOY` is the truncated integer mean of the acquisition-day map of pixel maxima, while `POS_DOY` comes from the AOI curve's monthly peak date. Differences mix temporal support, compositing, clipping, and spatial summaries. They cannot be interpreted as measured accuracy without independent reference data and a matched comparison design.

## Annual aggregation — notebook 04

Annual input files must share one grid and include all 12 months. The default is the median across monthly rolling NDVI. Pixelwise NaNs are excluded unless `require_all_months=True`, which excludes pixels lacking any monthly value. File completeness and pixel completeness are separate conditions.

Mean, median, max, and sum are supported. A sum of monthly NDVI is an index aggregate rather than a physical biomass/NPP quantity. Any change of annual metric requires reconsideration of the indicators and thresholds. Notebooks 05–07 all use this annual branch; they do not use the phenology vPOS rasters.

## Trajectory — notebook 05

Each default window contains 16 consecutive annual rasters; windows advance four years. For annual series y at times t, the code calculates:

`S = sum(sign(y[j] − y[i]))` for all `i < j`.

The inherited variance is `n(n−1)(2n+5)/18`, with n equal to the window length. Z uses a ±1 continuity correction for positive/negative S and is zero when S=0. Two-sided p-values use the standard normal approximation. Sen slope is the median of `(y[j] − y[i]) / (t[j] − t[i])` and has NDVI/year units. OLS slope is optional.

This implementation does not correct variance for ties, autocorrelation, or missing observations, and does not adjust for multiple pixel tests. The default complete-pixel mask is therefore retained. Relaxing completeness without revising the variance calculation is unsuitable for inference. No rainfall normalization or causal attribution is performed.

| Product | Classes | Nodata |
| --- | --- | --- |
| `SDG2_*` | 1 if Z < −1.96; 0 otherwise | 255 |
| `LDN3_*` | 1 if Z < −1.28; 2 if −1.28 ≤ Z ≤ 1.28; 3 if Z > 1.28 | 255 |
| `Z5_*` | 1 below −1.96; 2 from −1.96 to below −1.28; 3 from −1.28 through 1.28; 4 above 1.28 through 1.96; 5 above 1.96 | 255 |
| `sig_p05_*` | 1 if p ≤0.05; 0 otherwise | 255 |
| `sig_dir_*` | −1 significant decrease; 0 not significant; 1 significant increase | −128 |

The binary cutoff uses a strict inequality at −1.96; the two-sided p-value diagnostic uses p≤0.05, so boundary classifications should be read from the explicit code. Inherited `SDG2`/`LDN3` filenames are retained for compatibility and are not certification of an external standard.

The whole-area diagnostic computes annual spatial medians, then a trend of those medians. It can conceal local changes. Its sample limit is applied after collecting all valid raster values, so it does not bound peak RAM.

## State — notebook 06

For each default 16-year window, the first 13 years form the baseline B and the last three form the recent period R:

`Z_state = (mean(R) − mean(B)) / (std(B, ddof=0) / sqrt(3))`.

At least 10 baseline and two recent pixel values are required. Means and standard deviations ignore missing values. The standard-error denominator uses configured recent length, even when fewer recent values are valid. Zero baseline variance or nonfinite results become nodata. These choices are retained and should be reported when interpreting the statistic.

Binary state uses Z < −1.96; three and five classes use the same ±1.28 / ±1.96 cutpoints as trajectory. State class rasters use 255 nodata and continuous Z uses −9999. The baseline advances with the window, whereas performance has a fixed baseline.

## Relative performance — notebook 07

Let B_p be a pixel's mean of annual NDVI values during 2000–2015. For its WorldCover class c, compute `reference_c = max(B_p)` across valid pixels in that class **within the AOI**. For a pixel metric M_p, performance is `M_p / reference_c`. Invalid or nonpositive reference values become nodata.

The baseline product uses M_p=B_p. Assessment products use the selected single annual raster. Default reporting products average 2016–2018 for report 2019 and 2020–2022 for report 2023. These intervals exclude the assessment year. Minimum valid pixel counts are not enforced for these means, although every requested annual file must now exist.

Binary low performance is ratio<0.5. Three classes are low (<0.32), moderate (0.32 through 0.64), and high (>0.64). These classes describe relative levels, rather than temporal degradation/improvement. Assessment ratios can exceed 1 when a later value exceeds the fixed baseline reference.

The inherited names `LCEU` and `NPPmax` refer here to land-cover-only groups and an NDVI maximum. The implementation does not construct climate/soil/ecological strata or estimate NPP. The maximum is sensitive to outliers, AOI size, and membership. A 2021 land-cover map is used for historical periods; document this temporal mismatch and test sensitivity to land-cover change. Nearest-neighbour reprojection preserves categorical values on the annual NDVI grid.

## Integration and area — notebook 08

Each input must be aligned and binary: 1 denotes a flagged pixel and 0 an unflagged pixel. The explicit criteria CSV assigns a final result to each of the eight combinations. Pixels with any missing/invalid indicator remain nodata. The integration helper validates all scenarios before writing.

The integrated raster is cropped to the study polygon with pixel-center inclusion. Individual indicator rasters retain their source masks for the summary. Degraded and nondegraded areas are counted separately; valid area counts only 0/1 pixels. Consequently, indicator totals and the cropped integrated total can differ. Compare masks before comparing areas; percentages over different valid domains require careful interpretation.

Pixel map area is the absolute affine-transform determinant. A projected CRS in metres is required, with an equal-area CRS recommended. EPSG:6933 is the default. A projected scale bar does not imply locally undistorted ground distance. No field validation, causal attribution, land-cover-change indicator, or soil-carbon indicator is produced by this step.
