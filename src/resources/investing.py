import logging
from datetime import date
from urllib.parse import urljoin

import httpx

from src.http_client import HTTPClient

logger = logging.getLogger(__name__)

EVENTS_API_URL_TEMPLATE = (
    "https://www.investing.com/economic-calendar/Service/getCalendarFilteredData"
)
HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.6",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://investing.com",
    "priority": "u=1, i",
    "referer": "https://investing.com/economic-calendar/",
    "sec-ch-ua": '"Brave";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-gpc": "1",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    ),
    "x-requested-with": "XMLHttpRequest",
}

COUNTRIES_MAPPING = {
    "95": "Albania",
    "86": "Angola",
    "29": "Argentina",
    "25": "Australia",
    "54": "Austria",
    "114": "Azerbaijan",
    "145": "Bahrain",
    "47": "Bangladesh",
    "34": "Belgium",
    "8": "Bermuda",
    "174": "Bosnia-Herzegovina",
    "163": "Botswana",
    "32": "Brazil",
    "70": "Bulgaria",
    "6": "Canada",
    "232": "Cayman Islands",
    "27": "Chile",
    "37": "China",
    "122": "Colombia",
    "15": "Costa Rica",
    "78": "Cote D'Ivoire",
    "113": "Croatia",
    "107": "Cyprus",
    "55": "Czech Republic",
    "24": "Denmark",
    "121": "Ecuador",
    "59": "Egypt",
    "89": "Estonia",
    "72": "Euro Zone",
    "71": "Finland",
    "22": "France",
    "17": "Germany",
    "74": "Ghana",
    "51": "Greece",
    "39": "Hong Kong",
    "93": "Hungary",
    "106": "Iceland",
    "14": "India",
    "48": "Indonesia",
    "66": "Iraq",
    "33": "Ireland",
    "23": "Israel",
    "10": "Italy",
    "119": "Jamaica",
    "35": "Japan",
    "92": "Jordan",
    "102": "Kazakhstan",
    "57": "Kenya",
    "94": "Kuwait",
    "204": "Kyrgyzstan",
    "97": "Latvia",
    "68": "Lebanon",
    "96": "Lithuania",
    "103": "Luxembourg",
    "111": "Malawi",
    "42": "Malaysia",
    "109": "Malta",
    "188": "Mauritius",
    "7": "Mexico",
    "139": "Mongolia",
    "247": "Montenegro",
    "105": "Morocco",
    "82": "Mozambique",
    "172": "Namibia",
    "21": "Netherlands",
    "43": "New Zealand",
    "20": "Nigeria",
    "60": "Norway",
    "87": "Oman",
    "44": "Pakistan",
    "193": "Palestinian Territory",
    "148": "Paraguay",
    "125": "Peru",
    "45": "Philippines",
    "53": "Poland",
    "38": "Portugal",
    "170": "Qatar",
    "100": "Romania",
    "56": "Russia",
    "80": "Rwanda",
    "52": "Saudi Arabia",
    "238": "Serbia",
    "36": "Singapore",
    "90": "Slovakia",
    "112": "Slovenia",
    "110": "South Africa",
    "11": "South Korea",
    "26": "Spain",
    "162": "Sri Lanka",
    "9": "Sweden",
    "12": "Switzerland",
    "46": "Taiwan",
    "85": "Tanzania",
    "41": "Thailand",
    "202": "Tunisia",
    "63": "Türkiye",
    "123": "Uganda",
    "61": "Ukraine",
    "143": "United Arab Emirates",
    "4": "United Kingdom",
    "5": "United States",
    "180": "Uruguay",
    "168": "Uzbekistan",
    "138": "Venezuela",
    "178": "Vietnam",
    "84": "Zambia",
    "75": "Zimbabwe",
}

CATEGORIES = [
    "_employment",
    "_economicActivity",
    "_inflation",
    "_credit",
    "_centralBanks",
    "_confidenceIndex",
    "_balance",
    "_Bonds",
]
IMPACT_LEVELS = ["1", "2", "3"]

EVENTS_API_PARAMS = {
    "countries": COUNTRIES_MAPPING.keys(),
    "categories": CATEGORIES,
    "impact_levels": IMPACT_LEVELS,
    "timeZone": "55",  # UTC
    "timeFilter": "timeOnly",
    "currentTab": "custom",
    "limit_from": 0,
}


class InvestingResource:
    def __init__(
        self,
        http_client: HTTPClient,
    ) -> None:
        self.http_client = http_client

    def get_calendar_events(self, start_date: date, end_date: date) -> list[dict]:
        logger.info("Getting calendar events for %s to %s ...", start_date, end_date)

        params = EVENTS_API_PARAMS.copy()
        params["dateFrom"] = start_date.strftime("%Y-%m-%d")
        params["dateTo"] = end_date.strftime("%Y-%m-%d")

        response_list = []

        page_num = 0
        while True:
            response = self.http_client.request(
                method="POST",
                url=EVENTS_API_URL_TEMPLATE,
                headers=HEADERS,
                data=params,
            )
            data = response.json()
            response_list.append(data)

            if not data["bind_scroll_handler"]:
                break

            page_num += 1
            params["limit_from"] = page_num
            params["last_time_scope"] = data["last_time_scope"]

        return response_list

    def get_event_details(self, event_url: str) -> httpx.Response:
        logger.info("Getting event details for %s ...", event_url)
        url = urljoin("https://www.investing.com/", event_url)
        response = self.http_client.request(
            method="GET",
            url=url,
            headers=HEADERS,
        )

        return response
