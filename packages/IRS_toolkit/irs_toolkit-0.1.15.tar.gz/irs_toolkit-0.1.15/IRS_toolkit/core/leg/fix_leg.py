import warnings
from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta

from IRS_toolkit.core import cash_flow
from IRS_toolkit.utils import core,financial
from IRS_toolkit.utils.constants import VALID_FILL_TYPE,VALID_CONVENTIONS
from IRS_toolkit.utils import schedule
from IRS_toolkit.core.curve import yield_curve
warnings.filterwarnings("ignore")


class FixLeg:
    """
    this class compute the float leg of the swap

        Args:
            nominal (float): notionel amount
            start_date (date): start date
            maturity_date (date): end date
            fix_rate (float): swap fixed rate
            periodicity (int, optional): coupon payment periodicity. Defaults to 3.
            type_fill (str, optional): type of filling schedule. Defaults to "Forward".
    """

    def __init__(
        self,
        nominal:float,
        fix_rate:float,
        schedule:schedule.Schedule,
    ):
        self.date_format = schedule.date_format
        self.nominal = nominal
        self.fix_rate = fix_rate
        self.cashflow_leg_fix = pd.DataFrame()
        self.accrued_coupon_fix = 0
        self.spread = 0
        self.date_convention = schedule.date_convention
        self.schedule_fix = schedule

    def compute_cash_flow(self, date_value, spreadHC=0.0, spreadGC=0.0):
        """
        this function compute the float cash flows

        """
        self.cashflow_leg_fix = self.schedule_fix.df.copy()
        self.cashflow_leg_fix["cashflow"] = (
            float(self.nominal) * float(self.fix_rate) * self.cashflow_leg_fix["day_count"]
        )
        """        for i in range(0, len(self.cashflow.end_date) - 1, 1):
            if (
                pd.Timestamp(date_value) > self.cashflow.start_date[i]
                and pd.Timestamp(date_value) < self.cashflow.end_date[i]
            ):
                self.cashflow.day_count[i] = day_count(
                    pd.Timestamp(date_value), self.cashflow.end_date[i]
                )
                self.cashflow["cashflow"][i] = (
                    self.nominal * self.fix_rate * self.cashflow.day_count[i]
                )"""

        coupon_period = core.day_count(
            core.previous_coupon_date(self.cashflow_leg_fix["start_date"], self.cashflow_leg_fix["end_date"], pd.Timestamp(date_value)),
            pd.Timestamp(date_value),
            self.date_convention,
        )
        self.accrued_coupon_fix = self.nominal * self.fix_rate * coupon_period
        self.spreadHC = financial.spread_amount(
            self.cashflow_leg_fix["start_date"], self.cashflow_leg_fix["end_date"], self.nominal, spreadHC, valuation_date=date_value, convention=self.date_convention
        )
        self.spreadGC = financial.spread_amount(
            self.cashflow_leg_fix["start_date"], self.cashflow_leg_fix["end_date"], self.nominal, spreadGC, valuation_date=date_value, convention=self.date_convention
        )
        self.spread = self.spreadGC + self.spreadHC

    def discount_cashflow(
        self, discount_curve:yield_curve.YieldCurve, date_valo:datetime=None, relative_delta:relativedelta=None
    ):
        """
        used to discount future cashflows to the date_valo

        Args:
            discount_curve (curve): yield curve
            date_valo (date, optional): valuation date. Defaults to None.
        """
        relative_delta=relativedelta(days=0)

        dates = [date_obj.strftime(self.date_format) for date_obj in self.cashflow_leg_fix.end_date]
        amounts = self.cashflow_leg_fix["cashflow"].to_list()

        discount_cashflow_fix = cash_flow.cash_flow(dates, amounts)

        if date_valo:
            discount_cashflow_fix.npv(date_valo, discount_curve, relative_delta)
        else:
            discount_cashflow_fix.npv(discount_curve.date_curve, discount_curve, relative_delta)
        self.cashflow_leg_fix[["discount_cashflow_amounts", "DF"]] = (
            discount_cashflow_fix.cashflows[["discount_cashflow_amounts", "DF"]].values
        )
        self.NPV = discount_cashflow_fix.NPV

