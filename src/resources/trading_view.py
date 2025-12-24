import logging
from datetime import date, datetime, time

import httpx

from src.http_client import HTTPClient

logger = logging.getLogger(__name__)

EVENTS_API_URL = "https://economic-calendar.tradingview.com/events"
EVENT_DETAILS_URL_TEMPLATE = "https://www.tradingview.com/symbols/{event_ticker}/"
HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.6",
    "origin": "https://www.tradingview.com",
    "priority": "u=1, i",
    "referer": "https://www.tradingview.com/",
    "sec-ch-ua": '"Brave";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "sec-gpc": "1",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    ),
}

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
COUNTRIES = [
    "AR",
    "AU",
    "BR",
    "CA",
    "CN",
    "FR",
    "DE",
    "IN",
    "ID",
    "IT",
    "JP",
    "KR",
    "MX",
    "RU",
    "SA",
    "ZA",
    "TR",
    "GB",
    "US",
    "EU",
]

EVENTS_API_PARAMS = {
    "countries": COUNTRIES,
    "from": "",
    "to": "",
}


class TradingViewResource:
    def __init__(
        self,
        http_client: HTTPClient,
    ) -> None:
        self.http_client = http_client

    def get_calendar_events(self, start_date: date, end_date: date) -> list[dict]:
        logger.info("Getting calendar events for %s to %s ...", start_date, end_date)

        params = EVENTS_API_PARAMS.copy()

        start_dt = datetime.combine(start_date, time(hour=0, minute=0, second=0))
        end_dt = datetime.combine(end_date, time(hour=23, minute=59, second=59))

        params["from"] = start_dt.strftime(DATETIME_FORMAT)
        params["to"] = end_dt.strftime(DATETIME_FORMAT)

        response = self.http_client.request(
            method="GET",
            url=EVENTS_API_URL,
            headers=HEADERS,
            params=params,
        )
        return response.json()

    def get_event_details(self, event_ticker: str) -> httpx.Response:
        logger.info("Getting event details for %s ...", event_ticker)
        url = EVENT_DETAILS_URL_TEMPLATE.format(event_ticker=event_ticker)
        response = self.http_client.request(
            method="GET",
            url=url,
            headers=HEADERS,
        )
        return response
