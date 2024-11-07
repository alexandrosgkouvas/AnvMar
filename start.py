import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
country= input("Select country")
countries=[]
list = []
url= f"https://www.sialparis.com/en/EXHIBITORS-2024/exhibitors?catalog.prod.sial.exhibitors.en.name-asc%5BrefinementList%5D%5Baddress.country%5D%5B0%5D={country}"

options = webdriver.ChromeOptions()
options.add_experimental_option(name="detach",value= True)
driver = webdriver.Chrome(options=options)

driver.get(url)
company_name = driver.find_elements(By.XPATH, value='//*[@id="catalog-v2"]//h3[contains(@class, "CatalogCardLine-title")]/div/span/span')
for element in company_name:
    list.append(element.text)
df = pd.DataFrame(list, columns=['Name of Company'])
driver.quit()
df.to_excel(f"{country}.xlsx", index = False)