""" Main module of the pc_part_sale_notifier """
from html.parser import HTMLParser
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
        return temp_data



class ElementURLParser(HTMLParser):
    """
    This class returns the data within any HTML element.
    :param attr_name: The attribute of the element
    :param start_value: The value of the attribute where you want to start collecting data
    :param end_value: The value of the attribute where you want to stop collecting data
    """

    def __init__(self, attr_name, start_value):
        super().__init__()
        self.save_data = False
        self.attr_name = attr_name
        self.start_value = start_value
        self.data = ""

    def handle_starttag(self, tag, attrs):
        for attr, value in attrs:
            if value == self.start_value:
                self.save_data = True
            if attr == "href" and self.save_data:
                print(value)
                self.data = value
                self.save_data = False
            if value != self.start_value:
                self.save_data = False

    def get_data(self):
        """ Returns the data within the parser and clears out the old data. """
        temp_data = self.data
        self.data = ""
        return temp_data


class NeweggItemParser():
    """ This class gets information for items sold on newegg.com """

    def __init__(self):
        self.name_parser = ElementParser(
            "class",
            "product-title",
            "product-action-group display-flex align-items-center justify-content-space-between")
        self.price_parser = ElementParser(
            "class", "price-current", "price-save")
        self.in_stock_parser = ElementParser(
            "class", "product-inventory", "product-bullets")
        self.search_parser = ElementURLParser(
            "class", "item-title")

    def _feed_item_parsers(self, html):
        self.name_parser.feed(html)
        self.price_parser.feed(html)
        self.in_stock_parser.feed(html)

    def get_item_info(self, html):
        """
        This function grabs the information about the item
        :param html: The HTML text of a webpage
        returns: the item name (str), the price (str), and if the item is in stock (boolean)
        """
        self._feed_parsers(html)
        name = self.name_parser.get_data()
        price = self.price_parser.get_data()
        in_stock = self.in_stock_parser.get_data() != "OUT OF STOCK."
        return name, price, in_stock

    def search(self, html):
        self.search_parser.feed(html)
        return self.search_parser.get_data()

def get_html(url):
    """ Gets the HTML text of a URL """
    request = requests.get(url)
    if request.status_code != 200:
        raise ValueError("Could not get html page.")
    return request.text


def main():
    """ Main function """
    urls = [
        'https://www.newegg.com/p/pl?d=intel'
    ]
    newegg = NeweggItemParser()
    for url in urls:
        with open("test.html", "w") as f:
            html = get_html(url)
            f.write(html)
            print(html)


if __name__ == "__main__":
    main()
