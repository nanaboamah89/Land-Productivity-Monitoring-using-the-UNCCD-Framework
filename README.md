# Land productivity monitoring with Landsat NDVI

A documented Jupyter workflow for generating monthly rolling NDVI, examining vegetation seasonality, and assessing land productivity through trajectory, state, and relative performance. The original application uses Mion District, Ghana, with Landsat observations from 2000–2024.

The eight notebooks include explanations of their inputs, outputs, parameters, calculations, interpretation, and reuse. Shared settings in [`workflow_config.json`](workflow_config.json) let researchers change study areas and periods without editing paths throughout the notebooks.

**Reproduction status:** the supplied material contains the eight notebooks, but does not include the original Mion boundary, `criteria.csv`, source rasters, or a locked software environment. Exact reproduction of the original maps requires those inputs and the original software/data versions. A small example polygon and an explicitly labelled example integration rule are included for learning the workflow. The revised notebooks have passed the checks in [`docs/VALIDATION.md`](docs/VALIDATION.md); a full live-data run remains to be completed in the DE Africa Sandbox.

## What this workflow produces

- Monthly rolling NDVI GeoTIFFs derived from Landsat red and near-infrared reflectance.
- Seasonal dates and NDVI magnitudes, spatial phenology panels, and peak-window MVC comparisons.
- Annual NDVI rasters and productivity trajectory, state, and performance indicators.
- An integrated productivity classification, indicator maps, and area summaries.

The integrated result concerns the **land productivity component** of land degradation assessment. Full SDG 15.3.1 assessment additionally requires land-cover change and soil organic carbon. NDVI indicates vegetation greenness and serves here as a productivity proxy; it does not directly measure biomass production or identify the cause of change.

## Notebook order

| Notebook | Purpose | Prerequisites | Main outputs |
| --- | --- | --- | --- |
| [01_GeoMAD_generation.ipynb](01_GeoMAD_generation.ipynb) | Monthly red/NIR geomedian, centered rolling-band median, then NDVI | AOI; Landsat data cube | `data/ndvi_roll3_YYYYMM_v01.tif` |
| [02_phenology.ipynb](02_phenology.ipynb) | Seasonal dates and magnitudes | 01 | Phenology CSVs, vPOS rasters, PNGs |
| [03_mvc.ipynb](03_mvc.ipynb) | Compare smoothed peak with a raw-observation peak-window MVC | 02; AOI; Landsat data cube | MVC rasters and comparison tables |
| [04_Annual_Computation.ipynb](04_Annual_Computation.ipynb) | Aggregate monthly NDVI to annual values | 01 | `annual_ndvi/ndvi_annual_median_YYYY.tif` |
| [05_trajectory.ipynb](05_trajectory.ipynb) | Mann–Kendall Z and Sen slope | 04 | Trend statistics and binary trajectory |
| [06_state.ipynb](06_state.ipynb) | Recent versus baseline NDVI state | 04 | State Z, class maps, and binary state |
| [07_performance.ipynb](07_performance.ipynb) | Relative performance within WorldCover classes | 04; AOI; WorldCover data cube | Baseline, assessment, and reporting maps |
| [08_Land_degradation.ipynb](08_Land_degradation.ipynb) | Combine binary indicators, crop, and summarize areas | 05–07; AOI; criteria CSV | Integrated raster, figures, area CSV |

For productivity mapping, run **01 → 04 → 05, 06, 07 → 08**. Run **01 → 02 → 03** for the optional seasonality and MVC comparison branch. Notebooks 05, 06, and 07 can be run independently after 04, but share the same configuration and annual rasters.

## Get started in the Digital Earth Africa Sandbox

1. Sign in to the [DE Africa Sandbox](https://sandbox.digitalearth.africa/) and open JupyterLab. Follow the [official access guide](https://docs.digitalearthafrica.org/en/latest/sandbox/access.html) if needed. For the full district and long time series, select a larger environment if available; 32 GB RAM is a practical starting point, with actual demand depending on extent and step.
2. Clone your GitHub repository or upload and extract this project. Open notebooks from the project root, beside `workflow_config.json` and `workflow_support.py`.
3. Supply your study boundary and complete integration criteria. The default locations are `mion_data/mion.geojson` and `mion_data/criteria.csv`. See [`docs/DATA_REQUIREMENTS.md`](docs/DATA_REQUIREMENTS.md).
4. Edit `workflow_config.json`. Confirm the AOI, output directory, years, grid, baseline, reporting year, and final performance input.
5. Before the first run, capture the environment and configuration from a terminal in the project root:

   ```bash
   python scripts/capture_environment.py
   python scripts/validate_repository.py
   ```

6. Open notebook 01, select the Python kernel, and run from top to bottom. For a quick acquisition pilot, temporarily set `start_year = end_year = 2020` in its processing-parameter cell. Use a small boundary, inspect the monthly outputs, then restore the configured years before running later stages. The indicators require the full configured history.
7. Continue along the relevant branch above. Restart the kernel between notebooks. Check logs and outputs before moving to the next notebook.

The Sandbox supplies `deafrica_tools` and data-cube configuration. A generic local Jupyter installation needs additional ODC database/index and data-access setup for notebooks 01, 03, and 07. Installing Python packages alone does not configure access to the DE Africa index. Notebook 02 needs the DE Africa temporal tools, but does not query the data cube.

## Try the supplied small example

This example uses an artificial rectangle in northern Ghana, **not the original Mion boundary**. Its criteria mark productivity as degraded when **any** binary indicator is degraded. These rules are illustrative and are not asserted to match the original research or an official reporting method.

From the project root, use the following commands to select the example configuration:

```bash
cp workflow_config.json workflow_config_mion_backup.json
cp examples/workflow_config_demo.json workflow_config.json
```

Then run the relevant notebooks in the Sandbox. The example keeps 2000–2024 so the default 16-year reporting windows remain feasible. Outputs go into `demo_output/`. The original study configuration can be restored with:

```bash
cp workflow_config_mion_backup.json workflow_config.json
```

These commands work in the Sandbox terminal. The same changes can be made with the JupyterLab file editor.

## Local environment

[`environment.yml`](environment.yml) lists the local raster-processing and validation dependencies. It is a **starting environment specification**, not an exact lock of the original Sandbox.

```bash
conda env create -f environment.yml
conda activate land-productivity
jupyter lab
```

Use the [DE Africa tools installation guidance](https://docs.digitalearthafrica.org/en/latest/sandbox/notebooks/Tools/index.html) and configure an ODC index separately for live-data steps. Record the exact installed package versions and the DE Africa tools checkout used for a successful run. For local work with existing rasters, notebooks 04, 05, 06, and 08 do not need data-cube access.

## Adapt the study

| Configuration field | Default | What to change or check |
| --- | --- | --- |
| `study_id` | `mion_data` | Filename-safe study label; it is separate from the output directory |
| `aoi_vector` | `mion_data/mion.geojson` | Your Polygon/MultiPolygon boundary with a known CRS; all features are combined |
| `output_dir` | `mion_data` | Use a fresh directory for a different study or changed method |
| `start_year`, `end_year` | 2000, 2024 | Inclusive acquisition and annual-processing range |
| `output_crs`, `resolution` | EPSG:6933, `[-30, 30]` | Keep one grid throughout; area summaries require a projected CRS in metres |
| `landsat_products` | Landsat 5, 7, 8, 9 SR | Product names must exist in the configured cube |
| `dask_chunks`, `block_size` | 500×500, 512 | Reduce to manage RAM; tile block size must be a multiple of 16 |
| `file_version` | `v01` | Monthly filename version read consistently by later notebooks |
| `annual_metric` | `median` | Alternatives: mean, max, sum; changing the metric changes the scientific interpretation |
| `require_all_months` | `false` | If true, require all 12 monthly pixel values; 12 files are required in either mode |
| `trajectory_window_years`, `report_step_years` | 16, 4 | Consecutive years per trajectory window and spacing of report periods |
| `state_baseline_len`, `state_recent_len` | 13, 3 | Their sum must match the trajectory window length |
| `state_min_baseline_valid`, `state_min_recent_valid` | 10, 2 | Minimum annual pixel observations for state |
| `performance_baseline_start`, `performance_baseline_end` | 2000, 2015 | Fixed baseline for the within-class NDVI maximum |
| `performance_threshold` | 0.5 | Binary low-performance cutoff; justify for your application |
| `assessment_years` | 2015, 2019, 2023 | Years for single-year assessment maps and intervening reporting windows |
| `esa_product`, `esa_time` | `esa_worldcover_2021`, 2021 | Land-cover grouping; consider historical land-cover stability |
| `report_end_year` | 2015 | Must correspond to a trajectory/state window |
| `final_performance_suffix` | `baseline_degraded_binary` | Exact performance product to combine in notebook 08 |
| `criteria_csv` | `mion_data/criteria.csv` | Supply the study's complete eight-scenario Y/N table |
| `skip_existing` | `true` | Used by 01, 04, 05, 06; 02, 03, 07, 08 overwrite their outputs |

Paths in the JSON file are resolved relative to that file. Notebook-specific settings, including the optional trajectory output flags and phenology method, remain visible in the relevant parameter cells.

Default report periods and performance choices are:

| Report end | Trajectory window | State baseline / recent | Possible performance suffix |
| --- | --- | --- | --- |
| 2015 | 2000–2015 | 2000–2012 / 2013–2015 | `baseline_degraded_binary` for 2000–2015, or `assessment_2015_degraded_binary` for 2015 only |
| 2019 | 2004–2019 | 2004–2016 / 2017–2019 | `assessment_2019_degraded_binary`, or `rep2019_2016_2018_degraded_binary` |
| 2023 | 2008–2023 | 2008–2020 / 2021–2023 | `assessment_2023_degraded_binary`, or `rep2023_2020_2022_degraded_binary` |

These performance alternatives use different time supports. Select and report the intended choice explicitly; changing only `report_end_year` does not choose a performance product automatically.

## Methods and interpretation

Read [`docs/METHODS.md`](docs/METHODS.md) before interpreting the maps. In particular:

- Notebook 01 retains the GeoMAD filename, but computes monthly red/NIR geomedians and rolling band medians; it does not export MAD layers.
- Phenology dates use monthly observations. The `_POS_YYYY.tif` raster contains **peak NDVI magnitude (vPOS)**, while CSV `POS` contains a date.
- Notebook 03 compares a peak-window MVC with a differently summarized smoothed peak. The difference is not a validation error.
- Trajectory inference retains the original simple Mann–Kendall variance; tie and autocorrelation adjustments require further methodological work.
- Performance groups pixels by land-cover class alone and uses the observed maximum within the study area. It does not estimate NPP or stratify climate/soil conditions.
- The criteria table determines integration. The example table cannot reproduce an unavailable original decision rule.

## Files and outputs

| Location | Contents |
| --- | --- |
| Project root | Eight notebooks, shared configuration, support functions, README, environment specification |
| `docs/` | Methods, data requirements, validation, and changes made to the supplied notebooks |
| `examples/` | Small polygon, example configuration, blank rule template, illustrative any-indicator rule |
| `scripts/` | Repository validation, synthetic-data checks, environment capture |
| `<output_dir>/data/` | Monthly NDVI GeoTIFFs |
| `<output_dir>/pheno/graph/` | Phenology and MVC products |
| `<output_dir>/annual_ndvi/` | Annual NDVI GeoTIFFs |
| `<output_dir>/trajectory/`, `state/`, `performance/` | Indicator rasters and diagnostics |
| `<output_dir>/final_map_YYYY/` | Integrated map, area CSV, PNGs |
| `<output_dir>/provenance/` | Configuration snapshot and software-version record |

Generated rasters are excluded from normal Git commits by `.gitignore`. Share large result datasets through an appropriate data repository and record their persistent identifiers alongside a code release.

## Troubleshooting

| Symptom | Check or action |
| --- | --- |
| `workflow_support` or configuration not found | Keep the notebooks and shared files together in the project root; restart the kernel there |
| Missing boundary or criteria file | Supply the original inputs, or deliberately select the documented demo configuration |
| Unknown cube product or no matching datasets | Inspect `dc.list_products()` / `dc.list_measurements()` and confirm spatial and temporal overlap |
| Missing annual year / no reporting windows | Confirm 12 monthly files per year and a complete 16-year annual history for the defaults |
| RAM exhausted | Start with a smaller AOI, reduce chunks/block size, and restart between notebooks; 02, 06, and 07 retain substantial arrays in RAM |
| Grid mismatch | Regenerate from one configuration; categorical classes require nearest-neighbour resampling |
| Old-looking results after changing settings | Use a fresh `output_dir`; skip-existing checks do not verify the processing history of old files |
| Unexpected phenology dates or metrics | Check input timestamps, units, monthly coverage, seasonal structure, and the installed `xr_phenology` version |
| Different areas among indicator maps | Compare nodata/valid masks; each total is calculated from that map's valid pixels |

## Prepare a GitHub release

Create a repository such as `land-productivity-geomad`, then upload the **contents** of this folder, keeping the relative layout. GitHub renders the root README and notebooks directly. If using Git, initialize locally and commit only the intended project files before connecting your repository remote.

Before presenting a release as reproducing the original study, include the original AOI and integration criteria where redistribution is permitted, complete a fresh-kernel Sandbox run, and archive its configuration, successful environment, data provenance, and outputs. Fill in the project's author, thesis/publication citation, repository URL, and release DOI when those details are confirmed; none have been invented in this package.

## Attribution and licence

The supplied notebooks declare their code under Apache License 2.0. That declaration is retained in this prepared workflow; see [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE). Keep attribution to Digital Earth Africa and its tools when adapting the code. Data licensing is separate: acknowledge Landsat/USGS and ESA WorldCover according to their respective product documentation, and document the source/licence of any study boundary or added data.

Relevant primary documentation:

- [DE Africa Sandbox access](https://docs.digitalearthafrica.org/en/latest/sandbox/access.html)
- [Landsat Collection 2 surface reflectance](https://docs.digitalearthafrica.org/en/latest/data_specs/Landsat_C2_SR_specs.html)
- [DE Africa tools](https://docs.digitalearthafrica.org/en/latest/sandbox/notebooks/Tools/index.html)
- [`xr_phenology` metrics and options](https://docs.digitalearthafrica.org/en/latest/sandbox/notebooks/Tools/gen/gen/deafrica_tools.temporal.xr_phenology.html)
- [ESA WorldCover product and ODC access](https://docs.digitalearthafrica.org/en/latest/data_specs/ESA_WorldCover_specs.html)

Documentation links were checked on 24 November 2026. Workflow-specific interpretation in this README is based on the supplied code, with methodological limitations stated explicitly.
