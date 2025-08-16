"""
Lightweight ML Component for SMS Payment Classification
This module provides simple machine learning functionality to classify
SMS messages and determine if they indicate successful payments.
"""

import re
from typing import Dict, List, Tuple


class PaymentSMSClassifier:
    """Lightweight classifier for determining if SMS indicates successful payment"""
    
    def __init__(self):
        # Keywords that typically indicate successful payment
        self.payment_success_keywords = [
            'received', 'sent', 'paid', 'successful', 'completed', 
            'confirmed', 'approved', 'transaction', 'transfer'
        ]
        
        # Keywords that indicate failed/pending payments
        self.payment_failure_keywords = [
            'failed', 'declined', 'insufficient', 'pending', 
            'cancelled', 'error', 'rejected'
        ]
        
        # Patterns for Rwandan MoMo SMS formats
        self.momo_patterns = [
            r'\*161\*TxId:\d+\*R\*',  # Standard MoMo format
            r'You have received \d+ RWF',  # Receive confirmation
            r'You have sent \d+ RWF',      # Send confirmation
        ]
    
    def extract_payment_info(self, sms_text: str) -> Dict[str, str]:
        """
        Extract key payment information from SMS text
        
        Args:
            sms_text: Raw SMS message text
            
        Returns:
            Dictionary containing extracted payment information
        """
        info = {
            'txid': '',
            'amount': '',
            'sender_name': '',
            'phone_digits': '',
            'is_payment_sms': False
        }
        
        # Check if this looks like a payment SMS
        info['is_payment_sms'] = self.is_payment_related(sms_text)
        
        if not info['is_payment_sms']:
            return info
        
        # Extract TxId
        txid_match = re.search(r'TxId[:\s]*(\d+)', sms_text, re.IGNORECASE)
        if txid_match:
            info['txid'] = txid_match.group(1)
        
        # Extract amount in RWF
        amount_match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)\s*RWF', sms_text)
        if amount_match:
            info['amount'] = amount_match.group(1)
        
        # Extract sender name
        sender_match = re.search(r'from ([A-Za-z\s]+)\s*\(', sms_text)
        if sender_match:
            info['sender_name'] = sender_match.group(1).strip()
        
        # Extract partial phone number (last few digits shown in SMS)
        phone_match = re.search(r'\(\*+(\d{2,3})\)', sms_text)
        if phone_match:
            info['phone_digits'] = phone_match.group(1)
        
        return info
    
    def is_payment_related(self, sms_text: str) -> bool:
        """
        Classify if SMS is payment-related using simple keyword matching
        
        Args:
            sms_text: SMS message text
            
        Returns:
            Boolean indicating if SMS is payment-related
        """
        text_lower = sms_text.lower()
        
        # Check for MoMo patterns
        for pattern in self.momo_patterns:
            if re.search(pattern, sms_text, re.IGNORECASE):
                return True
        
        # Check for payment keywords
        success_score = sum(1 for keyword in self.payment_success_keywords 
                          if keyword in text_lower)
        failure_score = sum(1 for keyword in self.payment_failure_keywords 
                          if keyword in text_lower)
        
        # Consider it payment-related if it has payment keywords
        return success_score > 0 or failure_score > 0
    
    def classify_payment_status(self, sms_text: str) -> str:
        """
        Classify the payment status from SMS text
        
        Args:
            sms_text: SMS message text
            
        Returns:
            Payment status: 'success', 'failed', or 'unknown'
        """
        if not self.is_payment_related(sms_text):
            return 'unknown'
        
        text_lower = sms_text.lower()
        
        # Check for failure indicators first
        for keyword in self.payment_failure_keywords:
            if keyword in text_lower:
                return 'failed'
        
        # Check for success indicators
        for keyword in self.payment_success_keywords:
            if keyword in text_lower:
                return 'success'
        
        return 'unknown'
    
    def get_confidence_score(self, sms_text: str) -> float:
        """
        Get confidence score for payment classification (0.0 to 1.0)
        
        Args:
            sms_text: SMS message text
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not sms_text.strip():
            return 0.0
        
        text_lower = sms_text.lower()
        total_score = 0.0
        
        # MoMo pattern match gives high confidence
        for pattern in self.momo_patterns:
            if re.search(pattern, sms_text, re.IGNORECASE):
                total_score += 0.7
                break
        
        # Keyword matches
        success_matches = sum(1 for keyword in self.payment_success_keywords 
                            if keyword in text_lower)
        failure_matches = sum(1 for keyword in self.payment_failure_keywords 
                            if keyword in text_lower)
        
        # Add confidence based on keyword matches
        total_score += min(0.3, (success_matches + failure_matches) * 0.1)
        
        return min(1.0, total_score)


# Initialize global classifier instance
classifier = PaymentSMSClassifier()


def classify_sms(sms_text: str) -> Dict[str, any]:
    """
    Convenience function to classify SMS and extract payment info
    
    Args:
        sms_text: Raw SMS message text
        
    Returns:
        Dictionary with classification results and extracted info
    """
    payment_info = classifier.extract_payment_info(sms_text)
    status = classifier.classify_payment_status(sms_text)
    confidence = classifier.get_confidence_score(sms_text)
    
    return {
        'payment_info': payment_info,
        'status': status,
        'confidence': confidence,
        'is_payment_sms': payment_info['is_payment_sms']
    }
