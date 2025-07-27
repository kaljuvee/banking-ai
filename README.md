# Banking AI - BPO Automation System

A proof of concept Streamlit application to automate banking Business Process Outsourcing (BPO) workflows, including document processing, customer verification, account management, and payment handling using OpenAI and Langchain for AI-powered processing.

## 🏗️ Architecture

The application follows a multi-page Streamlit architecture with the following components:

- **Frontend**: Streamlit multi-page application
- **AI Processing**: OpenAI GPT-4 and Vision API integration via Langchain
- **Data Management**: File-based database using CSV and JSON
- **Document Processing**: OCR and AI-powered information extraction

## 📋 Features

### 1. Document Processing (`pages/1_Document_Processing.py`)
- **OCR Text Extraction**: Extract text from PDFs and images
- **AI-Powered Analysis**: Classify documents and extract structured information
- **Document Validation**: Validate extracted information with confidence scoring
- **Support for Multiple Formats**: PDF, PNG, JPG, JPEG

### 2. Customer Verification (`pages/2_Customer_Verification.py`)
- **Customer Lookup**: Search customers by name, account number, or address
- **Fuzzy Matching**: AI-enhanced search with confidence scoring
- **Address Verification**: Compare extracted vs. registered addresses
- **Verification Workflow**: Approve, reject, or flag for manual review

### 3. Account Management (`pages/3_Account_Management.py`)
- **Balance Verification**: Check account balance and payment capability
- **Account Operations**: Freeze accounts, cancel overdraft protection
- **Product Management**: Manage customer banking products
- **Transaction History**: View recent account activity

### 4. Payment Processing (`pages/4_Payment_Processing.py`)
- **Automated Payments**: Process court-ordered garnishment payments
- **Multi-step Validation**: Authorization, validation, processing, confirmation
- **Creditor Management**: Handle creditor information and notifications
- **Payment Tracking**: Transaction history and status monitoring

### 5. Case Management (`pages/5_Case_Management.py`)
- **Case Tracking**: Monitor case progress through workflow stages
- **Timeline Management**: Track all case activities and status changes
- **Bulk Operations**: Handle multiple cases simultaneously
- **Reporting**: Generate case statistics and activity reports

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11+
- OpenAI API key
- Git

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/kaljuvee/banking-ai.git
   cd banking-ai
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_API_BASE=https://api.openai.com/v1
   ```

4. **Initialize sample data**:
   ```bash
   python -c "from utils.database import get_database; get_database()"
   ```

5. **Run the application**:
   ```bash
   streamlit run main.py
   ```

## 📁 Project Structure

```
banking-ai/
├── main.py                     # Main Streamlit application
├── pages/                      # Streamlit pages
│   ├── 1_Document_Processing.py
│   ├── 2_Customer_Verification.py
│   ├── 3_Account_Management.py
│   ├── 4_Payment_Processing.py
│   └── 5_Case_Management.py
├── utils/                      # Utility modules
│   ├── ai_processor.py         # OpenAI/Langchain integration
│   └── database.py             # Data management utilities
├── data/                       # Data files
│   ├── customers.csv           # Customer database
│   ├── cases.json              # Case management data
│   └── transactions.csv        # Transaction history
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in repo)
├── WORKFLOW_ANALYSIS.md        # Workflow documentation
└── README.md                   # This file
```

## 🔄 Workflow Process

The application automates the following banking BPO workflow:

1. **Document Receipt**: Court documents received via postal mail
2. **Document Processing**: OCR extraction and AI analysis
3. **Customer Verification**: Match customer details with internal records
4. **Account Management**: Freeze accounts, cancel products as needed
5. **Payment Processing**: Execute court-ordered payments
6. **Case Closure**: Complete workflow and send confirmations

## 🤖 AI Integration

### OpenAI GPT-4 Features:
- **Document Classification**: Identify document types with confidence scoring
- **Information Extraction**: Extract structured data from legal documents
- **Data Validation**: Verify and clean extracted information
- **Text Summarization**: Generate concise document summaries

### OpenAI Vision API Features:
- **OCR Processing**: Extract text from images and scanned documents
- **Visual Document Analysis**: Analyze document layout and structure

## 📊 Sample Data

The application includes sample data for testing:

- **5 Sample Customers**: With various account statuses and balances
- **3 Sample Cases**: In different workflow stages
- **Transaction History**: Sample payment records

## 🔧 Configuration

### Environment Variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_API_BASE`: OpenAI API base URL (optional)

### Customization:
- Modify `utils/database.py` to change data models
- Update `utils/ai_processor.py` to adjust AI processing logic
- Customize UI styling in individual page files

## 🧪 Testing

### Local Testing:
1. Start the application: `streamlit run main.py`
2. Navigate through each page to test functionality
3. Upload sample documents to test AI processing
4. Verify data persistence across sessions

### Browser Testing:
- Test on multiple browsers (Chrome, Firefox, Safari)
- Verify responsive design on different screen sizes
- Test file upload functionality

## 🚀 Deployment

### Streamlit Cloud Deployment:
1. Push code to GitHub repository
2. Connect repository to Streamlit Cloud
3. Set environment variables in Streamlit Cloud settings
4. Deploy application

### Local Production:
```bash
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```

## 🔐 Security Considerations

- **API Keys**: Never commit API keys to repository
- **Data Privacy**: Sample data only - no real customer information
- **Access Control**: Implement authentication for production use
- **Data Encryption**: Consider encrypting sensitive data files

## 📈 Future Enhancements

- **Database Integration**: Replace file-based storage with proper database
- **User Authentication**: Add role-based access control
- **Real-time Notifications**: Implement email/SMS notifications
- **Advanced Analytics**: Add reporting and analytics dashboard
- **API Integration**: Connect to real banking systems
- **Audit Trail**: Comprehensive logging and audit capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is a proof of concept for demonstration purposes.

## 📞 Support

For questions or issues, please create an issue in the GitHub repository.

---

**Note**: This is a proof of concept application with sample data. Do not use with real customer information or in production environments without proper security measures.

