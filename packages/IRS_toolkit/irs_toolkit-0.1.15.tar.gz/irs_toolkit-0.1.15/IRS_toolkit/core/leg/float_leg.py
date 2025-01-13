import warnings

import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta

from IRS_toolkit.core import cash_flow
from IRS_toolkit.utils import core,financial,schedule
from IRS_toolkit.core.curve import yield_curve,compounded
warnings.filterwarnings("ignore")


class FloatLeg:
    """
    this class compute the float leg of the swap

        Args:
            nominal (float): notionel amount
            start_date (date): start date
            maturity_date (date): end date
            curve (curve): yield curve
            periodicity (int, optional): coupon payment periodicity. Defaults to 3.
            type_fill (str, optional): type of filling schedule. Defaults to "Forward".
    """

    def __init__(
        self,
        nominal,
        yield_curve_object:yield_curve.YieldCurve,
        schedule:schedule.Schedule=None,
        ESTR_coumpounded:compounded.Compounded=None,
        relative_delta=None,
    ):
        self.schedule_float = schedule
        self.date_format = schedule.date_format
        self.nominal = nominal
        self.start_date = schedule.start_date
        self.maturity_date = schedule.maturity_date
        self.yield_curve_object=yield_curve_object
        self.ESTR_coumpounded = ESTR_coumpounded
        self.cashflow_leg_float = pd.DataFrame()
        self.accrued_coupon_float = 0
        self.date_convention = schedule.date_convention
        if relative_delta is None:
            relative_delta=relativedelta(days=0)
        self.relative_delta = relative_delta

    def compute_cash_flow(self, date_value:datetime):
        """
        this function computes the float cash flows

        Args:
            date_value (date): used to split the into accrued coupon and rest
        """

        self.cashflow_leg_float = self.schedule_float.df.copy()
        self.cashflow_leg_float["forward_zc"] = self.cashflow_leg_float.apply(
            lambda x: self.yield_curve_object.forward_rates(
                x["start_date"], x["end_date"], self.relative_delta
            ),
            axis=1,
        )
        # here we want to know which coupon we are computing so that we can split to float coupon and accured coupon

        for i in range(0, len(self.cashflow_leg_float.end_date), 1):
            if (
                pd.Timestamp(date_value) > list(self.cashflow_leg_float.start_date)[i]
                and pd.Timestamp(date_value) < list(self.cashflow_leg_float.end_date)[i]
            ):
                self.cashflow_leg_float["forward_zc"][self.cashflow_leg_float.index[i]] = (
                    self.yield_curve_object.forward_rates(
                        pd.Timestamp(date_value),
                        list(self.cashflow_leg_float.end_date)[i],
                        self.relative_delta,
                    )
                )
                self.cashflow_leg_float.day_count[self.cashflow_leg_float.index[i]] = core.day_count(
                    pd.Timestamp(date_value),
                    list(self.cashflow_leg_float.end_date)[i],
                    self.date_convention,
                )

        self.cashflow_leg_float["forward_simple_rate"] = self.cashflow_leg_float.apply(
            lambda x: financial.zc_to_simplerate(x["forward_zc"], x["day_count"]), axis=1
        )

        self.cashflow_leg_float["cashflow"] = self.nominal * (
            (1 + self.cashflow_leg_float.forward_zc) ** (self.cashflow_leg_float.day_count) - 1
        )

        self.accrued_coupon_float = self.accrued_coupon(
            valuation_date=date_value
        )

    def discount_cashflow(
        self, discount_curve, date_valo=None, relative_delta=None
    ):
        """
        used to discount future cashflows to the date_valo

        Args:
            discount_curve (curve): yield curve
            date_valo (date, optional): valuation date. Defaults to None.
        """

        if relative_delta is None:
            relative_delta=relativedelta(days=0)

        dates = [date.strftime(self.date_format) for date in self.cashflow_leg_float.end_date]
        amounts = self.cashflow_leg_float["cashflow"].to_list()

        discount_cashflow_float = cash_flow.cash_flow(dates, amounts)

        if date_valo:
            discount_cashflow_float.npv(date_valo, discount_curve, relative_delta)
        else:
            discount_cashflow_float.npv(discount_curve.date_curve, discount_curve, relative_delta)

        self.cashflow_leg_float[["discount_cashflow_amounts", "DF"]] = (
            discount_cashflow_float.cashflows[["discount_cashflow_amounts", "DF"]].values
        )

        self.NPV = discount_cashflow_float.NPV + self.accrued_coupon_float

    def accrued_coupon(self,
        valuation_date:datetime,
        relative_delta=None,
        ) -> float:
            """This function computes the accrued coupon of the float leg
                and for the past we use ESTR compounded and for the future we compute forwards

            Args:
                curve (curve): yield curve
                ESTR (dataframe): Estr compounded
                Cash_flows (Dataframe): dataframe
                notionel (float): float
                valuation_date (datetime): valuation date

            Returns:
                float: accrued coupon
            """

            if relative_delta is None:
                relative_delta=relativedelta(days=0)
            # if ESTR file is provided
            # we don't have weekends so we need to use interplation
            ESTR=self.ESTR_coumpounded.df
            date_min = min(ESTR["DATES"])
            date_max = max(ESTR["DATES"])
            SDate = financial.previous_coupon_date(self.cashflow_leg_float["start_date"], self.cashflow_leg_float["end_date"], pd.Timestamp(valuation_date))

            ESTR_start = ESTR[ESTR["DATES"] == SDate]["ESTR"]
            ESTR_end = ESTR[ESTR["DATES"] == valuation_date]["ESTR"]
            ESTR_max = ESTR[ESTR["DATES"] == date_max]["ESTR"]

            if (
                self.yield_curve_object.date_curve > SDate and date_max < SDate
                # Here my start Date is a Date in which no ESTR no FORWARD RATE (can't compute the forward)
            ):
                raise ValueError(
                    "Forward can't be computed (ex :Use an ESTR compounded up to curve date)"
                )

            result = 0


            if SDate < date_min or SDate > date_max:
                FRate = self.yield_curve_object.forward_rates(
                    financial.previous_coupon_date(self.cashflow_leg_float["start_date"], self.cashflow_leg_float["end_date"], pd.Timestamp(valuation_date)),
                    pd.Timestamp(valuation_date),
                    relative_delta,
                )

                Day_count_years = core.day_count(
                    financial.previous_coupon_date(self.cashflow_leg_float["start_date"], self.cashflow_leg_float["end_date"], pd.Timestamp(valuation_date)),
                    pd.Timestamp(valuation_date),
                    self.date_convention,
                )
                Perf = 0 if FRate is None else (1 + FRate) ** Day_count_years - 1
            elif valuation_date <= date_max:
                Perf = (float(ESTR_end) / float(ESTR_start)) - 1
            elif valuation_date > date_max:
                perf_0 = (float(ESTR_max) / float(ESTR_start)) - 1
                FRate0 = self.yield_curve_object.forward_rates(
                    pd.Timestamp(date_max) + timedelta(days=1),
                    pd.Timestamp(valuation_date),
                    relative_delta,
                )

                Day_count_years = core.day_count(
                    pd.Timestamp(date_max) + timedelta(days=1),
                    pd.Timestamp(valuation_date),
                    self.date_convention,
                )
                Perf = ((1 + FRate0) ** (Day_count_years) - 1) + perf_0 / self.nominal
            else:
                FRate = self.yield_curve_object.forward_rates(
                    financial.previous_coupon_date(self.cashflow_leg_float["start_date"], self.cashflow_leg_float["end_date"], pd.Timestamp(valuation_date)),
                    pd.Timestamp(valuation_date),
                    relative_delta,
                )

                Day_count_years = core.day_count(
                    financial.previous_coupon_date(self.cashflow_leg_float["start_date"], self.cashflow_leg_float["end_date"], pd.Timestamp(valuation_date)),
                    pd.Timestamp(valuation_date),
                )
                Perf = 0 if FRate is None else (1 + FRate) ** Day_count_years - 1
            result = self.nominal * Perf
            return result
