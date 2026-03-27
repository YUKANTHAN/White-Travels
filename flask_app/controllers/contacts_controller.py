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
    
    # NEW: AI Automated Response Logic
    ai_email_body = concierge.generate_email_content(
        result.get('contact_name', 'Valued Customer'),
        result.get('contact_subject', 'General Inquiry')
    )
    send_ai_followup(result.get('contact_email'), ai_email_body)

    return redirect('/')
