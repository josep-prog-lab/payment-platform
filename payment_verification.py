from supabase import create_client, Client
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in the environment.")
TABLE_NAME = "Messages"
REQUIRED_AMOUNT = 100  

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def verify_payment(txid, required_amount=REQUIRED_AMOUNT):
    # Look up the transaction by TxID
    db_result = supabase.table(TABLE_NAME).select('*').eq('txid', txid).execute()
    if not db_result.data or len(db_result.data) == 0:
        return {"status": "not_approved", "message": "Payment is not approved."}
    
    transaction = db_result.data[0]
    # Extract amount (assume format like '7000 RWF')
    amount_str = transaction.get('amount', '').replace(' RWF', '').replace(',', '').strip()
    try:
        paid_amount = int(amount_str)
    except Exception:
        return {"status": "not_approved", "message": "Payment is not approved (invalid amount format)."}

    if paid_amount == required_amount:
        return {"status": "approved", "message": "Payment is approved."}
    elif paid_amount < required_amount:
        shortage = required_amount - paid_amount
        return {"status": "not_approved", "message": f"Payment is not approved. You are short by {shortage} RWF."}
    else:
        return {"status": "approved", "message": "Payment is approved."}

def verify_payment_with_client_details(txid, client_name, client_phone, required_amount=REQUIRED_AMOUNT):
    """Verify payment using TxID, client name, and phone number matching"""
    # 1. Check payment in Messages table
    db_result = supabase.table(TABLE_NAME).select('*').eq('txid', txid).execute()
    if not db_result.data or len(db_result.data) == 0:
        return {"status": "not_approved", "message": "Payment not found. Please check your TxID."}

    transaction = db_result.data[0]
    
    # 2. Verify amount
    amount_str = transaction.get('amount', '').replace(' RWF', '').replace(',', '').strip()
    try:
        paid_amount = int(amount_str)
    except Exception:
        return {"status": "not_approved", "message": "Invalid payment amount format."}

    if paid_amount < required_amount:
        shortage = required_amount - paid_amount
        return {"status": "not_approved", "message": f"Insufficient payment. You are short by {shortage} RWF."}

    # 3. Verify client name (fuzzy matching)
    sms_sender_name = transaction.get('sender_name', '').lower().strip()
    client_name_lower = client_name.lower().strip()
    
    # Simple name matching - check if names are similar
    if not sms_sender_name or client_name_lower not in sms_sender_name and sms_sender_name not in client_name_lower:
        return {"status": "not_approved", "message": "Name verification failed. Please ensure you entered the correct name."}

    # 4. Verify phone number last digits
    client_last_digits = client_phone.replace('+', '').replace(' ', '').replace('-', '')[-3:]
    
    # Check if SMS contains partial phone digits
    sms_phone_digits = transaction.get('sender_phone_digits', '')
    if sms_phone_digits:
        # Verify last 2-3 digits match
        if not client_last_digits.endswith(sms_phone_digits[-2:]):
            return {"status": "not_approved", "message": "Phone number verification failed. Please check your mobile number."}
    
    # 5. Store verification in payments table
    try:
        payment_record = {
            'txid': txid,
            'client_name': client_name,
            'client_phone': client_phone,
            'verified_amount': paid_amount,
            'verification_status': 'approved',
            'created_at': datetime.now().isoformat()
        }
        
        supabase.table("payments").insert(payment_record).execute()
        
        return {
            "status": "approved", 
            "message": f"Payment verified successfully! Amount received: {paid_amount} RWF",
            "amount": paid_amount
        }
    except Exception as e:
        return {"status": "error", "message": "Failed to record payment verification."}
