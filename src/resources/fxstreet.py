import logging
from datetime import date, datetime, time

from src.http_client import HTTPClient

logger = logging.getLogger(__name__)

EVENTS_API_URL_TEMPLATE = (
    "https://calendar-api.fxsstatic.com/en/api/v2/eventDates/{start_date}/{end_date}"
)

EVENT_API_URL_TEMPLATE = (
    "https://calendar-api.fxsstatic.com/en/api/v1/eventDates/{event_id}"
)

HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.6",
    "origin": "https://www.fxstreet.com",
    "priority": "u=1, i",
    "referer": "https://www.fxstreet.com/",
    "sec-ch-ua": '"Brave";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "sec-gpc": "1",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    ),
}

CATEGORY_MAPPING = {
    "8896AA26-A50C-4F8B-AA11-8B3FCCDA1DFD": "Bond Auctions",
    "FA6570F6-E494-4563-A363-00D0F2ABEC37": "Capital Flows",
    "C94405B5-5F85-4397-AB11-002A481C4B92": "Central Banks",
    "E229C890-80FC-40F3-B6F4-B658F3A02635": "Consumption",
    "24127F3B-EDCE-4DC4-AFDF-0B3BD8A964BE": "Economic Activity",
    "DD332FD3-6996-41BE-8C41-33F277074FA7": "Energy",
    "7DFAEF86-C3FE-4E76-9421-8958CC2F9A0D": "Holidays",
    "1E06A304-FAC6-440C-9CED-9225A6277A55": "Housing Market",
    "33303F5E-1E3C-4016-AB2D-AC87E98F57CA": "Inflation",
    "9C4A731A-D993-4D55-89F3-DC707CC1D596": "Interest Rates",
    "91DA97BD-D94A-4CE8-A02B-B96EE2944E4C": "Labor Market",
    "E9E957EC-2927-4A77-AE0C-F5E4B5807C16": "Politics",
}

SUPPORTED_COUNTRIES = [
    "US",
    "UK",
    "EMU",
    "DE",
    "CN",
    "JP",
    "CA",
    "AU",
    "NZ",
    "CH",
    "FR",
    "IT",
    "ES",
    "UA",
    "IN",
    "RU",
    "TR",
    "ZA",
    "BR",
    "KR",
    "ID",
    "SG",
    "MX",
    "SE",
    "NO",
    "DK",
    "GR",
    "PT",
    "IE",
    "AT",
    "BE",
    "NL",
    "FI",
    "CZ",
    "PL",
    "HU",
    "RO",
    "CL",
    "CO",
    "AR",
    "IS",
    "HK",
    "SK",
    "IL",
    "SA",
    "VN",
    "KW",
    "EG",
    "AE",
    "QA",
    "TH",
]

SUPPORTED_VOLATILITIES = ["NONE", "LOW", "MEDIUM", "HIGH"]

EVENTS_API_PARAMS = {
    "volatilities": SUPPORTED_VOLATILITIES,
    "countries": SUPPORTED_COUNTRIES,
    "categories": CATEGORY_MAPPING.keys(),
}

REQUEST_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class FXStreetResource:
    def __init__(
        self,
        http_client: HTTPClient,
    ) -> None:
        """
        Initialize FXStreet resource.

        Args:
            http_client: HTTP client instance with retry and rate limiting
        """
        self.http_client = http_client

    def create_request_url(self, start_date: date, end_date: date) -> str:
        start_dt = datetime.combine(start_date, time(hour=0, minute=0, second=0))
        end_dt = datetime.combine(end_date, time(hour=23, minute=59, second=59))

        return EVENTS_API_URL_TEMPLATE.format(
            start_date=start_dt.strftime(REQUEST_DATETIME_FORMAT),
            end_date=end_dt.strftime(REQUEST_DATETIME_FORMAT),
        )

    def get_calendar_events(self, start_date: date, end_date: date) -> list[dict]:
        logger.info("Getting calendar events for %s to %s ...", start_date, end_date)
        url = self.create_request_url(start_date, end_date)
        response = self.http_client.request(
            method="GET",
            url=url,
            headers=HEADERS,
            params=EVENTS_API_PARAMS,
        )
        return response.json()

    def get_calendar_event(self, event_id: str) -> dict:
        logger.info("Getting calendar event for %s ...", event_id)
        url = EVENT_API_URL_TEMPLATE.format(event_id=event_id)
        response = self.http_client.request(
            method="GET",
            url=url,
            headers=HEADERS,
        )
        return response.json()
