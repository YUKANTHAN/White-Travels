import os
import sys
import re
import smtplib
import traceback
from flask_app.config.mongodb_connection import connectToMongo
from bson.objectid import ObjectId
from email.message import EmailMessage
from flask import flash
from dotenv import load_dotenv, find_dotenv

# Initialize environment immediately
load_dotenv(find_dotenv(), override=True)

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

    @staticmethod
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

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg_admin)
                smtp.send_message(msg_customer)
        except Exception as e:
            print(f"Failed to send email: {e}")

    @staticmethod
    def send_whatsapp_notification(phone_number, message_content):
        # 🟢 FORCE FRESH ENV RELOAD
        env_path = find_dotenv()
        load_dotenv(env_path, override=True)

        account_sid = os.environ.get('TWILIO_ACCOUNT_SID', '').strip()
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN', '').strip()
        from_number = os.environ.get('TWILIO_WHATSAPP_NUMBER', '').strip()

        # Debug Trace
        print(f"\n[DEBUG] --- WhatsApp Notification Attempt ---", flush=True)
        print(f"[DEBUG] ENV File: {env_path}", flush=True)
        print(f"[DEBUG] SID Found: {'Yes' if account_sid else 'No'} ({account_sid[:5]}...)", flush=True)
        print(f"[DEBUG] Token Found: {'Yes' if auth_token else 'No'}", flush=True)

        is_twilio_enabled = bool(account_sid and account_sid.startswith('AC') and auth_token)

        if is_twilio_enabled:
            try:
                from twilio.rest import Client
                client = Client(account_sid, auth_token)
                
                # E.164 Normalization: Remove all spaces for Twilio
                clean_to = "".join(filter(str.isdigit, phone_number))
                if not clean_to.startswith('+'): clean_to = f"+{clean_to}"
                
                clean_from = "".join(filter(str.isdigit, from_number))
                if not clean_from.startswith('+'): clean_from = f"+{clean_from}"
                
                print(f"[DEBUG] Sending to: {clean_to} from: {clean_from}", flush=True)

                msg = client.messages.create(
                    from_=f'whatsapp:{clean_from}',
                    body=message_content,
                    to=f'whatsapp:{clean_to}'
                )
                print(f"[SUCCESS] WhatsApp Sent! SID: {msg.sid}", flush=True)
                return True
            except Exception as e:
                print(f"[TWILIO ERROR]: {str(e)}", flush=True)
                traceback.print_exc()
        else:
            print("[INFO] Twilio credentials missing or invalid. Check your .env file.", flush=True)

        # 🟡 BROWSER FALLBACK
        allow_browser_raw = os.environ.get('ALLOW_BROWSER_WHATSAPP', 'True')
        allow_browser = allow_browser_raw.split('#')[0].strip().lower() == 'true'
        
        if not allow_browser:
            print(f"[TERMINATED] Browser fallback disabled in .env. No message sent.", flush=True)
            return False

        print(f"[🟠 FALLBACK] Launching Browser automation...", flush=True)
        try:
            import pywhatkit
            pywhatkit.sendwhatmsg_instantly(
                phone_no=phone_number,
                message=message_content,
                wait_time=15, 
                tab_close=True,
                close_time=5
            )
            return True
        except Exception as e:
            print(f"Browser automation failed: {e}", flush=True)
            return False


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
