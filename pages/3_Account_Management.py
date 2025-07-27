import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.database import get_database, get_customer_data
from utils.ai_processor import BankingAIProcessor
import random

st.set_page_config(
    page_title="Account Management",
    page_icon="💳",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .account-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    .balance-info {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .payment-check {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .insufficient-funds {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .action-button {
        margin: 0.25rem;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

def load_account_data(account_number):
    """Load account data for the specified account"""
    db = get_database()
    customer = db.get_customer_by_account(account_number)
    
    if customer:
        # Add some mock additional data
        customer.update({
            'last_transaction_date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
            'account_type': 'Checking',
            'overdraft_protection': True,
            'monthly_fee': 12.00,
            'interest_rate': 0.01,
            'credit_score': random.randint(650, 800)
        })
    
    return customer

def calculate_payment_capability(balance, overdraft_limit, required_amount):
    """Calculate if payment is possible and provide details"""
    available_balance = balance + overdraft_limit
    
    return {
        'payment_possible': available_balance >= required_amount,
        'current_balance': balance,
        'overdraft_limit': overdraft_limit,
        'available_balance': available_balance,
        'required_amount': required_amount,
        'remaining_after_payment': available_balance - required_amount,
        'uses_overdraft': required_amount > balance,
        'overdraft_amount': max(0, required_amount - balance)
    }

def main():
    st.title("💳 Account Management")
    st.markdown("---")
    
    # Sidebar for account operations
    with st.sidebar:
        st.header("Account Operations")
        
        operation_type = st.selectbox(
            "Select Operation",
            ["Balance Check", "Account Freeze", "Overdraft Management", "Product Cancellation"],
            help="Choose the account operation to perform"
        )
        
        if operation_type in ["Account Freeze", "Overdraft Management"]:
            required_amount = st.number_input(
                "Required Payment Amount (€)",
                min_value=0.0,
                value=1250.0,
                step=50.0,
                help="Amount required for garnishment"
            )
        
        st.markdown("---")
        st.info("💡 Manage customer accounts and verify payment capabilities")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("🏦 Account Information")
        
        # Account selection
        account_number = st.selectbox(
            "Select Account",
            ["ACC-2024-001234", "ACC-2024-005678", "ACC-2024-009876", "ACC-2024-112233", "ACC-2024-445566"],
            help="Choose customer account to manage"
        )
        
        # Load account data
        if account_number:
            account_data = load_account_data(account_number)
            
            if account_data:
                # Account Overview
                st.subheader("📊 Account Overview")
                
                st.markdown(f"""
                <div class="account-card">
                    <p><strong>Customer:</strong> {account_data['name']}</p>
                    <p><strong>Account:</strong> {account_data['account_number']}</p>
                    <p><strong>Status:</strong> {account_data['status']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Balance Information
                st.subheader("💰 Balance Information")
                
                balance_col1, balance_col2 = st.columns(2)
                
                with balance_col1:
                    st.metric("Current Balance", f"€{account_data['balance']:,.2f}")
                    st.metric("Available Balance", f"€{account_data['balance'] + account_data['overdraft_limit']:,.2f}")
                
                with balance_col2:
                    st.metric("Overdraft Limit", f"€{account_data['overdraft_limit']:,.2f}")
                    st.metric("Overdraft Used", "€0.00")
                
                # Account Details
                with st.expander("📋 Account Details"):
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.write("**Account Type:**", account_data.get('account_type', 'Unknown'))
                        st.write("**Date Opened:**", account_data.get('date_opened', 'Unknown'))
                        st.write("**Last Transaction:**", account_data.get('last_transaction_date', 'Unknown'))
                    
                    with detail_col2:
                        st.write("**Monthly Fee:**", f"€{account_data.get('monthly_fee', 0):.2f}")
                        st.write("**Interest Rate:**", f"{account_data.get('interest_rate', 0)*100:.2f}%")
                        st.write("**Credit Score:**", account_data.get('credit_score', 'Unknown'))
                
                # Payment Capability Check (if required amount is specified)
                if operation_type in ["Account Freeze", "Overdraft Management"]:
                    st.subheader("💳 Payment Capability Check")
                    
                    payment_info = calculate_payment_capability(
                        account_data['balance'],
                        account_data['overdraft_limit'],
                        required_amount
                    )
                    
                    if payment_info['payment_possible']:
                        st.markdown(f"""
                        <div class="payment-check">
                            <h4>✅ Payment Possible</h4>
                            <p><strong>Required Amount:</strong> €{payment_info['required_amount']:,.2f}</p>
                            <p><strong>Total Available:</strong> €{payment_info['available_balance']:,.2f}</p>
                            <p><strong>Remaining After Payment:</strong> €{payment_info['remaining_after_payment']:,.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if payment_info['uses_overdraft']:
                            st.warning(f"⚠️ Payment will use €{payment_info['overdraft_amount']:,.2f} of overdraft credit")
                    
                    else:
                        shortfall = payment_info['required_amount'] - payment_info['available_balance']
                        st.markdown(f"""
                        <div class="insufficient-funds">
                            <h4>❌ Insufficient Funds</h4>
                            <p><strong>Required Amount:</strong> €{payment_info['required_amount']:,.2f}</p>
                            <p><strong>Available Balance:</strong> €{payment_info['available_balance']:,.2f}</p>
                            <p><strong>Shortfall:</strong> €{shortfall:,.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            else:
                st.error("❌ Account not found")
    
    with col2:
        st.header("⚙️ Account Operations")
        
        if operation_type == "Balance Check":
            st.subheader("💰 Balance Check")
            
            if st.button("🔄 Refresh Balance", use_container_width=True):
                st.success("✅ Balance refreshed successfully")
                st.rerun()
            
            st.info("Current balance information is displayed in the left panel")
            
            # Action summary
            st.markdown("---")
            st.subheader("📋 Action Summary")
            
            if account_data:
                summary_items = [
                    "✅ Account verified",
                    "✅ Balance sufficient" if account_data['balance'] > 1000 else "⚠️ Low balance",
                    "⏳ Ready for payment"
                ]
                
                for item in summary_items:
                    st.write(item)
        
        elif operation_type == "Account Freeze":
            st.subheader("🧊 Account Freeze")
            
            freeze_reason = st.selectbox(
                "Freeze Reason",
                ["Court Order", "Garnishment", "Suspicious Activity", "Customer Request"],
                help="Select reason for account freeze"
            )
            
            freeze_duration = st.selectbox(
                "Freeze Duration",
                ["Until Further Notice", "30 Days", "60 Days", "90 Days"],
                help="Select freeze duration"
            )
            
            if st.button("🧊 Freeze Account", type="primary", use_container_width=True):
                st.success(f"✅ Account frozen due to: {freeze_reason}")
                st.info(f"Duration: {freeze_duration}")
            
            if st.button("🔓 Unfreeze Account", use_container_width=True):
                st.success("✅ Account unfrozen successfully")
        
        elif operation_type == "Overdraft Management":
            st.subheader("💳 Overdraft Management")
            
            action = st.radio(
                "Overdraft Action",
                ["Cancel Overdraft", "Modify Limit", "Suspend Overdraft"],
                help="Choose overdraft management action"
            )
            
            if action == "Modify Limit":
                new_limit = st.number_input(
                    "New Overdraft Limit (€)",
                    min_value=0.0,
                    max_value=5000.0,
                    value=500.0,
                    step=100.0
                )
            
            if st.button(f"✅ Execute {action}", type="primary", use_container_width=True):
                if action == "Cancel Overdraft":
                    st.success("✅ Overdraft protection cancelled")
                elif action == "Modify Limit":
                    st.success(f"✅ Overdraft limit updated to €{new_limit:,.2f}")
                else:
                    st.success("✅ Overdraft protection suspended")
        
        elif operation_type == "Product Cancellation":
            st.subheader("🚫 Product Cancellation")
            
            products = st.multiselect(
                "Select Products to Cancel",
                ["Overdraft Protection", "Credit Card", "Savings Account", "Investment Account", "Loan"],
                help="Choose products to cancel"
            )
            
            cancellation_reason = st.text_area(
                "Cancellation Reason",
                placeholder="Enter reason for product cancellation...",
                help="Provide reason for cancellation"
            )
            
            if st.button("🚫 Cancel Selected Products", type="primary", use_container_width=True):
                if products:
                    st.success(f"✅ Cancelled products: {', '.join(products)}")
                else:
                    st.warning("⚠️ No products selected")
        
        # Quick Actions
        st.markdown("---")
        st.subheader("⚡ Quick Actions")
        
        quick_col1, quick_col2 = st.columns(2)
        
        with quick_col1:
            if st.button("💰 Proceed to Payment", use_container_width=True):
                st.switch_page("pages/4_Payment_Processing.py")
            
            if st.button("📧 Notify Customer", use_container_width=True):
                st.info("📧 Customer notification sent")
        
        with quick_col2:
            if st.button("📋 Update Case", use_container_width=True):
                st.switch_page("pages/5_Case_Management.py")
            
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.success("🔄 Data refreshed")
                st.rerun()
        
        # Pending Operations
        st.markdown("---")
        st.subheader("⏳ Pending Operations")
        
        pending_ops = [
            "🧊 Account freeze (if required)",
            "🚫 Overdraft cancellation", 
            "📧 Customer notification"
        ]
        
        for op in pending_ops:
            st.write(op)
        
        # Next Steps
        st.subheader("📊 Next Steps")
        
        next_steps = [
            "💰 Process payment",
            "📋 Update case status",
            "✉️ Send confirmations"
        ]
        
        for step in next_steps:
            st.write(step)
    
    # Account Activity History
    st.markdown("---")
    st.header("📊 Account Activity History")
    
    # Mock transaction history
    if account_data:
        transactions = []
        for i in range(10):
            date = (datetime.now() - timedelta(days=i*3)).strftime('%Y-%m-%d')
            amount = random.uniform(50, 500)
            transaction_type = random.choice(['Debit', 'Credit', 'Transfer', 'Fee'])
            
            transactions.append({
                'Date': date,
                'Type': transaction_type,
                'Amount': f"€{amount:.2f}",
                'Balance': f"€{account_data['balance'] + random.uniform(-200, 200):.2f}",
                'Description': f"{transaction_type} transaction"
            })
        
        df_transactions = pd.DataFrame(transactions)
        st.dataframe(df_transactions, use_container_width=True)
    
    # Account Statistics
    st.markdown("---")
    st.header("📈 Account Statistics")
    
    if account_data:
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            st.metric("Average Monthly Balance", f"€{account_data['balance'] * 1.1:,.2f}")
        
        with stat_col2:
            st.metric("Transactions This Month", "23")
        
        with stat_col3:
            st.metric("Overdraft Usage", "0%")
        
        with stat_col4:
            st.metric("Account Age", f"{(datetime.now() - datetime.strptime(account_data['date_opened'], '%Y-%m-%d')).days // 365} years")

if __name__ == "__main__":
    main()

