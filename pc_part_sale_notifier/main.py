import sys
import requests

def make_request(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r
    return False

def main():
    html_page = make_request('https://www.newegg.com/asus-geforce-rtx-3080-tuf-rtx3080-o10g-gaming/p/N82E16814126452')
    if not html_page:
        print("URL did not work")
        sys.exit(1)
    print(html_page.text)


if __name__ == "__main__":
    main()
