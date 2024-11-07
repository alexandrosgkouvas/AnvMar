from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException  # Import exceptions
from selenium import webdriver  # Importing webdriver here

import pandas as pd
import time
from urllib.parse import quote
company_names = []
country= input("Select country")
#Scroll and Click the more exhibitors button to show evry exhibitor
driver = webdriver.Chrome()
driver.get(f"https://www.sialparis.com/en/EXHIBITORS-2024/exhibitors?catalog.prod.sial.exhibitors.en.name-asc%5BrefinementList%5D%5Baddress.country%5D%5B0%5D={country}")
while True:
    try:
        see_more_exhibitors = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            '//*[@id="catalog-v2"]//div[contains(@class, "ais-InfiniteHits")]/div[contains(@class, "CatalogButton CatalogButton--textCenter CatalogButton--large CatalogButton--accent")]'))
        )

        driver.execute_script("arguments[0].scrollIntoView();", see_more_exhibitors)
        time.sleep(2)

        see_more_exhibitors.click()

    except Exception as e:
        break

company_name = driver.find_elements(By.XPATH, value='//*[@id="catalog-v2"]//h3[contains(@class, "CatalogCardLine-title")]/div/span/span')
for element in company_name:
    company_names.append(element.text)
print(company_names)

#df = pd.DataFrame(company_names, columns=['Name of Company'])
driver.quit()
#df.to_excel(f"{country}.xlsx", index = False)
# RUN DRIVER FOR ADDRESS
addresses = []


def format_company_name(company):
    # Remove the trailing period if it exists
    if company.endswith("."):
        company = company[:-1]  # Remove the last character (the period)

    # Replace spaces with hyphens, replace periods with hyphens, and handle special characters
    formatted_name = (
        company.replace(" ", "-")  # Replace spaces with hyphens
        .replace(".", "-")  # Replace periods with hyphens (except the last one which is already removed)
        .replace("&", "and")  # Replace `&` with "and"
        .replace("(", "")  # Remove left parenthesis
        .replace(")", "")  # Remove right parenthesis
    )
    while "--" in formatted_name:
        formatted_name = formatted_name.replace("--", "-")

    return formatted_name


# Format URLs
urls = [quote(format_company_name(company)) for company in company_names]
for company in urls:
    url = f"https://www.sialparis.com/en/EXHIBITORS-2024/exhibitor/{company}"
    #print(url)
    options = webdriver.ChromeOptions()
    options.add_experimental_option(name="detach", value=True)
    driver = webdriver.Chrome(options=options)

    success = False

    # Attempt to access the initial URL
    for i in range(6):  # Try the URL with suffixes -1 to -5, and then without suffix
        url_suffix = f"{company}-" + str(i) if i > 0 else company
        url = f"https://www.sialparis.com/en/EXHIBITORS-2024/exhibitor/{url_suffix}"

        try:
            driver.get(url)
            time.sleep(2)
            # Try to locate the address element
            address = driver.find_element(By.XPATH,
                                          '//*[@id="catalog-v2"]/div[1]/div[1]/section[2]/div[2]/div[2]/div[1]/p')
            addresses.append(address.text)
            #print(f"Address found for {url}: {address.text}")
            success = True
            break  # Exit the loop if successful
        except NoSuchElementException:
            print(f"Address element not found for URL: {url}. Trying next.")
        except WebDriverException as e:
            print(f"Failed to access URL: {url}. Error: {e}")

    if not success:
        print(f"Address not found for {company_name} after trying all suffixes.")

    driver.quit()

#print(addresses)
data = {
    'Company Name': company_names,
    'Address': addresses
}
df = pd.DataFrame(data)

# Save to Excel file
df.to_excel(f"{country}.xlsx", index=False)

