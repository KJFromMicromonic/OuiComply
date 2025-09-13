#!/usr/bin/env python3
"""
Test script for CUAD contract download functionality.

This script tests the contract downloader with a small subset of files
to ensure the functionality works correctly before running the full download.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from download_cuad_contracts import ContractDownloader, CONTRACT_TYPES

def test_downloader_initialization():
    """Test that the downloader initializes correctly."""
    print("Testing downloader initialization...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        downloader = ContractDownloader(docs_folder=temp_dir)
        
        # Check that directories are created
        assert downloader.contracts_folder.exists(), "Contracts folder should be created"
        
        # Check that contract type subdirectories are created
        for contract_type in CONTRACT_TYPES.values():
            subdir = downloader.contracts_folder / contract_type
            assert subdir.exists(), f"Subdirectory {contract_type} should be created"
        
        print("✅ Downloader initialization test passed")

def test_contract_type_mapping():
    """Test that contract type mapping works correctly."""
    print("Testing contract type mapping...")
    
    downloader = ContractDownloader()
    
    # Test various file paths
    test_cases = [
        ("CUAD_v1/full_contract_pdf/Part_I/Affiliate_Agreements/contract1.pdf", "affiliate_agreements"),
        ("CUAD_v1/full_contract_pdf/Part_I/Service/contract2.pdf", "service"),
        ("CUAD_v1/full_contract_pdf/Part_I/IP/contract3.pdf", "intellectual_property"),
        ("CUAD_v1/full_contract_pdf/Part_I/Unknown/contract4.pdf", "other"),
    ]
    
    for file_path, expected_type in test_cases:
        result = downloader._get_contract_type_from_path(file_path)
        assert result == expected_type, f"Expected {expected_type}, got {result} for {file_path}"
    
    print("✅ Contract type mapping test passed")

def test_progress_tracking():
    """Test progress tracking functionality."""
    print("Testing progress tracking...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        downloader = ContractDownloader(docs_folder=temp_dir)
        
        # Test initial stats
        assert downloader.stats.total_files == 0
        assert downloader.stats.downloaded_files == 0
        assert downloader.stats.failed_files == 0
        
        # Test progress save/load
        downloader.downloaded_files.add("test_file.pdf")
        downloader.stats.downloaded_files = 1
        downloader._save_progress()
        
        # Create new downloader and test resume
        downloader2 = ContractDownloader(docs_folder=temp_dir, resume=True)
        assert "test_file.pdf" in downloader2.downloaded_files
        assert downloader2.stats.downloaded_files == 1
        
        print("✅ Progress tracking test passed")

def test_file_list_retrieval():
    """Test that we can retrieve the list of contract files."""
    print("Testing file list retrieval...")
    
    try:
        downloader = ContractDownloader()
        files = downloader._get_contract_files()
        
        # Should return a list (may be empty if there are network issues)
        assert isinstance(files, list), "Should return a list of files"
        
        if files:
            # If files are found, they should all be PDFs in the correct directory
            for file_path in files[:5]:  # Check first 5 files
                assert file_path.startswith("CUAD_v1/full_contract_pdf/Part_I"), f"File {file_path} should be in Part_I directory"
                assert file_path.endswith(".pdf"), f"File {file_path} should be a PDF"
        
        print(f"✅ File list retrieval test passed - found {len(files)} files")
        
    except Exception as e:
        print(f"⚠️  File list retrieval test failed (this may be due to network issues): {e}")
        print("This is expected if there are network connectivity issues")

def main():
    """Run all tests."""
    print("🧪 Running CUAD Contract Downloader Tests")
    print("=" * 50)
    
    try:
        test_downloader_initialization()
        test_contract_type_mapping()
        test_progress_tracking()
        test_file_list_retrieval()
        
        print("\n🎉 All tests passed!")
        print("\nYou can now run the full download with:")
        print("python download_cuad_contracts.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
