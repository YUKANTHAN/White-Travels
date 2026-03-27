from flask_app.config.mongodb_connection import connectToMongo
from bson.objectid import ObjectId
import re
import os
import smtplib
from email.message import EmailMessage
from flask import flash
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
LETTER_REGEX = re.compile(r"^[\w'\-,.][^0-9_!¡?÷?¿/\\+=@#$%ˆ&*(){}|~<>;:[\]]{2,}$")
PHONE_REGEX = re.compile(r"^(\+\d{1,2}\s?)?1?\-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$")
DATABASE = "white_travels_db"
EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_APP_PASS')

class Contact:
    def __init__(self,data):
        self.id = data['id']
        self.contact_name = data['contact_name']
        self.contact_email = data['contact_email']
        self.contact_number = data['contact_number']
        self.contact_subject = data['contact_subject']
        self.contact_message = data['contact_message']
        self.user_id = data['user_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def save(cls, data):
        db = connectToMongo(DATABASE)
        contacts = db.get_collection("contacts")
        data['created_at'] = data.get('created_at', "")
        data['updated_at'] = data.get('updated_at', "")
        return str(contacts.insert_one(data).inserted_id)

    def sendContactForm(result):
        # 1. Send Email to Admin
        msg_admin = EmailMessage()
        msg_admin['Subject'] = f"New Enquiry from {result['contact_name']}: {result['contact_subject']}"
        msg_admin['From'] = EMAIL_ADDRESS
        msg_admin['To'] = EMAIL_ADDRESS
        msg_admin.set_content(f"""
        Hello there,

        You just recieved a contact form from White Travels.

        Name: {result['contact_name']}
        Email: {result['contact_email']}
        Phone Number: {result['contact_number']}
        Message: {result['contact_message']}

        Kind Regards,
        System Admin
        """)

        # 2. Send Acknowledgement Email to Customer
        msg_customer = EmailMessage()
        msg_customer['Subject'] = f"Request Received: {result['contact_subject']} - White Travels"
        msg_customer['From'] = EMAIL_ADDRESS
        msg_customer['To'] = result['contact_email']
        
        # Determine packages to suggest based on the subject/message
        # Simple keyword matching for relevance, fallback to generic popular packages
        customer_content = f"""
        Dear {result['contact_name']},

        Thank you for reaching out to White Travels! We have successfully received your enquiry regarding:
        "{result['contact_subject']}"
        
        You mentioned: "{result['contact_message']}"

        Our travel experts are reviewing your request and will get back to you very soon.

        In the meantime, you might be interested in some of our exclusive hand-picked travel packages:
        ✈️ Tropical Escapes: Discover the pristine beaches of Cabo and Honolulu.
        ✈️ Urban Adventures: Explore the bustling streets of New York, Tokyo, or London.
        ✈️ Romantic Getaways: Experience the magic of Paris.

        You can view all our destinations on our website.
        We look forward to crafting an unforgettable journey for you!

        Warm regards,
        White Travels Support Team
        """
        msg_customer.set_content(customer_content)

        # 3. Simulate/Prepare WhatsApp Notification
        whatsapp_message = f"Hello {result['contact_name']}! \U0001F30D We've received your enquiry regarding '{result['contact_subject']}' at White Travels. Our team is looking into it and will contact you soon. While you wait, check out our amazing packages to destinations like Paris, Tokyo, and Cabo! \u2708\ufe0f\U0001F3D6\ufe0f"
        Contact.send_whatsapp_notification(result['contact_number'], whatsapp_message)

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg_admin)
                smtp.send_message(msg_customer)
        except Exception as e:
            print(f"Failed to send email: {e}")

    @staticmethod
    def send_whatsapp_notification(phone_number, message_content):
        # 1. Cleaning number for pywhatkit (ensure it includes +country code)
        # If no plus, we assume default country is India (+91) as requested by context
        clean_number = str(phone_number).strip()
        if not clean_number.startswith("+"):
            clean_number = f"+91{clean_number}"

        print(f"[🟢 WhatsApp Notification via PyWhatKit]")
        print(f"Targeting: {clean_number}")

        try:
            import pywhatkit
            # sendwhatmsg_instantly(phone_no, message, wait_time, tab_close, close_time)
            # This opens a browser tab (default 15s wait for WhatsApp Web login)
            pywhatkit.sendwhatmsg_instantly(
                phone_no=clean_number,
                message=message_content,
                wait_time=15, 
                tab_close=True,
                close_time=5
            )
            print(f"WhatsApp browser window opened for: {clean_number}")
        except Exception as e:
            print(f"Failed to send WhatsApp via pywhatkit: {e}")
            print("Troubleshooting: Ensure pywhatkit is installed and you are logged into WhatsApp Web on your default browser.")


    @staticmethod
    def validate(data_data):
        is_valid = True
        if len(data_data['contact_name']) < 2:
            is_valid = False
            flash("Contact name must be at least 2 characters long", "err_contact_name")
        elif not LETTER_REGEX.match(data_data['contact_name']):
            flash("Contact name must only be letters", "err_contact_name")
            is_valid = False 
        if not EMAIL_REGEX.match(data_data['contact_email']): 
            flash("Invalid email address!", "err_contact_email")
            is_valid = False
        if not PHONE_REGEX.match(data_data['contact_number']):
            flash("Phone number must be 10 digits including area code", "err_contact_number")
        if len(data_data['contact_subject']) < 2:
            is_valid = False
            flash("Subject field must be at least 2 characters long", "err_contact_subject")
        if len(data_data['contact_message']) < 2:
            is_valid = False
            flash("Message field must be at least 2 characters long", "err_contact_message")
        return is_valid
