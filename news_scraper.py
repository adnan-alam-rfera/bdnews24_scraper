import os, sys, time
import logging, subprocess

log_filename = "bdnews_scraper.log"
logging.basicConfig(filename=log_filename, level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")

try:
    from selenium import webdriver
except ImportError as e:
    logging.info("selenium not installed! Installing it...")
    subprocess.call(["pip", "install", "selenium"])
    logging.info("selenium installed. Please re run the script.")
    sys.exit(1)

try:
    import pandas as pd
except ImportError as e:
    logging.info("pandas not installed! Installing it...")
    subprocess.call(["pip", "install", "pandas"])
    logging.info("pandas installed. Please re run the script.")
    sys.exit(1)

try:
    import xlsxwriter
except ImportError as e:
    logging.info("xlsxwriter not installed! Installing it...")
    subprocess.call(["pip", "install", "xlsxwriter"])
    logging.info("xlsxwriter installed. Please re run the script.")
    sys.exit(1)


data_list = []
count = 0

def get_news(start_url, search_kw):

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-logging")
    driver = webdriver.Chrome(chrome_options=chrome_options)

    driver.get(start_url)
    time.sleep(3)
    search_field = driver.find_element_by_xpath("//input[@name='searchString']")
    search_field.send_keys(search_kw)
    search_button = driver.find_element_by_xpath("//input[@value='Search']")
    driver.execute_script("arguments[0].click();", search_button)
    time.sleep(1)
    news_list = driver.find_elements_by_class_name("summary")

    for news in news_list:
        img_url = ""
        news_url = ""
        news_title = ""
        news_date = ""

        try:
            img_url = news.find_element_by_tag_name("img").get_attribute("src")
            news_span = driver.find_element_by_class_name("resultTitle")
            news_a_tag = news_span.find_element_by_tag_name("a")
            news_url = news_a_tag.get_attribute("href")
            news_title = news_a_tag.text.strip()
            news_date = driver.find_element_by_class_name("resultDateInfo").text.strip().split("\n")[-1]
        except Exception as e:
            logging.info(e)

        data_dict = {
            "Title": news_title,
            "Url": news_url,
            "Image": img_url,
            "Published Date": news_date
        }

        data_list.append(data_dict)
