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

class ScrapOneBook:
    def __init__(self, url):
        self.url = url

    def get_title(self, soup):
    """
    Return the title of the book
    """
        title = soup.find('div', {'class': 'product_main'}
                ).find('h1')
        return title
    
    def get_product_description(self, soup): 
    """
    Return the description of the book
    """
        description = soup.find('p', {'class': ''})
        if description != None:
            return description.text
        else: 
            return "No description"

    def get_table_value(self, soup):
        """
        Return an array of books informations :
        upc, prices with taxes, price without taxes,
        stock
        """
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

    def get_star_rating(self, soup):
        """
        Return the rating of the book
        """
        class_name = []
        for element in soup.find_all(class_='star-rating'):
            class_name.extend(element["class"])
        return f"{class_name[1]} out of five"

    def get_category(self, soup):
        """
        Return an array containing the books category
        """
        category_data = []
        category = soup.find('ul', {'class': 'breadcrumb'})
        row_category = category.find_all('li')
        for row in row_category:
            cols = row.find_all('a')
            cols = [ele.text.strip() for ele in cols]
            category_data.append([ele for ele in cols if ele])
        return category_data

    def get_image_url(self, soup):
        """
        Return the image url of the book
        """
        image_url = soup.find('div', {'class': 'item active'})
        image_url = image_url.find('img')
        image_url = image_url['src'].replace('../../',
                                            'http://books.toscrape.com/')
        return image_url

    def remove_special_char(self, url):
        """
        Return a string with no special character in it
        """
        response = requests.get(self.url, stream = True)
        soup = BeautifulSoup(response.text, 'lxml')
        title = self.get_title(soup).text
        no_special_char_string = [character for character in title if character.isalnum()]
        no_special_char_string = "".join(no_special_char_string)
        return no_special_char_string

    def download_book_image(self):
        """
        Download the books cover picture in the image_folder 
        """
        response = requests.get(self.url, stream = True)
        soup = BeautifulSoup(response.text, 'lxml')
        img_url = self.get_image_url(soup)
        title = self.remove_special_char(self.url)
        if not os.path.exists('./image_folder'):
            os.mkdir('image_folder')
        if not os.path.exists(f"./image_folder/{title}.jpg"):
            response = requests.get(img_url, stream=True)
            with open(f"./image_folder/{title}.jpg", "wb") as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)


    def get_book_info(self, url):
    """
    Return an array containing all the required informations
    """
        book_info = []
        response = requests.get(self.url)
        print(self.url)
        if response.ok:
            soup = BeautifulSoup(response.text, 'lxml')
            title = self.get_title(soup)
            description = self.get_product_description(soup)
            table_info = self.get_table_value(soup)
            rating = self.get_star_rating(soup)
            category = self.get_category(soup)
            image_url = self.get_image_url(soup)
            book_info.append([title.text, description, table_info, rating, category[2][0], image_url])
        return book_info


    def put_book_info_in_csv(self):
        """
        Writes the informations in a csv
        """
        book_info = self.get_book_info(self.url)
        category = book_info[0][4]
        headers = ['url', 'upc', 'title', 'price_including_taxe', 'price_excluding_taxe', 
                'number_available', 'product_description', 'category', 'review_rating',
                'image_url']
        with open(f'{category}.csv', 'a', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames = headers)
            if os.stat(f'{category}.csv').st_size == 0: #check if file is empty so we can add headers
                writer.writeheader()
            writer.writerow({'url' : self.url, 
                            'upc': book_info[0][2][0], 
                            'title': book_info[0][0], 
                            'price_including_taxe': book_info[0][2][3], 
                            'price_excluding_taxe': book_info[0][2][2], 
                            'number_available': book_info[0][2][5], 
                            'product_description': book_info[0][1], 
                            'category': book_info[0][4],
                            'review_rating': book_info[0][3], 
                            'image_url': book_info[0][5]})

if __name__ == '__main__':  
    try:
        url = sys.argv[1]
        scrap = ScrapOneBook(url)
        book_info = scrap.get_book_info(url)
        category = book_info[0][4]
        if os.path.exists(f"{category}.csv"):
            os.remove(f"{category}.csv")
        scrap.put_book_info_in_csv()
        scrap.download_book_image()
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