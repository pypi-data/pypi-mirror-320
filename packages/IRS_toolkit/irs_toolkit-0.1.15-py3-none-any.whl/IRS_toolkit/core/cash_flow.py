import warnings

import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

from IRS_toolkit.utils import core
from IRS_toolkit.core.curve import yield_curve
from IRS_toolkit.utils.constants import VALID_CONVENTIONS

warnings.filterwarnings("ignore")


class cash_flow:
    """
    cash flows handling
        Args:
            dates (Datframe): dates
            amounts (Dataframe): coupons
    """

    def __init__(self, dates:list[datetime], amounts:list[float],date_format="%Y-%m-%d",date_convention:VALID_CONVENTIONS="ACT/360"):
        dates = [datetime.strptime(dt, date_format) if isinstance(dt, str) else dt for dt in dates]
        self.cashflows = pd.DataFrame(
            {"cash_flow_date": dates, "cash_flow_amount": amounts}
        )
        self.date_convention = date_convention

    def npv(self, valuation_date:datetime, curve:yield_curve.YieldCurve, relative_delta=None,date_format="%Y-%m-%d"):
        """
        Compute the Net present value

        Args:
            valuation_date (date): valuation date
            curve (curve): yield curve

        Returns:
            float: Net present value of future cash flows
        """
        if relative_delta is None:
            relative_delta=relativedelta(days=0)
        self.cashflows["discount_cashflow_amounts"] = 0
        self.cashflows["DF"] = 0

        valuation_date = datetime.strptime(valuation_date, date_format) if isinstance(valuation_date, str) else valuation_date
        valuation_date = valuation_date + timedelta(days=1)

        for ind, dt in self.cashflows.iterrows():
            if dt.cash_flow_date > valuation_date:
                self.cashflows.loc[ind, "DF"] = 1 / (
                    1
                    + curve.forward_rates(
                        valuation_date, dt.cash_flow_date, relative_delta
                    )
                ) ** (core.day_count(valuation_date, dt.cash_flow_date,self.date_convention))

        self.cashflows["discount_cashflow_amounts"] = (
            self.cashflows.DF * self.cashflows.cash_flow_amount
        )
        self.NPV = self.cashflows["discount_cashflow_amounts"].sum()
        return self.cashflows["discount_cashflow_amounts"].sum()

    # wighted present value for bonds
    def wpv(self, valuation_date:datetime, curve:yield_curve.YieldCurve, relative_delta=None,date_format="%Y-%m-%d"):
        """
        Weighted Net present value

        Args:
            valuation_date (date): valuation date
            curve (curve): yield curve

        Returns:
            float: time weightide Net present value of future cash flows
        """
        if relative_delta is None:
            relative_delta=relativedelta(days=0)

        self.cashflows["wdiscount_cashflow_amounts"] = 0
        self.cashflows["DF"] = 0

        valuation_date = datetime.strptime(valuation_date, date_format) if isinstance(valuation_date, str) else valuation_date

        for ind, dt in self.cashflows.iterrows():
            if dt.cash_flow_date > valuation_date:
                self.cashflows.loc[ind, "DF"] = 1 / (
                    1
                    + curve.forward_rates(
                        valuation_date, dt.cash_flow_date, relative_delta
                    )
                ) ** (core.day_count(valuation_date, dt.cash_flow_date))

        self.cashflows["wdiscount_cashflow_amounts"] = (
            self.cashflows.DF
            * self.cashflows.cash_flow_amount
            * self.cashflows.cash_flow_date.apply(
                lambda x: core.day_count(valuation_date, x, self.date_convention)
            )
        )
        self.WPV = (self.cashflows["wdiscount_cashflow_amounts"]).sum()
        return self.cashflows["wdiscount_cashflow_amounts"].sum()
