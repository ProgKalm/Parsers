# MinecraftModsParser

This parser work by beautifulsoup4 and requests
Parser work with site: *https://minecraft-inside.ru/*

# Docs

**class Categories**

Contains all categories as dict to work with it realised two methods
1. get(name) {returned None or site eval of category by name}
2. get_all() {returns set by all categories name on site}

***

**class CustomJSONEncoder**

This class was made to parse custom class Item to JsonObject

***

**class Item**

This class contains all data of item(objects) on site. This class load data and save it.

***

**class MineParser**

This class realise to parse website by page and save all results of parse

**Attributes**
1. __category {save site-view of category name}
2. __item_count {save what count of item must return method *find*}

**Methods**

1. set_category(name) {set category by getting site value with get(name) and if name is invalid nothing do}
2. set_item_count(count) {set count value as __item_count value if count low or more 0 then nothing do}
3. find() {returned list of Items from website}
4. find_first(count) {work as *find()* but at first call *set_item_count(count)*, to set new value of count by items}