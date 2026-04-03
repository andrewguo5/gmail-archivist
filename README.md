# Gmail Archivist

A Python tool to automatically archive old Gmail messages while preserving starred conversations.

## Features

- Archive Gmail messages older than a specified time threshold (e.g., 3 days, 1 week, 2 months)
- Automatically skip starred messages and all messages in their threads
- Batch processing for large operations with progress logging
- Interactive confirmation before archiving
- Configurable search iterations and batch sizes

## Prerequisites

- Python 3.10 or higher
- A Google account with Gmail
- Google Cloud project with Gmail API enabled

## Installation

### Option 1: Install from PyPI (recommended)

```bash
pip install gmail-archivist
```

### Option 2: Install from source

```bash
git clone https://github.com/andrewguo5/gmail-archivist.git
cd gmail-archivist
pip install -r requirements.txt
```

## Google API Setup

Before using Gmail Archivist, you need to set up Gmail API credentials:

### 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name your project (e.g., "Gmail Archivist") and click "Create"

### 2. Enable Gmail API

1. In your project, go to **APIs & Services** → **Library**
2. Search for "Gmail API"
3. Click on it and press "Enable"

### 3. Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select "External" user type and click "Create"
3. Fill in the required fields:
   - App name: "Gmail Archivist" (or your preferred name)
   - User support email: your email
   - Developer contact: your email
4. Click "Save and Continue"
5. On the "Scopes" page, click "Save and Continue" (we'll add scopes via code)
6. On the "Test users" page, add your Gmail address as a test user
7. Click "Save and Continue"

### 4. Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click "Create Credentials" → "OAuth client ID"
3. Select "Desktop app" as the application type
4. Name it "Gmail Archivist Client"
5. Click "Create"
6. Click "Download JSON" on the credential you just created
7. Rename the downloaded file to `credentials.json`
8. Place `credentials.json` in the directory where you'll run the tool

## Usage

### Basic Usage

Archive emails older than 3 days (default):

```bash
python archive_messages.py
```

Or if installed via PyPI:

```bash
gmail-archivist
```

### Custom Time Threshold

Archive emails older than 1 week:

```bash
python archive_messages.py --ttl 1w
```

Archive emails older than 2 months:

```bash
python archive_messages.py --ttl 2m
```

Supported time formats:
- `d` for days (e.g., `3d`, `7d`)
- `w` for weeks (e.g., `1w`, `2w`)
- `m` for months (e.g., `1m`, `6m`)

### Advanced Options

```bash
python archive_messages.py --ttl 7d --max-iter 500 --max-results 100
```

Options:
- `--ttl`: Time threshold for archiving (default: `3d`)
- `--max-iter`: Maximum number of search iterations (default: `1000`)
- `--max-results`: Maximum emails to fetch per iteration (default: `500`)

### First Run

On the first run:
1. A browser window will open asking you to authorize the application
2. Sign in with your Google account
3. Click "Continue" when you see the "unverified app" warning (this is normal for personal projects)
4. Grant the requested permissions
5. The tool will create a `token.json` file to store your credentials for future runs

## How It Works

1. **Discovery**: Searches for all messages in your inbox older than the specified TTL
2. **Starred Protection**: Identifies all starred messages and expands to include all messages in their threads
3. **Filtering**: Removes starred messages (and their threads) from the archive list
4. **Confirmation**: Shows a summary and asks for confirmation
5. **Archiving**:
   - For < 100 messages: Processes individually
   - For ≥ 100 messages: Processes in batches of up to 1000 messages (Google API limit)
6. **Validation**: Samples random messages to verify archiving succeeded

## Batch Processing

When archiving 100+ messages, the tool automatically uses batch operations:

```
=== Archive Summary ===
Total messages found: 2500
Starred messages (skipped): 150
Messages to archive: 2350
=======================

Operation will be batched:
  Batch size: 1000 messages per batch
  Total batches: 3

Processing batch 1/3 (1000 messages)...
Batch 1/3 completed.
Processing batch 2/3 (1000 messages)...
Batch 2/3 completed.
Processing batch 3/3 (350 messages)...
Batch 3/3 completed.
```

## Security & Privacy

- Your credentials never leave your machine
- The `credentials.json` and `token.json` files contain sensitive data and are excluded from version control
- The tool only requests `gmail.modify` scope (read and modify labels, not delete messages)
- All operations are performed locally through Google's official API

## Troubleshooting

### "The file token.json stores invalid credentials"
Delete `token.json` and run the tool again to re-authenticate.

### "Access blocked: Gmail Archivist has not completed the Google verification process"
Make sure you added your email as a test user in the OAuth consent screen settings.

### Rate limit errors
The tool respects Google's API quotas. If you hit rate limits, wait a few minutes and try again with smaller `--max-results` values.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this tool for personal or commercial projects.

## Acknowledgments

Built using the [Gmail API Python Client](https://github.com/googleapis/google-api-python-client).
