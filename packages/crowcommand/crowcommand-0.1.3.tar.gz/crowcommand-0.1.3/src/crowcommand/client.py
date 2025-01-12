import requests
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class APIClient:
    PRODUCTION_API_BASE = "https://api.crowcommand.com"
    DEVELOPMENT_API_BASE = "http://localhost:8000"
    
    def __init__(self, api_key: str):
        load_dotenv()
        
        self.api_key = api_key
        
        is_development = os.getenv("CROWCOMMANDER_ENV") == "development"
        base = self.DEVELOPMENT_API_BASE if is_development else self.PRODUCTION_API_BASE
        self.base_url = base
        
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        })
        
    def _make_request(self, method: str, endpoint: str, json: Optional[Dict[str, Any]] = None):
        """Make an HTTP request to the API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, json=json)
        response.raise_for_status()  
        return response.json()
