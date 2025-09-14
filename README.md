# OuiComply - AI-Assisted Legal Compliance Checker

OuiComply is a comprehensive AI-powered legal compliance checking system that leverages Mistral's LeChat as the frontend, Mistral DocumentAI for intelligent document parsing, and a custom MCP (Model Context Protocol) server for advanced compliance analysis.

## 🚀 Features

### Core Capabilities
- **Multi-Framework Compliance Analysis**: Support for GDPR, SOX, CCPA, HIPAA, and other major compliance frameworks
- **DocumentAI Integration**: Advanced document parsing and analysis using Mistral's DocumentAI service
- **Risk Assessment**: Comprehensive risk scoring and mitigation recommendations
- **LeChat Memory Integration**: Autonomous decision-making through stored compliance assessments
- **Audit Trail Generation**: GitHub-integrated audit trails for compliance tracking
- **Structured Reporting**: JSON, Markdown, and HTML report generation

### Supported Compliance Frameworks
- **GDPR** (General Data Protection Regulation)
- **SOX** (Sarbanes-Oxley Act)
- **CCPA** (California Consumer Privacy Act)
- **HIPAA** (Health Insurance Portability and Accountability Act)

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   LeChat        │    │   OuiComply      │    │   Mistral       │
│   Frontend      │◄──►│   MCP Server     │◄──►│   DocumentAI    │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   GitHub         │
                       │   Audit Trails   │
                       └──────────────────┘
```

## 📋 Prerequisites

- Python 3.8 or higher
- Mistral API key
- LeChat API access (optional, for memory integration)
- GitHub repository (optional, for audit trails)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ouicomply.git
   cd ouicomply
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

## ⚙️ Configuration

Create a `.env` file with the following variables:

```env
# Required
MISTRAL_KEY=your_mistral_api_key_here

# Optional - LeChat Memory Integration
LECHAT_API_URL=https://api.lechat.ai
LECHAT_API_KEY=your_lechat_api_key

# Optional - GitHub Integration
GITHUB_TOKEN=your_github_token
GITHUB_REPOSITORY=yourusername/your-repo

# Optional - Linear/Jira Integration
LINEAR_API_KEY=your_linear_api_key
JIRA_API_KEY=your_jira_api_key
JIRA_BASE_URL=https://yourcompany.atlassian.net

# Server Configuration
MCP_SERVER_NAME=ouicomply-mcp
MCP_SERVER_VERSION=1.0.0
LOG_LEVEL=INFO
```

## 📁 Contract Dataset Management

### CUAD Contract Download

OuiComply includes a comprehensive script to download and organize the CUAD (Contract Understanding Atticus Dataset) contract collection from Hugging Face. This dataset contains 199+ real-world legal contracts across 22 different categories, providing an excellent foundation for testing and training compliance analysis.

#### Downloading the CUAD Dataset

```bash
# Download all contracts (199 files across 22 categories)
python download_cuad_contracts.py

# Resume interrupted download
python download_cuad_contracts.py --resume

# Customize download parameters
python download_cuad_contracts.py --max-retries 5 --batch-size 20

# Test the download functionality first
python test_contract_download.py
```

#### Contract Categories

The downloaded contracts are organized into the following categories:

- **Affiliate Agreements** - Partnership and affiliate marketing contracts
- **Co-Branding** - Joint branding and marketing agreements
- **Development** - Software and product development contracts
- **Distributor** - Distribution and reseller agreements
- **Endorsement** - Celebrity and influencer endorsement deals
- **Franchise** - Franchise and licensing agreements
- **Hosting** - Web hosting and infrastructure contracts
- **Intellectual Property** - IP licensing and protection agreements
- **Joint Venture** - Joint venture and collaboration agreements
- **License Agreements** - Software and content licensing
- **Maintenance** - Service and maintenance contracts
- **Manufacturing** - Production and manufacturing agreements
- **Marketing** - Marketing and advertising contracts
- **Non-Compete** - Non-compete and non-solicitation agreements
- **Outsourcing** - Outsourcing and vendor contracts
- **Promotion** - Promotional and marketing agreements
- **Reseller** - Reseller and distribution contracts
- **Service** - General service agreements
- **Sponsorship** - Sponsorship and partnership deals
- **Strategic Alliance** - Strategic partnership agreements
- **Supply** - Supply chain and procurement contracts
- **Transportation** - Logistics and transportation agreements

#### Dataset Structure

```
docs/
└── cuad_contracts/
    ├── affiliate_agreements/
    ├── co_branding/
    ├── development/
    ├── distributor/
    ├── endorsement/
    ├── franchise/
    ├── hosting/
    ├── intellectual_property/
    ├── joint_venture/
    ├── license_agreements/
    ├── maintenance/
    ├── manufacturing/
    ├── marketing/
    ├── non_compete/
    ├── outsourcing/
    ├── promotion/
    ├── reseller/
    ├── service/
    ├── sponsorship/
    ├── strategic_alliance/
    ├── supply/
    └── transportation/
```

#### Features

- **Progress Tracking**: Real-time download progress with detailed logging
- **Resume Capability**: Interrupted downloads can be resumed from where they left off
- **Error Handling**: Robust retry mechanisms with exponential backoff
- **Concurrent Downloads**: Configurable batch processing for optimal performance
- **Organized Storage**: Automatic categorization by contract type
- **Comprehensive Logging**: Detailed logs for troubleshooting and monitoring

#### Usage with Compliance Analysis

Once downloaded, these contracts can be used for:

```python
# Analyze a downloaded contract for compliance
{
    "tool": "analyze_document_compliance",
    "arguments": {
        "document_content": "docs/cuad_contracts/service/contract_123.pdf",
        "compliance_frameworks": ["gdpr", "sox"],
        "analysis_depth": "comprehensive"
    }
}
```

## 🚀 Usage

### Starting the MCP Server

#### Local Development
```bash
python -m src.mcp_server
```

#### Web Exposure with ngrok (Recommended for Testing)
```bash
# Install ngrok (if not already installed)
# Download from https://ngrok.com/download

# Run MCP server with ngrok web exposure
python run_ngrok_mcp.py

# Or use the convenient batch script (Windows)
start_ngrok_mcp.bat

# Or use PowerShell script (Windows)
.\start_ngrok_mcp.ps1
```

#### Testing the Web-Exposed Server
```bash
# Test the ngrok-exposed server
python test_ngrok_mcp.py https://your-ngrok-url.ngrok.io

# Manual testing
curl https://your-ngrok-url.ngrok.io/health
curl https://your-ngrok-url.ngrok.io/info
```

#### ALPIC Integration
Once the ngrok server is running, use the provided URL in your ALPIC configuration:
```json
{
  "mcp_servers": {
    "ouicomply": {
      "url": "https://your-ngrok-url.ngrok.io/mcp",
      "name": "OuiComply MCP Server"
    }
  }
}
```

For detailed ngrok setup instructions, see [NGROK_SETUP.md](NGROK_SETUP.md).

## 🔌 API Endpoints

The OuiComply MCP Server provides both MCP protocol endpoints and function-based routing for direct API access.

### MCP Protocol Endpoints

- **`POST /mcp`** - Main MCP protocol endpoint for LeChat integration
- **`GET /mcp/sse`** - Server-Sent Events for real-time updates
- **`GET /health`** - Health check endpoint
- **`GET /`** - Server information and available endpoints

### Function-Based Routing Endpoints

The server now supports direct function calls through REST endpoints:

#### 📄 Document Analysis
```bash
POST /mcp/analyze_document
Content-Type: application/json

{
    "document_content": "Your document content here...",
    "document_type": "contract",  # optional
    "frameworks": ["gdpr", "sox"]  # optional
}
```

**Response:**
```json
{
    "function": "analyze_document",
    "status": "success",
    "result": {
        "report_id": "report_123",
        "status": "compliant",
        "risk_level": "low",
        "risk_score": 0.2,
        "issues_count": 0,
        "summary": "Document appears compliant with specified frameworks"
    }
}
```

#### 🧠 Memory Management
```bash
POST /mcp/update_memory
Content-Type: application/json

{
    "team_id": "team_123",
    "insight": "Compliance insight to store",
    "category": "privacy"  # optional
}
```

**Response:**
```json
{
    "function": "update_memory",
    "status": "success",
    "result": {
        "team_id": "team_123",
        "insight_stored": true,
        "memory_id": "memory_456"
    }
}
```

#### 📊 Compliance Status
```bash
POST /mcp/get_compliance_status
Content-Type: application/json

{
    "team_id": "team_123",
    "framework": "gdpr"  # optional
}
```

**Response:**
```json
{
    "function": "get_compliance_status",
    "status": "success",
    "result": {
        "team_id": "team_123",
        "framework": "gdpr",
        "status": "compliant",
        "last_updated": "2024-01-15T10:30:00Z"
    }
}
```

### Testing the API

Use the provided test script to verify all endpoints:

```bash
python test_function_routing.py
```

### Available Tools

#### 1. Document Compliance Analysis
```python
# Analyze a document for compliance issues
{
    "tool": "analyze_document_compliance",
    "arguments": {
        "document_content": "path/to/document.pdf",
        "compliance_frameworks": ["gdpr", "sox"],
        "analysis_depth": "comprehensive"
    }
}
```

#### 2. Generate Compliance Report
```python
# Generate a structured compliance report
{
    "tool": "generate_compliance_report",
    "arguments": {
        "report_id": "report_123",
        "format": "markdown"  # json, markdown, html
    }
}
```

#### 3. Store Assessment in Memory
```python
# Store compliance assessment in LeChat memory
{
    "tool": "store_assessment_in_memory",
    "arguments": {
        "report_id": "report_123",
        "user_id": "user_456",
        "organization_id": "org_789"
    }
}
```

#### 4. Search Compliance Memories
```python
# Search stored compliance assessments
{
    "tool": "search_compliance_memories",
    "arguments": {
        "query": "GDPR privacy policy",
        "category": "compliance_assessment",
        "limit": 10
    }
}
```

#### 5. Generate Audit Trail
```python
# Generate GitHub audit trail entry
{
    "tool": "generate_audit_trail",
    "arguments": {
        "report_id": "report_123",
        "repository": "yourusername/compliance-repo",
        "branch": "main"
    }
}
```

#### 6. Get Compliance History
```python
# Retrieve compliance assessment history
{
    "tool": "get_compliance_history",
    "arguments": {
        "user_id": "user_456",
        "organization_id": "org_789",
        "limit": 20
    }
}
```

#### 7. Analyze Risk Trends
```python
# Analyze compliance risk trends over time
{
    "tool": "analyze_risk_trends",
    "arguments": {
        "user_id": "user_456",
        "days": 30
    }
}
```

## 📊 Compliance Analysis Process

1. **Document Upload**: Document is uploaded to Mistral DocumentAI service
2. **Content Extraction**: Document content is extracted and processed
3. **Framework Analysis**: Document is analyzed against specified compliance frameworks
4. **Risk Assessment**: Risk score is calculated based on identified issues
5. **Report Generation**: Comprehensive compliance report is generated
6. **Memory Storage**: Assessment is stored in LeChat memory for future reference
7. **Audit Trail**: GitHub audit trail entry is created (optional)

## 🔍 Compliance Frameworks

### GDPR (General Data Protection Regulation)
- **Required Clauses**: Data processing purpose, legal basis, retention period, data subject rights
- **Risk Indicators**: Unclear processing purposes, missing legal basis, excessive retention

### SOX (Sarbanes-Oxley Act)
- **Required Clauses**: Financial reporting controls, internal control framework, management responsibility
- **Risk Indicators**: Weak internal controls, insufficient documentation, conflict of interest

### CCPA (California Consumer Privacy Act)
- **Required Clauses**: Personal information collection notice, consumer rights disclosure, opt-out mechanisms
- **Risk Indicators**: Unclear data collection, missing opt-out mechanisms

### HIPAA (Health Insurance Portability and Accountability Act)
- **Required Clauses**: Privacy notice, minimum necessary standard, patient consent procedures
- **Risk Indicators**: Insufficient privacy protections, unclear consent procedures

## 📈 Risk Assessment

The system calculates risk scores based on:
- **Missing Clauses** (30% weight)
- **Critical Issues** (40% weight)
- **High Priority Issues** (20% weight)
- **Medium Priority Issues** (10% weight)

Risk levels:
- **Low**: 0.0 - 0.3
- **Medium**: 0.3 - 0.6
- **High**: 0.6 - 0.8
- **Critical**: 0.8 - 1.0

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_document_ai.py

# Run with verbose output
pytest -v
```

## 📚 API Documentation

### DocumentAI Service

The `DocumentAIService` class provides comprehensive document analysis capabilities:

```python
from src.tools.document_ai import DocumentAIService, DocumentAnalysisRequest

# Initialize service
service = DocumentAIService()

# Create analysis request
request = DocumentAnalysisRequest(
    document_content="path/to/document.pdf",
    compliance_frameworks=["gdpr", "sox"],
    analysis_depth="comprehensive"
)

# Analyze document
result = await service.analyze_document(request)
```

### Compliance Engine

The `ComplianceEngine` class handles compliance analysis and reporting:

```python
from src.tools.compliance_engine import ComplianceEngine

# Initialize engine
engine = ComplianceEngine()

# Analyze document compliance
report = await engine.analyze_document_compliance(
    document_content="path/to/document.pdf",
    frameworks=["gdpr"],
    analysis_depth="comprehensive"
)

# Generate audit trail
audit_trail = await engine.generate_audit_trail_entry(report)
```

### Memory Integration

The `LeChatMemoryService` class manages LeChat memory integration:

```python
from src.tools.memory_integration import LeChatMemoryService

# Initialize service
memory_service = LeChatMemoryService()

# Store assessment
memory_id = await memory_service.store_compliance_assessment(
    report=compliance_report,
    user_id="user123",
    organization_id="org456"
)

# Search memories
results = await memory_service.search_memories(
    query="GDPR compliance",
    category="compliance_assessment",
    limit=10
)
```

## 🚀 Deployment

### ALPIC Deployment (Recommended)

OuiComply MCP Server is optimized for ALPIC deployment. See [ALPIC_DEPLOYMENT.md](ALPIC_DEPLOYMENT.md) for detailed instructions.

**Quick ALPIC Setup:**
1. **Build Settings**:
   - Install Command: `uv sync --locked`
   - Start Command: `python main.py`

2. **Environment Variables**:
   ```env
   MISTRAL_KEY=your_mistral_api_key_here
   ALPIC_ENV=true
   ENABLE_HEALTH_CHECK=true
   ```

3. **Health Check**: Available at `/health` endpoint

### Docker Deployment

1. **Build Docker image**
   ```bash
   docker build -t ouicomply-mcp .
   ```

2. **Run container**
   ```bash
   docker run -p 3000:3000 --env-file .env ouicomply-mcp
   ```

### Local Development

1. **Start the server**
   ```bash
   python main.py
   ```

2. **Test health check**
   ```bash
   curl http://localhost:3000/health
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the documentation wiki

## 🔮 Roadmap

- [ ] Additional compliance frameworks (PCI DSS, ISO 27001)
- [ ] Real-time compliance monitoring
- [ ] Integration with more project management tools
- [ ] Advanced analytics dashboard
- [ ] Automated remediation suggestions
- [ ] Multi-language support

---

**OuiComply** - Making compliance checking intelligent, automated, and accessible.
