from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


URL = "http://127.0.0.1:5000"


def run_test():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(URL)

        # wait for first question to load
        wait.until(EC.presence_of_element_located((By.ID, "question")))

        print("Starting Selenium Quiz Test")

        for i in range(5):  # run 5 question cycles

            # get question text
            question_text = driver.find_element(By.ID, "question").text
            print(f"\nQ{i+1}: {question_text}")

            # wait for buttons
            buttons = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#options button"))
            )

            if not buttons:
                raise Exception("No answer buttons found")

            # click first option (simple deterministic test)
            buttons[0].click()

            # wait for result to appear
            result = wait.until(
                EC.presence_of_element_located((By.ID, "result"))
            )

            print("Result:", result.text)

            # wait for next question to load (question text changes)
            old_text = question_text

            wait.until(
                lambda d: d.find_element(By.ID, "question").text != old_text
            )

            print("➡ Next question loaded")

            time.sleep(0.5)

        print("\nSelenium test completed successfully")

    finally:
        driver.quit()


if __name__ == "__main__":
    run_test()