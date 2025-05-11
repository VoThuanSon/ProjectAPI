import json
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os,time, requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
import pandas as pd
class Book(BaseModel):
    title: str
    price: str
    availability: str
    product_link: str
    rating: int
    publisher_country: str
DATA_FILE = "books_with_country.json"

def rating_to_numeric(rating):
    rating_map = {
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }
    return rating_map.get(rating, 0)
router = APIRouter()
base_url = 'https://books.toscrape.com/catalogue/category/books/young-adult_21/index.html'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
@router.get("/api/craw_book_data", response_class=HTMLResponse)
def craw_book_data(request: Request):
    book_data = get_book_data()
    df = pd.DataFrame(book_data)
    df.to_csv('list_book.csv', index=False)
    with open(DATA_FILE, "w", encoding="utf-8") as json_file:
        json.dump(book_data, json_file, indent=2, ensure_ascii=False)
    return templates.TemplateResponse("book_views.html", {"request": request, "books": book_data,"message" : 'Save books data success to list_book.csv'})

@router.get("/api/books", response_class=HTMLResponse)
def get_all_books(request: Request, country: Optional[str] = Query(None)):
    books = []
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, encoding="utf-8") as f:
            books = json.load(f)
    if country:
        books = [book for book in books if book.get("publisher_country", "").lower() == country.lower()]
    # return JSONResponse(content={"books": books})
    return templates.TemplateResponse("book_views.html", {"request": request, "books": books,})

@router.delete("/api/books/{title}")
def delete_book(title: str, request: Request):
    books = []
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, encoding="utf-8") as f:
            books = json.load(f)
    books = [book for book in books if book.get("title", "").lower() != title.lower()]
    save_data(books)
    return templates.TemplateResponse("book_views.html", {"request": request, "books": books,})
@router.post("/api/books")
def create_book(book: Book, request: Request):
    books = []
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        try:
            with open(DATA_FILE, encoding="utf-8") as f:
                books = json.load(f)
        except json.JSONDecodeError:
            books = []
    books.insert(0, book.dict())
    save_data(books)
    return templates.TemplateResponse("book_views.html", {"request": request, "books": books,})


def get_book_data():
    # Scrape data from multiple pages
    all_books = []
    for page_num in range(1, 4):  # Adjust the range for more pages
        url = f'{base_url[:-10]}page-{page_num}.html'
        print(f'Scraping {url}...')
        books = scrape_page(url)
        all_books.extend(books)
        time.sleep(1)
    return all_books

def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    books = soup.find_all('article', class_='product_pod')
    book_data = []

    for book in books:
        title = book.h3.a['title']
        price = book.find('p', class_='price_color').text
        availability = book.find('p', class_='instock availability').text.strip()
        rating_class = book.p['class'][1]
        rating = rating_to_numeric(rating_class)
        product_page_link = 'https://books.toscrape.com/catalogue' + book.h3.a['href'][8:]
        # Save the raw HTML of the product page
        product_page_response = requests.get(product_page_link)
        with open(f'html_backup/{title}.html', 'w', encoding='utf-8') as f:
            f.write(product_page_response.text)

        book_data.append({
            'title': title,
            'price': price,
            'availability': availability,
            'rating': rating,
            'product_link': product_page_link
        })

    return book_data

def save_data(books: list):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2, ensure_ascii=False)