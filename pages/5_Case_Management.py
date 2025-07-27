import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.database import get_database, get_case_data, create_new_case
import random
import json

st.set_page_config(
    page_title="Case Management",
    page_icon="📋",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .case-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #6f42c1;
        margin: 1rem 0;
    }
    .case-active {
        border-left-color: #28a745;
        background-color: #d4edda;
    }
    .case-review {
        border-left-color: #ffc107;
        background-color: #fff3cd;
    }
    .case-completed {
        border-left-color: #6c757d;
        background-color: #e2e3e5;
    }
    .case-processing {
        border-left-color: #007bff;
        background-color: #cce5ff;
    }
    .timeline-item {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 3px solid #007bff;
    }
    .workflow-stage {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    .stage-document { background-color: #e3f2fd; color: #1976d2; }
    .stage-verification { background-color: #fff3e0; color: #f57c00; }
    .stage-account { background-color: #e8f5e8; color: #388e3c; }
    .stage-payment { background-color: #fce4ec; color: #c2185b; }
    .stage-completed { background-color: #f3e5f5; color: #7b1fa2; }
</style>
""", unsafe_allow_html=True)

def get_workflow_stage_class(stage):
    """Get CSS class for workflow stage"""
    stage_classes = {
        'document_processing': 'stage-document',
        'customer_verification': 'stage-verification',
        'account_management': 'stage-account',
        'payment_processing': 'stage-payment',
        'completed': 'stage-completed'
    }
    return stage_classes.get(stage, 'stage-document')

def get_case_status_class(status):
    """Get CSS class for case status"""
    if status == 'Active':
        return 'case-active'
    elif status == 'Under Review':
        return 'case-review'
    elif status == 'Completed':
        return 'case-completed'
    elif status == 'Payment Processing':
        return 'case-processing'
    else:
        return 'case-card'

def generate_case_timeline(case_data):
    """Generate timeline events for a case"""
    timeline = []
    
    # Document processing
    timeline.append({
        'date': case_data['date_created'],
        'event': 'Case Created',
        'description': f"Case {case_data['case_id']} created for {case_data['customer_name']}",
        'stage': 'document_processing'
    })
    
    # Add mock timeline events based on case status
    if case_data['workflow_stage'] in ['customer_verification', 'account_management', 'payment_processing', 'completed']:
        timeline.append({
            'date': (datetime.strptime(case_data['date_created'], '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d'),
            'event': 'Document Processed',
            'description': 'Court documents processed and information extracted',
            'stage': 'document_processing'
        })
    
    if case_data['workflow_stage'] in ['account_management', 'payment_processing', 'completed']:
        timeline.append({
            'date': (datetime.strptime(case_data['date_created'], '%Y-%m-%d') + timedelta(days=2)).strftime('%Y-%m-%d'),
            'event': 'Customer Verified',
            'description': 'Customer identity and account verified',
            'stage': 'customer_verification'
        })
    
    if case_data['workflow_stage'] in ['payment_processing', 'completed']:
        timeline.append({
            'date': (datetime.strptime(case_data['date_created'], '%Y-%m-%d') + timedelta(days=3)).strftime('%Y-%m-%d'),
            'event': 'Account Frozen',
            'description': 'Customer account frozen per court order',
            'stage': 'account_management'
        })
    
    if case_data['workflow_stage'] == 'completed':
        timeline.append({
            'date': case_data['last_updated'],
            'event': 'Payment Processed',
            'description': f"Payment of €{case_data['garnishment_amount']:,.2f} sent to creditor",
            'stage': 'payment_processing'
        })
        
        timeline.append({
            'date': case_data['last_updated'],
            'event': 'Case Closed',
            'description': 'Case completed successfully',
            'stage': 'completed'
        })
    
    return timeline

def main():
    st.title("📋 Case Management")
    st.markdown("---")
    
    # Sidebar for case filters and actions
    with st.sidebar:
        st.header("Case Filters")
        
        status_filter = st.multiselect(
            "Filter by Status",
            ["Active", "Under Review", "Payment Processing", "Completed"],
            default=["Active", "Under Review", "Payment Processing"],
            help="Filter cases by status"
        )
        
        workflow_filter = st.selectbox(
            "Filter by Workflow Stage",
            ["All", "Document Processing", "Customer Verification", "Account Management", "Payment Processing", "Completed"],
            help="Filter by workflow stage"
        )
        
        date_range = st.date_input(
            "Date Range",
            value=[datetime.now() - timedelta(days=30), datetime.now()],
            help="Filter cases by date range"
        )
        
        st.markdown("---")
        
        # Quick actions
        st.header("Quick Actions")
        
        if st.button("➕ Create New Case", use_container_width=True):
            st.session_state.show_new_case_form = True
        
        if st.button("📊 Generate Report", use_container_width=True):
            st.info("📊 Report generation feature coming soon!")
        
        if st.button("📤 Export Cases", use_container_width=True):
            st.info("📤 Export feature coming soon!")
        
        st.markdown("---")
        st.info("💡 Track and manage customer cases through the complete workflow")
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Active Cases", "📊 Case Details", "📈 Analytics", "⚙️ Bulk Operations"])
    
    with tab1:
        st.header("📋 Active Cases Overview")
        
        try:
            # Load cases from database
            db = get_database()
            cases = db.get_cases()
            
            # Apply filters
            filtered_cases = []
            for case in cases:
                # Status filter
                if status_filter and case['status'] not in status_filter:
                    continue
                
                # Workflow filter
                if workflow_filter != "All":
                    workflow_map = {
                        "Document Processing": "document_processing",
                        "Customer Verification": "customer_verification", 
                        "Account Management": "account_management",
                        "Payment Processing": "payment_processing",
                        "Completed": "completed"
                    }
                    if case['workflow_stage'] != workflow_map.get(workflow_filter):
                        continue
                
                filtered_cases.append(case)
            
            # Display cases
            if filtered_cases:
                for case in filtered_cases:
                    status_class = get_case_status_class(case['status'])
                    stage_class = get_workflow_stage_class(case['workflow_stage'])
                    
                    with st.container():
                        st.markdown(f"""
                        <div class="{status_class}">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <h4>📋 {case['case_id']} - {case['customer_name']}</h4>
                                    <p><strong>Creditor:</strong> {case['creditor']} | <strong>Amount:</strong> €{case['garnishment_amount']:,.2f}</p>
                                    <p><strong>Status:</strong> {case['status']} | <strong>Created:</strong> {case['date_created']}</p>
                                </div>
                                <div>
                                    <span class="workflow-stage {stage_class}">
                                        {case['workflow_stage'].replace('_', ' ').title()}
                                    </span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Case actions
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            if st.button(f"👁️ View Details", key=f"view_{case['case_id']}"):
                                st.session_state.selected_case = case['case_id']
                        
                        with col2:
                            if st.button(f"✏️ Edit Case", key=f"edit_{case['case_id']}"):
                                st.session_state.edit_case = case['case_id']
                        
                        with col3:
                            if st.button(f"⚡ Advance Stage", key=f"advance_{case['case_id']}"):
                                # Advance workflow stage
                                stage_progression = {
                                    'document_processing': 'customer_verification',
                                    'customer_verification': 'account_management',
                                    'account_management': 'payment_processing',
                                    'payment_processing': 'completed'
                                }
                                
                                new_stage = stage_progression.get(case['workflow_stage'])
                                if new_stage:
                                    db.update_case(case['case_id'], {'workflow_stage': new_stage})
                                    st.success(f"✅ Case {case['case_id']} advanced to {new_stage.replace('_', ' ').title()}")
                                    st.rerun()
                        
                        with col4:
                            if case['workflow_stage'] != 'completed':
                                if st.button(f"✅ Close Case", key=f"close_{case['case_id']}"):
                                    db.update_case(case['case_id'], {
                                        'status': 'Completed',
                                        'workflow_stage': 'completed'
                                    })
                                    st.success(f"✅ Case {case['case_id']} closed successfully")
                                    st.rerun()
                        
                        st.markdown("---")
            
            else:
                st.info("No cases match the current filters")
        
        except Exception as e:
            st.error(f"Error loading cases: {str(e)}")
    
    with tab2:
        st.header("📊 Case Details")
        
        # Case selection
        if 'selected_case' in st.session_state:
            try:
                db = get_database()
                case = db.get_case_by_id(st.session_state.selected_case)
                
                if case:
                    # Case overview
                    st.subheader(f"📋 Case {case['case_id']}")
                    
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.write("**Customer:**", case['customer_name'])
                        st.write("**Case Number:**", case['case_number'])
                        st.write("**Creditor:**", case['creditor'])
                        st.write("**Status:**", case['status'])
                    
                    with detail_col2:
                        st.write("**Amount Owed:**", f"€{case['amount_owed']:,.2f}")
                        st.write("**Garnishment Amount:**", f"€{case['garnishment_amount']:,.2f}")
                        st.write("**Date Created:**", case['date_created'])
                        st.write("**Last Updated:**", case['last_updated'])
                    
                    # Workflow progress
                    st.subheader("🔄 Workflow Progress")
                    
                    workflow_stages = [
                        ('document_processing', 'Document Processing'),
                        ('customer_verification', 'Customer Verification'),
                        ('account_management', 'Account Management'),
                        ('payment_processing', 'Payment Processing'),
                        ('completed', 'Completed')
                    ]
                    
                    current_stage = case['workflow_stage']
                    current_index = next((i for i, (stage, _) in enumerate(workflow_stages) if stage == current_stage), 0)
                    
                    progress_cols = st.columns(len(workflow_stages))
                    
                    for i, (stage, label) in enumerate(workflow_stages):
                        with progress_cols[i]:
                            if i <= current_index:
                                st.success(f"✅ {label}")
                            else:
                                st.info(f"⏳ {label}")
                    
                    # Case timeline
                    st.subheader("📅 Case Timeline")
                    
                    timeline = generate_case_timeline(case)
                    
                    for event in timeline:
                        st.markdown(f"""
                        <div class="timeline-item">
                            <p><strong>{event['date']}</strong> - {event['event']}</p>
                            <p>{event['description']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Documents
                    st.subheader("📄 Associated Documents")
                    
                    if case.get('documents'):
                        for doc in case['documents']:
                            st.write(f"📄 {doc}")
                    else:
                        st.info("No documents associated with this case")
                    
                    # Notes
                    st.subheader("📝 Case Notes")
                    
                    current_notes = case.get('notes', '')
                    new_notes = st.text_area("Add Notes", value=current_notes, height=100)
                    
                    if st.button("💾 Save Notes"):
                        db.update_case(case['case_id'], {'notes': new_notes})
                        st.success("✅ Notes saved successfully")
                        st.rerun()
                
                else:
                    st.error("Case not found")
            
            except Exception as e:
                st.error(f"Error loading case details: {str(e)}")
        
        else:
            st.info("👆 Select a case from the Active Cases tab to view details")
    
    with tab3:
        st.header("📈 Case Analytics")
        
        try:
            db = get_database()
            cases = db.get_cases()
            
            # Case statistics
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            
            with stat_col1:
                st.metric("Total Cases", len(cases))
            
            with stat_col2:
                active_cases = len([c for c in cases if c['status'] == 'Active'])
                st.metric("Active Cases", active_cases)
            
            with stat_col3:
                completed_cases = len([c for c in cases if c['workflow_stage'] == 'completed'])
                completion_rate = (completed_cases / len(cases) * 100) if cases else 0
                st.metric("Completion Rate", f"{completion_rate:.1f}%")
            
            with stat_col4:
                total_amount = sum([c['garnishment_amount'] for c in cases])
                st.metric("Total Amount", f"€{total_amount:,.2f}")
            
            # Case status distribution
            st.subheader("📊 Case Status Distribution")
            
            status_counts = {}
            for case in cases:
                status = case['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if status_counts:
                status_df = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
                st.bar_chart(status_df.set_index('Status'))
            
            # Workflow stage distribution
            st.subheader("🔄 Workflow Stage Distribution")
            
            stage_counts = {}
            for case in cases:
                stage = case['workflow_stage'].replace('_', ' ').title()
                stage_counts[stage] = stage_counts.get(stage, 0) + 1
            
            if stage_counts:
                stage_df = pd.DataFrame(list(stage_counts.items()), columns=['Stage', 'Count'])
                st.bar_chart(stage_df.set_index('Stage'))
            
            # Recent activity
            st.subheader("📅 Recent Activity")
            
            # Sort cases by last updated
            recent_cases = sorted(cases, key=lambda x: x['last_updated'], reverse=True)[:5]
            
            activity_data = []
            for case in recent_cases:
                activity_data.append({
                    'Date': case['last_updated'],
                    'Case ID': case['case_id'],
                    'Customer': case['customer_name'],
                    'Status': case['status'],
                    'Stage': case['workflow_stage'].replace('_', ' ').title()
                })
            
            if activity_data:
                activity_df = pd.DataFrame(activity_data)
                st.dataframe(activity_df, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error loading analytics: {str(e)}")
    
    with tab4:
        st.header("⚙️ Bulk Operations")
        
        # Bulk case selection
        st.subheader("📋 Select Cases for Bulk Operations")
        
        try:
            db = get_database()
            cases = db.get_cases()
            
            # Create case selection
            case_options = [f"{case['case_id']} - {case['customer_name']}" for case in cases]
            selected_cases = st.multiselect(
                "Select Cases",
                case_options,
                help="Select multiple cases for bulk operations"
            )
            
            if selected_cases:
                st.write(f"Selected {len(selected_cases)} cases")
                
                # Bulk operations
                st.subheader("⚡ Bulk Operations")
                
                bulk_col1, bulk_col2 = st.columns(2)
                
                with bulk_col1:
                    # Bulk status update
                    new_status = st.selectbox(
                        "Update Status",
                        ["Active", "Under Review", "Payment Processing", "Completed"],
                        help="Update status for selected cases"
                    )
                    
                    if st.button("📝 Update Status", use_container_width=True):
                        for case_option in selected_cases:
                            case_id = case_option.split(' - ')[0]
                            db.update_case(case_id, {'status': new_status})
                        
                        st.success(f"✅ Updated status to '{new_status}' for {len(selected_cases)} cases")
                        st.rerun()
                
                with bulk_col2:
                    # Bulk workflow advancement
                    if st.button("⚡ Advance All Stages", use_container_width=True):
                        stage_progression = {
                            'document_processing': 'customer_verification',
                            'customer_verification': 'account_management',
                            'account_management': 'payment_processing',
                            'payment_processing': 'completed'
                        }
                        
                        updated_count = 0
                        for case_option in selected_cases:
                            case_id = case_option.split(' - ')[0]
                            case = db.get_case_by_id(case_id)
                            
                            if case:
                                new_stage = stage_progression.get(case['workflow_stage'])
                                if new_stage:
                                    db.update_case(case_id, {'workflow_stage': new_stage})
                                    updated_count += 1
                        
                        st.success(f"✅ Advanced {updated_count} cases to next workflow stage")
                        st.rerun()
                
                # Bulk notes
                st.subheader("📝 Add Bulk Notes")
                
                bulk_notes = st.text_area(
                    "Notes to add to all selected cases",
                    placeholder="Enter notes to be added to all selected cases...",
                    help="These notes will be appended to existing notes"
                )
                
                if st.button("💾 Add Notes to Selected Cases") and bulk_notes:
                    for case_option in selected_cases:
                        case_id = case_option.split(' - ')[0]
                        case = db.get_case_by_id(case_id)
                        
                        if case:
                            existing_notes = case.get('notes', '')
                            new_notes = f"{existing_notes}\n\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {bulk_notes}" if existing_notes else bulk_notes
                            db.update_case(case_id, {'notes': new_notes})
                    
                    st.success(f"✅ Added notes to {len(selected_cases)} cases")
                    st.rerun()
            
            else:
                st.info("👆 Select cases to perform bulk operations")
        
        except Exception as e:
            st.error(f"Error in bulk operations: {str(e)}")
    
    # New case form (if triggered)
    if st.session_state.get('show_new_case_form', False):
        with st.expander("➕ Create New Case", expanded=True):
            with st.form("new_case_form"):
                st.subheader("📋 New Case Information")
                
                new_customer_name = st.text_input("Customer Name", help="Enter customer full name")
                new_case_number = st.text_input("Court Case Number", help="Enter court case number")
                new_creditor = st.text_input("Creditor Name", help="Enter creditor name")
                new_amount_owed = st.number_input("Amount Owed (€)", min_value=0.0, step=100.0)
                new_garnishment_amount = st.number_input("Garnishment Amount (€)", min_value=0.0, step=50.0)
                
                if st.form_submit_button("✅ Create Case", type="primary"):
                    try:
                        # Get customer ID (simplified - in real app would do proper lookup)
                        customer_id = f"CUST-{random.randint(100, 999)}"
                        
                        case_data = {
                            'customer_id': customer_id,
                            'customer_name': new_customer_name,
                            'case_number': new_case_number,
                            'creditor': new_creditor,
                            'amount_owed': new_amount_owed,
                            'garnishment_amount': new_garnishment_amount,
                            'status': 'Active',
                            'workflow_stage': 'document_processing',
                            'documents': [],
                            'notes': 'Case created via web interface'
                        }
                        
                        db = get_database()
                        case_id = db.create_case(case_data)
                        
                        st.success(f"✅ Case {case_id} created successfully!")
                        st.session_state.show_new_case_form = False
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"Error creating case: {str(e)}")

if __name__ == "__main__":
    main()

