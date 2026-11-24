# Validation and execution limits

Prepared on 24 November 2026. The revised workflow is intended for a fresh-kernel run in the Digital Earth Africa Sandbox.

**Observed result:** all eight notebooks passed schema/syntax checks, and all offline synthetic checks passed on 24 November 2026. The package versions used for those checks are recorded in `validation_environment.json`. Expected NumPy warnings were emitted for deliberately all-missing pixels; the tests confirmed those pixels remain nodata.

## Checks

Run from the project root:

```bash
python scripts/validate_repository.py
python scripts/check_synthetic.py
```

The repository validator checks all eight notebooks against the nbformat schema, compiles every code cell after IPython magic conversion, confirms clean execution state, checks local documentation links and shared configuration, and validates the working example decision table.

The synthetic-data script loads function definitions directly from the revised notebooks and checks:

- Annual medians, pixel completeness rules, small-image tiling, duplicate months, and shifted-grid rejection.
- Positive/negative Sen slopes, trajectory binary/nodata encoding, reporting windows, and generation of newly requested outputs when principal files already exist.
- State Z against a separately calculated expected value, constant-baseline nodata, class cutoffs, and GeoTIFF writing.
- Within-class maxima, performance ratios and classes, missing-year rejection, reporting-window definitions, and the offline performance driver using an artificial land-cover grid.
- All eight example integration scenarios, blank-template rejection, differing source nodata conventions, hectare calculations, clipping, and PNG generation.
- Example boundary loading and rejection of an invalid configuration.

These checks use tiny artificial rasters with analytically known values. They exercise the offline aggregation, indicator, and integration logic; they are not scientific validation of the research results.

## Live-data execution still required

No revised full-history run against Landsat, WorldCover, or the DE Africa index has been completed in this preparation environment. The acquisition/compositing stages, installed DE Africa temporal-tool behaviour, cloud-mask effects, source-data availability, and large-AOI performance therefore remain to be verified in the target Sandbox environment. The original Mion boundary and criteria table were not supplied.

Before publishing reproduced study results:

1. Supply the actual boundary and original decision table.
2. Run the notebooks in fresh kernels with the shared configuration and archive complete logs.
3. Check all monthly/annual periods, grids, masks, and output ranges.
4. Record a successful environment and the exact DE Africa tools revision, together with data provenance.
5. Compare reproduced rasters/summary tables with archived original outputs and explain any differences introduced by the documented data-handling corrections.

`environment.yml` is an unpinned starting environment. Environment snapshots record installed versions but do not verify that an analysis completed. No full-run date, live numerical equivalence, or reference-data accuracy is claimed.
