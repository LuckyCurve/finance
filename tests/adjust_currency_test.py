from db.entity import CurrencyType
from service.adjust import adjust_currency

adjust_currency(153230.82 + 464705.2, CurrencyType.CNY)
adjust_currency(229820.63 + 717.8, CurrencyType.HKD)
adjust_currency(1231.8 + 3270, CurrencyType.USD)
