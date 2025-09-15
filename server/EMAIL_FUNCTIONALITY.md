# Email Report Functionality

## Overview
The new `/send-report` endpoint allows users to request the latest accessibility report for a specific URL to be sent via email.

## API Endpoint

### POST /send-report
Send the latest accessibility report for a URL to the specified email address.

**Request Body:**
```json
{
    "email": "user@example.com",
    "url": "www.example.com"
}
```

**Response (Success):**
```json
{
    "message": "Report sent successfully",
    "email": "user@example.com",
    "url": "www.example.com",
    "report_file": "www.example.com_20250915160000.pdf",
    "report_date": "2025-09-15 16:00:00 UTC"
}
```

**Response (Error - No Report Found):**
```json
{
    "detail": "No accessibility report found for URL: www.nonexistent.com"
}
```

## File Structure

### Reports Directory
- Location: `/server/reports/`
- Naming Convention: `{url}_{datetime}.pdf`
  - `{url}`: URL with special characters replaced (https:// → '', / → '_', : → '_')
  - `{datetime}`: UTC timestamp in format YYYYMMDDHHMMSS
  - Example: `www.example.com_20250915160000.pdf`

### Mock PDFs Created
For testing purposes, the following mock PDFs have been created:
- `www.example.com_20250915120000.pdf`
- `www.example.com_20250915140000.pdf`
- `www.example.com_20250915160000.pdf` (latest)
- `www.google.com_20250915143000.pdf`

## Email Configuration

### Environment Variables
Add these to your `.env` file:

```env
# Email Configuration (for sending reports)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

### Gmail Setup (Recommended)
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use the generated app password (not your regular Gmail password)

### Alternative SMTP Providers
The system supports any SMTP server. Common configurations:

**Outlook/Hotmail:**
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

**Yahoo:**
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

## How It Works

1. **URL Matching**: The system normalizes the requested URL to match the filename pattern
2. **Report Discovery**: Searches the `/reports` directory for files matching the URL pattern
3. **Latest Selection**: Parses timestamps from filenames and selects the most recent report
4. **Email Composition**: Creates an email with the PDF as attachment
5. **Delivery**: Sends via configured SMTP server

## Testing

### Using the Test Script
```bash
python test_email.py
```

### Using curl
```bash
# Test with curl (server must be running)
curl -X POST "http://localhost:8000/send-report" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "url": "www.example.com"}'
```

### Using the FastAPI Docs
1. Start the server: `python app.py`
2. Go to: http://localhost:8000/docs
3. Find the `/send-report` endpoint
4. Click "Try it out"
5. Enter test data and execute

## Error Handling

The system handles various error scenarios:
- **404**: No report found for the specified URL
- **500**: Email configuration missing or invalid
- **500**: Email delivery failure
- **422**: Invalid email format or missing fields

## Security Notes

1. **Email Credentials**: Never commit actual email credentials to version control
2. **Rate Limiting**: Consider implementing rate limiting for the email endpoint
3. **Email Validation**: The system validates email format using pydantic's EmailStr
4. **File Access**: The system only accesses files within the designated reports directory

## Dependencies Added
- `email-validator`: For email format validation
- Standard library modules: `smtplib`, `email.mime.*`, `glob`, `re`

## GitIgnore Updates
The following entries were added to `.gitignore`:
- `server/reports/*.pdf` - Excludes generated PDF reports
- `venv/` - Excludes virtual environment folders
