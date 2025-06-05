#!/usr/bin/env python3
"""
Gmail Search Integration Test

This script tests the search functionality with real Gmail credentials.
Run this from the project root directory after setting up credentials.json
"""

import sys
import os

# Add src directory to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gmail_auth import GmailAuthenticator
from gmail_search import GmailSearcher


def test_search_integration():
    """Test the search functionality with real Gmail authentication."""
    print("=== Gmail Search Integration Test ===\n")
    
    try:
        # Test 1: Authentication
        print("1. Testing Authentication...")
        auth = GmailAuthenticator()
        service = auth.authenticate()
        print("✅ Authentication successful")
        
        # Test 2: Search Integration
        print("\n2. Testing Search Integration...")
        searcher = GmailSearcher(authenticator=auth)
        print("✅ Search module integrated with authenticator")
        
        # Test 3: Basic Search
        print("\n3. Testing Basic Search (first 3 inbox messages)...")
        results = searcher.search("is:inbox", max_results=3)
        
        if results:
            print(f"✅ Found {len(results)} messages")
            for i, msg in enumerate(results, 1):
                print(f"\n   Message {i}:")
                print(f"   From: {msg['from']}")
                print(f"   Subject: {msg['subject']}")
                print(f"   Date: {msg['date']}")
                print(f"   Snippet: {msg['snippet'][:80]}...")
        else:
            print("❌ No messages found in inbox")
        
        # Test 4: Message Count
        print("\n4. Testing Message Count...")
        inbox_count = searcher.get_message_count("is:inbox")
        print(f"✅ Total inbox messages: {inbox_count}")
        
        # Test 5: Search by Date (last 30 days)
        print("\n5. Testing Date Range Search (last 30 days)...")
        from datetime import datetime, timedelta
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y/%m/%d')
        recent_count = searcher.get_message_count(f"after:{thirty_days_ago}")
        print(f"✅ Messages in last 30 days: {recent_count}")
        
        print("\n=== All Tests Passed! ===")
        print("The Gmail search functionality is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = test_search_integration()
    if success:
        print("\n🎉 Gmail Search is ready for use!")
    else:
        print("\n❌ Please check your setup and try again.")

