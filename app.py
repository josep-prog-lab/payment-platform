from flask import Flask, request, jsonify, render_template
import re
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv
import os
import sys
from payment_verification import verify_payment
from ml_classifier import classify_sms

#  CONFIG for supabase keys
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
TABLE_NAME = "Messages"  

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in the environment.")
    sys.exit(1)

# --- INIT ---
app = Flask(__name__)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- REGEX PATTERNS ---
NAME_PATTERN = r"Name[:\s]+([A-Za-z ]+)"
AMOUNT_PATTERN = r"Amount[:\s]+([\d,.]+)"
ACCOUNT_PATTERN = r"Account(?: No\.| Number)[:\s]+(\d+)"

def extract_fields(text):
    # TxId
    txid = ''
    txid_match = re.search(r'TxId[:\s]*([\d]+)', text)
    if not txid_match:
        txid_match = re.search(r'\*161\*TxId:([\d]+)\*R\*', text)
    if txid_match:
        txid = txid_match.group(1)

    # Amount
    amount = ''
    amount_match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)\s*RWF', text)
    if amount_match:
        amount = amount_match.group(0)

    # Sender name
    sender_name = ''
    sender_match = re.search(r'from ([A-Za-z ]+) \(', text)
    if sender_match:
        sender_name = sender_match.group(1).strip()

    # Timestamp
    timestamp = ''
    timestamp_match = re.search(r'at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', text)
    if timestamp_match:
        timestamp = timestamp_match.group(1)

    return {
        'raw_text': text,
        'txid': txid or '',
        'amount': amount or '',
        'sender_name': sender_name or '',
        'timestamp': timestamp or None
    }

# --- ROUTES ---
@app.route('/receive-sms', methods=['POST'])
def receive_sms():
    data = request.get_json()
    message = data.get('message', '')

    # Use ML classifier to determine if this is a payment SMS
    classification = classify_sms(message)
    
    if not classification['is_payment_sms']:
        return jsonify({
            "status": "ignored", 
            "reason": "Not a payment-related SMS",
            "confidence": classification['confidence']
        })
    
    # Only process successful payment SMS
    if classification['status'] != 'success':
        return jsonify({
            "status": "ignored", 
            "reason": f"Payment status: {classification['status']}",
            "confidence": classification['confidence']
        })

    # Extract fields and store with ML-extracted info
    fields = extract_fields(message)
    
    # Add ML-extracted information
    ml_info = classification['payment_info']
    if ml_info['phone_digits']:
        fields['sender_phone_digits'] = ml_info['phone_digits']
    
    fields['ml_confidence'] = classification['confidence']
    fields['payment_status'] = classification['status']
    
    supabase.table(TABLE_NAME).insert(fields).execute()
    return jsonify({
        "status": "saved", 
        "data": fields,
        "ml_classification": classification
    })

@app.route('/verify-payment-web', methods=['GET', 'POST'])
def verify_payment_web():
    result_message = None
    result_status = None
    verified_amount = None
    
    if request.method == 'POST':
        client_name = request.form.get('client_name')
        client_phone = request.form.get('client_phone')
        txid = request.form.get('txid')
        
        if client_name and client_phone and txid:
            from payment_verification import verify_payment_with_client_details
            result = verify_payment_with_client_details(txid, client_name, client_phone)
            result_message = result['message']
            result_status = result['status']
            verified_amount = result.get('amount')
        else:
            result_message = "All fields are required."
            result_status = "not_approved"
            
    return render_template('verify_payment.html', 
                         result_message=result_message, 
                         result_status=result_status,
                         verified_amount=verified_amount)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 