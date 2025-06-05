#!/usr/bin/env python3
"""
Gmail Search Module

Handles searching Gmail using native Gmail search syntax.
Returns message IDs and basic metadata for further processing.
"""

from gmail_auth import GmailAuthenticator


class GmailSearcher:
    """Handles Gmail search operations using native Gmail search syntax."""
    
    def __init__(self, authenticator=None, credentials_file=None):
        """
        Initialize the searcher.
        
        Args:
            authenticator (GmailAuthenticator): Optional authenticator instance
            credentials_file (str): Path to credentials file (if not using existing authenticator)
        """
        if authenticator:
            self.auth = authenticator
            self.service = authenticator.get_service()
        else:
            # Default to looking in parent directory for credentials
            if not credentials_file:
                credentials_file = '../credentials.json'
            token_file = '../token.pickle'
            self.auth = GmailAuthenticator(credentials_file=credentials_file, token_file=token_file)
            self.service = None
    
    def authenticate(self):
        """Authenticate with Gmail API if not already done."""
        if not self.service:
            self.service = self.auth.authenticate()
        return self.service
    
    def search(self, query, max_results=100):
        """
        Search Gmail using native Gmail search syntax.
        
        Args:
            query (str): Gmail search query (e.g., "from:john@example.com", "subject:meeting")
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of message dictionaries with basic metadata
            
        Example queries:
            - "from:john@example.com"
            - "subject:meeting"
            - "from:john@example.com subject:project"
            - "after:2023/01/01 before:2023/12/31"
            - "has:attachment"
            - "is:unread"
        """
        if not self.service:
            self.authenticate()
        
        print(f"Searching Gmail with query: '{query}'")
        print(f"Maximum results: {max_results}")
        
        try:
            # Execute the search
            result = self.service.users().messages().list(
                userId='me', 
                q=query, 
                maxResults=max_results
            ).execute()
            
            messages = result.get('messages', [])
            
            if not messages:
                print(f"No messages found matching query: '{query}'")
                return []
            
            print(f"Found {len(messages)} messages")
            
            # Get basic metadata for each message
            message_list = []
            for i, msg in enumerate(messages):
                if (i + 1) % 10 == 0:
                    print(f"Processing message {i + 1}/{len(messages)}...")
                
                # Get basic message info
                message_data = self.service.users().messages().get(
                    userId='me', 
                    id=msg['id'], 
                    format='metadata',
                    metadataHeaders=['From', 'To', 'Subject', 'Date']
                ).execute()
                
                # Extract headers
                headers = message_data['payload'].get('headers', [])
                header_dict = {h['name']: h['value'] for h in headers}
                
                message_info = {
                    'id': msg['id'],
                    'thread_id': message_data['threadId'],
                    'snippet': message_data['snippet'],
                    'from': header_dict.get('From', 'Unknown'),
                    'to': header_dict.get('To', 'Unknown'),
                    'subject': header_dict.get('Subject', 'No Subject'),
                    'date': header_dict.get('Date', 'Unknown'),
                    'labels': message_data.get('labelIds', [])
                }
                
                message_list.append(message_info)
            
            print(f"Search complete. Retrieved {len(message_list)} messages.")
            return message_list
            
        except Exception as e:
            print(f"Error during search: {e}")
            return []
    
    def search_by_sender(self, sender_email, max_results=100):
        """
        Search for emails from a specific sender.
        
        Args:
            sender_email (str): Email address of the sender
            max_results (int): Maximum number of results
            
        Returns:
            list: List of message dictionaries
        """
        query = f"from:{sender_email}"
        return self.search(query, max_results)
    
    def search_by_subject(self, subject_text, max_results=100):
        """
        Search for emails with specific subject text.
        
        Args:
            subject_text (str): Text to search for in subject
            max_results (int): Maximum number of results
            
        Returns:
            list: List of message dictionaries
        """
        query = f"subject:{subject_text}"
        return self.search(query, max_results)
    
    def search_by_date_range(self, after_date=None, before_date=None, max_results=100):
        """
        Search for emails within a date range.
        
        Args:
            after_date (str): Date in YYYY/MM/DD format (inclusive)
            before_date (str): Date in YYYY/MM/DD format (exclusive)
            max_results (int): Maximum number of results
            
        Returns:
            list: List of message dictionaries
        """
        query_parts = []
        
        if after_date:
            query_parts.append(f"after:{after_date}")
        if before_date:
            query_parts.append(f"before:{before_date}")
        
        if not query_parts:
            raise ValueError("At least one date (after_date or before_date) must be provided")
        
        query = " ".join(query_parts)
        return self.search(query, max_results)
    
    def search_with_attachments(self, max_results=100):
        """
        Search for emails that have attachments.
        
        Args:
            max_results (int): Maximum number of results
            
        Returns:
            list: List of message dictionaries
        """
        query = "has:attachment"
        return self.search(query, max_results)
    
    def search_unread(self, max_results=100):
        """
        Search for unread emails.
        
        Args:
            max_results (int): Maximum number of results
            
        Returns:
            list: List of message dictionaries
        """
        query = "is:unread"
        return self.search(query, max_results)
    
    def get_message_count(self, query):
        """
        Get the total count of messages matching a query without retrieving them.
        
        Args:
            query (str): Gmail search query
            
        Returns:
            int: Total number of matching messages
        """
        if not self.service:
            self.authenticate()
        
        try:
            result = self.service.users().messages().list(
                userId='me', 
                q=query, 
                maxResults=1  # We only need the count
            ).execute()
            
            # Gmail returns resultSizeEstimate for the total count
            total_count = result.get('resultSizeEstimate', 0)
            print(f"Query '{query}' matches approximately {total_count} messages")
            return total_count
            
        except Exception as e:
            print(f"Error getting message count: {e}")
            return 0


def main():
    """Test the search functionality."""
    print("Testing Gmail Search Module...")
    
    # Test 1: Module imports correctly
    print("✅ Module imports successfully")
    
    # Test 2: Class instantiation
    try:
        searcher = GmailSearcher()
        print("✅ GmailSearcher class instantiates correctly")
    except Exception as e:
        print(f"❌ GmailSearcher instantiation failed: {e}")
        return
    
    # Test 3: Method availability
    methods_to_test = [
        'search', 'search_by_sender', 'search_by_subject', 
        'search_by_date_range', 'search_with_attachments', 
        'search_unread', 'get_message_count'
    ]
    
    for method_name in methods_to_test:
        if hasattr(searcher, method_name):
            print(f"✅ Method '{method_name}' available")
        else:
            print(f"❌ Method '{method_name}' missing")
    
    print("\n=== Module Structure Test Complete ===")
    print("Note: Authentication and actual search testing requires credentials.json")
    print("This module is ready for integration with authenticated GmailAuthenticator")


if __name__ == "__main__":
    main()

