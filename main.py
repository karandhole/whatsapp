import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from urllib.parse import quote
import time
from flask import Flask, request, send_from_directory

app = Flask(__name__)

# Function to read contacts from CSV
def read_contacts():
    contacts = []
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
    time.sleep(15)
    
    # Loop through the contacts and send the personalized message
    for name, phone_number in contacts:
        personalized_msg = f"Hi, {name}"
        personalized_msg = quote(personalized_msg)
        
        # Construct the WhatsApp URL
        link = f'https://web.whatsapp.com/send?phone=91{phone_number}&text={personalized_msg}'
        
        # Open the URL
        driver.get(link)
        time.sleep(10)
        
        # Send the message by pressing Enter
        action = ActionChains(driver)
        action.send_keys(Keys.ENTER)
        action.perform()
        time.sleep(10)
    
    # Keep the browser open for a while
    time.sleep(2000)

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
