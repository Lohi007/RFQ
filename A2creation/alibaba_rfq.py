import requests
from bs4 import BeautifulSoup
import csv
import datetime
import time
import re

def clean(text):
    return re.sub(r'\s+', ' ', text.strip())

base_url = "https://sourcing.alibaba.com/rfq/rfq_search_list.htm"
params = {
    "country": "United Arab Emirates",
    "recently": "Y",
    "tracelog": "newest",
    "page": 1
}

scraping_date = datetime.datetime.now().strftime("%d-%m-%Y")
rfqs = []
max_pages = 3  # You can increase this

for page in range(1, max_pages + 1):
    print(f"Scraping page {page}")
    params["page"] = page
    response = requests.get(base_url, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')
    cards = soup.find_all("div", class_="rfq-item")  # Update if structure changes

    for card in cards:
        try:
            title_tag = card.find("a", class_="title")
            title = clean(title_tag.text) if title_tag else ""
            rfq_url = "https:" + title_tag['href']
            rfq_id = re.search(r'rfqId=(\d+)', rfq_url).group(1) if rfq_url else ""

            buyer_name = clean(card.find("div", class_="user-name").text)
            buyer_image = card.find("img")["src"] if card.find("img") else ""
            inquiry_time = clean(card.find("div", class_="rfq-time").text)
            quotes_left = clean(card.find("span", class_="quote-left").text)
            country = clean(card.find("span", class_="country").text)
            quantity = clean(card.find("span", class_="quantity").text)

            email_confirmed = "Yes" if "Email Confirmed" in card.text else "No"
            experienced_buyer = "Yes" if "Experienced Buyer" in card.text else "No"
            complete_order = "Yes" if "Complete Order via RFQ" in card.text else "No"
            typical_replies = "Yes" if "Typically replies" in card.text else "No"
            interactive_user = "Yes" if "Interactive User" in card.text else "No"

            rfqs.append([
                rfq_id, title, buyer_name, buyer_image, inquiry_time, quotes_left,
                country, quantity, email_confirmed, experienced_buyer,
                complete_order, typical_replies, interactive_user,
                rfq_url, scraping_date, scraping_date
            ])
        except Exception as e:
            print("Error parsing card:", e)
            continue

    time.sleep(1)

# Write to CSV
with open("alibaba_rfq_output.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        'RFQ ID', 'Title', 'Buyer Name', 'Buyer Image', 'Inquiry Time', 'Quotes Left',
        'Country', 'Quantity Required', 'Email Confirmed', 'Experienced Buyer',
        'Complete Order via RFQ', 'Typical Replies', 'Interactive User',
        'Inquiry URL', 'Inquiry Date', 'Scraping Date'
    ])
    writer.writerows(rfqs)

print("Scraping complete! Output saved to alibaba_rfq_output.csv")
