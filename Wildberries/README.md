# Wildberries
This parser worked by selenium.

# Docs:

**class Item**:

Realize view of wildberries item with some data
 
* url - this url of item self webpage
* name - head of item
* price - item price
* details - some details of item

****

**class FilterKey**

Realize enum of some filters

1. *PRICE_MORE* - this is constant what eval that filter-method must take item also it price more than value
2. *PRICE_LOW* - this is constant what eval that filter-method must take item also it price low than value
3. method *check(cls, type_, eq_val, value)* static method of *FilterKey.class*

    + *type_* - this is one of constant of class *FilterKey*
    + *value* - needed params from item
    + *eq_val* - this values is neded to check *value* by filter key(*type_*)

****

**class SortMode**
    This clas is enum of parametrs to sort on wildberries site

****

**class Wildberries**

This class work with website and parse it

*class constant*

1. __host - constant which contain std path to wildberries
2. __options_params - dict which contains params for option on webdriver
    
*class methods*

1) set_max_page_count(count:int) - set count pages to parse and 
    returned None
2) set_sort_mode(sort_mode:*SortMode*) - set mode to sort on wildberries website and 
    returned None
3) find(request:str) - method what start parse website to get *Items* by request and 
    returned list[*Items*]
4) close() - close all of selenium drivers and 
    returned None
5) filter_by_price(data: list[*Item*], by, value) - 
        method filter item by filterkey(param 'by') and value all items from data list and returned list[*Item*]
