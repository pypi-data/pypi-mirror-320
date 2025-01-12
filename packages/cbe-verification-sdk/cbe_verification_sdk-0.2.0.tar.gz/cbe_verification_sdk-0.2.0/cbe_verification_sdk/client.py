import requests
from PyPDF2 import PdfReader
from io import BytesIO
import logging
from typing import Dict, Optional

class CBEVerificationClient:
    def __init__(self, api_key: str, api_base_url: str = "http://localhost:8000"):
        """
        Initialize the CBE Verification Client
        
        Args:
            api_key (str): Your API key for authentication
            api_base_url (str): Base URL of the verification API
        """
        self.api_key = api_key
        self.api_base_url = api_base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        })
        
    def _get_transaction_pdf(self, transaction_id: str, account_number: str) -> str:
        """
        Fetch and extract text from CBE transaction PDF
        
        Args:
            transaction_id (str): Transaction ID from CBE (starts with 'FT')
            account_number (str): CBE account number
            
        Returns:
            str: Extracted text from the PDF
        """
        try:
            # Construct CBE URL with both parameters
            cbe_url = f"https://apps.cbe.com.et:100/?id={transaction_id}&accountno={account_number}"
            
            # Fetch PDF
            response = requests.get(cbe_url, verify=False)
            response.raise_for_status()
            
            # Read PDF content
            pdf_file = BytesIO(response.content)
            pdf_reader = PdfReader(pdf_file)
            
            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
                
            return text.strip()
            
        except Exception as e:
            logging.error(f"Error fetching PDF: {str(e)}")
            raise
            
    def verify_transaction(self, reference_number: str, account_number: str) -> Dict:
        """
        Verify a CBE transaction
        
        Args:
            reference_number (str): Transaction reference number (starts with 'FT')
            account_number (str): CBE account number
            
        Returns:
            Dict: Verification result containing transaction details
        """
        try:
            # Get PDF content with both parameters
            pdf_data = self._get_transaction_pdf(reference_number, account_number)
            
            # Prepare request data
            payload = {
                "reference_number": reference_number,
                "account_number": account_number,
                "pdf_data": pdf_data
            }
            
            # Make API request
            response = self.session.post(
                f"{self.api_base_url}/api/verify-transaction",
                json=payload
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {str(e)}")
            raise 