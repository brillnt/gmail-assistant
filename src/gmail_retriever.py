#!/usr/bin/env python3
"""
Gmail Email Retrieval and Export Module

Handles retrieving full email content and exporting data in various formats.
Works with Gmail's native JSON format to minimize data transformation.
"""

import json
import csv
import base64
import re
from datetime import datetime
from gmail_auth import GmailAuthenticator


class GmailRetriever:
    """Handles retrieving full email content and exporting data."""
    
    def __init__(self, authenticator=None, credentials_file=None):
        """
        Initialize the retriever.
        
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
    
    def get_full_message(self, message_id):
        """
        Retrieve full message content by ID.
        
        Args:
            message_id (str): Gmail message ID
            
        Returns:
            dict: Full message data in Gmail's native JSON format
        """
        if not self.service:
            self.authenticate()
        
        try:
            # Get full message with all parts
            message = self.service.users().messages().get(
                userId='me', 
                id=message_id, 
                format='full'
            ).execute()
            
            return message
            
        except Exception as e:
            print(f"Error retrieving message {message_id}: {e}")
            return None
    
    def get_multiple_messages(self, message_ids, show_progress=True):
        """
        Retrieve multiple messages by their IDs.
        
        Args:
            message_ids (list): List of Gmail message IDs
            show_progress (bool): Whether to show progress updates
            
        Returns:
            list: List of full message data dictionaries
        """
        if not self.service:
            self.authenticate()
        
        messages = []
        total = len(message_ids)
        
        if show_progress:
            print(f"Retrieving {total} messages...")
        
        for i, msg_id in enumerate(message_ids):
            if show_progress and (i + 1) % 10 == 0:
                print(f"Retrieved {i + 1}/{total} messages...")
            
            message = self.get_full_message(msg_id)
            if message:
                messages.append(message)
        
        if show_progress:
            print(f"Successfully retrieved {len(messages)} messages")
        
        return messages
    
    def extract_email_body(self, message):
        """
        Extract readable text body from a Gmail message.
        
        Args:
            message (dict): Full Gmail message data
            
        Returns:
            str: Extracted email body text
        """
        def decode_base64(data):
            """Decode base64 email content."""
            try:
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
            except:
                return ""
        
        def extract_from_payload(payload):
            """Recursively extract text from message payload."""
            body_text = ""
            
            # Check if this part has body data
            if 'body' in payload and 'data' in payload['body']:
                if payload.get('mimeType') == 'text/plain':
                    body_text += decode_base64(payload['body']['data'])
                elif payload.get('mimeType') == 'text/html':
                    # For HTML, we'll include it but could add HTML stripping later
                    html_content = decode_base64(payload['body']['data'])
                    # Simple HTML tag removal (basic)
                    clean_text = re.sub(r'<[^>]+>', '', html_content)
                    body_text += clean_text
            
            # Check for parts (multipart messages)
            if 'parts' in payload:
                for part in payload['parts']:
                    body_text += extract_from_payload(part)
            
            return body_text
        
        if 'payload' in message:
            return extract_from_payload(message['payload'])
        
        return ""
    
    def extract_message_metadata(self, message):
        """
        Extract key metadata from a Gmail message.
        
        Args:
            message (dict): Full Gmail message data
            
        Returns:
            dict: Extracted metadata
        """
        # Extract headers
        headers = message.get('payload', {}).get('headers', [])
        header_dict = {h['name']: h['value'] for h in headers}
        
        # Extract attachments info
        attachments = []
        def find_attachments(payload):
            if 'parts' in payload:
                for part in payload['parts']:
                    if 'filename' in part and part['filename']:
                        attachments.append({
                            'filename': part['filename'],
                            'mimeType': part.get('mimeType', ''),
                            'size': part.get('body', {}).get('size', 0)
                        })
                    find_attachments(part)
        
        find_attachments(message.get('payload', {}))
        
        # Parse date
        date_str = header_dict.get('Date', '')
        parsed_date = None
        if date_str:
            try:
                # Try to parse the date string
                parsed_date = datetime.strptime(
                    date_str.split(' (')[0].strip(), 
                    '%a, %d %b %Y %H:%M:%S %z'
                ).isoformat()
            except:
                parsed_date = date_str
        
        return {
            'id': message['id'],
            'thread_id': message['threadId'],
            'labels': message.get('labelIds', []),
            'snippet': message.get('snippet', ''),
            'from': header_dict.get('From', ''),
            'to': header_dict.get('To', ''),
            'cc': header_dict.get('Cc', ''),
            'bcc': header_dict.get('Bcc', ''),
            'subject': header_dict.get('Subject', ''),
            'date': parsed_date,
            'date_raw': date_str,
            'attachments': attachments,
            'attachment_count': len(attachments)
        }
    
    def save_messages_json(self, messages, filename):
        """
        Save messages to JSON file in Gmail's native format.
        
        Args:
            messages (list): List of Gmail message dictionaries
            filename (str): Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(messages, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(messages)} messages to {filename}")
        except Exception as e:
            print(f"Error saving to JSON: {e}")
    
    def save_messages_csv(self, messages, filename):
        """
        Save message metadata to CSV file.
        
        Args:
            messages (list): List of Gmail message dictionaries
            filename (str): Output filename
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if not messages:
                    print("No messages to save")
                    return
                
                # Extract metadata from first message to get fieldnames
                sample_metadata = self.extract_message_metadata(messages[0])
                fieldnames = list(sample_metadata.keys()) + ['body_preview']
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for message in messages:
                    metadata = self.extract_message_metadata(message)
                    # Add body preview (first 200 chars)
                    body = self.extract_email_body(message)
                    metadata['body_preview'] = body[:200] + '...' if len(body) > 200 else body
                    writer.writerow(metadata)
            
            print(f"Saved {len(messages)} messages to {filename}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")
    
    def save_messages_text(self, messages, filename):
        """
        Save messages as readable text file.
        
        Args:
            messages (list): List of Gmail message dictionaries
            filename (str): Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for i, message in enumerate(messages, 1):
                    metadata = self.extract_message_metadata(message)
                    body = self.extract_email_body(message)
                    
                    f.write(f"{'='*60}\n")
                    f.write(f"MESSAGE {i} of {len(messages)}\n")
                    f.write(f"{'='*60}\n")
                    f.write(f"ID: {metadata['id']}\n")
                    f.write(f"From: {metadata['from']}\n")
                    f.write(f"To: {metadata['to']}\n")
                    f.write(f"Subject: {metadata['subject']}\n")
                    f.write(f"Date: {metadata['date']}\n")
                    if metadata['attachments']:
                        f.write(f"Attachments: {len(metadata['attachments'])} files\n")
                    f.write(f"\nBody:\n{'-'*40}\n")
                    f.write(body)
                    f.write(f"\n\n")
            
            print(f"Saved {len(messages)} messages to {filename}")
        except Exception as e:
            print(f"Error saving to text: {e}")
    
    def export_search_results(self, search_query, max_results=100, output_prefix="gmail_export"):
        """
        Complete workflow: search, retrieve, and export messages.
        
        Args:
            search_query (str): Gmail search query
            max_results (int): Maximum number of messages to retrieve
            output_prefix (str): Prefix for output filenames
            
        Returns:
            dict: Summary of exported data
        """
        # Import here to avoid circular imports
        from gmail_search import GmailSearcher
        
        print(f"Starting export for query: '{search_query}'")
        
        # Step 1: Search for messages
        searcher = GmailSearcher(authenticator=self.auth)
        search_results = searcher.search(search_query, max_results)
        
        if not search_results:
            print("No messages found to export")
            return {'message_count': 0, 'files_created': []}
        
        # Step 2: Get message IDs
        message_ids = [msg['id'] for msg in search_results]
        
        # Step 3: Retrieve full messages
        full_messages = self.get_multiple_messages(message_ids)
        
        # Step 4: Export in multiple formats
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        files_created = []
        
        # JSON export (full Gmail data)
        json_file = f"{output_prefix}_{timestamp}.json"
        self.save_messages_json(full_messages, json_file)
        files_created.append(json_file)
        
        # CSV export (metadata)
        csv_file = f"{output_prefix}_{timestamp}.csv"
        self.save_messages_csv(full_messages, csv_file)
        files_created.append(csv_file)
        
        # Text export (readable format)
        text_file = f"{output_prefix}_{timestamp}.txt"
        self.save_messages_text(full_messages, text_file)
        files_created.append(text_file)
        
        summary = {
            'search_query': search_query,
            'message_count': len(full_messages),
            'files_created': files_created,
            'timestamp': timestamp
        }
        
        print(f"\nExport complete!")
        print(f"Messages exported: {len(full_messages)}")
        print(f"Files created: {', '.join(files_created)}")
        
        return summary


def main():
    """Test the retrieval and export functionality."""
    print("Testing Gmail Retrieval and Export...")
    
    retriever = GmailRetriever()
    
    try:
        # Test export workflow with a small sample
        print("\n=== Testing Export Workflow ===")
        summary = retriever.export_search_results(
            search_query="is:inbox",
            max_results=3,
            output_prefix="test_export"
        )
        
        print(f"\nExport Summary:")
        print(f"Query: {summary['search_query']}")
        print(f"Messages: {summary['message_count']}")
        print(f"Files: {summary['files_created']}")
        
    except Exception as e:
        print(f"Export test failed: {e}")


if __name__ == "__main__":
    main()

