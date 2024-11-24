url = "https://www.sialparis.com/en/EXHIBITORS-2024/exhibitor/KRACO-3"

driver = webdriver.Chrome()
driver.get(url)
button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '.CatalogRoundedButton.cc2-icon-web.CatalogRoundedButton--light.bgLight.textVariant'))
)
button = driver.find_element(By.CSS_SELECTOR, '.CatalogRoundedButton.cc2-icon-web.CatalogRoundedButton--light.bgLight.textVariant')
link = button.get_attribute('href')
print(link)

driver.quit()