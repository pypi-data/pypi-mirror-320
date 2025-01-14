import warnings

import pandas as pd
from scipy.optimize import minimize

from IRS_toolkit.core.leg import fix_leg, float_leg
from datetime import datetime
from dateutil.relativedelta import relativedelta
from IRS_toolkit.core.curve import compounded, yield_curve
from IRS_toolkit.utils import schedule

warnings.filterwarnings("ignore")


class Swap:
    """
    A class that provides various outputs related to swap pricing.


    Args:
        fix_leg (legFix): fixed leg
        float_leg (legFloat): float leg
    """

    def __init__(self,
                nominal:float,
                fix_rate:float,
                yield_curve_fix:yield_curve.YieldCurve=None,
                yield_curve_float:yield_curve.YieldCurve=None,
                ESTR_compounded:compounded.Compounded=None,
                schedule_fix:schedule.Schedule=None,
                schedule_float:schedule.Schedule=None,
                relative_delta=None,
                fix_rate_base:int=1):

        self.nominal=nominal
        self.fix_rate=fix_rate/fix_rate_base
        self.yield_curve_fix=yield_curve_fix
        self.yield_curve_float=yield_curve_float
        self.ESTR_compounded=ESTR_compounded
        self.schedule_fix=schedule_fix
        self.schedule_float=schedule_float
        self.relative_delta=relative_delta
        self.cashflow=pd.DataFrame()
    
        fix_leg_object=fix_leg.FixLeg(nominal=nominal,
        fix_rate=self.fix_rate,
        schedule=schedule_fix)

        float_leg_object=float_leg.FloatLeg(nominal=nominal,
                                            yield_curve_object=yield_curve_float,
                                            schedule=schedule_float,
                                            ESTR_coumpounded=ESTR_compounded,
                                            relative_delta=relative_delta)

        self.fix_leg_object = fix_leg_object
        self.float_leg_object = float_leg_object

    def npv(self, valuation_date:datetime):
        """
        Net present value of the swap

        Args:
            discount_curve (curve): yield curve
            date_valo (date, optional): valuation date. Defaults to None.
            RunningCouv (float, optional): spread. Defaults to 0.00.
            GainGC (float, optional): spread. Defaults to 0.00.

        Returns:
            float: Net present value
        """
        self.fix_leg_object.discount_cashflow(self.yield_curve_fix, valuation_date)
        self.float_leg_object.discount_cashflow(self.yield_curve_float, valuation_date)
        self.NPV_ = self.fix_leg_object.NPV - self.float_leg_object.NPV

        result_dict = {"Nominal":self.nominal,
                       "Fix_Rate":self.fix_rate,
                       "Valuation_Date":valuation_date,
                       "Swap_NPV":self.NPV_,
                       "Fixed_Leg_NPV":self.fix_leg_object.NPV,
                       "Float_Leg_NPV":self.float_leg_object.NPV,
                       "Accrued_Coupon_Float":self.float_leg_object.accrued_coupon_float,
                       "Accrued_Coupon_Fix":self.fix_leg_object.accrued_coupon_fix,
                       "Spread_Hedging_Cost":self.fix_leg_object.spreadHC,
                       "Spread_Global_Collateral":self.fix_leg_object.spreadGC,
                       "Fair_Rate":self.fair_rate(valuation_date)[1],
                       "Global_Collateral":self.fix_leg_object.spreadGC+self.float_leg_object.accrued_coupon_float,
                       "SWAP_ALL_IN":self.fix_leg_object.spreadGC+self.float_leg_object.accrued_coupon_float+self.fix_leg_object.spreadHC+self.NPV_}
        df_str=pd.DataFrame.from_dict(result_dict,orient="index")
        self.df=df_str.T
        self.df["Exit_cost"]=self.df["Swap_NPV"]-self.df["Accrued_Coupon_Fix"]+self.df["Accrued_Coupon_Float"]+self.df["Spread_Hedging_Cost"]
        return self.NPV_

    def fair_rate(self, valuation_date:datetime):
        """
        fair rate of the swap

        Args:
            date_valo (date): date valuation
            ImpSchedule (dataframe) : in case you use imported schedule

        Returns:
            float, float: fair rate, theorical fair rate
        """

        fix_rate = self.fix_leg_object.fix_rate
        fix_leg_object_nominal=self.fix_leg_object.nominal
        fix_leg_object_schedule=self.fix_leg_object.schedule_fix

        def loss_func(fix_rate:float):
            leg_fix = fix_leg.FixLeg(
                nominal=fix_leg_object_nominal,
                fix_rate=fix_rate,
                schedule=fix_leg_object_schedule,
            )
            leg_fix.compute_cash_flow(pd.Timestamp(valuation_date))
            leg_fix.discount_cashflow(self.float_leg_object.yield_curve_object, valuation_date)
            return (leg_fix.NPV - self.float_leg_object.NPV) * (
                leg_fix.NPV - self.float_leg_object.NPV
            )

        res = minimize(
            loss_func,
            fix_rate,
            method="nelder-mead",
            options={"xatol": 1e-8, "disp": True},
        )
        self.faire_rate = float(res.x)
        self.faire_rate_theory = (
            self.float_leg_object.NPV
            / (
                self.fix_leg_object.nominal
                * self.fix_leg_object.cashflow_leg_fix.iloc[:, 3]
                * self.fix_leg_object.cashflow_leg_fix.DF
            ).sum()
        )
        return self.faire_rate, self.faire_rate_theory

    def price(self, valuation_date:datetime,spreadHC:float,spreadGC:float):
        if self.relative_delta is None:
            relative_delta=relativedelta(days=0)
        else:
            relative_delta=self.relative_delta

        self.fix_leg_object.compute_cash_flow(valuation_date, spreadHC, spreadGC)
        self.fix_leg_object.discount_cashflow(self.yield_curve_fix, valuation_date, relative_delta)

        self.float_leg_object.compute_cash_flow(valuation_date)
        self.float_leg_object.discount_cashflow(self.yield_curve_float, valuation_date, relative_delta)

        cashflow = self.fix_leg_object.cashflow_leg_fix.merge(
            self.float_leg_object.cashflow_leg_float,
            on=["start_date", "end_date"],
            how="inner",
            suffixes=("_fix", "_float"),
        )

        cashflow.rename(columns={'start_date':'start date',
                                 'end_date':'end date',
                                 'Period_fix':'fix Period years',
                                 'day_count_fix':'fix day_count',
                                 'cashflow_fix':'fix cashflow',
                                 'discount_cashflow_amounts_fix':'fix DCF',
                                 'DF_fix':'fix DF', 'forward_zc_fix':'forward_ZC',
                                 'forward_simple_rate_fix':'forward_simple_rate',
                                 'Period_float':'float Period years',
                                 'day_count_float':'float day_count',
                                 'cashflow_float':'float cashflow',
                                 'discount_cashflow_amounts_float':'float DCF',
                                 'DF_float':'float DF',
                                 'forward_zc_float':'forward_ZC',
                                 'forward_simple_rate_float':'forward_simple_rate'}, inplace=True)
        self.cashflow = cashflow

