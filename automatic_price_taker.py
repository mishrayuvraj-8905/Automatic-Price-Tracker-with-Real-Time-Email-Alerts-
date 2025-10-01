import requests
from bs4 import BeautifulSoup
import smtplib
import time
import configparser

# Load configuration from a file (config.ini recommended)
config = configparser.ConfigParser()
config.read('config.ini')

URL = config['PRODUCT']['url']
HEADERS = {'User-Agent': config['REQUEST']['user_agent']}
PRICE_THRESHOLD = float(config['ALERT']['price_threshold'])
CHECK_INTERVAL = int(config['SETTINGS']['check_interval_seconds'])

# Email settings
SMTP_SERVER = config['EMAIL']['smtp_server']
SMTP_PORT = int(config['EMAIL']['smtp_port'])
EMAIL_ADDRESS = config['EMAIL']['email_address']
EMAIL_PASSWORD = config['EMAIL']['email_password']
TO_ADDRESS = config['EMAIL']['to_address']

def get_price():
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Customize the selector below for the specific e-commerce site
    price_tag = soup.select_one(config['SELECTOR']['price_css_selector'])
    if price_tag:
        price_text = price_tag.get_text().strip()
        price = parse_price(price_text)
        return price
    return None

def parse_price(price_str):
    # Extract numerical value from price string (e.g., '$1,234.56' -> 1234.56)
    filtered = ''.join(c for c in price_str if (c.isdigit() or c == '.' or c == ','))
    filtered = filtered.replace(',', '')
    try:
        return float(filtered)
    except:
        return None

def send_email(price):
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        subject = "Price Alert: Item now below threshold!"
        body = f"The price has dropped to {price}.\nCheck the product here: {URL}"
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(EMAIL_ADDRESS, TO_ADDRESS, message)

def main():
    last_price = None
    while True:
        current_price = get_price()
        if current_price is not None:
            print(f"Current price: {current_price}")
            if current_price <= PRICE_THRESHOLD:
                if last_price is None or current_price < last_price:
                    print("Price threshold met, sending alert email...")
                    send_email(current_price)
                    last_price = current_price
                else:
                    print("Price is below threshold but no drop since last alert.")
            else:
                print("Price is above threshold.")
        else:
            print("Failed to retrieve price.")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
