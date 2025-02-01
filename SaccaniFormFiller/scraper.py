import re
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class BusinessScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        from webdriver_manager.chrome import ChromeDriverManager
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def setup_driver(self):
        """Initialize the driver if it was closed"""
        if not self.driver:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            from webdriver_manager.chrome import ChromeDriverManager
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def scrape_business(self, business_name, city):
        search_variations = self.generate_search_variations(business_name)
        
        for variation in search_variations:
            result = self.search_and_scrape(variation, city)
            if result:
                return result
        
        logging.warning(f"No results found for all variations of '{business_name}' in {city}")
        return None

    def generate_search_variations(self, business_name):
        variations = [
            business_name,
            re.sub(r'[^\w\s]', '', business_name),  # Remove punctuation
            business_name.lower(),
            ' '.join(business_name.split()[:2]),  # First two words
            ' '.join(business_name.split()[:2]).lower(),  # First two words, lowercase
        ]
        return list(dict.fromkeys(variations))  # Remove duplicates while preserving order

    def search_and_scrape(self, business_name, city):
        try:
            self.driver.get("https://www.abc.ca.gov/licensing/license-lookup/business-name/")
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "BusinessName"))
            )
            search_input.clear()
            search_input.send_keys(business_name)
            search_input.submit()

            if self.is_on_details_page():
                return self.extract_license_details()
            elif self.has_search_results():
                return self.perform_city_search(city)
            else:
                logging.info(f"No results found for '{business_name}'")
                return None
        except Exception as e:
            logging.error(f"Error searching for business '{business_name}': {str(e)}")
            return None

    def is_on_details_page(self):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="et-boc"]/div/div[1]/div/div/div[2]/div/div[2]/div[1]/div[1]/h2'))
            )
            return True
        except TimeoutException:
            return False

    def has_search_results(self):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "abc_licenses"))
            )
            return True
        except TimeoutException:
            return False

    def extract_license_details(self):
        return self.follow_license_chain()

    def follow_license_chain(self):
        try:
            status_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//dt[contains(text(), 'License Type Status:')]/following-sibling::dd[1]"))
            )
            status = status_element.text.strip().upper()

            if status == "ACTIVE":
                logging.info("Found active license. Extracting details.")
                return self.extract_active_license_details()
            elif status == "CANCELED":
                logging.info("License is canceled. Attempting to find new license number.")
                transfer_element = self.driver.find_element(By.XPATH, "//dt[contains(text(), 'Transfers:')]/following-sibling::dd[1]")
                new_license_link = transfer_element.find_element(By.XPATH, ".//a[contains(@href, '/licensing/license-lookup/single-license/?RPTTYPE=12&LICENSE=')]")
                new_license_number = new_license_link.text
                logging.info(f"Found new license number: {new_license_number}")
                new_license_link.click()
                
                # Wait for the new page to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="et-boc"]/div/div[1]/div/div/div[2]/div/div[2]/div[1]/div[1]/h2'))
                )
                
                # Recursively follow the chain
                return self.follow_license_chain()
            else:
                logging.warning(f"Unexpected license status: {status}")
                return None

        except (TimeoutException, NoSuchElementException) as e:
            logging.error(f"Error while following license chain: {str(e)}")
            return None

    def extract_active_license_details(self):
        mappings = {
            'LICENSE_NUMBER': "//dt[contains(text(), 'License Number:')]/following-sibling::dd[1]",
            'PRIMARY_OWNER': "//dt[contains(text(), 'Primary Owner:')]/following-sibling::dd[1]",
            'BUSINESS_NAME': "//h2[contains(text(), 'Business Name')]/following-sibling::p[1]",
            'BUSINESS_ADDRESS': "//h2[contains(text(), 'Business Address')]/following-sibling::p[1]",
            'COUNTY': "//dt[contains(text(), 'County:')]/following-sibling::dd[1]",
            'LICENSE_TYPE_STATUS': "//dt[contains(text(), 'License Type Status:')]/following-sibling::dd[1]"
        }

        account_data = {}
        for key, xpath in mappings.items():
            try:
                element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
                text = element.text.strip()
                account_data[key] = text.encode('ascii', 'ignore').decode('ascii')  # Remove non-ASCII characters
            except TimeoutException:
                account_data[key] = "Not found"
            except Exception as e:
                logging.error(f"Error extracting {key}: {str(e)}")
                account_data[key] = "Error"
        return account_data

    def perform_city_search(self, city):
        try:
            city_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.form-control.input-sm[aria-controls='abc_licenses']"))
            )
            city_input.clear()
            city_input.send_keys(city)

            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "table#abc_licenses"))
            )

            active_or_pending_rows = self.driver.find_elements(By.XPATH, "//tr[td[contains(text(), '(ACTIVE)') or contains(text(), '(PEND)')]]")
            results = []
            for row in active_or_pending_rows:
                license_link = row.find_element(By.XPATH, ".//a")
                license_link.click()
                result = self.extract_license_details()
                results.append(result)
                self.driver.back()
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "table#abc_licenses"))
                )
            return results[0] if results else None  # Return the first result if any
        except Exception as e:
            logging.error(f"Error during city search: {str(e)}")
            return None

    def close_driver(self):
        if self.driver:
            self.driver.quit()
