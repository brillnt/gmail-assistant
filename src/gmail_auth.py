#!/usr/bin/env python3
"""
Gmail Authentication Module

Handles OAuth2 authentication flow for Gmail API access.
Manages token storage and refresh automatically.
"""

import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError


class GmailAuthenticator:
    """Handles Gmail API authentication using OAuth2."""
    
    # Gmail API scope for read-only access
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, credentials_file='credentials.json', token_file='token.pickle'):
        """
        Initialize the authenticator.
        
        Args:
            credentials_file (str): Path to the OAuth2 credentials JSON file
            token_file (str): Path to store the authentication token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
    
    def authenticate(self):
        """
        Authenticate with Gmail API and return service instance.
        
        Returns:
            googleapiclient.discovery.Resource: Authenticated Gmail service
            
        Raises:
            FileNotFoundError: If credentials file is missing
            Exception: If authentication fails
        """
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"Credentials file '{self.credentials_file}' not found. "
                "Please download it from Google Cloud Console."
            )
        
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no valid credentials available, run OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print("Refreshing expired token...")
                    creds.refresh(Request())
                except RefreshError:
                    print("Token refresh failed. Re-authenticating...")
                    creds = self._run_oauth_flow()
            else:
                print("No valid credentials found. Starting OAuth flow...")
                creds = self._run_oauth_flow()
            
            # Save the credentials for the next run
            self._save_token(creds)
        
        # Build and return the Gmail service
        self.service = build('gmail', 'v1', credentials=creds)
        print("Successfully authenticated with Gmail API")
        return self.service
    
    def _run_oauth_flow(self):
        """
        Run the OAuth2 flow to get new credentials.
        
        Returns:
            google.oauth2.credentials.Credentials: Fresh credentials
        """
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_file, self.SCOPES)
        creds = flow.run_local_server(port=0)
        return creds
    
    def _save_token(self, creds):
        """
        Save credentials to token file.
        
        Args:
            creds: Google OAuth2 credentials to save
        """
        with open(self.token_file, 'wb') as token:
            pickle.dump(creds, token)
        print(f"Token saved to {self.token_file}")
    
    def get_service(self):
        """
        Get the authenticated Gmail service instance.
        
        Returns:
            googleapiclient.discovery.Resource: Gmail service or None if not authenticated
        """
        return self.service
    
    def is_authenticated(self):
        """
        Check if currently authenticated.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.service is not None


def main():
    """Test the authentication module."""
    print("Testing Gmail Authentication...")
    
    auth = GmailAuthenticator()
    
    try:
        service = auth.authenticate()
        
        # Test the connection by getting user profile
        profile = service.users().getProfile(userId='me').execute()
        print(f"Successfully connected to Gmail for: {profile['emailAddress']}")
        print(f"Total messages: {profile['messagesTotal']}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure credentials.json is in the current directory.")
    except Exception as e:
        print(f"Authentication failed: {e}")


if __name__ == "__main__":
    main()

