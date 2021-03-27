try:
    import sys
    import requests
    from bs4 import BeautifulSoup
    import csv
    from scrap_one_book_class import ScrapOneBook
    from scrap_one_category_class import ScrapOneCategory
    import os.path
    import shutil
    from os import path
except ModuleNotFoundError as e:
    print("\nCertains modules sont manquants," 
          "veuillez taper 'pip install -r "
          "requirements.txt' pour les installer\n")
    raise SystemExit(e)

class ScrapAll:
    def __init__(self, url):
        self.url = url

    def get_categories_url(self, url):
        """
        Return an array of all categories urls
        """
        response = requests.get(homepage_url)
        if(response.ok):
            soup = BeautifulSoup(response.text, 'lxml')
            links = soup.find_all('a')
            categories_array = []
            for link in links:
                if "catalogue/category" in link['href']:
                    categories_array.append("http://books.toscrape.com/" 
                    + link['href'])
            return categories_array

    def scrap_all_books(self, url):
        """
        Puts all the books informations from the website in multiple csvs
        """
        categories_urls = self.get_categories_url(homepage_url)
        print(categories_urls)
        categories_urls.pop(0)
        for category in categories_urls:
            scrap_one_category = ScrapOneCategory(category)
            scrap_one_category.put_books_info_in_csv(category)


if __name__ == '__main__':
    try:
        homepage_url = "https://books.toscrape.com/"
        scrap = ScrapOneCategory(homepage_url)
        scrap_all = ScrapAll(homepage_url)
        category_array = scrap.get_category(homepage_url)
        for category in category_array:
            if os.path.exists(f"{category}.csv"):
                os.remove(f"{category}.csv")
        scrap_all.scrap_all_books(homepage_url)
        print('\n**** Success ****\n')
    except requests.exceptions.RequestException as e: 
        print("\nErreur de connection, veuillez vérifier" 
              " votre connection internet ou rentrer un url valide\n")
        raise SystemExit(e)