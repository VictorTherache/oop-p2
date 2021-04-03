try:
    import sys
    import requests
    from bs4 import BeautifulSoup
    import csv
    from Book import Book
    # from scrap_one_category_class import ScrapOneCategory
    import os.path
    import shutil
    from os import path
except ModuleNotFoundError as e:
    print("\nCertains modules sont manquants," 
          "veuillez taper 'pip install -r "
          "requirements.txt' pour les installer\n")
    raise SystemExit(e)


class SiteInternet(object):
    """
    This class can put Books info in csv's
    """

    def _remove_special_char(self, url):
        """
        Return a string with no special character in it
        """
        response = requests.get(url, stream = True)
        soup = BeautifulSoup(response.text, 'lxml')
        book = Book(url)
        title = book._get_title(url)
        no_special_char_string = [character for character in title if character.isalnum()]
        no_special_char_string = "".join(no_special_char_string)
        return no_special_char_string


    def _download_book_image(self, url):
        """
        Download the books cover picture in the image_folder 
        """
        book = Book(url)
        response = requests.get(url, stream = True)
        soup = BeautifulSoup(response.text, 'lxml')
        img_url = book._get_image_url(url)
        title = self._remove_special_char(url)
        if not os.path.exists('./image_folder'):
            os.mkdir('image_folder')
        if not os.path.exists(f"./image_folder/{title}.jpg"):
            response = requests.get(img_url, stream=True)
            with open(f"./image_folder/{title}.jpg", "wb") as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)


    def put_book_info_in_csv(self, url):
        """
        Writes the informations in a csv
        """
        book = Book(url)
        self._download_book_image(url)
        headers = ['url', 'upc', 'title', 'price_including_taxe', 'price_excluding_taxe', 
                'number_available', 'product_description', 'category', 'review_rating',
                'image_url']
        with open(f'{book.category[0]}.csv', 'a', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames = headers)
            if os.stat(f'{book.category[0]}.csv').st_size == 0: #check if file is empty so we can add headers
                writer.writeheader()
            writer.writerow({'url' : book.url, 
                            'upc': book.upc, 
                            'title': book.title, 
                            'price_including_taxe': book.price_including_taxe, 
                            'price_excluding_taxe': book.price_excluding_taxe, 
                            'number_available': book.number_available, 
                            'product_description': book.description, 
                            'category': book.category[0],
                            'review_rating': book.rating, 
                            'image_url': book.image_url})

    def _get_nbr_of_pages(self, url):
        """
        Return the number of a category's pages
        """
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        nbr = soup.find('ul', {'class': 'pager'})
        if(nbr):
            nbr = nbr.find('li', {'class': 'current'})
            nbr = int(nbr.text.strip()[-2:])  # Keep the integer in the string
            return nbr

    def _split_url(self, url): # Change the url so it can be iterated
        """
        Return a url that can be used for iteration
        """
        url = url.split('index') 
        url = url[0] + 'page-1.html'
        url = url.split('page-')
        url = f"{url[0]}page-1.html"
        return url

    def _get_books_url(self, url):
        """
        Return an array of all books url of a category
        """
        url_array = []
        nbr_pages = self._get_nbr_of_pages(url) 
        if(nbr_pages == None):
            nbr_pages = 1
        formatted_url = self._split_url(url)
        formatted_url = formatted_url.split('page')
        for i in range(1, int(nbr_pages) + 1):
            if nbr_pages != 1:
                join_url = formatted_url[0] + 'page-' + str(i) + '.html'
            else: 
                join_url = url
            response = requests.get(join_url)
            if(response.ok):
                soup = BeautifulSoup(response.text, 'lxml')
                table = soup.find('ol', {'class': 'row'})
                rows = table.find_all('a', href=True)
            for row in rows:
                if row.text:
                    url_array.append(
                        "http://books.toscrape.com/catalogue/" 
                        + row['href'].strip('../'))
        return url_array


    def put_books_info_in_csv(self, url):
        """
        Put all the books informations of a category in a csv
        """
        books_urls = self._get_books_url(url)
        for url in books_urls:
            self.put_book_info_in_csv(url)


if __name__ == '__main__':  
    try:
        url = sys.argv[1] if len(sys.argv) > 1 else url = "https://books.toscrape.com/"
        d = SiteInternet()
        d.put_books_info_in_csv(url)
        print('\n**** Success ****\n')
    except IndexError:
        print('Veuillez entrer un url en tant que paramètre')
    except requests.exceptions.RequestException as e: 
        print("\nErreur de connection, veuillez vérifier votre connection"
              " internet ou entrer un url valide\n")
        raise SystemExit(e)
    except (AttributeError, UnboundLocalError) as e:
        print("Veuillez rentrer une url valide, ex : " 
              "https://books.toscrape.com/catalogue/a-walk-to-remember_312/index.html'")
