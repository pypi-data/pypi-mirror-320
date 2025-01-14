from enum import Enum


class Currency(Enum):
    USD = "USD"  # United States Dollar
    EUR = "EUR"  # Euro
    JPY = "JPY"  # Japanese Yen
    GBP = "GBP"  # British Pound Sterling
    AUD = "AUD"  # Australian Dollar
    CAD = "CAD"  # Canadian Dollar
    CHF = "CHF"  # Swiss Franc
    CNY = "CNY"  # Chinese Yuan
    HKD = "HKD"  # Hong Kong Dollar
    NZD = "NZD"  # New Zealand Dollar
    SEK = "SEK"  # Swedish Krona
    KRW = "KRW"  # South Korean Won
    SGD = "SGD"  # Singapore Dollar
    NOK = "NOK"  # Norwegian Krone
    MXN = "MXN"  # Mexican Peso
    INR = "INR"  # Indian Rupee
    RUB = "RUB"  # Russian Ruble
    ZAR = "ZAR"  # South African Rand
    TRY = "TRY"  # Turkish Lira
    BRL = "BRL"  # Brazilian Real
    PLN = "PLN"  # Polish Zloty


class Country(Enum):
    """Country subject enumeration class."""

    USA = "United States"
    EU = "Euro Area"
    Japan = "Japan"
    UK = "United Kingdom"
    Australia = "Australia"
    Canada = "Canada"
    Switzerland = "Switzerland"
    China = "China"
    Mexico = "Mexico"
    India = "India"
    Russia = "Russia"
    Turkey = "Turkey"
    Poland = "Poland"

    @property
    def _currencies(self) -> dict:
        return {
            self.USA: "USD",
            self.EU: "EUR",
            self.Japan: "JPY",
            self.UK: "GBP",
            self.Australia: "AUD",
            self.Canada: "CAD",
            self.Switzerland: "CHF",
            self.China: "CNY",
            self.Mexico: "MXN",
            self.India: "INR",
            self.Russia: "RUB",
            self.Turkey: "TRY",
            self.Poland: "PLN",
        }

    @property
    def currency(self) -> str:
        """
        Get the currency of the country.

        Returns
        -------
        str
            Currency code.

        """
        return self._currencies[self]

    @classmethod
    def get_subject_names(cls) -> list[str]:
        """Get the list of country subject names."""
        return [subject.value for subject in cls]
