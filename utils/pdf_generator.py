"""
PDF Generator for Banking BPO Sample Documents
Generates sample court documents, garnishment orders, and legal notices
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime, timedelta
import os
import random

class BankingDocumentGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.custom_styles = self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        styles = {}
        
        # Header style
        styles['CustomHeader'] = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        # Court style
        styles['CourtHeader'] = ParagraphStyle(
            'CourtHeader',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            alignment=1,  # Center alignment
            fontName='Helvetica-Bold'
        )
        
        # Legal text style
        styles['LegalText'] = ParagraphStyle(
            'LegalText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            leftIndent=20,
            rightIndent=20
        )
        
        return styles
    
    def generate_garnishment_order(self, output_path, customer_data=None):
        """Generate a sample garnishment order document"""
        if customer_data is None:
            customer_data = self._get_sample_customer_data()
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        # Header
        story.append(Paragraph("SUPERIOR COURT OF CALIFORNIA", self.custom_styles['CourtHeader']))
        story.append(Paragraph("COUNTY OF SAN FRANCISCO", self.custom_styles['CourtHeader']))
        story.append(Spacer(1, 20))
        
        # Case information
        case_info = [
            ["Case No:", customer_data['case_number']],
            ["Plaintiff:", customer_data['creditor']],
            ["Defendant:", customer_data['customer_name']],
            ["Date Filed:", customer_data['date_filed']]
        ]
        
        case_table = Table(case_info, colWidths=[1.5*inch, 4*inch])
        case_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(case_table)
        story.append(Spacer(1, 30))
        
        # Title
        story.append(Paragraph("WRIT OF EXECUTION - EARNINGS WITHHOLDING ORDER", self.custom_styles['CustomHeader']))
        story.append(Spacer(1, 20))
        
        # Order text
        order_text = f"""
        TO: {customer_data['bank_name']}<br/>
        {customer_data['bank_address']}<br/><br/>
        
        YOU ARE HEREBY COMMANDED to withhold from the earnings of {customer_data['customer_name']}, 
        Account Number: {customer_data['account_number']}, the amount of ${customer_data['garnishment_amount']:,.2f} 
        plus interest and costs as specified in the judgment.<br/><br/>
        
        This order is effective immediately upon service and shall remain in effect until the 
        judgment is satisfied in full or until further order of the court.<br/><br/>
        
        The total judgment amount is ${customer_data['total_judgment']:,.2f} as of {customer_data['date_filed']}.
        """
        
        story.append(Paragraph(order_text, self.custom_styles['LegalText']))
        story.append(Spacer(1, 30))
        
        # Signature block
        signature_data = [
            ["", ""],
            ["_" * 40, "Date: " + customer_data['date_filed']],
            ["Clerk of the Court", ""],
        ]
        
        sig_table = Table(signature_data, colWidths=[3*inch, 2*inch])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(sig_table)
        
        doc.build(story)
        return output_path
    
    def generate_court_notice(self, output_path, customer_data=None):
        """Generate a sample court notice document"""
        if customer_data is None:
            customer_data = self._get_sample_customer_data()
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        # Header
        story.append(Paragraph("NOTICE TO FINANCIAL INSTITUTION", self.custom_styles['CustomHeader']))
        story.append(Spacer(1, 20))
        
        # Notice content
        notice_text = f"""
        <b>TO:</b> {customer_data['bank_name']}<br/>
        <b>RE:</b> Account Holder: {customer_data['customer_name']}<br/>
        <b>Account Number:</b> {customer_data['account_number']}<br/>
        <b>Case Number:</b> {customer_data['case_number']}<br/><br/>
        
        You are hereby notified that a Writ of Execution has been issued in the above-entitled action 
        requiring you to freeze the account(s) of the above-named judgment debtor and to pay over to 
        the levying officer any amounts on deposit.<br/><br/>
        
        <b>Amount to be Withheld:</b> ${customer_data['garnishment_amount']:,.2f}<br/>
        <b>Effective Date:</b> {customer_data['date_filed']}<br/><br/>
        
        You must comply with this order within 10 days of service. Failure to comply may result in 
        liability for the full amount of the judgment.<br/><br/>
        
        For questions regarding this notice, contact the court clerk at (415) 551-4000.
        """
        
        story.append(Paragraph(notice_text, self.custom_styles['LegalText']))
        
        doc.build(story)
        return output_path
    
    def generate_account_freeze_order(self, output_path, customer_data=None):
        """Generate a sample account freeze order"""
        if customer_data is None:
            customer_data = self._get_sample_customer_data()
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        # Header
        story.append(Paragraph("ACCOUNT FREEZE ORDER", self.custom_styles['CustomHeader']))
        story.append(Spacer(1, 20))
        
        # Order details
        order_text = f"""
        <b>Court:</b> Superior Court of California, County of San Francisco<br/>
        <b>Case Number:</b> {customer_data['case_number']}<br/>
        <b>Date Issued:</b> {customer_data['date_filed']}<br/><br/>
        
        <b>TO:</b> {customer_data['bank_name']}<br/><br/>
        
        You are hereby ordered to immediately freeze all accounts held by:<br/>
        <b>Account Holder:</b> {customer_data['customer_name']}<br/>
        <b>Primary Account:</b> {customer_data['account_number']}<br/><br/>
        
        <b>FREEZE AMOUNT:</b> ${customer_data['garnishment_amount']:,.2f}<br/><br/>
        
        This freeze order is effective immediately and shall remain in place until:<br/>
        1. The specified amount is paid to the court, OR<br/>
        2. Further order of the court<br/><br/>
        
        You must provide written confirmation of compliance within 5 business days.
        """
        
        story.append(Paragraph(order_text, self.custom_styles['LegalText']))
        
        doc.build(story)
        return output_path
    
    def _get_sample_customer_data(self):
        """Generate sample customer data for documents"""
        customers = [
            {
                'customer_name': 'John Michael Doe',
                'account_number': 'ACC-2024-001234',
                'case_number': 'CV-2024-001234',
                'creditor': 'ABC Collections Agency',
                'bank_name': 'First National Bank',
                'bank_address': '123 Banking Street, San Francisco, CA 94102',
                'garnishment_amount': 1250.00,
                'total_judgment': 5000.00,
                'date_filed': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%m/%d/%Y')
            },
            {
                'customer_name': 'Jane Elizabeth Smith',
                'account_number': 'ACC-2024-005678',
                'case_number': 'CV-2024-005678',
                'creditor': 'XYZ Legal Services',
                'bank_name': 'First National Bank',
                'bank_address': '123 Banking Street, San Francisco, CA 94102',
                'garnishment_amount': 850.00,
                'total_judgment': 3400.00,
                'date_filed': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%m/%d/%Y')
            },
            {
                'customer_name': 'Robert James Johnson',
                'account_number': 'ACC-2024-009876',
                'case_number': 'CV-2024-009876',
                'creditor': 'Legal Recovery Associates',
                'bank_name': 'First National Bank',
                'bank_address': '123 Banking Street, San Francisco, CA 94102',
                'garnishment_amount': 2100.00,
                'total_judgment': 8400.00,
                'date_filed': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%m/%d/%Y')
            }
        ]
        
        return random.choice(customers)
    
    def generate_all_sample_documents(self, output_dir):
        """Generate all types of sample documents"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        documents = []
        
        # Generate multiple documents of each type
        for i in range(3):
            customer_data = self._get_sample_customer_data()
            
            # Garnishment order
            garnishment_path = os.path.join(output_dir, f"garnishment_order_{i+1}.pdf")
            self.generate_garnishment_order(garnishment_path, customer_data)
            documents.append(("Garnishment Order", garnishment_path))
            
            # Court notice
            notice_path = os.path.join(output_dir, f"court_notice_{i+1}.pdf")
            self.generate_court_notice(notice_path, customer_data)
            documents.append(("Court Notice", notice_path))
            
            # Account freeze order
            freeze_path = os.path.join(output_dir, f"account_freeze_order_{i+1}.pdf")
            self.generate_account_freeze_order(freeze_path, customer_data)
            documents.append(("Account Freeze Order", freeze_path))
        
        return documents

def generate_sample_pdfs():
    """Utility function to generate sample PDFs"""
    generator = BankingDocumentGenerator()
    output_dir = "data/sample_documents"
    return generator.generate_all_sample_documents(output_dir)

if __name__ == "__main__":
    # Generate sample documents when run directly
    docs = generate_sample_pdfs()
    print(f"Generated {len(docs)} sample documents:")
    for doc_type, path in docs:
        print(f"  - {doc_type}: {path}")

