# Standard library imports
from datetime import datetime

# Third-party library imports
import pandas as pd
from IRS_toolkit.utils.constants import VALID_CONVENTIONS
from IRS_toolkit.utils.core import day_count, previous_coupon_date
# Constants


def zc_to_simplerate(zero_coupon_rate_coumpound:float, day_count:float) -> float:
    """
    Convert zero coupon rate to simple rate.

    Args:
        zero_coupon_rate_coumpound (float): Zero coupon rate (compound)
        day_count (float): Period of time in years

    Returns:
        float: Simple rate
    """
    # Return 0 if day_count is 0 or zc is None to avoid division by zero or None errors
    if day_count == 0 or zero_coupon_rate_coumpound is None:
        return 0

    # Calculate and return the simple rate
    return ((1 + zero_coupon_rate_coumpound) ** day_count - 1) / day_count


def spread_amount(list_start_dates_cashflow:list[datetime], list_end_dates_cashflow:list[datetime], notionel:float, spread:float, valuation_date:datetime, convention:VALID_CONVENTIONS) -> float:
    """this function compute the spread amount for a giving valuation date and start date

    Args:
        cashflow (dataframe): coupon start and end dates
        notionel (float): notionel amount
        spread (float): swap spread
        valuation_date (datetime): valuation date

    Returns:
        float: the spread amount
    """
    period = day_count(
        previous_coupon_date(list_start_dates_cashflow, list_end_dates_cashflow, pd.Timestamp(valuation_date)),
        pd.Timestamp(valuation_date),
        convention,
    )
    return notionel * (spread) * period

def dv01(actual: float, up: float, down: float) -> float:
    """

    Args:
        actual (float): unshifted value
        up (float): value with shifted curve (+1 bps)
        down (float): value with shifted curve (-1 bps)

    Returns:
        float: sensitivity of the swap price
    """
    return (abs(actual - up) + abs(actual - down)) / 2