"""
PDF Parser Tool - Extracts text from PDF files.
Part of MCP tool suite for document processing.
"""

import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)


class PDFParser:
    """
    Extracts text content from PDF files.
    Supports multiple parsing backends.
    """
    
    def __init__(self):
        """Initialize PDF parser with available backend."""
        self.backend = self._detect_backend()
        logger.info(f"PDF parser initialized with backend: {self.backend}")
    
    def _detect_backend(self) -> str:
        """Detect available PDF parsing library."""
        try:
            import PyPDF2
            return 'pypdf2'
        except ImportError:
            pass
        
        try:
            import pdfplumber
            return 'pdfplumber'
        except ImportError:
            pass
        
        logger.warning("No PDF parsing library found. Install with: pip install PyPDF2 or pip install pdfplumber")
        return 'none'
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return ""
        
        if self.backend == 'pypdf2':
            return self._extract_with_pypdf2(file_path)
        elif self.backend == 'pdfplumber':
            return self._extract_with_pdfplumber(file_path)
        else:
            logger.error("No PDF parser available")
            return ""
    
    def _extract_with_pypdf2(self, file_path: str) -> str:
        """Extract text using PyPDF2."""
        try:
            import PyPDF2
            
            text = []
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text.append(page.extract_text())
            
            extracted_text = '\n'.join(text)
            logger.info(f"Extracted {len(extracted_text)} characters from {file_path}")
            
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting with PyPDF2: {e}")
            return ""
    
    def _extract_with_pdfplumber(self, file_path: str) -> str:
        """Extract text using pdfplumber (better formatting)."""
        try:
            import pdfplumber
            
            text = []
            
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            
            extracted_text = '\n'.join(text)
            logger.info(f"Extracted {len(extracted_text)} characters from {file_path}")
            
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting with pdfplumber: {e}")
            return ""
    
    def extract_text_from_pages(self, file_path: str, start_page: int, end_page: int) -> str:
        """
        Extract text from specific page range.
        
        Args:
            file_path: Path to PDF file
            start_page: Starting page number (0-indexed)
            end_page: Ending page number (inclusive)
            
        Returns:
            Extracted text from specified pages
        """
        if self.backend == 'pypdf2':
            try:
                import PyPDF2
                
                text = []
                
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    for page_num in range(start_page, min(end_page + 1, len(pdf_reader.pages))):
                        page = pdf_reader.pages[page_num]
                        text.append(page.extract_text())
                
                return '\n'.join(text)
                
            except Exception as e:
                logger.error(f"Error extracting pages: {e}")
                return ""
        
        return self.extract_text(file_path)  # Fallback to full extraction
    
    def get_page_count(self, file_path: str) -> int:
        """Get number of pages in PDF."""
        try:
            if self.backend == 'pypdf2':
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    return len(pdf_reader.pages)
            elif self.backend == 'pdfplumber':
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    return len(pdf.pages)
        except Exception as e:
            logger.error(f"Error getting page count: {e}")
            return 0