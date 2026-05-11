from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

from app.core.config import settings
from app.core.constants import MOON_PHASE_MAP


@dataclass
class ModelBundle:
    model: RandomForestRegressor | None
    version: str
    rmse: float | None
    fallback_used: bool
    feature_columns: list[str]


FEATURE_COLUMNS = [
    "lag_1",
    "lag_2",
    "lag_3",
    "air_pressure_hpa",
    "temperature_c",
    "moon_phase_numeric",
    "moon_illumination",
    "gravity_factor",
    "hour_of_day",
    "day_of_week",
]


def _artifact_path(station_id: int) -> Path:
    base_dir = Path(settings.model_artifacts_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / f"station_{station_id}_rf.joblib"


def build_training_frame(readings: pd.DataFrame, moon_positions: pd.DataFrame) -> pd.DataFrame:
    if readings.empty:
        return pd.DataFrame()

    readings = readings.sort_values("recorded_at").copy()
    moon_positions = moon_positions.sort_values("calculated_at").copy()
    if moon_positions.empty:
        readings["moon_phase"] = "New Moon"
        readings["moon_illumination"] = 0.0
        readings["gravity_factor"] = 1.0
    else:
        readings = pd.merge_asof(
            readings,
            moon_positions,
            left_on="recorded_at",
            right_on="calculated_at",
            direction="backward",
        )

    readings["lag_1"] = readings["water_level_cm"].shift(1)
    readings["lag_2"] = readings["water_level_cm"].shift(2)
    readings["lag_3"] = readings["water_level_cm"].shift(3)
    readings["hour_of_day"] = readings["recorded_at"].dt.hour
    readings["day_of_week"] = readings["recorded_at"].dt.dayofweek
    readings["moon_phase_numeric"] = readings["moon_phase"].map(MOON_PHASE_MAP).fillna(0)
    readings["target"] = readings["water_level_cm"].shift(-1)
    readings = readings.dropna(subset=FEATURE_COLUMNS + ["target"])
    return readings


def train_model(readings: pd.DataFrame, moon_positions: pd.DataFrame, station_id: int) -> ModelBundle:
    training_df = build_training_frame(readings, moon_positions)
    if len(training_df) < 30:
        return ModelBundle(
            model=None,
            version="fallback-v1",
            rmse=None,
            fallback_used=True,
            feature_columns=FEATURE_COLUMNS,
        )

    split_index = max(int(len(training_df) * 0.8), 1)
    train_df = training_df.iloc[:split_index]
    test_df = training_df.iloc[split_index:]

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(train_df[FEATURE_COLUMNS], train_df["target"])

    rmse = None
    if not test_df.empty:
        predictions = model.predict(test_df[FEATURE_COLUMNS])
        mse = mean_squared_error(test_df["target"], predictions)
        rmse = float(np.sqrt(mse))

    version = "rf-v1"
    bundle = {
        "model": model,
        "version": version,
        "rmse": rmse,
        "feature_columns": FEATURE_COLUMNS,
    }
    joblib.dump(bundle, _artifact_path(station_id))
    return ModelBundle(
        model=model,
        version=version,
        rmse=rmse,
        fallback_used=False,
        feature_columns=FEATURE_COLUMNS,
    )


def load_model(station_id: int) -> ModelBundle | None:
    path = _artifact_path(station_id)
    if not path.exists():
        return None
    payload = joblib.load(path)
    return ModelBundle(
        model=payload["model"],
        version=payload["version"],
        rmse=payload.get("rmse"),
        fallback_used=False,
        feature_columns=payload.get("feature_columns", FEATURE_COLUMNS),
    )
