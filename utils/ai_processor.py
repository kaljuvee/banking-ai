"""
AI Processor for Banking BPO Automation
Handles document processing, OCR, and information extraction using OpenAI
"""

import openai
import os
from typing import Dict, List, Optional, Tuple
import json
import base64
from PIL import Image
import PyPDF2
import io
from datetime import datetime
import re

class BankingAIProcessor:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        )
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error extracting text from PDF: {str(e)}"
    
    def process_image_with_vision(self, image_file) -> str:
        """Process image using OpenAI Vision API for OCR"""
        try:
            # Convert image to base64
            image = Image.open(image_file)
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all text from this document image. Maintain the original formatting and structure."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_str}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error processing image: {str(e)}"
    
    def classify_document(self, text: str) -> Dict:
        """Classify document type and extract key information"""
        try:
            prompt = f"""
            Analyze this legal document and extract the following information in JSON format:
            
            Document text:
            {text}
            
            Please extract:
            1. document_type (e.g., "garnishment_order", "court_notice", "account_freeze_order", "legal_notice")
            2. customer_name
            3. account_number
            4. case_number
            5. creditor_name
            6. amount (if specified)
            7. date_filed
            8. bank_name
            9. confidence_score (0-100)
            10. summary (brief description)
            
            Return only valid JSON format.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert legal document analyzer. Extract information accurately and return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {
                "document_type": "unknown",
                "customer_name": "",
                "account_number": "",
                "case_number": "",
                "creditor_name": "",
                "amount": 0,
                "date_filed": "",
                "bank_name": "",
                "confidence_score": 0,
                "summary": f"Error processing document: {str(e)}"
            }
    
    def verify_customer_information(self, extracted_info: Dict, customer_database: List[Dict]) -> Dict:
        """Verify extracted customer information against database"""
        try:
            # Simple fuzzy matching for customer verification
            best_match = None
            best_score = 0
            
            for customer in customer_database:
                score = 0
                
                # Name matching
                if extracted_info.get('customer_name', '').lower() in customer.get('name', '').lower():
                    score += 40
                
                # Account number matching
                if extracted_info.get('account_number', '') == customer.get('account_number', ''):
                    score += 60
                
                if score > best_score:
                    best_score = score
                    best_match = customer
            
            return {
                "match_found": best_score > 50,
                "confidence": best_score,
                "customer_data": best_match if best_match else {},
                "verification_status": "verified" if best_score > 80 else "needs_review" if best_score > 50 else "not_found"
            }
            
        except Exception as e:
            return {
                "match_found": False,
                "confidence": 0,
                "customer_data": {},
                "verification_status": "error",
                "error": str(e)
            }
    
    def generate_processing_summary(self, document_info: Dict, verification_result: Dict) -> str:
        """Generate a summary of document processing results"""
        try:
            prompt = f"""
            Generate a professional summary of this document processing result:
            
            Document Information:
            {json.dumps(document_info, indent=2)}
            
            Customer Verification:
            {json.dumps(verification_result, indent=2)}
            
            Create a concise summary that includes:
            1. Document type and key details
            2. Customer verification status
            3. Recommended next actions
            4. Any concerns or flags
            
            Keep it professional and actionable.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a banking operations specialist. Provide clear, actionable summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def validate_account_balance(self, required_amount: float, account_balance: float, overdraft_limit: float = 0) -> Dict:
        """Validate if account has sufficient funds for payment"""
        available_balance = account_balance + overdraft_limit
        
        return {
            "sufficient_funds": available_balance >= required_amount,
            "account_balance": account_balance,
            "overdraft_limit": overdraft_limit,
            "available_balance": available_balance,
            "required_amount": required_amount,
            "shortfall": max(0, required_amount - available_balance),
            "recommendation": "proceed_with_payment" if available_balance >= required_amount else "insufficient_funds"
        }
    
    def generate_payment_instructions(self, customer_info: Dict, amount: float, creditor_info: Dict) -> str:
        """Generate payment processing instructions"""
        try:
            prompt = f"""
            Generate detailed payment processing instructions for this garnishment order:
            
            Customer: {customer_info.get('name', 'Unknown')}
            Account: {customer_info.get('account_number', 'Unknown')}
            Amount: ${amount:,.2f}
            Creditor: {creditor_info.get('name', 'Unknown')}
            
            Include:
            1. Step-by-step payment process
            2. Required documentation
            3. Compliance requirements
            4. Timeline expectations
            5. Confirmation procedures
            
            Make it clear and actionable for banking operations staff.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a banking operations expert. Provide detailed, compliant instructions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating payment instructions: {str(e)}"

# Utility functions for easy access
def process_uploaded_document(file, file_type: str) -> Dict:
    """Process an uploaded document and return extracted information"""
    processor = BankingAIProcessor()
    
    if file_type.lower() == 'pdf':
        text = processor.extract_text_from_pdf(file)
    else:
        text = processor.process_image_with_vision(file)
    
    document_info = processor.classify_document(text)
    document_info['extracted_text'] = text
    document_info['processing_timestamp'] = datetime.now().isoformat()
    
    return document_info

def verify_customer_against_database(document_info: Dict, customer_db: List[Dict]) -> Dict:
    """Verify customer information against database"""
    processor = BankingAIProcessor()
    return processor.verify_customer_information(document_info, customer_db)

def generate_case_summary(document_info: Dict, verification_result: Dict) -> str:
    """Generate a case processing summary"""
    processor = BankingAIProcessor()
    return processor.generate_processing_summary(document_info, verification_result)

