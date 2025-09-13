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

## 🚀 Usage

### Starting the MCP Server

```bash
python -m src.mcp_server
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
