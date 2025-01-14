import datamazing.pandas as pdz
import pandas as pd

from .masterdata_manager import MasterdataManager


class PlantManager(MasterdataManager):
    """
    Manager which simplifies the process of getting plants from masterdata.
    """

    def __init__(
        self,
        db: pdz.Database,
        time_interval: pdz.TimeInterval,
        resolution: pd.Timedelta,
        cache_masterdata: bool = False,
    ) -> None:
        self.db = db
        self.time_interval = time_interval
        self.resolution = resolution
        self.cache_masterdata = cache_masterdata

    def get_plants(
        self,
        filters: dict = {},
        columns: list | None = None,
    ) -> pd.DataFrame:
        """Gets the plants for a given plant type.
        Filters for plants valid at the end of time interval.
        Filters by default for plants in operation.
        """
        default_columns = [
            "plant_id",
            "masterdata_gsrn",
            "datahub_gsrn_e18",
            "installed_power_MW",
            "price_area",
            "is_tso_connected",
            "valid_from_date_utc",
            "valid_to_date_utc",
        ]
        if not columns:
            columns = default_columns
        else:
            columns = list(set(default_columns + columns))
        return self.get_data("masterdataPlant", filters=filters, columns=columns)

    def get_installed_power_timeseries(self, gsrn: str) -> pd.DataFrame:
        """Gets the installed power timeseries for a plant."""

        df_times = self.time_interval.to_range(self.resolution).to_frame(
            index=False, name="time_utc"
        )

        # explode plant to time series
        df_plant = self.get_operational_entities("masterdataPlant")
        df_plant = df_plant.query(f"masterdata_gsrn == '{gsrn}'")

        df_plant = pdz.merge(
            df_times,
            df_plant,
            left_time="time_utc",
            right_period=("valid_from_date_utc", "valid_to_date_utc"),
        )

        return df_plant.filter(["time_utc", "installed_power_MW"]).reset_index(
            drop=True
        )

    def _get_corrected_installed_power(
        self, gsrn: str, df_invalid_periods: pd.DataFrame
    ):
        df_times = self.time_interval.to_range(self.resolution).to_frame(
            index=False, name="time_utc"
        )
        df = self.get_installed_power_timeseries(gsrn=gsrn)

        # explode invalid periods to time series
        df_invalid_periods = df_invalid_periods.query(f"masterdata_gsrn == '{gsrn}'")
        df_invalid_periods = pdz.merge(
            df_times,
            df_invalid_periods,
            left_time="time_utc",
            right_period=("start_date_utc", "end_date_utc"),
        )

        df = pdz.merge(
            df,
            df_invalid_periods,
            on="time_utc",
            how="left",
        )

        # correct installed power for invalid periods
        df["installed_power_MW"] = df["installed_power_MW"].where(
            df["corrected_installed_power_MW"].isnull(),
            df["corrected_installed_power_MW"],
        )

        df = df[["time_utc", "installed_power_MW"]]

        return df
