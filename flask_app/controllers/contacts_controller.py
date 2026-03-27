from flask_app import app
from flask import redirect,request,session,url_for
from flask_app.models.users import User
from flask_app.models.contacts import Contact
from ai_agent_backend.deep_concierge import DeepConcierge
import os

# Initialize AI Assistant for Inquiry Analysis
concierge = DeepConcierge()

def send_ai_followup(email, body):
    """Simulates sending a high-fidelity AI-generated email to the customer."""
    print(f"\n--- [AI AUTOMATED EMAIL OUTBOUND] ---")
    print(f"TO: {email}")
    print(f"BODY:\n{body}")
    print(f"--- [OUTBOUND SUCCESSFUL] ---\n")
    # For Hackathon demo: Write to a fake 'sent_emails.log'
    with open('sent_emails.log', 'a', encoding='utf-8') as f:
        f.write(f"\n[TO: {email}] Subject: Your Customized White Travels Package\n{body}\n{'-'*50}\n")

@app.route('/contact', methods=["POST"])
def contact_us():
    if not Contact.validate(request.form):
        return redirect(url_for("index")+"#contact_form")
    data = {
        **request.form,
        'user_id': session['user_id']
    }
    result = {}

    result['contact_name'] = request.form['contact_name']
    result['contact_email'] = request.form['contact_email']
    result['contact_number'] = request.form['contact_number']
    result['contact_subject'] = request.form['contact_subject']
    result['contact_message'] = request.form['contact_message']
    
    Contact.sendContactForm(result)
    Contact.save(data)
    
    # NEW: OVERWRITE ACTIVE ITINERARY WITH ENQUIRY DATA
    import json, random
    new_itinerary = {
        "status": "CONFIRMED",
        "passenger_name": result.get('contact_name', 'Traveling Passenger'),
        "seat": f"{random.randint(1,40)}{random.choice('ABCDEF')}",
        "class_type": "Premium Economy",
        "gate": f"{random.choice('ABCD')}{random.randint(1,30)}",
        "boarding_time": "AUTO_SYNCED",
        "flight_no": f"WT-{random.randint(100,999)}",
        "train_no": f"METRO-{random.randint(10,99)}",
        "origin": "Current Location",
        "destination": result.get('contact_subject', 'Paris'),
        "pnr": f"PNR-{random.randint(10000, 99999)}",
        "budget_limit": 2500,
        "budget_spent": random.randint(200, 800),
        "carbon_kg": f"{random.randint(200, 500)}kg",
        "visa_status": "Processing Draft..."
    }
    with open('itinerary.json', 'w') as f:
        json.dump([new_itinerary], f, indent=4)

    # NEW: AI Automated Response Logic
    ai_email_body = concierge.generate_email_content(
        result.get('contact_name', 'Valued Customer'),
        result.get('contact_subject', 'General Inquiry')
    )
    send_ai_followup(result.get('contact_email'), ai_email_body)

    return redirect('/')
