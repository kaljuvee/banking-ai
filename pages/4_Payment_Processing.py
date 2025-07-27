import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.database import get_database, get_customer_data
import random
import uuid

st.set_page_config(
    page_title="Payment Processing",
    page_icon="💰",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .payment-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .payment-step {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 3px solid #2196f3;
    }
    .payment-success {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .payment-pending {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .payment-error {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .creditor-info {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def generate_payment_reference():
    """Generate a unique payment reference number"""
    return f"PAY-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

def calculate_payment_breakdown(amount, fees=True):
    """Calculate payment breakdown including fees"""
    base_amount = amount
    processing_fee = 2.50 if fees else 0.0
    wire_fee = 15.00 if amount > 1000 and fees else 0.0
    total_amount = base_amount + processing_fee + wire_fee
    
    return {
        'base_amount': base_amount,
        'processing_fee': processing_fee,
        'wire_fee': wire_fee,
        'total_amount': total_amount
    }

def get_creditor_info(creditor_name):
    """Get creditor information"""
    creditors = {
        'ABC Collections Agency': {
            'name': 'ABC Collections Agency',
            'address': '456 Collection Street, San Francisco, CA 94107',
            'account_number': 'CRED-ABC-001',
            'routing_number': '123456789',
            'contact_phone': '(555) 987-6543',
            'contact_email': 'payments@abccollections.com'
        },
        'XYZ Legal Services': {
            'name': 'XYZ Legal Services',
            'address': '789 Legal Avenue, San Francisco, CA 94108',
            'account_number': 'CRED-XYZ-002',
            'routing_number': '987654321',
            'contact_phone': '(555) 876-5432',
            'contact_email': 'garnishments@xyzlegal.com'
        },
        'Legal Recovery Associates': {
            'name': 'Legal Recovery Associates',
            'address': '321 Recovery Road, San Francisco, CA 94109',
            'account_number': 'CRED-LRA-003',
            'routing_number': '456789123',
            'contact_phone': '(555) 765-4321',
            'contact_email': 'payments@legalrecovery.com'
        }
    }
    
    return creditors.get(creditor_name, {
        'name': creditor_name,
        'address': 'Address not available',
        'account_number': 'Unknown',
        'routing_number': 'Unknown',
        'contact_phone': 'Unknown',
        'contact_email': 'Unknown'
    })

def main():
    st.title("💰 Payment Processing")
    st.markdown("---")
    
    # Sidebar for payment settings
    with st.sidebar:
        st.header("Payment Settings")
        
        payment_method = st.selectbox(
            "Payment Method",
            ["Wire Transfer", "ACH Transfer", "Check", "Electronic Payment"],
            help="Choose payment method"
        )
        
        priority_level = st.selectbox(
            "Priority Level",
            ["Standard", "Expedited", "Same Day"],
            help="Select payment priority"
        )
        
        include_fees = st.checkbox(
            "Include Processing Fees",
            value=True,
            help="Include processing and wire fees"
        )
        
        st.markdown("---")
        st.info("💡 Process court-ordered garnishment payments")
    
    # Initialize session state
    if 'payment_stage' not in st.session_state:
        st.session_state.payment_stage = 'setup'
    if 'payment_data' not in st.session_state:
        st.session_state.payment_data = {}
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("💳 Payment Setup")
        
        # Payment form
        with st.form("payment_form"):
            st.subheader("Payment Details")
            
            # Customer selection
            customer_account = st.selectbox(
                "Customer Account",
                ["ACC-2024-001234 (John Doe)", "ACC-2024-005678 (Jane Smith)", 
                 "ACC-2024-009876 (Robert Johnson)", "ACC-2024-112233 (Maria Rodriguez)"],
                help="Select customer account for payment"
            )
            
            # Payment amount
            payment_amount = st.number_input(
                "Payment Amount (€)",
                min_value=0.0,
                value=1250.0,
                step=50.0,
                help="Enter garnishment amount"
            )
            
            # Creditor information
            creditor_name = st.selectbox(
                "Creditor",
                ["ABC Collections Agency", "XYZ Legal Services", "Legal Recovery Associates"],
                help="Select creditor for payment"
            )
            
            # Case reference
            case_reference = st.text_input(
                "Case Reference",
                value="CV-2024-001234",
                help="Enter court case reference number"
            )
            
            # Payment description
            payment_description = st.text_area(
                "Payment Description",
                value="Court-ordered garnishment payment",
                help="Enter payment description"
            )
            
            # Submit button
            setup_payment = st.form_submit_button("⚡ Setup Payment", type="primary")
        
        if setup_payment:
            # Calculate payment breakdown
            payment_breakdown = calculate_payment_breakdown(payment_amount, include_fees)
            
            # Store payment data
            st.session_state.payment_data = {
                'customer_account': customer_account,
                'payment_amount': payment_amount,
                'creditor_name': creditor_name,
                'case_reference': case_reference,
                'payment_description': payment_description,
                'payment_method': payment_method,
                'priority_level': priority_level,
                'payment_breakdown': payment_breakdown,
                'payment_reference': generate_payment_reference(),
                'setup_timestamp': datetime.now().isoformat()
            }
            
            st.session_state.payment_stage = 'review'
            st.rerun()
    
    with col2:
        st.header("🔄 Payment Status")
        
        if st.session_state.payment_stage == 'setup':
            st.info("👆 Please setup payment details to proceed")
            
            # Payment workflow steps
            st.subheader("📋 Payment Workflow")
            
            workflow_steps = [
                "1️⃣ Payment Setup & Validation",
                "2️⃣ Customer Account Verification", 
                "3️⃣ Creditor Information Confirmation",
                "4️⃣ Payment Authorization",
                "5️⃣ Payment Processing",
                "6️⃣ Confirmation & Documentation"
            ]
            
            for step in workflow_steps:
                st.markdown(f"""
                <div class="payment-step">
                    {step}
                </div>
                """, unsafe_allow_html=True)
        
        elif st.session_state.payment_stage == 'review':
            payment_data = st.session_state.payment_data
            
            st.subheader("📋 Payment Review")
            
            # Payment summary
            st.markdown(f"""
            <div class="payment-card">
                <h4>💰 Payment Summary</h4>
                <p><strong>Reference:</strong> {payment_data['payment_reference']}</p>
                <p><strong>Customer:</strong> {payment_data['customer_account']}</p>
                <p><strong>Amount:</strong> €{payment_data['payment_amount']:,.2f}</p>
                <p><strong>Method:</strong> {payment_data['payment_method']}</p>
                <p><strong>Priority:</strong> {payment_data['priority_level']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Payment breakdown
            breakdown = payment_data['payment_breakdown']
            
            st.subheader("💵 Payment Breakdown")
            breakdown_col1, breakdown_col2 = st.columns(2)
            
            with breakdown_col1:
                st.metric("Base Amount", f"€{breakdown['base_amount']:,.2f}")
                st.metric("Processing Fee", f"€{breakdown['processing_fee']:,.2f}")
            
            with breakdown_col2:
                st.metric("Wire Fee", f"€{breakdown['wire_fee']:,.2f}")
                st.metric("Total Amount", f"€{breakdown['total_amount']:,.2f}")
            
            # Creditor information
            st.subheader("🏢 Creditor Information")
            creditor_info = get_creditor_info(payment_data['creditor_name'])
            
            st.markdown(f"""
            <div class="creditor-info">
                <p><strong>Name:</strong> {creditor_info['name']}</p>
                <p><strong>Address:</strong> {creditor_info['address']}</p>
                <p><strong>Account:</strong> {creditor_info['account_number']}</p>
                <p><strong>Routing:</strong> {creditor_info['routing_number']}</p>
                <p><strong>Contact:</strong> {creditor_info['contact_phone']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            st.markdown("---")
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                if st.button("✅ Authorize Payment", type="primary"):
                    st.session_state.payment_stage = 'processing'
                    st.rerun()
            
            with action_col2:
                if st.button("✏️ Edit Payment"):
                    st.session_state.payment_stage = 'setup'
                    st.rerun()
            
            with action_col3:
                if st.button("❌ Cancel Payment"):
                    st.session_state.payment_stage = 'setup'
                    st.session_state.payment_data = {}
                    st.rerun()
        
        elif st.session_state.payment_stage == 'processing':
            payment_data = st.session_state.payment_data
            
            st.subheader("⚡ Processing Payment")
            
            # Simulate processing steps
            progress_bar = st.progress(0)
            status_placeholder = st.empty()
            
            processing_steps = [
                ("Validating customer account...", 20),
                ("Verifying available funds...", 40),
                ("Connecting to payment network...", 60),
                ("Transferring funds...", 80),
                ("Generating confirmation...", 100)
            ]
            
            # Auto-advance through processing steps
            if 'processing_step' not in st.session_state:
                st.session_state.processing_step = 0
            
            if st.session_state.processing_step < len(processing_steps):
                step_text, progress = processing_steps[st.session_state.processing_step]
                progress_bar.progress(progress)
                status_placeholder.info(f"🔄 {step_text}")
                
                # Auto-advance after a delay (in real app, this would be actual processing)
                if st.button("⏭️ Continue Processing"):
                    st.session_state.processing_step += 1
                    st.rerun()
            else:
                # Processing complete
                progress_bar.progress(100)
                status_placeholder.success("✅ Payment processed successfully!")
                
                st.session_state.payment_stage = 'completed'
                st.rerun()
        
        elif st.session_state.payment_stage == 'completed':
            payment_data = st.session_state.payment_data
            
            st.markdown(f"""
            <div class="payment-success">
                <h4>✅ Payment Completed Successfully</h4>
                <p><strong>Reference:</strong> {payment_data['payment_reference']}</p>
                <p><strong>Amount:</strong> €{payment_data['payment_breakdown']['total_amount']:,.2f}</p>
                <p><strong>Status:</strong> Completed</p>
                <p><strong>Processed:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Confirmation details
            st.subheader("📄 Payment Confirmation")
            
            confirmation_data = {
                'Transaction ID': payment_data['payment_reference'],
                'Date Processed': datetime.now().strftime('%Y-%m-%d'),
                'Time Processed': datetime.now().strftime('%H:%M:%S'),
                'Customer Account': payment_data['customer_account'].split(' ')[0],
                'Creditor': payment_data['creditor_name'],
                'Amount': f"€{payment_data['payment_breakdown']['total_amount']:,.2f}",
                'Method': payment_data['payment_method'],
                'Status': 'Completed'
            }
            
            for key, value in confirmation_data.items():
                st.write(f"**{key}:** {value}")
            
            # Action buttons
            st.markdown("---")
            conf_col1, conf_col2, conf_col3 = st.columns(3)
            
            with conf_col1:
                if st.button("📧 Send Confirmation"):
                    st.success("📧 Confirmation sent to all parties")
            
            with conf_col2:
                if st.button("📋 Update Case"):
                    st.switch_page("pages/5_Case_Management.py")
            
            with conf_col3:
                if st.button("🔄 New Payment"):
                    st.session_state.payment_stage = 'setup'
                    st.session_state.payment_data = {}
                    st.session_state.processing_step = 0
                    st.rerun()
    
    # Payment History
    st.markdown("---")
    st.header("📊 Payment History")
    
    # Mock payment history data
    payment_history = []
    for i in range(10):
        date = (datetime.now() - timedelta(days=i*2)).strftime('%Y-%m-%d')
        amount = random.uniform(500, 2500)
        status = random.choice(['Completed', 'Processing', 'Pending'])
        creditor = random.choice(['ABC Collections', 'XYZ Legal', 'Legal Recovery'])
        
        payment_history.append({
            'Date': date,
            'Reference': f"PAY-{date.replace('-', '')}-{random.randint(1000, 9999)}",
            'Customer': random.choice(['John Doe', 'Jane Smith', 'Robert Johnson']),
            'Amount': f"€{amount:,.2f}",
            'Creditor': creditor,
            'Status': status
        })
    
    df_history = pd.DataFrame(payment_history)
    st.dataframe(df_history, use_container_width=True)
    
    # Payment Statistics
    st.markdown("---")
    st.header("📈 Payment Statistics")
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric("Total Payments Today", "12")
    
    with stat_col2:
        st.metric("Amount Processed Today", "€18,750.00")
    
    with stat_col3:
        st.metric("Success Rate", "98.5%")
    
    with stat_col4:
        st.metric("Avg Processing Time", "4.2 min")

if __name__ == "__main__":
    main()

