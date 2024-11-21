import csv
import time
import os
from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import quote
from webdriver_manager.chrome import ChromeDriverManager
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'csv', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_contacts(file_path):
    contacts = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            for row in csv_reader:
                if len(row) >= 3:
                    name, phone, village = row[0], row[1], row[2]
                    contacts.append((name, phone, village))
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return contacts

def send_whatsapp_messages(contacts, message_template, image_path):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get('https://web.whatsapp.com')
    print("Please scan the QR code in WhatsApp Web.")
    time.sleep(60)  # Increased time to ensure QR code scan

    for name, phone, village in contacts:
        message = message_template.replace("{name}", name).replace("{village}", village)
        encoded_message = quote(message)
        whatsapp_url = f"https://web.whatsapp.com/send?phone=91{phone}&text={encoded_message}"

        driver.get(whatsapp_url)
        time.sleep(15)  # Increased time for message box to load

        action = ActionChains(driver)
        action.send_keys(Keys.ENTER).perform()
        time.sleep(15)  # Increased time to ensure the message is sent

         # Attach and send image if an image path is provided
        if image_path:
            try:
                # Wait for the attach button to be clickable and click it
                attach_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@title="Attach"]'))
                )
                attach_button.click()
                time.sleep(3)  # Small delay to ensure the options are visible

                # Wait for the file input element to be visible and upload the image
                file_input = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@type="file" and @accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
                )

                # Send the image file path to the input field
                file_input.send_keys(image_path)
                time.sleep(10)  # Increased time for the image to load

                # Click the "Send" button for the image
                send_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[contains(@aria-label, "Send")]'))
                )
                send_button.click()
                time.sleep(10)  # Increased time to ensure the image is sent

                print(f"Image sent successfully to {name} ({phone})!")

            except Exception as e:
                print(f"Error while sending image to {name} ({phone}): {e}")



            driver.quit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send-messages', methods=['POST'])
def send_messages():
    csv_file = request.files['csv_file']
    image_file = request.files.get('image_file')
    message_template = request.form['message_template']

    if csv_file and allowed_file(csv_file.filename):
        csv_filename = secure_filename(csv_file.filename)
        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
        csv_file.save(csv_path)

        image_path = ""
        if image_file and allowed_file(image_file.filename):
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

        contacts = read_contacts(csv_path)
        send_whatsapp_messages(contacts, message_template, image_path)
        return "Messages sent successfully!"
    else:
        return "Invalid file. Please upload a valid CSV file.", 400

if __name__ == '__main__':
    app.run(debug=True)
