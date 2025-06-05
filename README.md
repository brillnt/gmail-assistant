# Gmail Assistant

A focused tool for systematically retrieving Gmail emails for research purposes.

## Purpose

This tool is designed to:
- Authenticate with Gmail API using OAuth2
- Search for emails using Gmail's native search syntax
- Retrieve email data in its natural JSON format
- Export data for collaborative analysis

## Setup Requirements

### 1. Google Cloud Project Setup
You need to create a Google Cloud project and enable the Gmail API:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Gmail API
4. Configure OAuth consent screen
5. Create OAuth 2.0 credentials for a desktop application
6. Download the credentials as `credentials.json`

### 2. Python Dependencies
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 3. Credentials File
Place your `credentials.json` file in the project root directory.

## Project Structure

```
gmail-assistant/
├── src/
│   ├── gmail_auth.py      # Authentication module
│   ├── gmail_search.py    # Search functionality
│   └── gmail_export.py    # Data export utilities
├── tests/
├── docs/
├── credentials.json       # Your OAuth2 credentials (not in git)
└── README.md
```

## Usage

The tool is built incrementally with each module tested independently:

1. **Authentication**: Handles OAuth2 flow and token management
2. **Search**: Executes Gmail searches and retrieves message IDs
3. **Retrieval**: Gets full email content in native JSON format
4. **Export**: Saves data for analysis

## Security

- `credentials.json` and `token.pickle` are excluded from git
- Uses read-only Gmail scope for security
- All authentication handled through Google's OAuth2 flow

## Development

This project uses incremental development with Git commits for each working component.

