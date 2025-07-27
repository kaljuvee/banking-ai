import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Banking BPO Automation",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .process-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f4e79;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    .status-active {
        background-color: #28a745;
        color: white;
    }
    .status-pending {
        background-color: #ffc107;
        color: black;
    }
    .status-completed {
        background-color: #6c757d;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Main header
    st.markdown('<h1 class="main-header">🏦 Banking BPO Automation System</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    st.sidebar.markdown("---")
    
    # Process overview in sidebar
    st.sidebar.subheader("Process Flow")
    processes = [
        "📄 Document Processing",
        "👤 Customer Verification", 
        "💳 Account Management",
        "💰 Payment Processing",
        "📋 Case Management"
    ]
    
    for process in processes:
        st.sidebar.markdown(f"• {process}")
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 Navigate using the pages in the sidebar to access different workflow steps.")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("System Overview")
        st.markdown("""
        This Banking BPO (Business Process Outsourcing) Automation System streamlines the processing 
        of customer requests, from initial document receipt through final payment processing.
        """)
        
        # Process flow cards
        st.subheader("Current Process Flow")
        
        # Document Processing Card
        st.markdown("""
        <div class="process-card">
            <h4>📄 Document Processing</h4>
            <p>Automated OCR and document analysis for incoming customer requests from courts.</p>
            <span class="status-badge status-active">Active</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Customer Verification Card
        st.markdown("""
        <div class="process-card">
            <h4>👤 Customer Verification</h4>
            <p>Automated customer lookup and verification against internal records.</p>
            <span class="status-badge status-pending">Ready</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Account Management Card
        st.markdown("""
        <div class="process-card">
            <h4>💳 Account Management</h4>
            <p>Account operations including overdraft cancellation and account freezing.</p>
            <span class="status-badge status-pending">Ready</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Payment Processing Card
        st.markdown("""
        <div class="process-card">
            <h4>💰 Payment Processing</h4>
            <p>Automated payment processing and creditor notifications.</p>
            <span class="status-badge status-pending">Ready</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Case Management Card
        st.markdown("""
        <div class="process-card">
            <h4>📋 Case Management</h4>
            <p>Ticket tracking and case closure management.</p>
            <span class="status-badge status-pending">Ready</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.header("System Stats")
        
        # Mock statistics
        st.metric("Active Cases", "127", "12")
        st.metric("Processed Today", "45", "8")
        st.metric("Success Rate", "94.2%", "2.1%")
        st.metric("Avg Processing Time", "4.2 min", "-0.8 min")
        
        st.markdown("---")
        
        st.subheader("Recent Activity")
        st.markdown("""
        • **10:30 AM** - Document processed: Case #2024-001
        • **10:25 AM** - Customer verified: John Doe
        • **10:20 AM** - Payment sent: €1,250.00
        • **10:15 AM** - Case closed: #2024-002
        • **10:10 AM** - New document received
        """)
        
        st.markdown("---")
        
        st.subheader("Quick Actions")
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.rerun()
        
        if st.button("📊 Generate Report", use_container_width=True):
            st.info("Report generation feature coming soon!")
        
        if st.button("⚙️ System Settings", use_container_width=True):
            st.info("Settings panel coming soon!")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        Banking BPO Automation System v1.0 | Built with Streamlit & OpenAI
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

