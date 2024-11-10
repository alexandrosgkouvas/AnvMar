from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException  # Import exceptions
from selenium import webdriver  # Importing webdriver here

import pandas as pd
import time
from urllib.parse import quote

# Function to format company names into valid URL segments
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

company_names = []
addresses = []
links = []  # New list to store the extracted links

country = input("Select country: ")

# Scroll and Click the "See More Exhibitors" button to load all exhibitors
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

company_name_elements = driver.find_elements(By.XPATH, '//*[@id="catalog-v2"]//h3[contains(@class, "CatalogCardLine-title")]/div/span/span')
for element in company_name_elements:
    company_names.append(element.text)

print(company_names)
driver.quit()

# Format URLs for each company
urls = [quote(format_company_name(company)) for company in company_names]
for company in urls:
    url = f"https://www.sialparis.com/en/EXHIBITORS-2024/exhibitor/{company}"
    options = webdriver.ChromeOptions()
    options.add_experimental_option(name="detach", value=True)
    driver = webdriver.Chrome(options=options)

    success = False
    address_found = False
    button_link = None  # Variable to store the link

    # Attempt to access the initial URL and extract address and link
    # Default values to ensure consistent list lengths
    addresses.append("Not found")  # Default value for this company
    links.append("No link found")  # Default value for this company

    for i in range(6):  # Try the URL with suffixes -1 to -5, and then without suffix
        url_suffix = f"{company}-" + str(i) if i > 0 else company
        url = f"https://www.sialparis.com/en/EXHIBITORS-2024/exhibitor/{url_suffix}"

        try:
            driver.get(url)
            time.sleep(2)

            # Reset the address and link before attempting to find them
            current_address = "Not found"
            current_link = "No link found"

            # Locate the address element
            try:
                address = driver.find_element(By.XPATH,
                                              '//*[@id="catalog-v2"]/div[1]/div[1]/section[2]/div[2]/div[2]/div[1]/p')
                current_address = address.text
            except NoSuchElementException:
                pass  # Keep the default value

            # Locate the button and extract the link if available
            try:
                button = driver.find_element(By.CSS_SELECTOR, '.CatalogRoundedButton.cc2-icon-web')
                current_link = button.get_attribute('href')
            except NoSuchElementException:
                pass  # Keep the default value

            # Update address and link in the lists if found
            addresses[-1] = current_address
            links[-1] = current_link

            # If we find the address and link, we can break out of the loop
            if current_address != "Not found" and current_link != "No link found":
                success = True
                break  # Exit the loop if successful

        except WebDriverException as e:
            print(f"Failed to access URL: {url}. Error: {e}")

    if not success:
        print(f"Address and link not found for {company}.")

    driver.quit()

# Create a DataFrame and save the data
data = {
    'Company Name': company_names,
    'Address': addresses,
    'WebAddress': links  # Include the extracted link in the data
}
df = pd.DataFrame(data)

# Save the DataFrame to an Excel file
df.to_excel(f"{country}.xlsx", index=False)
