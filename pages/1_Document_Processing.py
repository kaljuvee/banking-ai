import streamlit as st
import os
import pandas as pd
from datetime import datetime
import base64
from utils.pdf_generator import BankingDocumentGenerator, generate_sample_pdfs
from utils.ai_processor import process_uploaded_document, verify_customer_against_database, generate_case_summary
from utils.database import get_database, get_customer_data
from utils.document_processor import get_document_processor

st.set_page_config(
    page_title="Document Processing",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .upload-section {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .sample-doc-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }
    .processing-result {
        background-color: #e8f5e8;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .confidence-high { color: #28a745; font-weight: bold; }
    .confidence-medium { color: #ffc107; font-weight: bold; }
    .confidence-low { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def get_confidence_class(score):
    """Get CSS class based on confidence score"""
    if score >= 90:
        return "confidence-high"
    elif score >= 70:
        return "confidence-medium"
    else:
        return "confidence-low"

def create_download_link(file_path, filename):
    """Create a download link for a file"""
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            bytes_data = f.read()
        b64 = base64.b64encode(bytes_data).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📥 Download {filename}</a>'
        return href
    return "File not found"

def main():
    st.title("📄 Document Processing")
    st.markdown("---")
    
    # Sidebar for processing options
    with st.sidebar:
        st.header("Document Processing Options")
        
        processing_mode = st.selectbox(
            "Processing Mode",
            ["OCR + AI Analysis", "OCR Only", "AI Analysis Only"],
            help="Choose how to process uploaded documents"
        )
        
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.80,
            step=0.05,
            help="Minimum confidence score for automatic processing"
        )
        
        st.markdown("---")
        st.info("💡 Upload court documents (PDF/Image) for automated processing")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📁 Upload Court Documents")
        st.markdown("**Supported formats:** PDF, PNG, JPG, JPEG")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            help="Upload court documents for processing"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Process button
            if st.button("🔄 Process Document", type="primary"):
                with st.spinner("Processing document..."):
                    try:
                        # Determine file type
                        file_type = uploaded_file.name.split('.')[-1].lower()
                        
                        # Process the document
                        document_info = process_uploaded_document(uploaded_file, file_type)
                        
                        # Store in session state for display
                        st.session_state['processed_document'] = document_info
                        st.session_state['uploaded_filename'] = uploaded_file.name
                        
                        st.success("✅ Document processed successfully!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error processing document: {str(e)}")
        
        # Sample Documents Section
        st.markdown("---")
        st.header("📚 Sample Documents")
        st.markdown("Download sample court documents for testing:")
        
        # Generate sample documents if they don't exist
        sample_dir = "data/sample_documents"
        if not os.path.exists(sample_dir) or len(os.listdir(sample_dir)) == 0:
            with st.spinner("Generating sample documents..."):
                try:
                    docs = generate_sample_pdfs()
                    st.success(f"✅ Generated {len(docs)} sample documents")
                except Exception as e:
                    st.error(f"❌ Error generating samples: {str(e)}")
                    docs = []
        else:
            # List existing sample documents
            docs = []
            for filename in os.listdir(sample_dir):
                if filename.endswith('.pdf'):
                    file_path = os.path.join(sample_dir, filename)
                    doc_type = filename.replace('.pdf', '').replace('_', ' ').title()
                    docs.append((doc_type, file_path))
        
        # Display sample documents
        if docs:
            for i, (doc_type, file_path) in enumerate(docs):
                filename = os.path.basename(file_path)
                
                with st.container():
                    st.markdown(f"""
                    <div class="sample-doc-card">
                        <h4>📄 {doc_type}</h4>
                        <p><strong>File:</strong> {filename}</p>
                        {create_download_link(file_path, filename)}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add Process button for each document
                    col_download, col_process = st.columns([1, 1])
                    
                    with col_process:
                        if st.button(f"🔄 Process {filename}", key=f"process_{i}", help="Extract all information from this document"):
                            with st.spinner(f"Processing {filename}..."):
                                try:
                                    # Process the document using enhanced processor
                                    processor = get_document_processor()
                                    result = processor.process_sample_document(file_path, filename)
                                    
                                    # Store result in session state
                                    st.session_state[f'processed_sample_{i}'] = result
                                    st.session_state['last_processed_sample'] = i
                                    
                                    st.success(f"✅ {filename} processed successfully!")
                                    st.rerun()
                                    
                                except Exception as e:
                                    st.error(f"❌ Error processing {filename}: {str(e)}")
                    
                    # Display processing results if available
                    if f'processed_sample_{i}' in st.session_state:
                        result = st.session_state[f'processed_sample_{i}']
                        
                        with st.expander(f"📊 Processing Results - {filename}", expanded=False):
                            if result.get('status') == 'processed':
                                # Display summary
                                processor = get_document_processor()
                                summary = processor.get_document_summary(result)
                                st.markdown(summary)
                                
                                # Display detailed extraction
                                st.subheader("📋 Detailed Extraction")
                                
                                # Create columns for better display
                                detail_col1, detail_col2 = st.columns(2)
                                
                                with detail_col1:
                                    st.write("**Document Type:**", result.get('document_type', 'Unknown'))
                                    st.write("**Case Number:**", result.get('case_number', 'Not found'))
                                    st.write("**Court:**", result.get('court_name', 'Not found'))
                                    st.write("**County:**", result.get('county', 'Not found'))
                                
                                with detail_col2:
                                    customer = result.get('defendant_customer') or result.get('account_holder') or result.get('customer_name')
                                    st.write("**Customer:**", customer or 'Not found')
                                    
                                    amount = result.get('garnishment_amount') or result.get('amount_to_withhold') or result.get('freeze_amount')
                                    if amount:
                                        st.write("**Amount:**", f"€{amount:,.2f}")
                                    else:
                                        st.write("**Amount:**", 'Not specified')
                                    
                                    creditor = result.get('plaintiff_creditor') or result.get('creditor_name')
                                    st.write("**Creditor:**", creditor or 'Not found')
                                    
                                    st.write("**Confidence:**", f"{result.get('confidence_score', 0)}%")
                                
                                # Show all extracted fields
                                with st.expander("🔍 All Extracted Fields"):
                                    # Filter out system fields
                                    display_fields = {k: v for k, v in result.items() 
                                                    if k not in ['filename', 'status', 'raw_text', 'processing_timestamp'] and v is not None}
                                    
                                    for key, value in display_fields.items():
                                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                            
                            elif result.get('status') == 'error':
                                st.error(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
                            
                            else:
                                st.warning("⚠️ Partial processing - some information may be incomplete")
                                st.write("**Raw Response:**", result.get('raw_response', 'No response'))
        
        # Bulk processing option
        st.markdown("---")
        st.subheader("⚡ Bulk Processing")
        
        if st.button("🔄 Process All Sample Documents", type="primary"):
            with st.spinner("Processing all sample documents..."):
                try:
                    processor = get_document_processor()
                    results = processor.process_all_sample_documents()
                    
                    # Store results
                    st.session_state['bulk_processing_results'] = results
                    
                    st.success(f"✅ Processed {len(results)} documents successfully!")
                    
                    # Display summary
                    successful = len([r for r in results if r.get('status') == 'processed'])
                    st.info(f"📊 Processing Summary: {successful}/{len(results)} documents processed successfully")
                    
                except Exception as e:
                    st.error(f"❌ Bulk processing failed: {str(e)}")
        
        # Display bulk processing results
        if 'bulk_processing_results' in st.session_state:
            with st.expander("📊 Bulk Processing Results", expanded=False):
                results = st.session_state['bulk_processing_results']
                
                for result in results:
                    filename = result.get('filename', 'Unknown')
                    status = result.get('status', 'Unknown')
                    confidence = result.get('confidence_score', 0)
                    
                    if status == 'processed':
                        st.success(f"✅ {filename} - {confidence}% confidence")
                    elif status == 'error':
                        st.error(f"❌ {filename} - {result.get('error', 'Unknown error')}")
                    else:
                        st.warning(f"⚠️ {filename} - Partial success")
    
    with col2:
        st.header("🎯 Processing Results")
        
        # Display processing results if available
        if 'processed_document' in st.session_state:
            doc_info = st.session_state['processed_document']
            filename = st.session_state.get('uploaded_filename', 'Unknown')
            
            st.markdown(f"""
            <div class="processing-result">
                <h4>✅ Document Processed: {filename}</h4>
                <p><strong>Processing Time:</strong> {doc_info.get('processing_timestamp', 'Unknown')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Document Classification
            st.subheader("📋 Document Classification")
            doc_type = doc_info.get('document_type', 'Unknown')
            confidence = doc_info.get('confidence_score', 0)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Document Type", doc_type.replace('_', ' ').title())
            with col_b:
                confidence_class = get_confidence_class(confidence)
                st.markdown(f"**Confidence:** <span class='{confidence_class}'>{confidence}%</span>", 
                           unsafe_allow_html=True)
            
            # Extracted Information
            st.subheader("📊 Extracted Information")
            
            info_cols = st.columns(2)
            with info_cols[0]:
                st.write("**Customer Name:**", doc_info.get('customer_name', 'Not found'))
                st.write("**Account Number:**", doc_info.get('account_number', 'Not found'))
                st.write("**Case Number:**", doc_info.get('case_number', 'Not found'))
            
            with info_cols[1]:
                st.write("**Creditor:**", doc_info.get('creditor_name', 'Not found'))
                st.write("**Amount:**", f"${doc_info.get('amount', 0):,.2f}" if doc_info.get('amount') else 'Not specified')
                st.write("**Date Filed:**", doc_info.get('date_filed', 'Not found'))
            
            # Customer Verification
            if doc_info.get('customer_name') or doc_info.get('account_number'):
                st.subheader("👤 Customer Verification")
                
                # Get customer database
                customer_db = get_customer_data()
                
                # Verify customer
                verification_result = verify_customer_against_database(doc_info, customer_db)
                
                if verification_result['match_found']:
                    customer_data = verification_result['customer_data']
                    st.success(f"✅ Customer verified with {verification_result['confidence']}% confidence")
                    
                    # Display customer details
                    cust_cols = st.columns(2)
                    with cust_cols[0]:
                        st.write("**Name:**", customer_data.get('name', 'Unknown'))
                        st.write("**Account:**", customer_data.get('account_number', 'Unknown'))
                        st.write("**Status:**", customer_data.get('status', 'Unknown'))
                    
                    with cust_cols[1]:
                        st.write("**Balance:**", f"${customer_data.get('balance', 0):,.2f}")
                        st.write("**Phone:**", customer_data.get('phone', 'Unknown'))
                        st.write("**Email:**", customer_data.get('email', 'Unknown'))
                else:
                    st.warning("⚠️ Customer not found in database - manual verification required")
            
            # Document Summary
            st.subheader("📝 Processing Summary")
            summary = doc_info.get('summary', 'No summary available')
            st.write(summary)
            
            # Next Steps
            st.subheader("⚡ Recommended Actions")
            
            if confidence >= 90:
                st.success("🟢 **High Confidence** - Proceed to customer verification")
                if st.button("➡️ Proceed to Customer Verification"):
                    st.switch_page("pages/2_Customer_Verification.py")
            elif confidence >= 70:
                st.warning("🟡 **Medium Confidence** - Manual review recommended")
                st.button("👁️ Flag for Manual Review")
            else:
                st.error("🔴 **Low Confidence** - Manual processing required")
                st.button("✋ Require Manual Processing")
            
            # Save processed document
            if st.button("💾 Save to Case File"):
                try:
                    db = get_database()
                    doc_id = db.save_processed_document({
                        'filename': filename,
                        'document_type': doc_type,
                        'customer_name': doc_info.get('customer_name', ''),
                        'confidence_score': confidence,
                        'status': 'Processed',
                        'extracted_data': {
                            'amount': doc_info.get('amount', 0),
                            'case_number': doc_info.get('case_number', ''),
                            'creditor': doc_info.get('creditor_name', '')
                        }
                    })
                    st.success(f"✅ Document saved with ID: {doc_id}")
                except Exception as e:
                    st.error(f"❌ Error saving document: {str(e)}")
        
        else:
            st.info("👆 Please upload a document to see processing results")
            
            # Processing Capabilities
            st.subheader("🔧 Processing Capabilities")
            capabilities = [
                "✅ OCR text extraction from PDFs and images",
                "✅ AI-powered information extraction",
                "✅ Customer detail identification",
                "✅ Amount and case number extraction",
                "✅ Document type classification",
                "✅ Confidence scoring",
                "✅ Data validation and verification"
            ]
            
            for capability in capabilities:
                st.write(capability)
    
    # Recent Processing History
    st.markdown("---")
    st.header("📚 Recent Processing History")
    
    try:
        db = get_database()
        processed_docs = db.get_processed_documents()
        
        if processed_docs:
            # Create DataFrame for display
            history_data = []
            for doc in processed_docs[-10:]:  # Show last 10 documents
                history_data.append({
                    'Time': doc.get('processing_date', '').split('T')[0] if 'T' in doc.get('processing_date', '') else doc.get('processing_date', ''),
                    'Document': doc.get('filename', 'Unknown'),
                    'Status': '✅ Processed' if doc.get('status') == 'Processed' else '⚠️ Review',
                    'Confidence': f"{doc.get('confidence_score', 0):.1f}%"
                })
            
            df = pd.DataFrame(history_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No processing history available")
    
    except Exception as e:
        st.error(f"Error loading processing history: {str(e)}")

if __name__ == "__main__":
    main()

