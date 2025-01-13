import pandas as pd
from datetime import datetime
from IRS_toolkit.utils import core


class Compounded:
    def __init__(self,list_date:list[datetime],list_estr:list[float],as_of_date:datetime=None,data_base=1):
        self.data_base=data_base
        new_list_estr = [x / data_base for x in list_estr]
        self.list_date = list_date
        self.list_estr = new_list_estr
        self.as_of_date = as_of_date

        dict_estr = {"DATES":self.list_date,"ESTR":self.list_estr}
        df = pd.DataFrame(dict_estr)
        df["DATES"] = pd.to_datetime(df["DATES"])

        ESTR = core.linear_interpolation(df["DATES"].to_list(),df["ESTR"].to_list())
        ESTR.rename(columns={"VALUES":"ESTR"},inplace=True)
        ESTR["AS_OF_DATE"] = self.as_of_date
        ESTR["DATES"] = pd.to_datetime(ESTR["DATES"])
        ESTR["AS_OF_DATE"] = pd.to_datetime(ESTR["AS_OF_DATE"])

        self.df=ESTR

