import csv
import json
import random

from fastapi import APIRouter, requests
from fastapi.responses import HTMLResponse
import httpx
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os
router = APIRouter()
DATA_FILE = "books_with_country.json"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
@router.get("/api/get_all_country", response_class=HTMLResponse)
async def get_all_country_data(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://restcountries.com/v3.1/all")
        countries = response.json()
    return templates.TemplateResponse("countries_view.html", {"request": request, "countries": countries})
@router.get("/api/book_country_random",response_class=HTMLResponse)
async def random_country_for_book(request: Request):
    books = []
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        try:
            with open(DATA_FILE, encoding="utf-8") as f:
                books = json.load(f)
        except json.JSONDecodeError:
            books = []
    async with httpx.AsyncClient() as client:
        response = await client.get("https://restcountries.com/v3.1/all")
        countries = response.json()
        country_names = [country.get("name", {}).get("common") for country in countries if "name" in country]
        country_names = [name for name in country_names if name]  # Remove empty ones
    for book in books:
        book["publisher_country"] = random.choice(country_names)
    # Save to JSON
    with open("books_with_country.json", "w", encoding="utf-8") as json_file:
        json.dump(books, json_file, indent=2, ensure_ascii=False)
    return templates.TemplateResponse("book_views.html", {"request": request, "books": books,"message":'Random country for book successfully and save in books_with_country.json'})
