try:
    import sys
    import requests
    from bs4 import BeautifulSoup
    import csv
    import os.path
    import shutil
    from os import path
except ModuleNotFoundError as e:
    print("\nCertains modules sont manquants," 
          "veuillez taper 'pip install -r "
          "requirements.txt' pour les installer\n")
    raise SystemExit(e)

class Book(object):
    """
    This class takes a book url for argument and returns some informations of that book
    """

    def __init__(self, url):
        """
        Constructor method, called when an instance is created
        """
        self.url = url
        self.title = self._get_title(url)
        self.description = self._get_description(url)
        self.category = self._get_category(url)
        self.rating = self._get_rating(url)
        self.price_excluding_taxe = self._get_price_excluding_taxes(url)
        self.price_including_taxe = self._get_price_including_taxes(url)
        self.upc = self._get_upc(url)
        self.number_available = self._get_number_available(url)
        self.image_url = self._get_image_url(url)


    def _get_title(self, url):
        """
        Return the title of the book
        """
        response = requests.get(url, stream = True)
        soup = BeautifulSoup(response.text, 'lxml')
        self.title = soup.find('div', {'class': 'product_main'}
                ).find('h1')
        return self.title.text


    def _get_description(self, url):
        """
        Return the description of the book
        """
        response = requests.get(url, stream = True)
        soup = BeautifulSoup(response.text, 'lxml')
        self.description = soup.find('p', {'class': ''})
        if self.description != None:
            return self.description.text
        else: 
            return "No description"
    

    def _get_category(self, url):
        """
        Return an array containing the books category
        """
        response = requests.get(url, stream = True)
        soup = BeautifulSoup(response.text, 'lxml')
        self.category_data = []
        category = soup.find('ul', {'class': 'breadcrumb'})
        row_category = category.find_all('li')
        for row in row_category:
            cols = row.find_all('a')
            cols = [ele.text.strip() for ele in cols]
            self.category_data.append([ele for ele in cols if ele])
        return self.category_data[2]

    def _get_rating(self, url):
        """
        Return the rating of the book
        """
        response = requests.get(url, stream = True)
        soup = BeautifulSoup(response.text, 'lxml')
        class_name = []
        for element in soup.find_all(class_='star-rating'):
            class_name.extend(element["class"])
        return f"{class_name[1]} out of five"

    def _get_table_value(self, url):
        """
        Return an array of books informations :
        upc, prices with taxes, price without taxes,
        stock
        """
        response = requests.get(url, stream = True)
        soup = BeautifulSoup(response.text, 'lxml')
        data = []
        data2 = []
        table = soup.find('table', {'class': 'table-striped'})
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')  # Loop though the table and collect data
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])  # Get rid of empty values
        for elements in data:
            data2.append(elements[0])
        data2[2] = data2[2][1:] 
        data2[3] = data2[3][1:] 
        return data2

    def _get_price_excluding_taxes(self, url):
        """
        Return the price without taxes 
        """
        price = self._get_table_value(url)
        return price[2]
    
    def _get_price_including_taxes(self, url):
        """
        Return the price with taxes 
        """
        price = self._get_table_value(url)
        return price[3]   
    
    def _get_number_available(self, url):
        """
        Return the number of available books
        """
        price = self._get_table_value(url)
        return price[5]   
         
    def _get_upc(self, url):
        """
        Return the upc 
        """
        price = self.get_table_value(url)
        return price[0]  


    def _get_image_url(self, url):
        """
        Return the image url
        """
        response = requests.get(url, stream = True)
        soup = BeautifulSoup(response.text, 'lxml')
        image_url = soup.find('div', {'class': 'item active'})
        image_url = image_url.find('img')
        self.image_url = image_url['src'].replace('../../',
                                             'http://books.toscrape.com/')
        return self.image_url
