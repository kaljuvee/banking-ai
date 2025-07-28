"""
Enhanced Document Processor for Banking BPO System
Handles document processing with specialized extraction prompts
"""

import os
import json
from typing import Dict, List, Optional
from utils.ai_processor import BankingAIProcessor
import PyPDF2

class EnhancedDocumentProcessor:
    def __init__(self):
        self.ai_processor = BankingAIProcessor()
        self.prompts_dir = "prompts"
        
        # Document type to prompt file mapping
        self.prompt_mapping = {
            'garnishment_order': 'garnishment_order_extraction.txt',
            'court_notice': 'court_notice_extraction.txt',
            'account_freeze_order': 'account_freeze_extraction.txt'
        }
    
    def load_extraction_prompt(self, document_type: str) -> str:
        """Load the appropriate extraction prompt for document type"""
        prompt_file = self.prompt_mapping.get(document_type)
        if not prompt_file:
            return self._get_generic_prompt()
        
        prompt_path = os.path.join(self.prompts_dir, prompt_file)
        
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return self._get_generic_prompt()
    
    def _get_generic_prompt(self) -> str:
        """Generic extraction prompt for unknown document types"""
        return """
        You are an expert legal document analyzer. Extract all relevant information from this document in JSON format.
        
        Include these fields:
        - document_type
        - case_number
        - customer_name
        - account_number
        - creditor_name
        - amount
        - date_filed
        - bank_name
        - confidence_score (0-100)
        
        DOCUMENT TEXT:
        {document_text}
        """
    
    def determine_document_type(self, text: str) -> str:
        """Determine document type from text content"""
        text_lower = text.lower()
        
        if 'writ of execution' in text_lower or 'earnings withholding' in text_lower:
            return 'garnishment_order'
        elif 'notice to financial institution' in text_lower or 'levy notice' in text_lower:
            return 'court_notice'
        elif 'account freeze' in text_lower or 'freeze order' in text_lower:
            return 'account_freeze_order'
        else:
            return 'unknown'
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            return f"Error extracting text from PDF: {str(e)}"
    
    def process_sample_document(self, pdf_path: str, filename: str) -> Dict:
        """Process a sample document and extract all relevant information"""
        try:
            # Extract text from PDF
            document_text = self.extract_text_from_pdf(pdf_path)
            
            if document_text.startswith("Error"):
                return {
                    "filename": filename,
                    "status": "error",
                    "error": document_text,
                    "confidence_score": 0
                }
            
            # Determine document type
            doc_type = self.determine_document_type(document_text)
            
            # Load appropriate extraction prompt
            prompt_template = self.load_extraction_prompt(doc_type)
            
            # Format prompt with document text
            extraction_prompt = prompt_template.format(document_text=document_text)
            
            # Use AI to extract information
            extracted_info = self.ai_processor.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert legal document analyzer. Extract information accurately and return only valid JSON."
                    },
                    {
                        "role": "user", 
                        "content": extraction_prompt
                    }
                ],
                temperature=0.1
            )
            
            # Parse the JSON response
            try:
                result = json.loads(extracted_info.choices[0].message.content)
                result.update({
                    "filename": filename,
                    "status": "processed",
                    "raw_text": document_text[:500] + "..." if len(document_text) > 500 else document_text,
                    "processing_timestamp": "2024-01-27T10:30:00"
                })
                return result
                
            except json.JSONDecodeError as e:
                # If JSON parsing fails, return raw response
                return {
                    "filename": filename,
                    "status": "partial_success",
                    "raw_response": extracted_info.choices[0].message.content,
                    "error": f"JSON parsing error: {str(e)}",
                    "confidence_score": 50
                }
        
        except Exception as e:
            return {
                "filename": filename,
                "status": "error",
                "error": str(e),
                "confidence_score": 0
            }
    
    def process_all_sample_documents(self, sample_dir: str = "data/sample_documents") -> List[Dict]:
        """Process all sample documents in the directory"""
        results = []
        
        if not os.path.exists(sample_dir):
            return [{"error": "Sample documents directory not found"}]
        
        pdf_files = [f for f in os.listdir(sample_dir) if f.endswith('.pdf')]
        
        for filename in sorted(pdf_files):
            pdf_path = os.path.join(sample_dir, filename)
            result = self.process_sample_document(pdf_path, filename)
            results.append(result)
        
        return results
    
    def get_document_summary(self, extracted_data: Dict) -> str:
        """Generate a human-readable summary of extracted data"""
        if extracted_data.get('status') == 'error':
            return f"❌ Error processing document: {extracted_data.get('error', 'Unknown error')}"
        
        doc_type = extracted_data.get('document_type', 'Unknown')
        confidence = extracted_data.get('confidence_score', 0)
        
        summary = f"📄 **{doc_type.replace('_', ' ').title()}**\n"
        summary += f"🎯 **Confidence:** {confidence}%\n\n"
        
        # Add key information based on document type
        if 'customer' in extracted_data or 'defendant_customer' in extracted_data:
            customer = extracted_data.get('defendant_customer') or extracted_data.get('customer_name') or extracted_data.get('account_holder')
            if customer:
                summary += f"👤 **Customer:** {customer}\n"
        
        if 'case_number' in extracted_data:
            summary += f"📋 **Case:** {extracted_data['case_number']}\n"
        
        if 'garnishment_amount' in extracted_data or 'amount_to_withhold' in extracted_data or 'freeze_amount' in extracted_data:
            amount = extracted_data.get('garnishment_amount') or extracted_data.get('amount_to_withhold') or extracted_data.get('freeze_amount')
            if amount:
                summary += f"💰 **Amount:** €{amount:,.2f}\n"
        
        if 'creditor_name' in extracted_data or 'plaintiff_creditor' in extracted_data:
            creditor = extracted_data.get('creditor_name') or extracted_data.get('plaintiff_creditor')
            if creditor:
                summary += f"🏢 **Creditor:** {creditor}\n"
        
        if 'effective_date' in extracted_data or 'date_effective' in extracted_data:
            date = extracted_data.get('effective_date') or extracted_data.get('date_effective')
            if date:
                summary += f"📅 **Effective Date:** {date}\n"
        
        return summary

# Global processor instance
_processor_instance = None

def get_document_processor() -> EnhancedDocumentProcessor:
    """Get the global document processor instance"""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = EnhancedDocumentProcessor()
    return _processor_instance

