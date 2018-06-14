import sys, time, os
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

#list for saving scraped data
data_list = []

def get_news_data(start_url, search_kw):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(chrome_options=chrome_options)

    logging.info("Loading the page: {}".format(start_url))
    driver.get(start_url)
    time.sleep(3)
    logging.info("Searching for: {}".format(search_kw))
    search_field = driver.find_element_by_xpath("//input[@name='searchString']")
    search_field.send_keys(search_kw)
    search_button = driver.find_element_by_xpath("//input[@value='Search']")
    driver.execute_script("arguments[0].click();", search_button)
    time.sleep(5)
    news_list = driver.find_elements_by_class_name("summary")
    logging.info("Total news info scraped: {}".format(len(news_list)))

    for news in news_list:
        img_url = ""
        news_url = ""
        news_title = ""
        news_date = ""

        try:
            img_url = news.find_element_by_tag_name("img").get_attribute("src")
            news_span = news.find_element_by_class_name("resultTitle")
            news_a_tag = news_span.find_element_by_tag_name("a")
            news_url = news_a_tag.get_attribute("href")
            news_title = news_a_tag.text.strip()
            news_date = news.find_element_by_class_name("resultDateInfo").text.strip().split("\n")[-1]
        except Exception as e:
            logging.info(e)

        data_dict = {
            "Title": news_title,
            "Url": news_url,
            "Image": img_url,
            "Published Date": news_date
        }
        data_list.append(data_dict)

    try:
        driver.close()
        driver.quit()
    except Exception as e:
        logging.info(e)


def get_output(excel_file):
    if data_list:
        columns = ["Title", "Url", "Image", "Published Date"]
        df = pd.DataFrame(columns=columns)
        df = df.append(data_list, ignore_index=True)
        #options 'strings_to_urls=False' is used to convert url to text to avoid issues with long url
        writer = pd.ExcelWriter(excel_file, engine="xlsxwriter", options={"strings_to_urls": False})
        df.to_excel(writer, index=False)
        logging.info("Scraped data saved as: {}".format(excel_file))
    else:
        logging.info("No data found!")


if __name__ == "__main__":
    #English verison url
    start_url = "https://bdnews24.com/"
    #Bengali verison url
    #start_url = "https://bangla.bdnews24.com/"

    while True:
        search_kw = input("Enter keyword to search: ").strip()
        if search_kw:
            excel_file = "{}_news.xlsx".format(search_kw)
            break

    try:
        try:
            get_news_data(start_url, search_kw)
        except KeyboardInterrupt as e:
            logging.info(e)
    except Exception as e:
        logging.info(e)

    try:
        get_output(excel_file)
    except Exception as e:
        logging.info(e)
