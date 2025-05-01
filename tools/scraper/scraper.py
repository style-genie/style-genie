import time
import requests
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options
import getpass
from fake_useragent import UserAgent
import json
import os
import tempfile
import shutil
import random
from selenium.webdriver import DesiredCapabilities
# from selenium_recaptcha_solver import RecaptchaSolver
# import undetected_chromedriver as uc
allitems = []


def get_random_proxy(proxy_list_path):
    with open(proxy_list_path, 'r') as f:
        proxies = json.load(f)
    proxy = random.choice(proxies)
    return proxy['ip'], proxy['port']


def scrape_ssense(page_number):
    driver = None
    try:
        proxy_list_path = ",,/proxies.json"
        proxy_host, proxy_port = get_random_proxy(proxy_list_path)
        print(f"using proxy: {proxy_host}")
        # Use Firefox Options
        ua = UserAgent()
        firefox_options = FirefoxOptions()
        #firefox_options.add_argument("--headless")
        firefox_options.add_argument(f'user-agent={ua.random}')
        firefox_options.set_preference("network.proxy.type", 1)
        firefox_options.set_preference("network.proxy.http", proxy_host)
        firefox_options.set_preference("network.proxy.http_port", int(proxy_port))
        firefox_options.add_argument('--no-sandbox')
        firefox_options.add_argument("--disable-extensions")
        # profile = webdriver.FirefoxProfile()
        # profile.set_preference("general.useragent.override", ua.random)
        # profile.set_preference("accept-language", "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7")
        firefox_options.set_preference('acceptInsecureCerts', True) #Richtiger Code
        driver = webdriver.Firefox(options=firefox_options)#, firefox_profile=profile)
        # options = Options()
        # options.add_argument("--headless")  # Remove this if you want to see the browser (Headless makes the chromedriver not have a GUI)
        # options.add_argument("--window-size=1920,1080")
        # options.add_argument(f'--user-agent={ua}')
        # options.add_argument('--no-sandbox')
        # options.add_argument("--disable-extensions")
        # driver = uc.Chrome(headless=True,use_subprocess=False, port=9222, options=options)
        target_url = f'https://www.ssense.com/en-de/men?page={page_number}'
        # solver = RecaptchaSolver(driver=driver)
        # Check for CAPTCHA
        driver.get(target_url)
        driver.maximize_window()
        html = driver.page_source
        # with open("ssense.html", "w") as f:
        #     f.write(html)
        print("HTML saved to ssense.html")
        # time.sleep(5)  # Wait for the page to load after CAPTCHA
        product_tiles = driver.find_elements(By.CSS_SELECTOR, "div.plp-products__product-tile")
        items = []
        for tile in product_tiles:
                # time.sleep(10)
                title = tile.find_element(By.CSS_SELECTOR, "span[data-test^='productName']").text
                brand = tile.find_element(By.CSS_SELECTOR, "span[data-test^='productBrandName']").text
                price = tile.find_element(By.CSS_SELECTOR, "span[data-test^='productCurrentPrice']").text.replace(u'\\u20ac', u'€')
                link = tile.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                image_element = tile.find_element(By.CSS_SELECTOR, "source[data-srcset]")
                image_link = image_element.get_attribute("data-srcset") 
                print(image_link)
                price_string = price.replace("\u20ac", "")
                price_string = price_string.replace(".", "")
                price_string = price_string.replace(".", "") 
                price_string = price_string.replace(",", ".") 
                price_float = float(price_string)
                # target_url = link
                # driver.get(target_url)
                # driver.maximize_window()
                # driver.save_screenshot('nowsecure.png')
                # description = driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]').get_attribute("content")
                item = {
                    "name": title,
                    "brand": brand,
                    "price": price_float,
                    "link": link,
                    "image": image_link
                }
                print(image_link)
                # downloading the image
                # try:
                #     os.makedirs("images", exist_ok=True)
                #     if image_url.startswith("data:image"):
                #         # Handle base64 encoded images
                #         image_data = image_url.split(",")[1]
                #         item["image"] = image_path
                #         print(f"Downloaded image to {image_path}")
                #     else:
                #         # Handle regular image URLs
                #         image_name = image_url.split("/")[-1]
                #         # Extract image extension from URL
                #         image_extension = image_name.split(".")[-1]
                #         image_path = os.path.join("images", image_name)
                #         response = requests.get(image_url, stream=True)
                #         if response.status_code == 200:
                #             with open(image_path, 'wb') as f:
                #                 shutil.copyfileobj(response.raw, f)
                #             item["image"] = image_path  # Store the relative path
                #             print(f"Downloaded image to {image_path}")
                #         else:
                #             print(f"Failed to download image from {image_url}")
                # except Exception as e:
                #     print(f"Error downloading image: {e}")

                items.append(item)
                print(item)
        try:
            with open(f'./men_output_{page_number}.json', "w") as outfile:
                json.dump(items, outfile, indent=2)
            print("Data written to men_output.json")
        except Exception as e:
            print(f"Error writing to output.json: {e}")
        allitems.extend(items)
        print(items)

    finally:
        if driver:
            pass
            #driver.quit()


if __name__ == "__main__":
    page_number = 1
    #while page_number<2:
    print(f"Scraping page {page_number}...")
    scrape_ssense(page_number)
        # print(json.dumps(allitems, indent=2))
    #page_number += 1
    # try:
    #     with open("./output.json", "w") as outfile:
    #         json.dump(allitems, outfile, indent=2)
    #     print("Data written to output.json")
    # except Exception as e:
    #     print(f"Error writing to output.json: {e}")
