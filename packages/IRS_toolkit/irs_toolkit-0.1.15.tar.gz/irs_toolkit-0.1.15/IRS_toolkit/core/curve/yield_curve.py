# Standard library imports
import warnings
from datetime import datetime, timedelta

# Third-party imports
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

# Local/application imports
from IRS_toolkit.utils import core
from IRS_toolkit.utils.constants import VALID_COUPON_FREQUENCY,VALID_TENORS,VALID_CONVENTIONS,pay_frequency,TIMEZONE_PARIS

# Configure warnings
warnings.filterwarnings("ignore")


class YieldCurve:
    """
       A class for handling yield curves used in pricing and preparing
    zero-coupon curves for cash flow computation and discounting.
        Args:
               curve (dataframe): dataframe
               date_curve (date): date curve

        Attributs:
                date : curve date
                df : a dataframe that contains dates and ZC rates and Dfs

        Functions:
                setup() : create the dataframe and interpolate rate
                ForwardRate(begin,end) : compute the forward rate for two giving dates
                Bootstrap() : compute the ZC curve using the formula refer to notion appendix
                monthly_avg_daily() : compute the monthly average of instantaneous forward rates  using spot ZC curve


    """


    def __init__(self, list_tenor:list[str], list_rate:list[float], date_curve:datetime=None, date_convention:VALID_CONVENTIONS="ACT/360",date_format="%Y-%m-%d",data_base=1):
        """Initialize a YieldCurve instance.
        
        Args:
            list_tenor (list[str]): List of tenors (e.g. ["1M", "3M", "6M", "1Y"])
            list_rate (list[float]): List of corresponding rates
            date_curve (datetime, optional): Reference date for the curve. Defaults to None.
            convention (VALID_CONVENTIONS, optional): Day count convention. Defaults to "ACT/360".
        """
        self.base_data=data_base
        new_list_rate = [x / data_base for x in list_rate]

        # Store input parameters
        self.list_tenor = list_tenor
        self.list_rate = new_list_rate
        self.date_curve = date_curve
        self.date_convention = date_convention
        self.date_format=date_format

        # Create initial dataframe with input tenors and rates
        df = pd.DataFrame({
            "TENOR": ["0D"] + self.list_tenor,  # Add 0D tenor at start
            "STRIPPEDRATES": [np.nan] + self.list_rate  # Add NaN rate for 0D
        })

        # Add dates if date_curve is provided
        if date_curve is not None:
            df["AS_OF_DATE"] = date_curve
            df["DATE"] = pd.to_datetime(df["AS_OF_DATE"] + df["TENOR"].apply(core.tenor_to_period))
            
            # Calculate periods and day counts
            df["PERIOD"] = (df["DATE"] - self.date_curve).apply(lambda x: x.days)
            df["DAY_COUNT"] = df.apply(
                lambda x: core.day_count(self.date_curve, x["DATE"], convention=self.date_convention), 
                axis=1
            )

        df.sort_index(inplace=True)
        self.df = df

        # Create interpolated curve
        interpolated_df = df.copy()
        
        # Add relative date columns
        interpolated_df["RELATIVEDELTA"] = interpolated_df["TENOR"].apply(core.tenor_to_period)
        interpolated_df["RELATIVE_DATE"] = interpolated_df["RELATIVEDELTA"].apply(
            lambda x: (self.date_curve + x)
        )
        interpolated_df["PERIOD"] = interpolated_df["RELATIVE_DATE"].apply(
            lambda x: (x - self.date_curve).days
        )

        # Create daily periods and interpolate rates
        daily_periods = pd.DataFrame({
            "PERIOD": np.arange(1, max(interpolated_df["PERIOD"]) + 1)
        })
        interpolated_df = daily_periods.merge(interpolated_df, "left")
        interpolated_df["STRIPPEDRATES"] = interpolated_df["STRIPPEDRATES"].astype(float)

        
        # Add dates and day counts
        interpolated_df["DATE"] = interpolated_df["PERIOD"].apply(lambda x: self.date_curve + timedelta(x))
        interpolated_df["DAY_COUNT"] = interpolated_df.apply(
            lambda x: core.day_count(self.date_curve, x["DATE"], convention=self.date_convention),
            axis=1
        )

        interpolated_df.set_index("DAY_COUNT", inplace=True,drop=False)
        
        interpolated_df["STRIPPEDRATES"].interpolate(method="cubic", inplace=True, limit_direction="forward")
        #print(interpolated_df.head())
        # Add 0D row at start
        zero_day = pd.DataFrame([{
            "PERIOD": 0,
            "TENOR": "0D",
            "STRIPPEDRATES": np.nan,
            "DATE": self.date_curve,
            "DAY_COUNT": 0.0
        }])
        
        interpolated_df = pd.concat([zero_day, interpolated_df])
        #print(interpolated_df.head())
        interpolated_df.sort_index(inplace=True)
        # Keep only needed columns in final interpolated curve
        self.df_interpolated = interpolated_df[["TENOR", "STRIPPEDRATES", "PERIOD", "DATE","DAY_COUNT"]]


    def forward_rates(
        self,
        begin:datetime,
        end:datetime,
        relative_delta=None,
    ):
        """
        compute forward rates

        Args:
            begin (date): start date
            end (date): end date

        Returns:
            float: forward rate
        """

        if relative_delta is None:
            relative_delta=relativedelta(days=0)

        # try:
        # Convert string dates to datetime, if necessary
        begin_date = datetime.strptime(begin, self.date_format) if isinstance(begin, str) else begin
        end_date = datetime.strptime(end, self.date_format) if isinstance(end, str) else end
        end_date = end_date + relative_delta

        # Validation of date ranges
        if end_date < self.date_curve or begin_date >= end_date:
            return None

        # Extract zero-coupon rates for the given dates
        zc_begin = self.df[self.df["DATE"] == begin_date.strftime("%Y-%m-%d")]["ZC"]
        zc_end = self.df[self.df["DATE"] == end_date.strftime("%Y-%m-%d")]["ZC"]

        if zc_begin.empty:
            return None  # Return None if no ZC rates found for the dates
        if zc_end.empty:
            return None  # Return None if no ZC rates found for the dates

        # Calculate discount factors (DF)
        num = (1 + zc_end.iloc[0]) ** core.day_count(self.date_curve, end_date,self.date_convention)
        den = (1 + zc_begin.iloc[0]) ** core.day_count(self.date_curve, begin_date,self.date_convention)
        result = (num / den) ** (
            1.0 / core.day_count(begin_date, end_date, self.date_convention)
        ) - 1

        # Compute forward rate using the formula (DF2/DF1)^(1/delta(t)) - 1
        return result

        # except Exception as e:
        #     print(f"An error occurred while calculating forward rates: {e}")
        #     return None  # Return a default value or None

    def bootstrap(
        self, coupon_frequency:VALID_COUPON_FREQUENCY, zc_curve=None
    ):
        """
        It Transform the yield curve to a zero-coupon (ZC) curve.

        This function processes the initial curve data to compute zero-coupon rates and discount factors.
        It handles different date calculations based on whether the current day is the first of the month.
        """
        if zc_curve is None:
            zc_curve = self.df.copy()
        
        coupon_periods = int(12/pay_frequency[coupon_frequency])*30
        coupon_frequency_date = pay_frequency[coupon_frequency]
        
        zc_date = [
            self.date_curve + relativedelta(months=i * coupon_frequency_date)
            for i in range(coupon_periods + 1)
        ]
        zc_curve_before = zc_curve[zc_curve["DATE"] < zc_date[1]]
        zc_curve_before["PERIOD"] = (zc_curve_before["DATE"] - self.date_curve).apply(
            lambda x: x.days
        )

        zc_curve_before["Coupon_period"] = zc_curve_before["DAY_COUNT"]

        zc_curve_before["ZC"] = (
            1 + zc_curve_before["STRIPPEDRATES"] * zc_curve_before["Coupon_period"]
        ) ** (1 / zc_curve_before["Coupon_period"]) - 1
        zc_curve_before["DF"] = (
            1 / (1 + zc_curve_before["ZC"]) ** (zc_curve_before["Coupon_period"])
        )

        zc_curve_temp = zc_curve[zc_curve["DATE"].isin(zc_date[1:])]
        zc_curve_temp.reset_index(drop=True, inplace=True)

        zc_curve_temp["Date_lagg"] = zc_curve_temp["DATE"].shift()
        zc_curve_temp["Date_lagg"].fillna(self.date_curve, inplace=True)

        zc_curve_temp["Coupon_period"] = zc_curve_temp.apply(
            lambda x: core.day_count(x["Date_lagg"], x["DATE"], self.date_convention), axis=1
        )
        zc_curve_temp["DF"] = 1
        for i in range(zc_curve_temp.shape[0]):
            zc_curve_temp.loc[i, "DF"] = (
                1
                - (
                    zc_curve_temp["STRIPPEDRATES"][i]
                    * zc_curve_temp["Coupon_period"]
                    * zc_curve_temp["DF"]
                )[:i].sum()
            ) / (
                1
                + zc_curve_temp["STRIPPEDRATES"][i] * zc_curve_temp["Coupon_period"][i]
            )
        zc_curve_temp["ZC"] = (1 / zc_curve_temp["DF"]) ** (
            1 / zc_curve_temp["DAY_COUNT"]
        ) - 1
        #print(zc_curve_temp)
        #print(zc_curve_before)
        zc_curve = pd.concat([zc_curve_before, zc_curve_temp[zc_curve_before.columns]])
        zc_curve.reset_index(inplace=True, drop=True)
        self.df = zc_curve.merge(zc_curve.dropna(), "left")
        dates = pd.DataFrame(
            {
                "DATE": pd.date_range(
                    start=self.date_curve,
                    end=self.date_curve + relativedelta(years=30),
                    freq="D",
                ),
            }
        )

        self.df = dates.merge(zc_curve, "left")
        self.df["DF"] = self.df["DF"].astype(float)
        self.df["DF"].interpolate(
            method="cubic", inplace=True, limit_direction="forward"
        )
        self.df["PERIOD"] = (self.df["DATE"] - self.date_curve).apply(lambda x: x.days)
        self.df["DAY_COUNT"] = self.df.apply(
            lambda x: core.day_count(self.date_curve, x["DATE"], self.date_convention), axis=1
        )
        self.df["ZC"] = (1 / self.df["DF"]) ** (1 / self.df["DAY_COUNT"]) - 1
        self.df["STRIPPEDRATES"].interpolate(
            method="cubic", inplace=True, limit_direction="forward"
        )
        self.df.at[0, "DF"] = 1
        self.df.at[0, "Coupon_period"] = 0

    def monthly_avg_daily(
        self, start_date:datetime, end_date:datetime, frequency:str="D", relative_delta=None
    ):
        """

        Args:
            start_date (date): start date
            end_date (date): end date

        Returns:
            Dataframe: Monthly average of daily forward rates
        """
        if relative_delta is None:
            relative_delta=relativedelta(days=0)

        if frequency == "Between Tenor":
            date_list = []
            for tenor in VALID_TENORS:
                date_forward = datetime.strptime(start_date, self.date_format) + core.tenor_to_period(tenor)
                date_list.append(date_forward)
        else:
            date_list = pd.date_range(start_date, end=end_date, freq=frequency)

        foreward_df = pd.DataFrame([date_list[:-1], date_list[1:]]).T
        foreward_df.columns = ["start_date", "end_date"]
        foreward_list = []
        for i, j in zip(date_list[:-1], date_list[1:]):
            foreward_list.append(self.ForwardRates(i, j, relative_delta))
        foreward_df["foreward_ZC"] = foreward_list
        foreward_df["day_count"] = foreward_df.apply(
            lambda x: core.day_count(x["start_date"], x["end_date"]), axis=1
        )
        foreward_df["foreward_simple"] = foreward_df.apply(
            lambda x: core.ZC_to_simplerate(x["foreward_ZC"], x["day_count"]), axis=1
        )

        foreward_df = foreward_df.set_index("start_date")
        foreward_df.index = pd.to_datetime(foreward_df.index)

        return foreward_df.groupby(pd.Grouper(freq="M")).mean(), foreward_df

    def bootstrap_12m_semi_yearly_coupon(self, coupon_frequency:VALID_COUPON_FREQUENCY):
        """
        Transform the yield curve to a zero-coupon (ZC) curve.

        This function processes the initial curve data to compute zero-coupon rates and discount factors.
        It handles different date calculations based on whether the current day is the first of the month.
        """
        zc_curve = self.df.copy()

        coupon_periods = {
            "quarterly": 29 * 4,
            "yearly": 29,
            "monthly": 29 * 12,
            "semi_annual": 29 * 2,
        }[coupon_frequency]
        coupon_frequency_date = {
            "quarterly": pd.DateOffset(months=3),  # "3MS",
            "yearly": pd.DateOffset(years=1),
            "monthly": pd.DateOffset(months=1),
            "semi_annual": pd.DateOffset(months=6),
        }[coupon_frequency]

        # if self.date.day == 1:
        zc_date1 = pd.date_range(
            self.date.strftime(self.date_format),
            periods=2,
            freq=pd.DateOffset(months=6),
        )

        zc_date2 = pd.date_range(
            (self.date + pd.DateOffset(years=1)).strftime(self.date_format),
            periods=coupon_periods,
            freq=coupon_frequency_date,
        )

        zc_date = zc_date1.append(zc_date2)

        zc_curve_before = zc_curve[zc_curve["Date"] < zc_date[1]]
        zc_curve_before["Period"] = (zc_curve_before["Date"] - self.date).apply(
            lambda x: x.days
        )

        zc_curve_before["Coupon_period"] = zc_curve_before["day_count"]

        zc_curve_before["ZC"] = (
            1 + zc_curve_before["StrippedRates"] * zc_curve_before["Coupon_period"]
        ) ** (1 / zc_curve_before["Coupon_period"]) - 1
        zc_curve_before["DF"] = (
            1 / (1 + zc_curve_before["ZC"]) ** (zc_curve_before["Coupon_period"])
        )

        zc_curve_temp = zc_curve[zc_curve["Date"].isin(zc_date)]
        zc_curve_temp.reset_index(drop=True, inplace=True)
        zc_curve_temp["Date_lagg"] = zc_curve_temp["Date"].shift()
        zc_curve_temp["Date_lagg"].fillna(self.date, inplace=True)
        zc_curve_temp["Coupon_period"] = zc_curve_temp.apply(
            lambda x: core.day_count(x["Date_lagg"], x["Date"]), axis=1
        )
        zc_curve_temp["DF"] = 1
        for i in range(zc_curve_temp.shape[0]):
            zc_curve_temp.loc[i, "DF"] = (
                1
                - (
                    zc_curve_temp["StrippedRates"][i]
                    * zc_curve_temp["Coupon_period"]
                    * zc_curve_temp["DF"]
                )[:i].sum()
            ) / (
                1
                + zc_curve_temp["StrippedRates"][i] * zc_curve_temp["Coupon_period"][i]
            )
        zc_curve_temp["ZC"] = (1 / zc_curve_temp["DF"]) ** (
            1 / zc_curve_temp["day_count"]
        ) - 1
        zc_curve = pd.concat([zc_curve_before, zc_curve_temp[zc_curve_before.columns]])
        zc_curve.reset_index(inplace=True, drop=True)
        self.df = self.df.merge(zc_curve.dropna(), "left")
        dates = pd.DataFrame(
            {
                "Date": pd.date_range(
                    start=self.date + relativedelta(days=1),
                    end=self.date + relativedelta(years=30),
                    freq="D",
                ),
            }
        )

        self.df = dates.merge(self.df, "left")
        self.df["DF"] = self.df["DF"].astype(float)
        self.df["DF"].interpolate(
            method="cubic", inplace=True, limit_direction="forward"
        )
        self.df["Period"] = (self.df["Date"] - self.date).apply(lambda x: x.days)
        self.df["day_count"] = self.df.apply(
            lambda x: core.day_count(self.date, x["Date"]), axis=1
        )
        self.df["ZC"] = (1 / self.df["DF"]) ** (1 / self.df["day_count"]) - 1
        self.df["StrippedRates"].interpolate(
            method="cubic", inplace=True, limit_direction="forward"
        )
