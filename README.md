# Payment Platform in Rwanda

**Group Members:**
- Joseph Nishimwe
- Gedeon Ntigibeshya
- Elyse Tuyishimire
- Justine Neema

## Project Overview

A lightweight payment verification system designed specifically for the Rwandan market. This Python-based platform integrates with the familiar USSD-based MoMo code system (`*182*8*1*XXXXXX#`) to provide seamless payment verification for online businesses.

## How It Works

### Payment Flow
1. **Client Payment**: Clients dial the MoMo code on their phone
2. **SMS Confirmation**: MTN sends SMS confirmation with TxId to both client and business
3. **SMS Forwarding**: Business owner's SMS is forwarded to our backend via Android SMS forwarding app
4. **Client Verification**: Client enters details on web form for verification

### Verification Process
After payment, clients visit our verification page and provide:
- **Client Name** (Account Owner Name)
- **Mobile Number** 
- **TxId** (from SMS confirmation)

The system verifies payment by matching:
- TxId in our database
- Name similarity with SMS sender
- Last 2-3 digits of phone number
- Payment amount

## Features

- **Lightweight Architecture**: Minimal, efficient Python codebase
- **ML-Powered SMS Classification**: Automatic detection of payment-related SMS
- **Real-time Verification**: Instant payment confirmation
- **Rwandan Market Focus**: Designed for local MoMo ecosystem
- **Two-Table Database**: Simple structure (messages + payments)

## Project Structure

```
payment-main/
├── app.py                    # Main Flask application
├── payment_verification.py   # Payment verification logic
├── ml_classifier.py         # ML component for SMS classification
├── templates/
│   └── verify_payment.html  # Web form for client verification
├── requirements.txt         # Python dependencies
├── Procfile                 # Render.com deployment config
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Supabase account
- Environment variables

### Local Development

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd payment-main
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

   The app will be available at `http://localhost:5000`

### Database Setup (Supabase)

Create two tables in your Supabase database:

#### Messages Table
```sql
CREATE TABLE "Messages" (
    id SERIAL PRIMARY KEY,
    raw_text TEXT NOT NULL,
    txid VARCHAR(50),
    amount VARCHAR(20),
    sender_name VARCHAR(100),
    timestamp VARCHAR(50),
    sender_phone_digits VARCHAR(10),
    ml_confidence DECIMAL(3,2),
    payment_status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Payments Table
```sql
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    txid VARCHAR(50) UNIQUE NOT NULL,
    client_name VARCHAR(100) NOT NULL,
    client_phone VARCHAR(20) NOT NULL,
    verified_amount INTEGER NOT NULL,
    verification_status VARCHAR(20) DEFAULT 'approved',
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API Endpoints

### SMS Reception
- **POST** `/receive-sms`
- Receives forwarded SMS from Android app
- Uses ML classifier to filter payment-related messages
- Stores valid payments in Messages table

**Request Body:**
```json
{
  "message": "*161*TxId:123456*R*You have received 1000 RWF from John Doe (*567) on your mobile money account at 2025-08-16 10:30:00."
}
```

### Payment Verification
- **GET/POST** `/verify-payment-web`
- Web interface for clients to verify payments
- Matches client details with SMS records

## Machine Learning Component

The `ml_classifier.py` provides lightweight SMS classification:

- **Payment Detection**: Identifies payment-related SMS
- **Status Classification**: Determines if payment was successful
- **Confidence Scoring**: Provides reliability metrics
- **Information Extraction**: Extracts TxId, amount, name, phone digits

### Usage Example:
```python
from ml_classifier import classify_sms

result = classify_sms(sms_text)
print(f"Is Payment SMS: {result['is_payment_sms']}")
print(f"Status: {result['status']}")
print(f"Confidence: {result['confidence']}")
```

## Deployment

### Render.com Deployment

1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. The `Procfile` handles the deployment configuration
4. Your app will be available at: `https://your-app.onrender.com`

### Environment Variables for Production
- `SUPABASE_URL`
- `SUPABASE_KEY`

## Android SMS Forwarding Setup

To forward SMS messages to your deployed backend:

1. Install an SMS forwarding app on the business owner's phone
2. Configure it to forward messages to: `https://your-app.onrender.com/receive-sms`
3. Set up forwarding for messages containing MoMo payment confirmations

## Usage Flow

1. **Business Setup**: Deploy the app and set up SMS forwarding
2. **Client Payment**: Client dials MoMo code and makes payment
3. **SMS Processing**: System automatically captures and processes payment SMS
4. **Client Verification**: Client visits verification page and enters details
5. **Instant Confirmation**: System displays payment amount and confirmation

## Security Considerations

- Environment variables for sensitive data
- Input validation on all endpoints
- SQL injection prevention through Supabase client
- Phone number partial matching for privacy

## Future Enhancements

- Enhanced ML models for better SMS classification
- Support for multiple MoMo providers
- Real-time notifications
- Payment analytics dashboard
- Fraud detection mechanisms

## Development Notes

- Keep the codebase minimal and focused
- Prioritize Rwandan market compatibility
- Maintain two-table database structure
- Focus on lightweight ML implementation

## Meeting Schedule

**Next Meeting**: Monday 17th August 2025 [10:00-11:15 a.m]

Please prepare questions beforehand to keep meetings efficient.

## Contributing

1. Follow existing code patterns
2. Test thoroughly before committing
3. Update documentation for any changes
4. Keep the system lightweight and fast

## License

This project is developed for educational and commercial use in Rwanda's mobile money ecosystem.

---

For technical questions or contributions, please contact any of the group members listed above.

----

- download sms fowarder app into you phone
  https://github.com/bogkonstantin/android_income_sms_gateway_webhook.git     #please follow instruction as described in this shared github repository

- activating of the project locally 

- please deploy it on render to get public url link

- generate url link you must add<render url link>/receive-sms

- add this correctly configured url link to the sms forwarder you installed

- this will allow you to autoforwad messsages into the database and process them

- install all packages as found in requirement.txt file

- to activate the project locally 
	python3 app.py

- access it from here : http://127.0.0.1:5000

- make sure that .env file is create with all necessary cridentials , supabase cridentials must be shared for fully activation of the project 

