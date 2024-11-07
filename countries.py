import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
countries=[]
url= "https://www.sialparis.com/en/EXHIBITORS-2024/exhibitors"

options = webdriver.ChromeOptions()
options.add_experimental_option(name="detach",value= True)
driver = webdriver.Chrome(options=options)
driver.get(url)
country = driver.find_elements(By.XPATH, value='//*[@id="catalog-v2"]//div[contains(@class ,"CatalogFilterBlock-category")]/label')
for element in country:
    country_name = element.get_attribute("title").split(" ")[0]
    countries.append(country_name)
print(countries)
driver.quit()