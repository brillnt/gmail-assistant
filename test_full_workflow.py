#!/usr/bin/env python3
"""
Gmail Assistant Full Workflow Test

Tests the complete workflow: Authentication -> Search -> Retrieval -> Export
This demonstrates the full capabilities for research projects.
"""

import sys
import os
from datetime import datetime, timedelta

# Add src directory to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gmail_auth import GmailAuthenticator
from gmail_search import GmailSearcher
from gmail_retriever import GmailRetriever


def test_research_workflow():
    """Test a complete research workflow similar to what would be used for client analysis."""
    print("=== Gmail Assistant Full Workflow Test ===\n")
    
    try:
        # Step 1: Authentication
        print("1. Authenticating with Gmail...")
        auth = GmailAuthenticator()
        service = auth.authenticate()
        print("✅ Authentication successful\n")
        
        # Step 2: Initialize components
        searcher = GmailSearcher(authenticator=auth)
        retriever = GmailRetriever(authenticator=auth)
        
        # Step 3: Research-style searches
        print("2. Performing research-style searches...")
        
        # Search for recent emails (last 7 days)
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y/%m/%d')
        recent_query = f"after:{seven_days_ago}"
        recent_count = searcher.get_message_count(recent_query)
        print(f"   📧 Recent emails (last 7 days): {recent_count}")
        
        # Search for emails with attachments
        attachment_count = searcher.get_message_count("has:attachment")
        print(f"   📎 Emails with attachments: {attachment_count}")
        
        # Search for specific sender (using one from our test data)
        sender_results = searcher.search("from:julie@songbirdcreative.com", max_results=5)
        print(f"   👤 Emails from julie@songbirdcreative.com: {len(sender_results)}")
        
        # Step 4: Export workflow test
        print("\n3. Testing export workflow...")
        
        # Export recent emails (small sample for testing)
        export_summary = retriever.export_search_results(
            search_query=f"after:{seven_days_ago}",
            max_results=5,
            output_prefix="research_sample"
        )
        
        print(f"✅ Export completed:")
        print(f"   Query: {export_summary['search_query']}")
        print(f"   Messages exported: {export_summary['message_count']}")
        print(f"   Files created: {len(export_summary['files_created'])}")
        
        # Step 5: Demonstrate client-specific search
        print("\n4. Demonstrating client-specific research capabilities...")
        
        # Example searches that would be useful for project analysis
        example_queries = [
            "subject:project",
            "subject:meeting", 
            "has:attachment subject:contract",
            f"after:{seven_days_ago} subject:deadline"
        ]
        
        for query in example_queries:
            count = searcher.get_message_count(query)
            print(f"   '{query}': {count} messages")
        
        print("\n=== Full Workflow Test Complete ===")
        print("🎉 Gmail Assistant is ready for research projects!")
        
        # Summary of capabilities
        print("\n📋 Research Capabilities Summary:")
        print("   ✅ Authenticate with Gmail API")
        print("   ✅ Search by sender, subject, date range, attachments")
        print("   ✅ Retrieve full email content and metadata")
        print("   ✅ Export to JSON (full data), CSV (metadata), TXT (readable)")
        print("   ✅ Handle large datasets with progress tracking")
        print("   ✅ Work with Gmail's native data formats")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False


def demonstrate_client_research():
    """Demonstrate how this would be used for actual client research."""
    print("\n" + "="*60)
    print("CLIENT RESEARCH DEMONSTRATION")
    print("="*60)
    
    print("\nFor your website project efficiency research, you would:")
    print("\n1. Search for specific client emails:")
    print("   searcher.search('from:john@keylightdevelopment.com')")
    print("   searcher.search('from:johnmichaelboros@gmail.com')")
    
    print("\n2. Find project-specific communications:")
    print("   searcher.search('subject:Fuller Homes')")
    print("   searcher.search('from:john@keylightdevelopment.com subject:project')")
    
    print("\n3. Analyze timeline patterns:")
    print("   searcher.search('from:john@keylightdevelopment.com after:2023/01/01 before:2023/12/31')")
    
    print("\n4. Export for analysis:")
    print("   retriever.export_search_results('from:john@keylightdevelopment.com', max_results=100)")
    
    print("\n5. Then you and I would analyze the exported data to identify:")
    print("   • Timeline estimation accuracy")
    print("   • Scope creep patterns")
    print("   • Communication frequency and stress indicators")
    print("   • Revenue protection opportunities")


if __name__ == "__main__":
    success = test_research_workflow()
    
    if success:
        demonstrate_client_research()
        print(f"\n🚀 Gmail Assistant is ready for your project efficiency research!")
    else:
        print(f"\n❌ Please check the setup and try again.")

