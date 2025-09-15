# AZN-Intelligence: WCAG 2.2 Accessibility Analysis System

## Project Overview

A comprehensive web accessibility analysis system that evaluates websites against the Web Content Accessibility Guidelines (WCAG) 2.2 standards. The system provides automated accessibility scoring across all four WCAG principles with detailed analysis and reporting capabilities.

## 🏗️ Architecture

### Core Components

1. **FastAPI Web Server** (`server/app.py`)

   - RESTful API endpoints for accessibility analysis
   - Async request handling for optimal performance
   - CORS configuration for web extension integration

2. **Modular Analysis Engine** (`server/auto-analyse/`)

   - `web_analyser.py`: Central orchestrator with weighted scoring
   - `principle1_perceivable.py`: Text alternatives, media, adaptability
   - `principle2_operable.py`: Keyboard accessibility, timing, navigation
   - `principle3_understandable.py`: Readability, predictability, input assistance
   - `principle4_robust.py`: Compatibility, parsing standards

3. **Meta-Agent System** (`server/meta-agent/`)

   - AI-powered comprehensive accessibility reporting
   - PDF generation for detailed audit reports
   - Rate limiting and caching for API efficiency

4. **Browser Extension** (`web-extension/`)
   - Chrome/Firefox compatible extension
   - Real-time accessibility analysis
   - User-friendly popup interface

## 🔧 Technical Stack

### Backend Dependencies

- **Web Framework**: FastAPI 0.116.1 with Uvicorn 0.35.0
- **HTML Parsing**: BeautifulSoup4 4.13.5
- **HTTP Clients**: requests 2.32.5, aiohttp 3.12.15
- **AI Integration**: OpenAI 1.107.2, connectonion 0.1.1
- **PDF Generation**: PyMuPDF 1.26.4, fpdf2 2.8.4
- **Configuration**: python-dotenv 1.1.1

### Frontend Technologies

- Vanilla JavaScript (ES6+)
- Chrome Extension Manifest V3
- Responsive CSS Grid/Flexbox

## 📊 Analysis Methodology

### WCAG 2.2 Compliance Assessment

**Weighted Scoring System:**

- **Principles 1 & 2**: 70% weight (reliably analysable from HTML)
  - Perceivable: Images, headings, colour contrast, media
  - Operable: Keyboard navigation, focus management, timing
- **Principles 3 & 4**: 30% weight (limited HTML analysis capability)
  - Understandable: Language, consistency, error identification
  - Robust: Valid markup, compatibility standards

### Analysis Features

1. **Comprehensive HTML Parsing**

   - BeautifulSoup4 for robust DOM analysis
   - Custom user-agent headers for website compatibility
   - Session management for consistent access

2. **Detailed Scoring**
   - Individual principle scores (0-100)
   - Weighted overall accessibility score
   - Specific violation identification
   - Improvement recommendations

## 🚀 Key Features

### Web API Endpoints

- `GET /analyse/{url}`: Basic accessibility analysis
- `POST /send-report`: Send AI-powered accessibility report
- `GET /health`: System health check

### Browser Extension

- One-click accessibility analysis
- Visual score display with colour-coded results
- Direct link to detailed reports

### Caching System

- JSON-based accessibility cache
- Improved response times for repeated analyses
- Configurable cache expiration

### PDF Reporting

- Professional accessibility audit reports
- WCAG 2.2 compliance documentation
- Detailed violation listings and recommendations

## 🛠️ Development Setup

### Prerequisites

```bash
# Python 3.13+ with pip
python --version

# Virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # macOS/Linux
```

### Installation

```bash
# Install dependencies
pip install -r server/requirements.txt

# Start development server
cd server
uvicorn app:app --reload --port 8000
```

### Environment Configuration

Create `server/.env`:

```env
OPENAI_API_KEY=your_openai_key_here
# Add other API keys as needed
```

## 📁 Project Structure

```
AZN-Intelligence/
├── server/
│   ├── app.py                 # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   ├── auto-analyse/          # Core analysis modules
│   │   ├── web_analyser.py    # Analysis orchestrator
│   │   ├── principle1_perceivable.py
│   │   ├── principle2_operable.py
│   │   ├── principle3_understandable.py
│   │   └── principle4_robust.py
│   ├── meta-agent/            # AI reporting system
│   │   ├── agent.py           # Meta-analysis agent
│   │   └── rate_limiter.py    # API rate management
│   └── cache/                 # Analysis result cache
├── web-extension/             # Browser extension
│   ├── manifest.json          # Extension configuration
│   ├── popup.html             # Extension UI
│   ├── popup.js               # Extension logic
│   └── content.js             # Content script
└── docs/                      # Documentation
    ├── principles.md          # WCAG principles reference
    └── PROJECT_OVERVIEW.md    # This file
```

## 🎯 Usage Examples

### API Usage

```bash
# Basic analysis
curl "http://localhost:8000/analyse/https://example.com"

# Comprehensive analysis
curl "http://localhost:8000/comprehensive-analysis/https://example.com"
```

### Browser Extension

1. Load extension in Chrome/Firefox developer mode
2. Navigate to any website
3. Click extension icon for instant analysis
4. View detailed scores and recommendations

## 🔍 Analysis Capabilities

### Automated Detection

- **Images**: Alt text presence and quality
- **Headings**: Proper hierarchy and structure
- **Forms**: Labels, validation, accessibility features
- **Navigation**: Keyboard accessibility, focus indicators
- **Colour**: Contrast ratios and colour-only information
- **Media**: Captions, transcripts, autoplay prevention

### Limitations

- **JavaScript-dependent content**: Limited analysis of dynamic content
- **User interaction flows**: Cannot test complex user journeys
- **Subjective criteria**: Some WCAG requirements need human evaluation
- **Third-party content**: Limited analysis of embedded widgets/ads

## 🚀 Deployment

### Production Setup

1. Configure environment variables
2. Set up SSL/TLS certificates
3. Configure reverse proxy (nginx recommended)
4. Set up monitoring and logging
5. Configure auto-scaling if needed

### Browser Extension Distribution

1. Build extension package
2. Submit to Chrome Web Store / Firefox Add-ons
3. Configure update mechanism
4. Set up user feedback collection

## 🤝 Contributing

### Development Guidelines

- Follow UK English conventions in code and documentation
- Maintain modular architecture with clear separation of concerns
- Add comprehensive tests for new analysis features
- Update requirements.txt when adding dependencies
- Document new WCAG criteria implementations

### Code Quality

- Use type hints for Python functions
- Follow PEP 8 style guidelines
- Write descriptive commit messages
- Include error handling and logging

## 📈 Future Enhancements

### Planned Features

- **Real-time monitoring**: Continuous accessibility tracking
- **Advanced AI analysis**: Machine learning for better scoring
- **Integration APIs**: WordPress, Shopify, and CMS plugins
- **Mobile app**: Dedicated mobile accessibility analysis
- **Team collaboration**: Multi-user accessibility auditing
- **Automated testing**: CI/CD pipeline integration

### Technical Improvements

- **Performance optimisation**: Faster analysis algorithms
- **Enhanced caching**: Redis/database-backed caching
- **Microservices**: Distributed analysis architecture
- **GraphQL API**: More flexible query capabilities
- **WebSocket support**: Real-time analysis updates

## 📝 License

This project is part of the AIP Hackathon and follows the terms specified in the hackathon guidelines.

---

**Last Updated**: January 2025  
**Version**: 2.0.0  
**WCAG Compliance**: 2.2 Level AA Standards
