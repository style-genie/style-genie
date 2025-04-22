import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import json
import os
import tempfile
import shutil
import random
allitems=[]
def get_random_proxy(proxy_list_path):
    with open(proxy_list_path, 'r') as f:
        proxies = json.load(f)
    proxy = random.choice(proxies)
    return proxy['ip'], proxy['port']


def scrape_ssense(page_number):
    driver = None
    temp_dir = tempfile.mkdtemp(prefix="my_temp_dir_")
    try:
        # Set up Chrome options
        # chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--disable-gpu")
        proxy_list_path = '/root/StyleRecommendation/fashion_agent/proxies.agent'
        proxy_host, proxy_port = get_random_proxy(proxy_list_path)

        # Define custom options for the Selenium driver
        options = Options()
        proxy_server_url = f"https://{proxy_host}:{proxy_port}"
        print("proxy" + proxy_server_url)
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")  # Optional: Headless Modus
        options.add_argument(f'--proxy-server={proxy_server_url}')

        temp_user_data_dir = tempfile.mkdtemp(prefix="chrome-user-data-")
        # chrome_options.add_argument(f"--user-data-dir={temp_user_data_dir}")

    
        # driver = webdriver.Chrome(options=chrome_options)
        driver = webdriver.Firefox(options=firefox_options)
        # if os.path.exists("/scrape/ssense-chrome-user-data"):
        #     shutil.rmtree("/scrape/ssense-user-data") #Das Verzeichnis muss leer sein, chrome-user-data
        #     os.makedirs("/scrape/ssense-chrome-user-data")

        # Path to the ChromeDriver executable (replace with your actual path)
        chromedriver_path = "/usr/bin/chromedriver"  # Replace with the correct path

        # Set up the webdriver
        try:
            driver = webdriver.Chrome(options=firefox_options)
        except Exception as e:
            print(f"Error setting up webdriver: {e}")
            return

        # URL to scrape
        #target_url = 'https://www.ssense.com/en-de/men/sale'
        target_url = f'https://www.ssense.com/en-de/men/sale?page={page_number}'
        driver.get(target_url)
        driver.maximize_window()

        # Check for CAPTCHA
        try:
            driver.get(target_url)
            driver.maximize_window()

            element = driver.find_element_by_css_selector('#px-captcha')
            action = ActionChains(driver)
            action.click_and_hold(element)
            action.perform()
            time.sleep(10)
            action.release(element)
            action.perform()
            time.sleep(0.2)
            action.release(element)
            
            # element = driver.find_element(By.CSS_SELECTOR, '#px-captcha')
            # action = ActionChains(driver)
            # action.click_and_hold(element).perform()
            # time.sleep(10)
            # action.release(element).perform()
            # time.sleep(0.2)
            # action.release(element).perform()
        except:
            print("No CAPTCHA found")

        time.sleep(5)  # Wait for the page to load after CAPTCHA

        # Find all product tiles
        product_tiles = driver.find_elements(By.CSS_SELECTOR, "div.plp-products__product-tile")

        # Extract data from each product tile
        items = []
        for tile in product_tiles:
            try:
                title = tile.find_element(By.CSS_SELECTOR, "span[data-test^='productName']").text
                brand = tile.find_element(By.CSS_SELECTOR, "span[data-test^='productBrandName']").text
                price = tile.find_element(By.CSS_SELECTOR, "span[data-test^='productCurrentPrice']").text.replace(u'\\u20ac', u'€')
                link = tile.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                price_string = price.replace("\u20ac", "")

                # Tausendertrennzeichen entfernen/ersetzen (falls vorhanden)
                price_string = price_string.replace(".", "") # Punkt entfernen
                price_string = price_string.replace(",", ".") # Komma durch Punkt ersetzen (falls Komma als Dezimaltrennzeichen verwendet wird)


                # In Float umwandeln
                price_float = float(price_string)
                item = {
                    "name": title,
                    "brand": brand,
                    "price": price_float,
                    "link": link
                }
                print(json.dumps(item, indent=2))

                allitems.append(item)
            except Exception as e:
                print(f"Error extracting data from tile: {e}")

        # Print the extracted data as JSON
       

    except Exception as e:
        print(f"Error during scraping: {e}")

    finally:
        # Close the browser
        if driver:
            driver.quit()

# if __name__ == "__main__":
#     scrape_ssense()
if __name__ == "__main__":
    page_number = 1
    while page_number<2:
        print(f"Scraping page {page_number}...")
        items = scrape_ssense(page_number)
        if items is None:
            break
        page_number += 1

    # Print the extracted data as JSON
    print(json.dumps(allitems, indent=2))
    try:
        with open("./output.json", "w") as outfile:
            json.dump(allitems, outfile, indent=2)
        print("Data written to output.json")
    except Exception as e:
        print(f"Error writing to output.json: {e}")