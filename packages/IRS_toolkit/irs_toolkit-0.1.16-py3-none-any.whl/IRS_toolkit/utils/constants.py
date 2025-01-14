from typing import Literal
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

VALID_CONVENTIONS = Literal["ACT/360", "ACT/ACT","30/360"]
pay_frequency={"monthly":1, "quarterly":3, "semi_annual":6, "annual":12}
VALID_TENORS = Literal["D","W","M","Y"]
VALID_COUPON_FREQUENCY = Literal["quarterly","annual", "semi_annual", "monthly"]
VALID_TENORS = Literal[
            "1D",
            "1W",
            "2W",
            "3W",
            "1M",
            "2M",
            "3M",
            "4M",
            "5M",
            "6M",
            "7M",
            "8M",
            "9M",
            "10M",
            "11M",
            "1Y",
            "15M",
            "18M",
            "21M",
            "2Y",
            "3Y",
            "4Y",
            "5Y",
            "6Y",
            "7Y",
            "8Y",
            "9Y",
            "10Y",
            "11Y",
            "12Y",
            "15Y",
            "20Y",
            "25Y",
            "30Y",
]
VALID_FILL_TYPE = Literal["Back", "Forward"]

TIMEZONE_PARIS = ZoneInfo("Europe/Paris")