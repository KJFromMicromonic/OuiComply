#!/usr/bin/env python3
"""
CUAD Contract Download Script

This script downloads all contract PDFs from the CUAD dataset hosted on Hugging Face
and organizes them in the project's docs folder. The CUAD dataset contains various
types of legal contracts including affiliate agreements, licensing, service agreements,
and more.

The script provides:
- Progress tracking with detailed logging
- Error handling and retry mechanisms
- Organized folder structure by contract type
- Resume capability for interrupted downloads
- Comprehensive status reporting

Usage:
    python download_cuad_contracts.py [--resume] [--max-retries 3] [--batch-size 10]

Author: OuiComply Team
Version: 1.0.0
"""

import os
import sys
import time
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import json

try:
    from huggingface_hub import HfApi, hf_hub_download, list_repo_files
    from huggingface_hub.utils import RepositoryNotFoundError, EntryNotFoundError
except ImportError:
    print("Error: huggingface_hub library not found.")
    print("Please install it using: pip install huggingface_hub")
    sys.exit(1)

# Configuration
REPO_ID = "theatticusproject/cuad"
SUBDIR = "CUAD_v1/full_contract_pdf/Part_I"
DOCS_FOLDER = "docs"
CONTRACTS_FOLDER = "cuad_contracts"
LOG_FILE = "contract_download.log"
PROGRESS_FILE = "download_progress.json"

# Contract type mappings based on the dataset structure
CONTRACT_TYPES = {
    "Affiliate_Agreements": "affiliate_agreements",
    "Co_Branding": "co_branding",
    "Development": "development",
    "Distributor": "distributor", 
    "Endorsement": "endorsement",
    "Franchise": "franchise",
    "Hosting": "hosting",
    "IP": "intellectual_property",
    "Joint_Venture": "joint_venture",
    "License_Agreements": "license_agreements",
    "Maintenance": "maintenance",
    "Manufacturing": "manufacturing",
    "Marketing": "marketing",
    "Non_Compete_Non_Solicit": "non_compete",
    "Outsourcing": "outsourcing",
    "Promotion": "promotion",
    "Reseller": "reseller",
    "Service": "service",
    "Sponsorship": "sponsorship",
    "Strategic_Alliance": "strategic_alliance",
    "Supply": "supply",
    "Transportation": "transportation"
}

@dataclass
class DownloadStats:
    """Statistics for download progress tracking."""
    total_files: int = 0
    downloaded_files: int = 0
    failed_files: int = 0
    skipped_files: int = 0
    start_time: float = 0.0
    
    def __post_init__(self):
        if self.start_time == 0.0:
            self.start_time = time.time()
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self.start_time
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.downloaded_files / self.total_files) * 100
    
    @property
    def remaining_files(self) -> int:
        """Get number of remaining files to download."""
        return self.total_files - self.downloaded_files - self.failed_files - self.skipped_files

class ContractDownloader:
    """
    Handles downloading and organizing CUAD contract files.
    
    This class provides methods to download contract PDFs from the Hugging Face
    CUAD dataset and organize them by contract type in the local filesystem.
    """
    
    def __init__(self, docs_folder: str = DOCS_FOLDER, max_retries: int = 3, 
                 batch_size: int = 10, resume: bool = False):
        """
        Initialize the contract downloader.
        
        Args:
            docs_folder: Path to the docs folder where contracts will be stored
            max_retries: Maximum number of retry attempts for failed downloads
            batch_size: Number of files to download concurrently
            resume: Whether to resume from previous download session
        """
        self.docs_folder = Path(docs_folder)
        self.contracts_folder = self.docs_folder / CONTRACTS_FOLDER
        self.max_retries = max_retries
        self.batch_size = batch_size
        self.resume = resume
        self.stats = DownloadStats()
        self.progress_file = Path(PROGRESS_FILE)
        self.downloaded_files: set = set()
        
        # Setup logging
        self._setup_logging()
        
        # Setup directories
        self._setup_directories()
        
        # Load progress if resuming
        if self.resume and self.progress_file.exists():
            self._load_progress()
    
    def _setup_logging(self) -> None:
        """Configure logging for the download process."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _setup_directories(self) -> None:
        """Create necessary directories for storing contracts."""
        self.contracts_folder.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for each contract type
        for contract_type in CONTRACT_TYPES.values():
            (self.contracts_folder / contract_type).mkdir(exist_ok=True)
        
        self.logger.info(f"Created contracts directory: {self.contracts_folder}")
    
    def _load_progress(self) -> None:
        """Load progress from previous download session."""
        try:
            with open(self.progress_file, 'r') as f:
                progress_data = json.load(f)
                self.downloaded_files = set(progress_data.get('downloaded_files', []))
                self.stats.downloaded_files = len(self.downloaded_files)
                self.logger.info(f"Resumed download session. {len(self.downloaded_files)} files already downloaded.")
        except Exception as e:
            self.logger.warning(f"Could not load progress file: {e}")
    
    def _save_progress(self) -> None:
        """Save current progress to file."""
        try:
            progress_data = {
                'downloaded_files': list(self.downloaded_files),
                'stats': {
                    'total_files': self.stats.total_files,
                    'downloaded_files': self.stats.downloaded_files,
                    'failed_files': self.stats.failed_files,
                    'skipped_files': self.stats.skipped_files
                }
            }
            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save progress: {e}")
    
    def _get_contract_type_from_path(self, file_path: str) -> str:
        """
        Determine contract type from file path.
        
        Args:
            file_path: Path to the contract file
            
        Returns:
            Contract type folder name
        """
        path_parts = file_path.split('/')
        if len(path_parts) >= 2:
            folder_name = path_parts[-2]  # Get parent folder name
            return CONTRACT_TYPES.get(folder_name, "other")
        return "other"
    
    def _download_single_file(self, file_path: str, retry_count: int = 0) -> bool:
        """
        Download a single contract file.
        
        Args:
            file_path: Path to the file in the repository
            retry_count: Current retry attempt number
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            # Skip if already downloaded
            if file_path in self.downloaded_files:
                self.stats.skipped_files += 1
                return True
            
            # Determine local file path
            contract_type = self._get_contract_type_from_path(file_path)
            filename = os.path.basename(file_path)
            local_path = self.contracts_folder / contract_type / filename
            
            # Download the file
            downloaded_path = hf_hub_download(
                repo_id=REPO_ID,
                repo_type="dataset",
                filename=file_path,
                local_dir=self.contracts_folder / contract_type,
                local_files_only=False
            )
            
            # Verify download
            if os.path.exists(downloaded_path) and os.path.getsize(downloaded_path) > 0:
                self.downloaded_files.add(file_path)
                self.stats.downloaded_files += 1
                self.logger.info(f"Downloaded: {file_path} -> {downloaded_path}")
                return True
            else:
                raise Exception("Downloaded file is empty or doesn't exist")
                
        except Exception as e:
            if retry_count < self.max_retries:
                self.logger.warning(f"Retry {retry_count + 1}/{self.max_retries} for {file_path}: {e}")
                time.sleep(2 ** retry_count)  # Exponential backoff
                return self._download_single_file(file_path, retry_count + 1)
            else:
                self.logger.error(f"Failed to download {file_path} after {self.max_retries} retries: {e}")
                self.stats.failed_files += 1
                return False
    
    def _get_contract_files(self) -> List[str]:
        """
        Get list of all contract files in the dataset.
        
        Returns:
            List of file paths in the repository
        """
        try:
            self.logger.info("Fetching list of contract files...")
            api = HfApi()
            all_files = list_repo_files(
                repo_id=REPO_ID,
                repo_type="dataset",
                revision="main"
            )
            
            # Filter for PDF files in the Part_I directory
            contract_files = [
                f for f in all_files 
                if f.startswith(SUBDIR) and f.endswith('.pdf')
            ]
            
            self.logger.info(f"Found {len(contract_files)} contract files")
            return contract_files
            
        except Exception as e:
            self.logger.error(f"Failed to get file list: {e}")
            return []
    
    def download_contracts(self) -> bool:
        """
        Download all contract files from the CUAD dataset.
        
        Returns:
            True if all files downloaded successfully, False otherwise
        """
        try:
            # Get list of files to download
            contract_files = self._get_contract_files()
            if not contract_files:
                self.logger.error("No contract files found to download")
                return False
            
            self.stats.total_files = len(contract_files)
            self.logger.info(f"Starting download of {self.stats.total_files} contract files")
            
            # Download files in batches
            with ThreadPoolExecutor(max_workers=self.batch_size) as executor:
                # Submit all download tasks
                future_to_file = {
                    executor.submit(self._download_single_file, file_path): file_path
                    for file_path in contract_files
                }
                
                # Process completed downloads
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        success = future.result()
                        if success:
                            self._save_progress()  # Save progress periodically
                    except Exception as e:
                        self.logger.error(f"Unexpected error downloading {file_path}: {e}")
                        self.stats.failed_files += 1
            
            # Final progress save
            self._save_progress()
            
            # Print final statistics
            self._print_final_stats()
            
            return self.stats.failed_files == 0
            
        except Exception as e:
            self.logger.error(f"Download process failed: {e}")
            return False
    
    def _print_final_stats(self) -> None:
        """Print final download statistics."""
        elapsed_time = self.stats.elapsed_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        self.logger.info("=" * 60)
        self.logger.info("DOWNLOAD COMPLETE")
        self.logger.info("=" * 60)
        self.logger.info(f"Total files: {self.stats.total_files}")
        self.logger.info(f"Downloaded: {self.stats.downloaded_files}")
        self.logger.info(f"Skipped: {self.stats.skipped_files}")
        self.logger.info(f"Failed: {self.stats.failed_files}")
        self.logger.info(f"Success rate: {self.stats.success_rate:.1f}%")
        self.logger.info(f"Elapsed time: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
        self.logger.info(f"Contracts saved to: {self.contracts_folder}")
        self.logger.info("=" * 60)
    
    def cleanup(self) -> None:
        """Clean up temporary files."""
        if self.progress_file.exists():
            self.progress_file.unlink()
            self.logger.info("Cleaned up progress file")

def main():
    """Main function to run the contract downloader."""
    parser = argparse.ArgumentParser(
        description="Download CUAD contract dataset from Hugging Face",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python download_cuad_contracts.py
  python download_cuad_contracts.py --resume
  python download_cuad_contracts.py --max-retries 5 --batch-size 20
        """
    )
    
    parser.add_argument(
        '--resume', 
        action='store_true',
        help='Resume from previous download session'
    )
    parser.add_argument(
        '--max-retries', 
        type=int, 
        default=3,
        help='Maximum number of retry attempts (default: 3)'
    )
    parser.add_argument(
        '--batch-size', 
        type=int, 
        default=10,
        help='Number of concurrent downloads (default: 10)'
    )
    parser.add_argument(
        '--docs-folder',
        type=str,
        default=DOCS_FOLDER,
        help=f'Path to docs folder (default: {DOCS_FOLDER})'
    )
    
    args = parser.parse_args()
    
    # Create downloader instance
    downloader = ContractDownloader(
        docs_folder=args.docs_folder,
        max_retries=args.max_retries,
        batch_size=args.batch_size,
        resume=args.resume
    )
    
    try:
        # Start download process
        success = downloader.download_contracts()
        
        if success:
            print("\n✅ All contracts downloaded successfully!")
            downloader.cleanup()
            sys.exit(0)
        else:
            print(f"\n⚠️  Download completed with {downloader.stats.failed_files} failures")
            print("Check the log file for details on failed downloads")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Download interrupted by user")
        print("Progress has been saved. Use --resume to continue later.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
