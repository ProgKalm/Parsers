import json
import os.path
import time, fake_useragent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def to_int(text: str = "0"):
    if text is not None:
        text = text.strip().lower()
        if text != "":
            number = ""
            for char in text:
                if "0" <= char <= "9":
                    number = number + char
            try:
                return int(number)
            except Exception as ignored:
                return 0
    return 0


class SortMode:
    POPULAR = "popular"
    RATE = "rate"
    PRICEUP = "priceup"
    PRICEDOWN = "pricedown"
    UPDATE = "newly"
    BENEFIT = "benefit"


class Item:

    def __init__(self, url: str, data: dict):
        self.url = url
        self.data = data
        self.data['url'] = url
        self.name = data.get('name')
        self.price = data.get('price')
        self.details = data.get('details')

    def __str__(self) -> str:
        return self.data.__str__()

    def __repr__(self) -> str:
        return self.__str__()


class FilterKey:
    PRICE_MORE = "price_more"
    PRICE_LOW = "price_low"

    @classmethod
    def check(cls, type_, eq_val: int, value: int):
        if type_ == cls.PRICE_MORE:
            return eq_val <= value
        return eq_val >= value


class Wildberries:
    __host = "https://www.wildberries.ru/"
    __options_params = {
        "--user-agent": f"{fake_useragent.UserAgent().random}",  # create fake_user agent
        "--disable-blink-features": "AutomationControlled"  # delete browser param of bot_mode
    }

    def __init__(self, user: str = __name__):
        # load option
        options = webdriver.ChromeOptions()
        for option in self.__options_params:
            options.add_argument(f"{option}={self.__options_params[option]}")
        # build driver
        self.__driver = webdriver.Chrome(
            service=Service(r".\drivers\chrome32.exe"),
            options=options
        )
        self.__sort_mode = SortMode.POPULAR
        self.__max_page_count = 3
        self.__user = user

    def set_max_page_count(self, count: int = 1) -> None:
        if count <= 1:
            self.__max_page_count = 1
        else:
            self.__max_page_count = count

    def set_sort_mode(self, sort_mode: SortMode) -> None:
        self.__sort_mode = sort_mode

    @staticmethod
    def filter_by_price(data: list[Item], by: FilterKey = FilterKey.PRICE_MORE, value: int = 0) -> list[Item]:
        res = []
        for item in data:
            if FilterKey.check(by, value, item.price):
                res.append(item)
        return res

    def find(self, search_request: str) -> list[Item]:
        try:
            data: list[Item] = []
            items_urls = self.__pages_parse(search_request)
            for item_url in items_urls:
                item_data = self.__parse_item(item_url)
                if item_data is not None:
                    data.append(Item(item_url, item_data))
            return data
        except Exception as ex:
            print(ex)

    def __pages_parse(self, search_request: str) -> list[str]:
        page = 1
        items_urls = []
        while page <= self.__max_page_count:
            if self.__go_to_page(page, search_request):
                break
            items_list = self.__driver.find_element(By.CLASS_NAME, "product-card-overflow")
            items_list = items_list.find_elements(By.CLASS_NAME, "product-card__wrapper")
            for item in items_list:
                url = item.find_element(By.CLASS_NAME, "product-card__main")
                items_urls.append(url.get_attribute("href"))

            page += 1
        return items_urls

    def close(self) -> None:
        self.__driver.close()
        self.__driver.quit()

    def __parse_item(self, item_url) -> dict:
        try:
            if self.__go_to_item(item_url):
                return None
            item_data = {}
            item = self.__driver.find_element(By.CLASS_NAME, "product-page").find_element(By.CLASS_NAME,
                                                                                          "product-page__grid")
            # find name
            item_name = item.find_element(By.CLASS_NAME, "product-page__header-wrap").find_element(By.TAG_NAME, "h1")
            item_data.setdefault("name", item_name.text)
            # find price
            item_price = item.find_element(By.CLASS_NAME, "product-page__price-block")
            item_price = item_price.find_element(By.CLASS_NAME, "price-block")
            item_price = item_price.find_element(By.CLASS_NAME, "price-block__content")
            item_price = item_price.find_element(By.TAG_NAME, "p").find_element(By.TAG_NAME, "ins")
            item_price = int(to_int(item_price.text))
            item_data.setdefault("price", item_price)
            # find details
            item_details = item.find_element(By.CLASS_NAME, "product-page__details-section")
            item_details = item_details.find_element(By.CLASS_NAME, "product-params")
            item_details = item_details.find_elements(By.TAG_NAME, "table")
            details_data = {}
            for item_detail in item_details:
                detail_name = item_detail.find_element(By.TAG_NAME, "caption").text
                detail_data = {}
                detail_body = item_detail.find_element(By.TAG_NAME, "tbody")
                detail_rows = detail_body.find_elements(By.TAG_NAME, "tr")
                for row in detail_rows:
                    key = row.find_element(By.TAG_NAME, "th").text
                    value = row.find_element(By.TAG_NAME, "td").text
                    detail_data.setdefault(key, value)
                details_data.setdefault(detail_name, detail_data)
            item_data.setdefault("details", details_data)
            return item_data
        except Exception as ignored:
            pass
        return None

    def __go_to_item(self, item_url: str) -> bool:
        self.__driver.get(item_url)
        time.sleep(1)
        return self.__check_not_found()

    def __check_not_found(self) -> bool:
        try:
            not_found_text = self.__driver.find_element(By.CLASS_NAME, "catalog-page__text")
            return True
        except Exception as ignored:
            pass
        return False

    def __go_to_page(self, page, search_request: str) -> bool:
        req = f"{self.__host}catalog/0/search.aspx?page={page}&sort={self.__sort_mode}&search={search_request}"
        self.__driver.get(req)
        time.sleep(1)
        return self.__check_not_found()

    def save_result(self, results: list[Item]) -> None:
        self.__create_dir("./results/")
        file_name = f"{self.__user.strip('_')}.json"
        with open(f"./results/{file_name}", "w", encoding="utf-8") as file:
            file.write(json.dumps(results.__repr__()))

    @staticmethod
    def __is_valid_request(search_request: str) -> bool:
        return isinstance(search_request, str) and search_request is not None and search_request.strip() != ""

    @staticmethod
    def __create_dir(path) -> None:
        if not os.path.exists(path):
            os.mkdir(path)


def main():
    w = Wildberries()
    w.set_max_page_count(1)
    data = w.find("планшеты")
    data = w.filter_by_price(data, FilterKey.PRICE_LOW, 16000)
    w.save_result(data)
    w.close()


if __name__ == '__main__':
    main()
