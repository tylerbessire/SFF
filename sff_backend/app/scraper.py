from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from typing import List, Dict, Any
import re
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BusinessScraper:
    def __init__(self):
        try:
            logger.info("Initializing Chrome WebDriver")
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            driver_path = ChromeDriverManager().install()
            logger.info(f"ChromeDriver installed at: {driver_path}")
            
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
            raise

    def scrape_business(self, business_name: str, city: str):
        try:
            logger.info(f"Starting scrape for business: {business_name}, city: {city}")
            search_variations = self.generate_search_variations(business_name)
            results = []
            
            for search_term in search_variations:
                try:
                    logger.info(f"Trying search term: {search_term}")
                    self.driver.set_page_load_timeout(30)
                    self.driver.get("https://www.abc.ca.gov/licensing/license-lookup/")
                    logger.info("Successfully loaded ABC website")

                    search_box = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.ID, "dba"))
                    )
                    search_box.clear()
                    search_box.send_keys(search_term)
                    logger.info("Entered business name")
                    
                    city_box = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.ID, "city"))
                    )
                    city_box.clear()
                    city_box.send_keys(city)
                    logger.info("Entered city")
                    
                    search_button = WebDriverWait(self.driver, 20).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "btn-primary"))
                    )
                    search_button.click()
                    logger.info("Clicked search button")
                    
                    try:
                        WebDriverWait(self.driver, 20).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "table"))
                        )
                        current_results = self.extract_results()
                        logger.info(f"Found {len(current_results)} results")
                        results.extend(current_results)
                    except TimeoutException:
                        logger.info("No results found for this search term")
                        continue
                    
                except Exception as e:
                    logger.error(f"Error during search for term {search_term}: {str(e)}")
                    continue
            
            logger.info(f"Scraping completed. Total results: {len(results)}")
            return results
        except Exception as e:
            logger.error(f"Fatal error during scraping: {str(e)}")
            raise
        finally:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")

    def generate_search_variations(self, business_name: str) -> List[str]:
        variations = [business_name]
        words = business_name.split()
        if len(words) > 1:
            variations.append(" ".join(words[:2]))
        return variations

    def extract_results(self):
        results = []
        rows = self.driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")
        
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 6:
                result = {
                    "license_number": cols[0].text.strip(),
                    "business_name": cols[1].text.strip(),
                    "address": cols[2].text.strip(),
                    "city": cols[3].text.strip(),
                    "state": cols[4].text.strip(),
                    "zip": cols[5].text.strip(),
                    "status": cols[6].text.strip() if len(cols) > 6 else "Unknown"
                }
                results.append(result)
        
        return results
