import time
from playwright.sync_api import sync_playwright

def read_search_terms(file_path):
    """Reads search terms from a text file."""
    with open(file_path, "r") as file:
        terms = [line.strip() for line in file if line.strip()]
    return terms

def create_google_alerts(email, password, search_terms):
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Google login
        page.goto("https://accounts.google.com/")
        page.fill("input[type='email']", email)
        page.click("button:has-text('Next')")
        page.wait_for_selector("input[type='password']")
        page.fill("input[type='password']", password)
        page.click("button:has-text('Next')")
        # Wait for login to complete
        page.wait_for_timeout(500)

        # Google Alerts
        page.goto("https://www.google.com/alerts")
        page.wait_for_selector("input", timeout=10000)

        # Create alerts for each search term
        for term in search_terms:
            print(f"Creating alert for: {term}")
            # Fill the search term input field
            page.fill("input", term)
            page.press("input", "Enter")
            # Click the 'Create Alert' button
            create_alert_button = page.locator("span#create_alert")
            if create_alert_button.is_visible():
                create_alert_button.click()
            else:
                print(f"Alert for '{term}' already exists or couldn't be created.")
            time.sleep(2)

        # Close the browser
        browser.close()

if __name__ == "__main__":
    # Replace these with your Google credentials
    email = "monktest9876"
    password = "alicewonder123"

    # Path to the text file containing search terms
    file_path = "search_terms.txt"

    # Read search terms from the file
    search_terms = read_search_terms(file_path)

    # Create Google Alerts
    create_google_alerts(email, password, search_terms)