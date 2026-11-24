"""Shared configuration and input checks for the research notebooks.

Scientific calculations remain visible in their respective notebooks. Heavy
geospatial dependencies are imported only by the functions that use them.
"""
from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path


def load_config(path="workflow_config.json"):
    """Load settings and resolve paths relative to the configuration file."""
    config_path = Path(path).resolve()
    if not config_path.is_file():
        raise FileNotFoundError(
            "Open the notebook from the repository root, beside workflow_config.json."
        )
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    if cfg["start_year"] > cfg["end_year"]:
        raise ValueError("start_year must be <= end_year")
    if cfg["annual_metric"] not in {"mean", "median", "max", "sum"}:
        raise ValueError("annual_metric must be mean, median, max or sum")
    for key in ("trajectory_window_years", "report_step_years", "block_size",
                "state_baseline_len", "state_recent_len"):
        if not isinstance(cfg[key], int) or isinstance(cfg[key], bool) or cfg[key] < 1:
            raise ValueError(f"{key} must be a positive integer")
    if cfg["block_size"] % 16:
        raise ValueError("block_size must be a multiple of 16 for tiled GeoTIFFs")
    if cfg["trajectory_window_years"] != cfg["state_baseline_len"] + cfg["state_recent_len"]:
        raise ValueError("Trajectory and state periods must have the same total length")
    if len(cfg["resolution"]) != 2 or cfg["resolution"][0] >= 0 or cfg["resolution"][1] <= 0:
        raise ValueError("Use resolution [-pixel_height, pixel_width], e.g. [-30, 30]")
    if not 1 <= cfg["state_min_baseline_valid"] <= cfg["state_baseline_len"]:
        raise ValueError("state_min_baseline_valid exceeds the baseline length")
    if not 1 <= cfg["state_min_recent_valid"] <= cfg["state_recent_len"]:
        raise ValueError("state_min_recent_valid exceeds the recent length")
    if not cfg["start_year"] <= cfg["performance_baseline_start"] <= cfg["performance_baseline_end"] <= cfg["end_year"]:
        raise ValueError("The performance baseline must lie within the analysis years")
    if any(y < cfg["start_year"] or y > cfg["end_year"] for y in cfg["assessment_years"]):
        raise ValueError("Assessment years must lie within the analysis years")
    first_report = cfg["start_year"] + cfg["trajectory_window_years"] - 1
    if cfg["report_end_year"] not in range(first_report, cfg["end_year"] + 1, cfg["report_step_years"]):
        raise ValueError("report_end_year must match a trajectory/state reporting window")
    if not cfg["study_id"] or any(c in cfg["study_id"] for c in "/\\"):
        raise ValueError("study_id must be a filename-safe label without directory separators")
    for key in ("output_dir", "aoi_vector", "criteria_csv"):
        cfg[key] = str((config_path.parent / cfg[key]).resolve())
    return cfg


def require_files(*paths):
    """Stop early with the exact filenames a user needs to supply or generate."""
    missing = [str(p) for p in paths if not Path(p).is_file()]
    if missing:
        raise FileNotFoundError("Required input(s) missing:\n" + "\n".join(missing))


def load_aoi(vector_path):
    """Read every polygon, validate its CRS, and return a union in EPSG:4326."""
    import geopandas as gpd
    require_files(vector_path)
    gdf = gpd.read_file(vector_path)
    if gdf.empty or gdf.crs is None:
        raise ValueError("Supply a non-empty polygon boundary with a defined CRS")
    if gdf.geometry.isna().any() or gdf.geometry.is_empty.any() or not gdf.geometry.is_valid.all():
        raise ValueError("The AOI contains missing, empty or invalid geometries")
    if not gdf.geom_type.isin(["Polygon", "MultiPolygon"]).all():
        raise ValueError("The AOI must contain Polygon or MultiPolygon features")
    gdf = gdf.to_crs("EPSG:4326")
    geom = gdf.geometry.union_all() if hasattr(gdf.geometry, "union_all") else gdf.unary_union
    return gpd.GeoDataFrame(geometry=[geom], crs="EPSG:4326")


def assert_same_grid(paths):
    """Reject shifted or differently projected rasters before combining pixels."""
    import rasterio
    paths = list(paths)
    if not paths:
        raise ValueError("No rasters supplied")
    require_files(*paths)
    with rasterio.open(paths[0]) as ref:
        signature = (ref.crs, ref.transform, ref.width, ref.height)
    for path in paths[1:]:
        with rasterio.open(path) as src:
            if (src.crs, src.transform, src.width, src.height) != signature:
                raise ValueError(f"Raster grid mismatch: {path}")


def read_criteria(path):
    """Require one explicit Y/N result for all eight binary indicator scenarios."""
    require_files(path)
    columns = ["Trend", "State", "Performance", "Degraded"]
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not set(columns).issubset(reader.fieldnames):
            raise ValueError("Criteria CSV must contain: " + ", ".join(columns))
        rules = {}
        for row in reader:
            vals = [str(row.get(c, "")).strip().upper() for c in columns]
            if any(v not in {"Y", "N"} for v in vals):
                raise ValueError("Every criteria cell must be Y or N; fill the template first")
            scenario = tuple(int(v == "Y") for v in vals[:3])
            if scenario in rules:
                raise ValueError(f"Duplicate criteria scenario: {scenario}")
            rules[scenario] = int(vals[3] == "Y")
    if set(rules) != set(itertools.product((0, 1), repeat=3)):
        raise ValueError("Criteria CSV must contain all eight distinct scenarios")
    return rules
