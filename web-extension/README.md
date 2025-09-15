## Chrome Extension Setup

1. Project structure

```
web-extension/
  ├── manifest.json         # MV3 manifest
  ├── sw.js                 # background service worker
  ├── content.js            # runs on Google Search page
  ├── popup.html            # optional popup
  ├── popup.js              # optional popup logic (rescan)
  └── styles.css            # badge style
```

## Setup Instructions

1. **Install the Extension:**
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" in the top right
   - Click "Load unpacked" and select this `web-extension` folder

2. **Configure Server URL (Optional):**
   - The extension defaults to `http://localhost:8000`
   - To change the server URL:
     - Go to `chrome://extensions/`
     - Find "Grade-Able" extension
     - Click the "Details" button
     - Click "Extension options"
     - Set your custom server URL (e.g., `https://your-server.com`)
   - Click "Save Options"

3. **Start Your Server:**
   - Make sure your FastAPI server is running on the configured URL
   - Default: `python app.py` (runs on localhost:8000)

4. **Usage:**
   - Go to Google and search for anything
   - Accessibility badges will appear next to search results
   - **Click any badge** to open the email modal
   - Enter your email address and click "Send Report" to receive a PDF report

## Email Feature

The extension now includes an email feature that allows users to request accessibility reports:

- **Click Badge**: Click on any accessibility badge (AAA, AA, A, B, C) next to search results
- **Email Modal**: A sleek modal will appear asking for your email address  
- **Send Report**: Click "Send Report" to receive a detailed PDF accessibility report
- **Notifications**: Success/error messages appear in the top-right corner

## Features

- Real-time accessibility analysis of Google search results
- Visual badges with grades (AAA, AA, A, B, C) 
- Click-to-email functionality for detailed reports
- Modern, responsive modal design
- Success/error notifications
- Configurable server URL
