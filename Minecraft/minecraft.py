import json
import time
from typing import Any
from bs4 import BeautifulSoup, Tag
import requests, fake_useragent


class Categories:
    __categories = {
        "Mods": "mods",
        "Skins": "skins",
        "Textures": "resource-packs",
        "Maps": "maps",
        "Programs": "programs",
        "ModPacks": "modpacks",
        "Seeds": "seeds",
        "Commands": "commands",
        "DataPacks": "data-packs"
    }

    @classmethod
    def get(cls, name):
        return cls.__categories.get(str(name))

    @classmethod
    def get_all(cls):
        return cls.__categories.keys()


class CustomJSONEncoder(json.JSONEncoder):

    def default(self, o: Any) -> Any:
        return o.__dict__


class Item:
    __HOST = "https://minecraft-inside.ru"
    __headers = {
        "User-Agent": fake_useragent.UserAgent().random
    }

    def __init__(self, uri: str):
        self.url = self.__HOST + uri
        self.name = None
        self.versions = []
        self.download_link = None
        self.image = None
        self.__parse()

    def __parse(self):
        response = requests.get(self.url, headers=self.__headers)
        if response.status_code != 200:
            raise Exception(f"Invalid status code of response expected 200, but find {response.status_code}")
        soup = BeautifulSoup(response.text, "lxml")
        container = soup.find("div", class_="box_grass")
        head = container.find("div", class_="box__heading").find("h1").text
        self.__parse_head(head)
        body = container.find("div", class_="box__body")
        self.image = self.__HOST + body.find("img").get("src")
        href = body.find("table", class_="dl").find("a")
        self.download_link = href.get("href")

    def __parse_head(self, head: str):
        head = head.split("[")
        self.name = head[0]
        for i in range(1, len(head)):
            self.versions.append(head[i].split("]")[0])


class MineParser:
    __HOST = "https://minecraft-inside.ru/"
    __headers = {
        "User-Agent": fake_useragent.UserAgent().random
    }

    def __init__(self):
        self.__category = Categories.get("Mods")
        self.__item_count = 10

    def set_category(self, name: str = "Mods"):
        if name in Categories.get_all():
            self.__category = Categories.get(name)

    def set_item_count(self, count: int = 10):
        self.__item_count = count if count > 0 else self.__item_count

    def find(self):
        page = 1
        result = []
        while len(result) < self.__item_count:
            page_url = f"https://minecraft-inside.ru/{self.__category}/page/{page}"
            page_response = requests.get(page_url, headers=self.__headers)
            if page_response.status_code == 200:
                soup = BeautifulSoup(page_response.text, "lxml")
                content = soup.find("div", class_="container").find("div", class_="content").find("div", class_="page")

                content = content.findAll("div", class_="box_grass")

                for box in content:
                    try:
                        result.append(Item(box.find("a").get("href")))
                    except Exception as ignored:
                        pass
                    time.sleep(0.5)
                page += 1
            else:
                break
        return result[:self.__item_count]

    def find_first(self, count: int = 10):
        self.set_item_count(count)
        self.find()


def main():
    p = MineParser()
    p.set_item_count(50)
    x = p.find()
    with open(f"./{__name__}.json", "w") as file:
        file.write(json.dumps({"result": x}, cls=CustomJSONEncoder, indent=4))


if __name__ == '__main__':
    main()
