# CUAD Contract Dataset Download Guide

This guide explains how to download and use the CUAD (Contract Understanding Atticus Dataset) contract collection for testing and training compliance analysis.

## 🎯 Overview

The CUAD dataset contains 199+ real-world legal contracts across 22 different categories, providing an excellent foundation for:
- Testing compliance analysis algorithms
- Training machine learning models
- Benchmarking document processing capabilities
- Understanding various contract types and structures

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed on your system
2. **Internet connection** for downloading files
3. **Sufficient disk space** (~500MB for all contracts)

### Installation

1. **Install dependencies**:
   ```bash
   pip install huggingface_hub>=0.20.0
   ```

2. **Test the download functionality**:
   ```bash
   python test_contract_download.py
   ```

3. **Download all contracts**:
   ```bash
   python download_cuad_contracts.py
   ```

### Windows Users

Use the provided batch script for easy execution:

```cmd
download_contracts.bat
```

## 📊 Dataset Statistics

- **Total Files**: 199 contract PDFs
- **Categories**: 22 different contract types
- **Total Size**: ~500MB
- **Source**: [Hugging Face CUAD Dataset](https://huggingface.co/datasets/theatticusproject/cuad)

## 📁 File Organization

Contracts are automatically organized by type in the `docs/cuad_contracts/` directory:

```
docs/cuad_contracts/
├── affiliate_agreements/     (Partnership contracts)
├── co_branding/             (Joint branding deals)
├── development/             (Software development)
├── distributor/             (Distribution agreements)
├── endorsement/             (Celebrity endorsements)
├── franchise/               (Franchise agreements)
├── hosting/                 (Web hosting contracts)
├── intellectual_property/   (IP licensing)
├── joint_venture/           (Joint ventures)
├── license_agreements/      (Software licensing)
├── maintenance/             (Service contracts)
├── manufacturing/           (Production agreements)
├── marketing/               (Marketing contracts)
├── non_compete/             (Non-compete agreements)
├── outsourcing/             (Vendor contracts)
├── promotion/               (Promotional deals)
├── reseller/                (Reseller agreements)
├── service/                 (General services)
├── sponsorship/             (Sponsorship deals)
├── strategic_alliance/      (Strategic partnerships)
├── supply/                  (Supply chain)
└── transportation/          (Logistics contracts)
```

## ⚙️ Advanced Usage

### Command Line Options

```bash
# Basic download
python download_cuad_contracts.py

# Resume interrupted download
python download_cuad_contracts.py --resume

# Custom retry settings
python download_cuad_contracts.py --max-retries 5

# Adjust concurrent downloads
python download_cuad_contracts.py --batch-size 20

# Custom docs folder location
python download_cuad_contracts.py --docs-folder /path/to/docs
```

### Progress Tracking

The script provides detailed progress information:

- **Real-time logging** to console and log file
- **Progress persistence** for resume capability
- **Download statistics** including success rates
- **Error reporting** with retry attempts

### Log Files

- **`contract_download.log`**: Detailed download log
- **`download_progress.json`**: Progress tracking data

## 🔧 Troubleshooting

### Common Issues

1. **Network Timeouts**:
   ```bash
   # Increase retry attempts
   python download_cuad_contracts.py --max-retries 5
   ```

2. **Permission Errors**:
   ```bash
   # Run with appropriate permissions
   sudo python download_cuad_contracts.py  # Linux/Mac
   ```

3. **Disk Space**:
   - Ensure at least 1GB free space
   - Check available space: `df -h` (Linux/Mac) or `dir` (Windows)

4. **Interrupted Downloads**:
   ```bash
   # Resume from where it left off
   python download_cuad_contracts.py --resume
   ```

### Verification

After download, verify the dataset:

```bash
# Check total file count
find docs/cuad_contracts -name "*.pdf" | wc -l

# Check file sizes
find docs/cuad_contracts -name "*.pdf" -exec ls -lh {} \;
```

## 🧪 Testing

### Unit Tests

Run the test suite to verify functionality:

```bash
python test_contract_download.py
```

### Integration with Compliance Analysis

Test downloaded contracts with the compliance engine:

```python
from src.tools.document_ai import DocumentAIService

# Initialize service
service = DocumentAIService()

# Analyze a downloaded contract
result = await service.analyze_document(
    document_path="docs/cuad_contracts/service/contract_123.pdf",
    compliance_frameworks=["gdpr", "sox"]
)
```

## 📈 Performance Tips

1. **Concurrent Downloads**: Adjust `--batch-size` based on your connection
2. **Resume Capability**: Use `--resume` for large downloads
3. **Error Handling**: Higher `--max-retries` for unstable connections
4. **Monitoring**: Watch log files for progress and errors

## 🔄 Updates

To update the dataset:

1. **Remove old files**:
   ```bash
   rm -rf docs/cuad_contracts/*
   ```

2. **Re-download**:
   ```bash
   python download_cuad_contracts.py
   ```

## 📚 Additional Resources

- [CUAD Dataset Paper](https://arxiv.org/abs/2103.06275)
- [Hugging Face Dataset Page](https://huggingface.co/datasets/theatticusproject/cuad)
- [Contract Understanding Benchmark](https://www.theatticusproject.com/cuad)

## 🆘 Support

For issues with the download script:

1. Check the log file: `contract_download.log`
2. Verify network connectivity
3. Ensure sufficient disk space
4. Try with reduced batch size: `--batch-size 5`

---

**Note**: This dataset is for research and development purposes. Please review the original dataset license for commercial usage terms.
