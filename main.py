from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium import webdriver
import re
import pandas as pd
import time
from urllib.parse import quote
import phonenumbers
# Function to format company names into valid URL segments
def format_company_name(company):
    if company.endswith("."):
        company = company[:-1]  # Remove the last character (the period)

    formatted_name = (
        company.replace(" ", "-")
        .replace(".", "-")
        .replace("&", "and")
        .replace("(", "")
        .replace(")", "")
    )
    while "--" in formatted_name:
        formatted_name = formatted_name.replace("--", "-")

    return formatted_name

# Function to find email address when it's not in a 'mailto:' href
def find_email_using_text(driver):
    email = "Not found"
    try:
        # Get all the visible text on the page
        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Regex pattern to match common email formats (simple pattern)
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, body_text)
        if match:
            email = match.group()  # Return the first match found
    except NoSuchElementException:
        pass  # Keep default "Not found" if no element is found

    return email

def find_phone_number_using_phonenumbers(driver):
    phone_number = "Not found"
    try:
        # Get all the visible text on the page
        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Search for phone numbers using phonenumbers library
        possible_numbers = phonenumbers.PhoneNumberMatcher(body_text, "US")  # Default region is 'US'; adjust as necessary
        
        # Iterate over possible numbers found and format them
        for match in possible_numbers:
            number = match.number
            if phonenumbers.is_valid_number(number):
                phone_number = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                break  # Stop at the first valid phone number
    except NoSuchElementException:
        pass  # Keep "Not found" if element not found
    return phone_number


def find_phone_number_using_regex(driver):
    phone_number = "Not found"
    try:
        # Get all the visible text on the page
        body_text = driver.find_element(By.TAG_NAME, "body").text
        # Regex pattern for phone numbers (basic example, modify as needed)
        phone_number_pattern = r'\+?\d[\d\s().-]{8,}'  # Matches common phone number formats
        match = re.search(phone_number_pattern, body_text)
        if match:
            phone_number = match.group()  # Return the first match found
    except NoSuchElementException:
        pass
    return phone_number


countries = []
url = "https://www.sialparis.com/en/EXHIBITORS-2024/exhibitors"

options = webdriver.ChromeOptions()
options.add_experimental_option(name="detach", value=True)
driver = webdriver.Chrome(options=options)
driver.get(url)
country = driver.find_elements(By.XPATH, value='//*[@id="catalog-v2"]//div[contains(@class ,"CatalogFilterBlock-category")]/label')
for element in country:
    country_name = element.get_attribute("title").split(" ")[0]
    countries.append(country_name)
print(countries)
driver.quit()


company_names = []
addresses = []  # Added list to store addresses
links = []

# Scroll and Click the "See More Exhibitors" button to load all exhibitors
for country in countries:
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
    # After all content is loaded, scroll to the bottom to ensure all content is visible
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # Wait to make sure all content is loaded
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

    addresses.append("Not found")  # Default value for this company
    links.append("No link found")  # Default value for this company

    for i in range(6):  # Try the URL with suffixes -1 to -5, and then without suffix
        url_suffix = f"{company}-" + str(i) if i > 0 else company
        url = f"https://www.sialparis.com/en/EXHIBITORS-2024/exhibitor/{url_suffix}"

        try:
            driver.get(url)
            time.sleep(3)

            # Reset the address and link before attempting to find them
            current_address = "Not found"
            current_link = "No link found"

            try:
                address = driver.find_element(By.XPATH,
                                              '//*[@id="catalog-v2"]/div[1]/div[1]/section[2]/div[2]/div[2]/div[1]/p')
                current_address = address.text
            except NoSuchElementException:
                pass  # Keep the default value

            try:
                button = driver.find_element(By.CSS_SELECTOR, '.CatalogRoundedButton.cc2-icon-web')
                current_link = button.get_attribute('href')
            except NoSuchElementException:
                pass  # Keep the default value

            addresses[-1] = current_address
            links[-1] = current_link

            if current_address != "Not found" and current_link != "No link found":
                success = True
                break

        except WebDriverException as e:
            print(f"Failed to access URL: {url}. Error: {e}")

    if not success:
        print(f"Address and link not found for {company}.")

    driver.quit()

phone_numbers = []
emails = []
facebook_links = []
instagram_links = []
twitter_links = []
youtube_links = []

# Open browser for scraping additional details
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

for link in links:
    try:
        driver.get(link)
        time.sleep(3)  # Wait for the page to load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for page to load after scroll

        # Scrape telephone number
        phone_number = "Not found"  # Default value if no phone number is found
        try:
            # Look for 'tel:' in href attribute
            phone = driver.find_element(By.XPATH, "//a[starts-with(@href, 'tel:')]")
            phone_number = phone.get_attribute('href').replace('tel:', '')  # Remove 'tel:' prefix
        except NoSuchElementException:
            try:
                # Look for phone number in alt attribute containing 'mobile'
                phone = driver.find_element(By.XPATH, "//*[contains(@alt, 'mobile')]")
                phone_number = phone.get_attribute('alt')
            except NoSuchElementException:
                try:
                    phone_number = find_phone_number_using_phonenumbers(driver)
                except NoSuchElementException:
                    try:
                        phone_number = find_phone_number_using_regex(driver)
                    except NoSuchElementException:
                        pass  # Keep default "Not found" if no phone is found
        phone_numbers.append(phone_number)


        # Scrape email
        email = "Not found"  # Default value if no email is found
        try:
            # Look for 'mailto:' in href attribute
            email_element = driver.find_element(By.XPATH, "//a[starts-with(@href, 'mailto:')]")
            email = email_element.get_attribute('href').replace('mailto:', '')  # Remove 'mailto:' prefix
        except NoSuchElementException:
            try:
                # Look for email in alt attribute containing 'email'
                email_element = driver.find_element(By.XPATH, "//*[contains(@alt, 'email')]")
                email = email_element.get_attribute('alt')
            except NoSuchElementException:
                pass  # Keep default "Not found" if no email is found
        emails.append(email)

        # Scrape social media links
        facebook_link = "Not found"
        instagram_link = "Not found"
        twitter_link = "Not found"
        youtube_link = "Not found"

        try:
            facebook = driver.find_element(By.XPATH, "//a[contains(@href, 'facebook.com')]")
            time.sleep(3)
            facebook_link = facebook.get_attribute('href')
        except NoSuchElementException:
            pass  # Keep default "Not found"

        try:
            instagram = driver.find_element(By.XPATH, "//a[contains(@href, 'instagram.com')]")
            instagram_link = instagram.get_attribute('href')
        except NoSuchElementException:
            pass  # Keep default "Not found"

        try:
            twitter = driver.find_element(By.XPATH, "//a[contains(@href, 'twitter.com')]")
            twitter_link = twitter.get_attribute('href')
        except NoSuchElementException:
            pass  # Keep default "Not found"

        try:
            youtube = driver.find_element(By.XPATH, "//a[contains(@href, 'youtube.com')]")
            youtube_link = youtube.get_attribute('href')
        except NoSuchElementException:
            pass  # Keep default "Not found"

        # Append the found values (or "Not found") to the lists
        facebook_links.append(facebook_link)
        instagram_links.append(instagram_link)
        twitter_links.append(twitter_link)
        youtube_links.append(youtube_link)

    except Exception as e:
        print(f"Error with link {link}: {e}")
        # Append "Error" if there was an issue during scraping
        phone_numbers.append("Error")
        emails.append("Error")
        facebook_links.append("Error")
        instagram_links.append("Error")
        twitter_links.append("Error")
        youtube_links.append("Error")

# Once the scraping is done, create a DataFrame to store the results
data = {
    'Company Name': company_names,
    'Address': addresses,  # Add addresses to the DataFrame
    'Link': links,
    'Phone Number': phone_numbers,
    'Email': emails,
    'Facebook Link': facebook_links,
    'Instagram Link': instagram_links,
    'Twitter Link': twitter_links,
    'YouTube Link': youtube_links
}

df = pd.DataFrame(data)

# Save to Excel
df.to_excel(f'{country}.xlsx', index=False)

driver.quit()