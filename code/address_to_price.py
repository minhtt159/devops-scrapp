import requests
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from house_dataclass import HouseWOZ


class SeleniumDriver:
    def __init__(self, URL):
        self.LB_STICKY: str = ""
        self.SESSION: str = ""
        self.URL = URL
        # Set up options
        chromeOption = webdriver.ChromeOptions()
        # set up the web driver
        remote_selenium = os.environ.get("REMOTE_SELENIUM", "")
        if len(remote_selenium) != 0:
            self.driver = webdriver.Remote(
                command_executor=remote_selenium, options=chromeOption
            )
        else:
            self.driver = webdriver.Chrome(options=chromeOption)

    def save_cookie(self):
        # visit the website
        self.driver.get(self.URL)
        self.SESSION = WebDriverWait(self.driver, timeout=120).until(
            lambda d: d.get_cookie("SESSION")
        )["value"]
        self.LB_STICKY = WebDriverWait(self.driver, timeout=120).until(
            lambda d: d.get_cookie("LB_STICKY")
        )["value"]
        print(f"SESSION {self.SESSION}\nLB_STICKY {self.LB_STICKY}")
        return

    def __delete__(self):
        if self.driver is not None:
            self.driver.quit()


# def suggest_location(address):
#     base_url = "https://geodata.nationaalgeoregister.nl/locatieserver/v3/suggest"
#     base_address = f"{address['road']} {address['house_number']}"
#     if address["postcode"] is not None and len(address["postcode"]) != 0:
#         base_address += f", {address['postcode']}"
#     if address["city"] is not None and len(address["city"]) != 0:
#         base_address += f" {address['city']}"
#     params = {"q": base_address}
#     response = requests.get(base_url, params=params)
#     if response.status_code == 200:
#         results = response.json()["response"]["docs"]
#         if len(results) > 0:
#             return results[0]["id"], results[0]["weergavenaam"]
#         else:
#             return None
#     else:
#         return None


# def get_nummeraanduiding_id(location_id):
#     # print(location_id)
#     base_url = "https://geodata.nationaalgeoregister.nl/locatieserver/v3/lookup"
#     params = {"id": location_id}
#     response = requests.get(base_url, params=params)
#     if response.status_code == 200:
#         results = response.json()["response"]["docs"]
#         if len(results) > 0:
#             return results[0]["nummeraanduiding_id"]
#         else:
#             return None
#     else:
#         return None


def get_woz_value(house_number_id):
    # print(house_number_id)
    url = f"https://www.wozwaardeloket.nl/wozwaardeloket-api/v1/wozwaarde/nummeraanduiding/{house_number_id}"
    cookie = {"LB_STICKY": SD.LB_STICKY, "SESSION": SD.SESSION}
    # print(cookie)
    response = requests.get(url, cookies=cookie)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_price_from_location(house_numberbuilding_id):
    # if isinstance(location, Location):
    #     house_adr_id, house_name = suggest_location(location.raw["address"])
    # elif isinstance(location, str):
    #     pattern = r"(?P<road>[\w\-\ ]*) (?P<house_number>\d*[A-Z]?)(?:\, )?(?P<postcode>[\d]{4}(?: )?[A-Z]{2})?(?: )?(?P<city>[a-zA-Z]+(?:([\ \-\']|(\.\ ))[a-zA-Z]+)*)?"
    #     match = re.match(pattern, location).groupdict()
    #     house_adr_id, house_name = suggest_location(match)
    # else:
    #     raise Exception(f"Error parsing house address from location: {location}")
    # house_numberbuilding_id = get_nummeraanduiding_id(house_adr_id)
    # assert house_numberbuilding_id != None, "Can not get house building number"
    response_data = get_woz_value(house_numberbuilding_id)
    assert response_data != None, "Can not get WOZ value"
    woz_waarden = response_data["wozWaarden"]
    WOZ_instance = {}
    for row in woz_waarden:
        YEAR = "WOZ{}".format(row["peildatum"][:4])
        WOZ_instance[YEAR] = row["vastgesteldeWaarde"]
    return HouseWOZ(house_name=house_numberbuilding_id, WOZ=WOZ_instance)


SD = SeleniumDriver("https://www.wozwaardeloket.nl/")
SD.save_cookie()