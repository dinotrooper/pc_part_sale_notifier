""" Main module of the pc_part_sale_notifier """
import sys
from html.parser import HTMLParser
from lxml import etree, html
import requests


class ElementParser(HTMLParser):
    """
    This class returns the data within any HTML element.
    :param attr_name: The attribute of the element
    :param start_value: The value of the attribute where you want to start collecting data
    :param end_value: The value of the attribute where you want to stop collecting data
    """

    def __init__(self, attr_name, start_value, end_value):
        super().__init__()
        self.save_data = False
        self.attr_name = attr_name
        self.start_value = start_value
        self.end_value = end_value
        self.data = ""

    def handle_starttag(self, tag, attrs):
        for _, value in attrs:
            if value == self.start_value:
                self.save_data = True
            if value == self.end_value:
                self.save_data = False

    def handle_data(self, data):
        if self.save_data:
            self.data += data.strip()

    def get_data(self):
        """ Returns the data within the parser and clears out the old data. """
        temp_data = self.data
        self.data = ""
        split_data = temp_data.split()
        if len(split_data) < 10:
            return temp_data
        return " ".join(split_data[:9])


class ElementURLParser(HTMLParser):
    """
    This class returns the data within any HTML element.
    :param attr_name: The attribute of the element
    :param start_value: The value of the attribute where you want to start collecting data
    :param end_value: The value of the attribute where you want to stop collecting data
    """

    def __init__(self, attr_name, start_value, limit):
        super().__init__()
        self.index = 0
        self.search_limit = limit
        self.save_data = False
        self.attr_name = attr_name
        self.start_value = start_value
        self.data = []

    def handle_starttag(self, tag, attrs):
        for attr, value in attrs:
            if value == self.start_value:
                self.save_data = True
            if attr == "href" and self.save_data:
                if self.index < self.search_limit:
                    self.data.append(value)
                    self.save_data = False
                    self.index += 1
            if value != self.start_value:
                self.save_data = False

    def get_data(self):
        """ Returns the data within the parser and clears out the old data. """
        temp_data = self.data
        self.data = ""
        return temp_data


class SiteParser():
    """ Parent class for all site parsers """

    @classmethod
    def _get_html(cls, url):
        """ Gets the HTML text of a URL """
        request = requests.get(url)
        if request.status_code != 200:
            raise ValueError("Could not get html page.")
        return request.text

    def search(self, text, search_limit=0):
        """ Searches the site N number of items that match the url. """
        raise NotImplementedError


class NeweggParser(SiteParser):
    """ This class gets information for items sold on newegg.com """

    def __init__(self, search_combos=False):
        self.search_combos = search_combos
        self.base_url = 'https://www.newegg.com/p/pl?d='
        self.name_parser = ElementParser(
            "class",
            "product-title",
            "product-action-group display-flex align-items-center justify-content-space-between")
        self.price_parser = ElementParser(
            "class", "price-current", "price-save")
        self.in_stock_parser = ElementParser(
            "class", "product-inventory", "product-bullets")
        self.search_parser = ElementURLParser(
            "class", "item-container", limit=10)

    @classmethod
    def _is_combo_url(cls, url):
        return "ComboDealDetails" in url

    def _feed_item_parsers(self, html_text):
        self.name_parser.feed(html_text)
        self.price_parser.feed(html_text)
        self.in_stock_parser.feed(html_text)

    def get_item_info(self, html_text):
        """
        This function grabs the information about the item
        :param html: The HTML text of a webpage
        returns: the item name (str), the price (str), and if the item is in stock (boolean)
        """
        self._feed_item_parsers(html_text)
        name = self.name_parser.get_data()
        price = self.price_parser.get_data()
        in_stock = "OUT OF STOCK." not in self.in_stock_parser.get_data()
        if name and price and in_stock:
            return name, price, in_stock
        return None, None, None

    def search(self, text, search_limit=0):
        """ User can specify how many search results they want by assigning search_limit."""
        if search_limit:
            self.search_parser.search_limit = search_limit
        self.search_parser.feed(self._get_html(self.base_url + text))
        search_results = self.search_parser.get_data()
        items = []
        for url in search_results:
            if self._is_combo_url(url) and not self.search_combos:
                continue
            item = self.get_item_info(self._get_html(url))
            if item:
                items.append(item)
        return items


def format_html(text):
    """ Formats HTML to be more human-readabled """
    return etree.tostring(
        html.fromstring(text),
        encoding='unicode',
        pretty_print=True)


def main():
    """ Main function """
    while True:
        search_term = input(
            "What item do you want to search? Type 'exit' to quit.\n")
        if search_term == "exit":
            sys.exit(0)
        newegg = NeweggParser()
        items = newegg.search(search_term)
        for item in items:
            print(item)
        print("\n")


if __name__ == "__main__":
    main()
