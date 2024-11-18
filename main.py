import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
from flask import Flask, request, send_from_directory

app = Flask(__name__)
image_path = r"D:\whatsapp\imaged2.jpg"  # Use raw string or forward slashes

# Function to read contacts from CSV
def read_contacts():
    contacts = []
    try:
        with open('contacts.csv', 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            for row in csv_reader:
                if row and len(row) >= 2:  # Ensure the row is not empty and has two columns
                    name = row[0]
                    phone_number = row[1]
                    contacts.append((name, phone_number))
                else:
                    print(f"Skipping invalid or empty row: {row}")
    except FileNotFoundError:
        print("Error: 'contacts.csv' file not found.")
    return contacts

# Function to send WhatsApp messages
def send_whatsapp_messages():
    contacts = read_contacts()

    # Set up the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Open WhatsApp Web
    driver.get('https://web.whatsapp.com')

    # Delay to scan QR code
    print("Please scan the QR code in WhatsApp Web to log in.")
    time.sleep(30)  # Increased to give enough time to scan QR

    # Loop through the contacts and send the personalized message
    for name, phone_number in contacts:
        try:
            personalized_msg = f"Hi, {name}"
            personalized_msg = quote(personalized_msg)

            # Construct the WhatsApp URL
            link = f'https://web.whatsapp.com/send?phone=91{phone_number}&text={personalized_msg}'

            # Open the URL
            driver.get(link)
            time.sleep(10)  # Allow the page to load

            # Send the message by pressing Enter
            action = ActionChains(driver)
            action.send_keys(Keys.ENTER)
            action.perform()
            time.sleep(5)

            # Wait for the attachment button to be clickable and click it
            try:
                attach_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@title="Attach"]'))
                )
                attach_button.click()
            except Exception as e:
                print(f"Error while trying to click attach button: {e}")
                continue

            # Wait for the file input element and upload the image
            try:
                file_input = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
                )
                file_input.send_keys(image_path)
            except Exception as e:
                print(f"Error while trying to upload image: {e}")
                continue

            # Wait for the image to upload and then send the message
            time.sleep(5)
            action = ActionChains(driver)
            action.send_keys(Keys.ENTER)
            action.perform()
            time.sleep(5)

        except Exception as e:
            print(f"Error occurred while sending message to {phone_number}: {e}")

    # Keep the browser open for a while after sending all messages
    time.sleep(2000)
    driver.quit()

# Route for the homepage to display index.html
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')  # Serve index.html from the root directory

# Route to handle the form submission and trigger the send messages function
@app.route('/send-messages', methods=['POST'])
def send_messages():
    send_whatsapp_messages()
    return "Messages sent successfully!"

if __name__ == '__main__':
    app.run(debug=True)
