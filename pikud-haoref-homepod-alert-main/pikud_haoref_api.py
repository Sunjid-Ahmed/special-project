import requests
import json
from datetime import datetime

CATEGORIES_URL = "https://www.oref.org.il/alerts/alertCategories.json"
ALERT_URL = "https://www.oref.org.il/warningMessages/alert/Alerts.json"

HARDCODED_CATEGORIES = {
    "rockets_and_missiles": 1,          # missilealert
    "non_conventional": 2,              # nonconventional
    "earthquake_stage1": 3,             # earthquakealert1
    "earthquake_stage2": 3,             # earthquakealert2 (same matrix_id as stage1)
    "cbrne": 4,                         # radiological event
    "tsunami": 5,                       # tsunami
    "uav": 6,                           # hostileAircraftIntrusion
    "hazmat": 7,                        # hazardousMaterials
    "general_warning": 8,               # warning
    "notification": 10,                 # update
    "early_alert": 10,                  # flash
    "terrorist_infiltration": 13        # terroristInfiltration
}

CATEGORY_NAME_MAP = {
    "missilealert": "rockets_and_missiles",
    "uav": "uav",
    "nonconventional": "non_conventional",
    "warning": "general_warning",
    "earthquakealert1": "earthquake_stage1",
    "earthquakealert2": "earthquake_stage2",
    "cbrne": "cbrne",
    "terrorattack": "terrorist_infiltration",
    "tsunami": "tsunami",
    "hazmat": "hazmat",
    "update": "notification",
    "flash": "early_alert"
}


def fetch_and_map_categories():
    """
    Fetches alert categories and maps them to a dictionary of friendly_name → matrix_id.
    Reverts to hardcoded categories and ids if api mapping failed
    """
    try:
        response = requests.get(CATEGORIES_URL, timeout=2)
        response.raise_for_status()
        data = response.json()

        # Filter out drills and map friendly names to matrix_id
        mapped = {}
        for item in data:
            cat_name = item["category"]
            if item["matrix_id"] < 100 and cat_name in CATEGORY_NAME_MAP:
                mapped[CATEGORY_NAME_MAP[cat_name]] = item["matrix_id"]

        if mapped:
            print("Using dynamic categories from API.")
            return mapped
    except Exception as e:
        print(f"Failed to fetch categories, using fallback: {e}")

    print("Using hardcoded categories.")
    return HARDCODED_CATEGORIES


def fetch_current_alert():
    """
    Fetches the current alert JSON from Pikud HaOref and parses it.
    Returns a dict (parsed alert) or None if there is no alert or an error occurred.
    """
    try:
        response = requests.get(ALERT_URL)
        response.raise_for_status()
        print(datetime.now().strftime("%H:%M:%S") + " - " + str(response))
        return parse_response(response)
    except requests.RequestException as e:
        print(f"Failed to fetch alert: {e}")
    return None


def parse_response(response):
    """
    parses the api response into json and handles exceptions
    :param response: api response
    :return: parsed json
    """
    # check if the response is empty
    if not response.content.decode('utf-8-sig').isspace():
        # decode and print json
        try:
            return json.loads(response.content.decode('utf-8-sig'))
        # sometimes when there's no alert, JSON parsing raises an exception
        except json.JSONDecodeError:
            return None
    return None


def main():
    pass


if __name__ == "__main__":
    main()
