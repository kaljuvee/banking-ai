import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database import get_database, search_customer, get_customer_data
from utils.ai_processor import BankingAIProcessor

st.set_page_config(
    page_title="Customer Verification",
    page_icon="👤",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .verification-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    .match-found {
        background-color: #d4edda;
        border-left-color: #28a745;
    }
    .match-review {
        background-color: #fff3cd;
        border-left-color: #ffc107;
    }
    .match-not-found {
        background-color: #f8d7da;
        border-left-color: #dc3545;
    }
    .customer-info {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .verification-actions {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def fuzzy_match_score(search_term, target, field_weight=1.0):
    """Calculate fuzzy match score between search term and target"""
    if not search_term or not target:
        return 0
    
    search_term = search_term.lower().strip()
    target = target.lower().strip()
    
    # Exact match
    if search_term == target:
        return 100 * field_weight
    
    # Contains match
    if search_term in target or target in search_term:
        return 80 * field_weight
    
    # Word-by-word matching
    search_words = search_term.split()
    target_words = target.split()
    
    matches = 0
    for word in search_words:
        if any(word in target_word or target_word in word for target_word in target_words):
            matches += 1
    
    if matches > 0:
        return (matches / len(search_words)) * 60 * field_weight
    
    return 0

def verify_customer_advanced(customer_name, account_number, address, phone="", email=""):
    """Advanced customer verification with multiple fields"""
    db = get_database()
    customers = db.get_customers()
    
    best_matches = []
    
    for _, customer in customers.iterrows():
        total_score = 0
        match_details = {}
        
        # Name matching (highest weight)
        if customer_name:
            name_score = fuzzy_match_score(customer_name, customer['name'], 0.4)
            total_score += name_score
            match_details['name_match'] = name_score
        
        # Account number matching (highest weight)
        if account_number:
            account_score = fuzzy_match_score(account_number, customer['account_number'], 0.4)
            total_score += account_score
            match_details['account_match'] = account_score
        
        # Address matching
        if address:
            address_score = fuzzy_match_score(address, customer.get('address', ''), 0.15)
            total_score += address_score
            match_details['address_match'] = address_score
        
        # Phone matching
        if phone:
            phone_score = fuzzy_match_score(phone, customer.get('phone', ''), 0.025)
            total_score += phone_score
            match_details['phone_match'] = phone_score
        
        # Email matching
        if email:
            email_score = fuzzy_match_score(email, customer.get('email', ''), 0.025)
            total_score += email_score
            match_details['email_match'] = email_score
        
        if total_score > 20:  # Minimum threshold
            best_matches.append({
                'customer': customer.to_dict(),
                'total_score': total_score,
                'match_details': match_details
            })
    
    # Sort by score
    best_matches.sort(key=lambda x: x['total_score'], reverse=True)
    
    return best_matches[:5]  # Return top 5 matches

def main():
    st.title("👤 Customer Verification")
    st.markdown("---")
    
    # Sidebar for verification settings
    with st.sidebar:
        st.header("Verification Settings")
        
        search_method = st.selectbox(
            "Search Method",
            ["Exact Match", "Fuzzy Match", "AI-Enhanced"],
            help="Choose the customer matching algorithm"
        )
        
        match_threshold = st.slider(
            "Match Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.85,
            step=0.05,
            help="Minimum confidence for automatic verification"
        )
        
        st.markdown("---")
        st.info("💡 Verify customer information against internal records")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("🔍 Customer Search")
        
        # Customer search form
        with st.form("customer_search_form"):
            st.subheader("Enter Customer Information")
            
            customer_name = st.text_input(
                "Customer Name",
                value="John Doe",
                help="Enter full customer name"
            )
            
            account_number = st.text_input(
                "Account Number",
                value="ACC-2024-001234",
                help="Enter account number"
            )
            
            address = st.text_area(
                "Address",
                value="123 Main Street, City, State 12345",
                help="Enter customer address"
            )
            
            # Additional fields in expander
            with st.expander("Additional Information (Optional)"):
                phone = st.text_input("Phone Number", help="Customer phone number")
                email = st.text_input("Email Address", help="Customer email address")
            
            search_submitted = st.form_submit_button("🔍 Search Customer", type="primary")
            clear_form = st.form_submit_button("🗑️ Clear Form")
        
        if clear_form:
            st.rerun()
        
        # Manual verification section
        st.markdown("---")
        st.subheader("📋 Manual Verification")
        
        verification_notes = st.text_area(
            "Verification Notes",
            placeholder="Enter any additional verification notes or observations...",
            help="Document any manual verification steps or concerns"
        )
        
        manual_status = st.selectbox(
            "Manual Verification Status",
            ["Pending", "Verified", "Rejected", "Needs Review"],
            help="Set manual verification status"
        )
    
    with col2:
        st.header("🎯 Verification Results")
        
        if search_submitted and (customer_name or account_number):
            with st.spinner("Searching customer database..."):
                try:
                    # Perform customer verification
                    matches = verify_customer_advanced(
                        customer_name, account_number, address, phone, email
                    )
                    
                    if matches:
                        best_match = matches[0]
                        customer_data = best_match['customer']
                        confidence = best_match['total_score']
                        
                        # Determine verification status
                        if confidence >= 90:
                            status_class = "match-found"
                            status_text = "✅ Customer Match Found"
                            status_color = "success"
                        elif confidence >= 70:
                            status_class = "match-review"
                            status_text = "⚠️ Potential Match - Review Required"
                            status_color = "warning"
                        else:
                            status_class = "match-not-found"
                            status_text = "❌ Low Confidence Match"
                            status_color = "error"
                        
                        # Display verification result
                        st.markdown(f"""
                        <div class="verification-card {status_class}">
                            <h4>{status_text}</h4>
                            <p><strong>Confidence Score:</strong> {confidence:.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Customer information
                        st.subheader("📊 Customer Information")
                        
                        info_col1, info_col2 = st.columns(2)
                        
                        with info_col1:
                            st.write("**Customer ID:**", customer_data.get('customer_id', 'Unknown'))
                            st.write("**Name:**", customer_data.get('name', 'Unknown'))
                            st.write("**Account:**", customer_data.get('account_number', 'Unknown'))
                            st.write("**Status:**", customer_data.get('status', 'Unknown'))
                        
                        with info_col2:
                            st.write("**Balance:**", f"€{customer_data.get('balance', 0):,.2f}")
                            st.write("**Phone:**", customer_data.get('phone', 'Unknown'))
                            st.write("**Email:**", customer_data.get('email', 'Unknown'))
                            st.write("**Date Opened:**", customer_data.get('date_opened', 'Unknown'))
                        
                        # Address verification
                        st.subheader("🏠 Address Verification")
                        
                        registered_address = customer_data.get('address', 'Not available')
                        st.write("**Registered Address:**", registered_address)
                        
                        # Address match status
                        address_match = best_match['match_details'].get('address_match', 0)
                        if address_match >= 80:
                            st.success("✅ Address matches registered address")
                        elif address_match >= 50:
                            st.warning("⚠️ Partial address match - verify manually")
                        else:
                            st.error("❌ Address does not match - verification required")
                        
                        # Match details
                        with st.expander("🔍 Match Details"):
                            match_details = best_match['match_details']
                            
                            st.write("**Name Match:**", f"{match_details.get('name_match', 0):.1f}%")
                            st.write("**Account Match:**", f"{match_details.get('account_match', 0):.1f}%")
                            st.write("**Address Match:**", f"{match_details.get('address_match', 0):.1f}%")
                            
                            if match_details.get('phone_match', 0) > 0:
                                st.write("**Phone Match:**", f"{match_details.get('phone_match', 0):.1f}%")
                            if match_details.get('email_match', 0) > 0:
                                st.write("**Email Match:**", f"{match_details.get('email_match', 0):.1f}%")
                        
                        # Show alternative matches if any
                        if len(matches) > 1:
                            with st.expander("🔄 Alternative Matches"):
                                for i, match in enumerate(matches[1:], 1):
                                    alt_customer = match['customer']
                                    alt_confidence = match['total_score']
                                    
                                    st.write(f"**Match {i+1}:** {alt_customer.get('name', 'Unknown')} "
                                           f"({alt_customer.get('account_number', 'Unknown')}) - "
                                           f"{alt_confidence:.1f}% confidence")
                        
                        # Actions section
                        st.markdown("---")
                        st.subheader("⚡ Actions")
                        
                        action_col1, action_col2, action_col3 = st.columns(3)
                        
                        with action_col1:
                            if st.button("✅ Verify Customer", type="primary"):
                                st.success("Customer verified successfully!")
                                # Here you would update the database
                                
                        with action_col2:
                            if st.button("❌ Reject Customer"):
                                st.error("Customer verification rejected")
                                
                        with action_col3:
                            if st.button("📋 Flag for Review"):
                                st.warning("Customer flagged for manual review")
                    
                    else:
                        st.markdown("""
                        <div class="verification-card match-not-found">
                            <h4>❌ No Customer Match Found</h4>
                            <p>No customers found matching the provided criteria.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.subheader("🔍 Search Suggestions")
                        st.write("• Verify spelling of customer name")
                        st.write("• Check account number format")
                        st.write("• Try partial name search")
                        st.write("• Contact customer for verification")
                
                except Exception as e:
                    st.error(f"Error during customer verification: {str(e)}")
        
        else:
            st.info("👆 Enter customer information and click 'Search Customer' to begin verification")
            
            # Search tips
            st.subheader("💡 Search Tips")
            tips = [
                "• Use exact spelling for best results",
                "• Account numbers are case-sensitive", 
                "• Partial names may return multiple matches",
                "• Address matching uses fuzzy logic",
                "• Contact information helps with verification"
            ]
            
            for tip in tips:
                st.write(tip)
    
    # Customer Database Overview
    st.markdown("---")
    st.header("📊 Customer Database Overview")
    
    try:
        db = get_database()
        stats = db.get_dashboard_stats()
        
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            st.metric("Total Customers", stats['total_customers'])
        
        with stat_col2:
            st.metric("Active Customers", stats['active_customers'])
        
        with stat_col3:
            st.metric("Avg Balance", f"€{stats['avg_balance']:,.2f}")
        
        with stat_col4:
            verification_rate = 94.2  # Mock verification rate
            st.metric("Verification Rate", f"{verification_rate}%")
    
    except Exception as e:
        st.error(f"Error loading database stats: {str(e)}")
    
    # Recent Verifications
    st.subheader("📋 Recent Verifications")
    
    # Mock recent verification data
    recent_verifications = [
        {"Time": "10:35 AM", "Customer": "John Doe", "Status": "✅ Verified", "Confidence": "96.8%"},
        {"Time": "10:30 AM", "Customer": "Jane Smith", "Status": "✅ Verified", "Confidence": "94.2%"},
        {"Time": "10:25 AM", "Customer": "Unknown Customer", "Status": "❌ Rejected", "Confidence": "45.1%"},
        {"Time": "10:20 AM", "Customer": "Robert Johnson", "Status": "📋 Review", "Confidence": "78.3%"},
    ]
    
    df_verifications = pd.DataFrame(recent_verifications)
    st.dataframe(df_verifications, use_container_width=True)

if __name__ == "__main__":
    main()

