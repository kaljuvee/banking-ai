"""
Database utilities for Banking BPO Automation System
Handles customer data, cases, transactions, and document tracking
"""

import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

class BankingDatabase:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.customers_file = os.path.join(data_dir, "customers.csv")
        self.cases_file = os.path.join(data_dir, "cases.json")
        self.transactions_file = os.path.join(data_dir, "transactions.csv")
        self.documents_file = os.path.join(data_dir, "processed_documents.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize data files if they don't exist
        self._initialize_data_files()
    
    def _initialize_data_files(self):
        """Initialize data files with sample data if they don't exist"""
        
        # Initialize customers.csv
        if not os.path.exists(self.customers_file):
            customers_data = [
                {
                    "customer_id": "CUST-001",
                    "name": "John Michael Doe",
                    "email": "john.doe@email.com",
                    "phone": "(555) 123-4567",
                    "account_number": "ACC-2024-001234",
                    "balance": 2500.00,
                    "overdraft_limit": 500.00,
                    "status": "Active",
                    "address": "123 Main Street, San Francisco, CA 94102",
                    "date_opened": "2020-01-15"
                },
                {
                    "customer_id": "CUST-002",
                    "name": "Jane Elizabeth Smith",
                    "email": "jane.smith@email.com",
                    "phone": "(555) 234-5678",
                    "account_number": "ACC-2024-005678",
                    "balance": 1800.50,
                    "overdraft_limit": 300.00,
                    "status": "Active",
                    "address": "456 Oak Avenue, San Francisco, CA 94103",
                    "date_opened": "2019-06-20"
                },
                {
                    "customer_id": "CUST-003",
                    "name": "Robert James Johnson",
                    "email": "robert.johnson@email.com",
                    "phone": "(555) 345-6789",
                    "account_number": "ACC-2024-009876",
                    "balance": 3200.75,
                    "overdraft_limit": 750.00,
                    "status": "Active",
                    "address": "789 Pine Street, San Francisco, CA 94104",
                    "date_opened": "2021-03-10"
                },
                {
                    "customer_id": "CUST-004",
                    "name": "Maria Elena Rodriguez",
                    "email": "maria.rodriguez@email.com",
                    "phone": "(555) 456-7890",
                    "account_number": "ACC-2024-112233",
                    "balance": 950.25,
                    "overdraft_limit": 200.00,
                    "status": "Frozen",
                    "address": "321 Elm Street, San Francisco, CA 94105",
                    "date_opened": "2022-08-05"
                },
                {
                    "customer_id": "CUST-005",
                    "name": "David Michael Chen",
                    "email": "david.chen@email.com",
                    "phone": "(555) 567-8901",
                    "account_number": "ACC-2024-445566",
                    "balance": 4150.00,
                    "overdraft_limit": 1000.00,
                    "status": "Active",
                    "address": "654 Maple Drive, San Francisco, CA 94106",
                    "date_opened": "2018-11-30"
                }
            ]
            
            df = pd.DataFrame(customers_data)
            df.to_csv(self.customers_file, index=False)
        
        # Initialize cases.json
        if not os.path.exists(self.cases_file):
            cases_data = {
                "cases": [
                    {
                        "case_id": "CASE-2024-001",
                        "customer_id": "CUST-001",
                        "customer_name": "John Michael Doe",
                        "case_number": "CV-2024-001234",
                        "creditor": "ABC Collections Agency",
                        "amount_owed": 5000.00,
                        "garnishment_amount": 1250.00,
                        "status": "Active",
                        "date_created": "2024-01-15",
                        "last_updated": "2024-01-20",
                        "documents": ["garnishment_order_1.pdf"],
                        "notes": "Initial garnishment order received and processed",
                        "workflow_stage": "document_processing"
                    },
                    {
                        "case_id": "CASE-2024-002",
                        "customer_id": "CUST-002",
                        "customer_name": "Jane Elizabeth Smith",
                        "case_number": "CV-2024-005678",
                        "creditor": "XYZ Legal Services",
                        "amount_owed": 3400.00,
                        "garnishment_amount": 850.00,
                        "status": "Under Review",
                        "date_created": "2024-01-18",
                        "last_updated": "2024-01-22",
                        "documents": ["court_notice_2.pdf"],
                        "notes": "Customer verification in progress",
                        "workflow_stage": "customer_verification"
                    },
                    {
                        "case_id": "CASE-2024-003",
                        "customer_id": "CUST-004",
                        "customer_name": "Maria Elena Rodriguez",
                        "case_number": "CV-2024-009876",
                        "creditor": "Legal Recovery Associates",
                        "amount_owed": 8400.00,
                        "garnishment_amount": 2100.00,
                        "status": "Payment Processing",
                        "date_created": "2024-01-10",
                        "last_updated": "2024-01-25",
                        "documents": ["account_freeze_order_3.pdf", "garnishment_order_3.pdf"],
                        "notes": "Account frozen, payment processing initiated",
                        "workflow_stage": "payment_processing"
                    }
                ]
            }
            
            with open(self.cases_file, 'w') as f:
                json.dump(cases_data, f, indent=2)
        
        # Initialize transactions.csv
        if not os.path.exists(self.transactions_file):
            transactions_data = [
                {
                    "transaction_id": "TXN-001",
                    "case_id": "CASE-2024-001",
                    "customer_id": "CUST-001",
                    "amount": 1250.00,
                    "transaction_type": "Garnishment Payment",
                    "status": "Completed",
                    "date_processed": "2024-01-20",
                    "creditor": "ABC Collections Agency",
                    "reference_number": "REF-001234"
                },
                {
                    "transaction_id": "TXN-002",
                    "case_id": "CASE-2024-002",
                    "customer_id": "CUST-002",
                    "amount": 850.00,
                    "transaction_type": "Garnishment Payment",
                    "status": "Processing",
                    "date_processed": "2024-01-22",
                    "creditor": "XYZ Legal Services",
                    "reference_number": "REF-005678"
                },
                {
                    "transaction_id": "TXN-003",
                    "case_id": "CASE-2024-003",
                    "customer_id": "CUST-004",
                    "amount": 2100.00,
                    "transaction_type": "Account Freeze",
                    "status": "Pending",
                    "date_processed": "2024-01-25",
                    "creditor": "Legal Recovery Associates",
                    "reference_number": "REF-009876"
                }
            ]
            
            df = pd.DataFrame(transactions_data)
            df.to_csv(self.transactions_file, index=False)
        
        # Initialize processed_documents.json
        if not os.path.exists(self.documents_file):
            documents_data = {
                "processed_documents": [
                    {
                        "document_id": "DOC-001",
                        "filename": "garnishment_order_001.pdf",
                        "document_type": "garnishment_order",
                        "case_id": "CASE-2024-001",
                        "customer_name": "John Michael Doe",
                        "processing_date": "2024-01-15T10:30:00",
                        "confidence_score": 94.2,
                        "status": "Processed",
                        "extracted_data": {
                            "amount": 1250.00,
                            "case_number": "CV-2024-001234",
                            "creditor": "ABC Collections Agency"
                        }
                    },
                    {
                        "document_id": "DOC-002",
                        "filename": "court_notice_002.pdf",
                        "document_type": "court_notice",
                        "case_id": "CASE-2024-002",
                        "customer_name": "Jane Elizabeth Smith",
                        "processing_date": "2024-01-18T14:25:00",
                        "confidence_score": 91.8,
                        "status": "Processed",
                        "extracted_data": {
                            "amount": 850.00,
                            "case_number": "CV-2024-005678",
                            "creditor": "XYZ Legal Services"
                        }
                    }
                ]
            }
            
            with open(self.documents_file, 'w') as f:
                json.dump(documents_data, f, indent=2)
    
    def get_customers(self) -> pd.DataFrame:
        """Get all customers"""
        return pd.read_csv(self.customers_file)
    
    def get_customer_by_id(self, customer_id: str) -> Optional[Dict]:
        """Get customer by ID"""
        customers = self.get_customers()
        customer = customers[customers['customer_id'] == customer_id]
        return customer.iloc[0].to_dict() if not customer.empty else None
    
    def get_customer_by_account(self, account_number: str) -> Optional[Dict]:
        """Get customer by account number"""
        customers = self.get_customers()
        customer = customers[customers['account_number'] == account_number]
        return customer.iloc[0].to_dict() if not customer.empty else None
    
    def search_customers(self, search_term: str) -> List[Dict]:
        """Search customers by name, email, or account number"""
        customers = self.get_customers()
        search_term = search_term.lower()
        
        mask = (
            customers['name'].str.lower().str.contains(search_term, na=False) |
            customers['email'].str.lower().str.contains(search_term, na=False) |
            customers['account_number'].str.lower().str.contains(search_term, na=False)
        )
        
        return customers[mask].to_dict('records')
    
    def get_cases(self) -> List[Dict]:
        """Get all cases"""
        with open(self.cases_file, 'r') as f:
            data = json.load(f)
        return data.get('cases', [])
    
    def get_case_by_id(self, case_id: str) -> Optional[Dict]:
        """Get case by ID"""
        cases = self.get_cases()
        for case in cases:
            if case['case_id'] == case_id:
                return case
        return None
    
    def get_cases_by_customer(self, customer_id: str) -> List[Dict]:
        """Get all cases for a customer"""
        cases = self.get_cases()
        return [case for case in cases if case['customer_id'] == customer_id]
    
    def create_case(self, case_data: Dict) -> str:
        """Create a new case"""
        cases = self.get_cases()
        
        # Generate case ID
        case_id = f"CASE-{datetime.now().strftime('%Y')}-{len(cases) + 1:03d}"
        
        case_data.update({
            'case_id': case_id,
            'date_created': datetime.now().strftime('%Y-%m-%d'),
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'status': case_data.get('status', 'Active'),
            'workflow_stage': case_data.get('workflow_stage', 'document_processing')
        })
        
        cases.append(case_data)
        
        # Save back to file
        with open(self.cases_file, 'w') as f:
            json.dump({'cases': cases}, f, indent=2)
        
        return case_id
    
    def update_case(self, case_id: str, updates: Dict):
        """Update a case"""
        cases = self.get_cases()
        
        for i, case in enumerate(cases):
            if case['case_id'] == case_id:
                case.update(updates)
                case['last_updated'] = datetime.now().strftime('%Y-%m-%d')
                cases[i] = case
                break
        
        # Save back to file
        with open(self.cases_file, 'w') as f:
            json.dump({'cases': cases}, f, indent=2)
    
    def get_transactions(self) -> pd.DataFrame:
        """Get all transactions"""
        return pd.read_csv(self.transactions_file)
    
    def get_transactions_by_customer(self, customer_id: str) -> pd.DataFrame:
        """Get transactions for a customer"""
        transactions = self.get_transactions()
        return transactions[transactions['customer_id'] == customer_id]
    
    def create_transaction(self, transaction_data: Dict) -> str:
        """Create a new transaction"""
        transactions = self.get_transactions()
        
        # Generate transaction ID
        transaction_id = f"TXN-{len(transactions) + 1:03d}"
        
        transaction_data.update({
            'transaction_id': transaction_id,
            'date_processed': datetime.now().strftime('%Y-%m-%d')
        })
        
        # Add to dataframe and save
        new_transaction = pd.DataFrame([transaction_data])
        transactions = pd.concat([transactions, new_transaction], ignore_index=True)
        transactions.to_csv(self.transactions_file, index=False)
        
        return transaction_id
    
    def get_processed_documents(self) -> List[Dict]:
        """Get all processed documents"""
        if os.path.exists(self.documents_file):
            with open(self.documents_file, 'r') as f:
                data = json.load(f)
            return data.get('processed_documents', [])
        return []
    
    def save_processed_document(self, document_data: Dict) -> str:
        """Save processed document information"""
        documents = self.get_processed_documents()
        
        # Generate document ID
        document_id = f"DOC-{len(documents) + 1:03d}"
        
        document_data.update({
            'document_id': document_id,
            'processing_date': datetime.now().isoformat()
        })
        
        documents.append(document_data)
        
        # Save back to file
        with open(self.documents_file, 'w') as f:
            json.dump({'processed_documents': documents}, f, indent=2)
        
        return document_id
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        customers = self.get_customers()
        cases = self.get_cases()
        transactions = self.get_transactions()
        
        return {
            'total_customers': len(customers),
            'active_customers': len(customers[customers['status'] == 'Active']),
            'total_cases': len(cases),
            'active_cases': len([c for c in cases if c['status'] == 'Active']),
            'total_transactions': len(transactions),
            'completed_transactions': len(transactions[transactions['status'] == 'Completed']),
            'avg_balance': customers['balance'].mean(),
            'total_garnishment_amount': sum([c['garnishment_amount'] for c in cases])
        }

# Global database instance
_db_instance = None

def get_database() -> BankingDatabase:
    """Get the global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = BankingDatabase()
    return _db_instance

# Utility functions for easy access
def get_customer_data() -> List[Dict]:
    """Get all customer data as list of dictionaries"""
    db = get_database()
    return db.get_customers().to_dict('records')

def search_customer(search_term: str) -> List[Dict]:
    """Search for customers"""
    db = get_database()
    return db.search_customers(search_term)

def get_case_data() -> List[Dict]:
    """Get all case data"""
    db = get_database()
    return db.get_cases()

def create_new_case(customer_id: str, case_details: Dict) -> str:
    """Create a new case"""
    db = get_database()
    return db.create_case({
        'customer_id': customer_id,
        **case_details
    })

