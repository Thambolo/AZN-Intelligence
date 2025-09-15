# AZN-Intelligence: Intelligent Web Accessibility Analysis & Search Enhancement

## Project Overview

An intelligent web accessibility analysis system that automatically evaluates websites against WCAG 2.2 standards and enhances Google search results with accessibility grades. The system combines automated WCAG compliance scoring, AI-powered accessibility reports, intelligent search result reordering, and comprehensive email reporting capabilities.

## 🚀 Core Features

### 1. Auto Analyse and Grading on WCAG Standards

- **Real-time WCAG 2.2 compliance analysis** with automated scoring across all four principles
- **Weighted scoring system** prioritizing reliably analysable HTML-based criteria
- **Grade assignment** (AAA, AA, A, or Non-compliant) based on comprehensive evaluation
- **Detailed violation detection** with specific WCAG guideline references

### 2. Reordering Google Search Results by Accessibility Grade

- **Smart browser extension** that automatically analyses search result URLs
- **Visual accessibility badges** displayed on each search result with colour-coded grades
- **Intelligent result reordering** prioritizing more accessible websites
- **Non-intrusive integration** that enhances rather than replaces search functionality

### 3. AI-Powered Accessibility Reports

- **ConnectOnion meta-agent** generating comprehensive accessibility feedback
- **Intelligent recommendations** tailored to specific WCAG violations found
- **Fast execution** (~2-5 seconds) using optimized LLM calls
- **Structured output** with actionable developer guidance

### 4. Email Reporting System

- **Professional PDF reports** with detailed accessibility analysis
- **SMTP email delivery** for sharing reports with teams and stakeholders
- **Comprehensive documentation** including violation details and improvement suggestions
- **Automated report generation** from web extension or API endpoints

## 🏗️ Architecture

### Core Components

1. **Chrome Browser Extension** (`web-extension/`)

   - **Content Script**: Automatically detects Google search results and injects accessibility badges
   - **Popup Interface**: On-demand accessibility analysis with email reporting options
   - **Smart Badge System**: Click-to-analyze functionality with visual grade indicators
   - **Search Enhancement**: Intelligent reordering of search results based on accessibility scores

2. **FastAPI Web Server** (`server/app.py`)

   - RESTful API endpoints for accessibility analysis and email reporting
   - Async request handling for optimal performance
   - CORS configuration for seamless web extension integration
   - Email functionality with SMTP configuration

3. **Modular Analysis Engine** (`server/auto-analyse/`)

   - `web_analyser.py`: Central orchestrator with comprehensive_analyse_url function
   - `principle1_perceivable.py`: Text alternatives, media, adaptability analysis
   - `principle2_operable.py`: Keyboard accessibility, timing, navigation evaluation
   - `principle3_understandable.py`: Readability, predictability, input assistance
   - `principle4_robust.py`: Compatibility and parsing standards validation

4. **AI Meta-Agent System** (`server/meta-agent/`)
   - **ConnectOnion Framework**: AI-powered accessibility feedback generation
   - **Optimized Performance**: Fast execution using llm_do function calls
   - **Structured Output**: Consistent feedback and recommendations format
   - **PDF Report Generation**: Professional accessibility audit documentation

## 🔧 Technical Stack

### Backend Dependencies

- **Web Framework**: FastAPI 0.116.1 with Uvicorn 0.35.0
- **HTML Parsing**: BeautifulSoup4 4.13.5 for robust DOM analysis
- **HTTP Clients**: requests 2.32.5, aiohttp 3.12.15 for efficient web scraping
- **AI Integration**: OpenAI 1.107.2, connectonion 0.1.1 with litellm for model compatibility
- **PDF Generation**: PyMuPDF 1.26.4, fpdf2 2.8.4 for professional report creation
- **Email Services**: Built-in SMTP support for automated report delivery
- **Configuration**: python-dotenv 1.1.1 for secure environment management

### Frontend Technologies

- **Chrome Extension**: Manifest V3 compatibility with modern security standards
- **Content Scripts**: Advanced DOM manipulation for search result enhancement
- **Vanilla JavaScript**: ES6+ with async/await for optimal performance
- **Responsive CSS**: Grid/Flexbox layout with accessibility-focused design

## 🎯 How It Works

### Google Search Enhancement Workflow

1. **Automatic Detection**: Extension content script identifies Google search results
2. **Parallel Analysis**: Each result URL is analysed for WCAG compliance in the background
3. **Visual Indicators**: Accessibility badges (AAA, AA, A, or ⚠️) appear next to search results
4. **Smart Reordering**: Results are intelligently reorganized with more accessible sites promoted
5. **Click-to-Analyze**: Badge clicks trigger detailed analysis with email report options

### Accessibility Analysis Process

1. **HTML Retrieval**: Robust web scraping with proper user-agent headers and session management
2. **WCAG Evaluation**: Comprehensive analysis across all four WCAG 2.2 principles
3. **Weighted Scoring**: Intelligent scoring prioritizing reliably analysable HTML criteria
4. **AI Enhancement**: ConnectOnion meta-agent generates actionable feedback and recommendations
5. **Report Generation**: Professional PDF reports with detailed findings and improvement guidance

### Email Reporting System

1. **Report Compilation**: Combines automated analysis with AI-generated insights
2. **PDF Generation**: Professional formatting with WCAG compliance documentation
3. **SMTP Delivery**: Secure email delivery to specified recipients
4. **Team Collaboration**: Easy sharing of accessibility findings with development teams

## � Analysis Methodology

### WCAG 2.2 Compliance Assessment

**Intelligent Weighted Scoring System:**

- **Principles 1 & 2**: 70% weight (reliably analysable from HTML)
  - Perceivable: Images, headings, colour contrast, media accessibility
  - Operable: Keyboard navigation, focus management, timing controls
- **Principles 3 & 4**: 30% weight (contextual analysis with AI enhancement)
  - Understandable: Language, consistency, error identification
  - Robust: Valid markup, compatibility standards

### Advanced Analysis Features

1. **Comprehensive HTML Parsing**

   - BeautifulSoup4 for robust DOM analysis with error recovery
   - Custom user-agent headers ensuring website compatibility
   - Session management for consistent access across page resources

2. **UK English Standards Compliance**

   - "analyse" vs "analyze" terminology consistency
   - "colour" vs "color" specifications in documentation
   - "labelled" vs "labeled" conventions throughout codebase

3. **Multi-layered Scoring System**

   - Individual principle scores (0-100) with detailed breakdowns
   - Weighted overall accessibility score with transparent calculation
   - Specific violation identification with WCAG guideline references
   - AI-powered improvement recommendations with actionable steps

4. **Search Result Intelligence**
   - Real-time accessibility evaluation during Google searches
   - Dynamic badge assignment with visual grade indicators
   - Intelligent result reordering promoting accessible content
   - Non-intrusive enhancement preserving search experience

## 🛠️ API Endpoints

### Core Analysis Endpoints

- **`GET /comprehensive-analysis/{url}`**: Full WCAG analysis with AI-powered insights
- **`POST /test-meta-agent`**: AI feedback and recommendations generation
- **`POST /send-email-report`**: Email delivery of accessibility reports
- **`GET /health`**: System health and status monitoring

### Browser Extension Integration

- **Automatic Badge Injection**: Seamless integration with Google search results
- **Click-to-Analyze**: Instant detailed analysis from search result badges
- **Email Modal System**: In-browser email reporting with professional PDF attachments
- **Cross-browser Compatibility**: Chrome and Firefox support with Manifest V3

### Intelligent Caching System

- **JSON-based Cache**: Optimized accessibility result storage and retrieval
- **Performance Enhancement**: Significantly improved response times for repeated analyses
- **Smart Expiration**: Configurable cache policies balancing freshness and speed
- **Background Updates**: Proactive cache refreshing for frequently accessed sites

### Professional PDF Reporting

- **Comprehensive Audit Reports**: Detailed WCAG 2.2 compliance documentation
- **AI-Enhanced Insights**: Meta-agent generated feedback and recommendations
- **Developer-Focused Format**: Actionable violation listings with specific guidance
- **Professional Presentation**: Publication-ready reports for stakeholder sharing

## 🛠️ Development Setup

### Prerequisites

```bash
# Python 3.13+ with pip
python --version

# Virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

### Installation

```bash
# Clone repository
git clone https://github.com/Thambolo/AZN-Intelligence.git
cd AZN-Intelligence

# Install server dependencies
pip install -r server/requirements.txt

# Start development server
cd server
uvicorn app:app --reload --port 8000
```

### Environment Configuration

Create `server/.env`:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_key_here

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Model Configuration (optional)
MODEL=gpt-4o-mini-2024-07-18
max_completion_tokens=1500
```

### Browser Extension Setup

```bash
# Load extension in Chrome
1. Open Chrome and navigate to chrome://extensions/
2. Enable "Developer mode" in the top right
3. Click "Load unpacked" and select the web-extension/ folder
4. The AZN-Intelligence extension should appear in your toolbar

# Test functionality
1. Perform a Google search
2. Look for accessibility badges next to search results
3. Click badges to analyze specific websites
4. Use the extension popup for detailed analysis and email reporting
```

## 📁 Project Structure

```
AZN-Intelligence/
├── server/                    # Backend API server
│   ├── app.py                # FastAPI application with email endpoints
│   ├── requirements.txt      # Python dependencies
│   ├── auto-analyse/         # Core WCAG analysis modules
│   │   ├── web_analyser.py   # comprehensive_analyse_url orchestrator
│   │   ├── principle1_perceivable.py    # Text alternatives, media
│   │   ├── principle2_operable.py       # Keyboard, navigation
│   │   ├── principle3_understandable.py # Readability, consistency
│   │   └── principle4_robust.py         # Compatibility, parsing
│   ├── meta-agent/           # AI-powered reporting system
│   │   ├── agent.py          # ConnectOnion meta-analysis agent
│   │   └── rate_limiter.py   # API rate management
│   ├── cache/                # Analysis result caching
│   │   └── accessibility_cache.json
│   └── reports/              # Generated PDF reports
├── web-extension/            # Chrome browser extension
│   ├── manifest.json         # Extension configuration (Manifest V3)
│   ├── popup.html           # Extension popup interface
│   ├── popup.js             # Popup logic and email functionality
│   ├── content.js           # Google search enhancement script
│   ├── styles.css           # Extension styling
│   └── sw.js                # Service worker
└── docs/                    # Documentation
    ├── principles.md        # WCAG principles reference
    └── README.md            # This file
```

## 🎯 Usage Examples

### Browser Extension Usage

```javascript
// Automatic Google Search Enhancement
1. Install the AZN-Intelligence Chrome extension
2. Perform any Google search
3. Observe accessibility badges appearing next to search results
4. Click badges for instant detailed analysis
5. Use email modal to share reports with teams

// Manual Website Analysis
1. Navigate to any website
2. Click the AZN-Intelligence extension icon
3. Click "Analyze Current Page"
4. Review detailed WCAG compliance scores
5. Generate and email comprehensive PDF reports
```

### API Usage Examples

```bash
# Comprehensive WCAG analysis with AI insights
curl "http://localhost:8000/comprehensive-analysis/https://example.com"

# Generate AI feedback and recommendations
curl -X POST "http://localhost:8000/test-meta-agent" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Email accessibility report
curl -X POST "http://localhost:8000/send-email-report" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "recipient_email": "team@company.com",
    "analysis_result": {...}
  }'

# System health check
curl "http://localhost:8000/health"
```

### Integration Examples

```python
# Python integration example
import requests

# Analyze website accessibility
response = requests.get(
    "http://localhost:8000/comprehensive-analysis/https://example.com"
)
analysis = response.json()

print(f"Grade: {analysis['grade']}")
print(f"Score: {analysis['score']}/100")
print(f"Principle Scores: {analysis['principle_scores']}")
```

## 🔍 Analysis Capabilities

### Automated WCAG 2.2 Detection

- **Images & Media**: Alt text presence, quality assessment, and media accessibility features
- **Headings & Structure**: Proper hierarchy, semantic markup, and content organization
- **Forms & Controls**: Labels, validation, error handling, and accessibility features
- **Navigation & Focus**: Keyboard accessibility, focus indicators, and interaction patterns
- **Colour & Contrast**: Contrast ratios, colour-only information dependencies
- **Links & Content**: Descriptive link text, content readability, and semantic structure

### AI-Enhanced Analysis

- **ConnectOnion Meta-Agent**: Advanced AI feedback generation with structured output
- **Contextual Recommendations**: Specific improvement suggestions based on detected violations
- **Developer Guidance**: Actionable code examples and implementation strategies
- **Performance Optimization**: Fast execution (~2-5 seconds) using optimized LLM calls

### Search Result Intelligence

- **Real-time Evaluation**: Automatic accessibility analysis during Google searches
- **Visual Grade Indicators**: Colour-coded badges (🟢 AAA, 🔵 AA, 🟡 A, ⚠️ Non-compliant)
- **Smart Reordering**: Intelligent promotion of more accessible search results
- **Background Processing**: Non-blocking analysis preserving search performance

### Comprehensive Reporting

- **Professional PDF Generation**: Detailed audit reports with WCAG compliance documentation
- **Email Integration**: Automated report delivery with SMTP configuration
- **Multi-format Output**: JSON API responses and formatted PDF reports
- **Team Collaboration**: Easy sharing of findings with development and design teams

### Limitations & Considerations

- **JavaScript-dependent Content**: Limited analysis of dynamically generated content
- **User Interaction Flows**: Cannot test complex multi-step user journeys
- **Subjective Criteria**: Some WCAG requirements require human evaluation and context
- **Third-party Content**: Limited analysis of embedded widgets, ads, and external content
- **Performance Impact**: Analysis time varies based on page complexity and network conditions

## 🚀 Deployment

### Production Server Setup

```bash
# Production environment configuration
# Set up SSL/TLS certificates for HTTPS
# Configure reverse proxy (nginx recommended)
# Set up monitoring and logging systems
# Configure auto-scaling and load balancing

# Environment variables for production
export OPENAI_API_KEY="your_production_openai_key"
export SMTP_SERVER="your_production_smtp_server"
export SMTP_USERNAME="your_production_email"
export SMTP_PASSWORD="your_production_app_password"

# Start production server
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Browser Extension Distribution

```bash
# Build extension package for Chrome Web Store
1. Update manifest.json with production URLs
2. Test extension thoroughly across different websites
3. Create extension package (.zip) for store submission
4. Submit to Chrome Web Store with required metadata
5. Configure update mechanism for automatic updates
6. Set up user feedback collection and analytics

# Firefox Add-ons distribution (future enhancement)
1. Adapt manifest.json for Firefox compatibility
2. Test with Firefox-specific APIs and behaviours
3. Submit to Firefox Add-ons marketplace
```

### Docker Deployment (Optional)

```dockerfile
# Dockerfile example for containerized deployment
FROM python:3.13-slim

WORKDIR /app
COPY server/requirements.txt .
RUN pip install -r requirements.txt

COPY server/ .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

### Development Guidelines

- **UK English Conventions**: Maintain consistency with "analyse", "colour", "labelled" throughout codebase
- **Modular Architecture**: Preserve clear separation of concerns between analysis, AI, and reporting components
- **Comprehensive Testing**: Add tests for new analysis features and API endpoints
- **Dependency Management**: Update requirements.txt when adding new Python packages
- **Documentation**: Document new WCAG criteria implementations and API changes

### Code Quality Standards

- **Type Hints**: Use comprehensive type hints for all Python functions and methods
- **PEP 8 Compliance**: Follow Python style guidelines with consistent formatting
- **Error Handling**: Include robust error handling and informative logging
- **Performance**: Optimize analysis algorithms and API response times
- **Security**: Implement secure handling of API keys and user data

### Extension Development

- **Manifest V3**: Ensure compatibility with latest Chrome extension standards
- **Content Security**: Follow secure coding practices for content scripts
- **User Experience**: Maintain non-intrusive integration with search results
- **Cross-browser**: Test functionality across different browser environments

### AI and Analysis Enhancement

- **ConnectOnion Integration**: Optimize meta-agent performance and output quality
- **WCAG Updates**: Stay current with WCAG 2.2 guidelines and emerging standards
- **Model Compatibility**: Ensure compatibility with various LLM providers and models
- **Feedback Quality**: Continuously improve AI-generated recommendations and insights

## 📈 Future Enhancements

### Planned Core Features

- **Real-time Accessibility Monitoring**: Continuous tracking of website accessibility improvements over time
- **Advanced Search Intelligence**: Enhanced search result reordering with user preference learning
- **Team Collaboration Platform**: Multi-user accessibility auditing with shared dashboards and progress tracking
- **Mobile App Development**: Dedicated mobile accessibility analysis application
- **CMS Integrations**: WordPress, Shopify, and major CMS platform plugins for seamless accessibility monitoring

### AI and Analysis Improvements

- **Machine Learning Enhancement**: Advanced ML algorithms for better accessibility pattern detection
- **Multi-language Support**: International accessibility standard compliance beyond WCAG 2.2
- **Automated Testing Integration**: CI/CD pipeline integration for continuous accessibility testing
- **Predictive Analysis**: AI-powered prediction of accessibility issues before deployment
- **Custom Rule Engine**: User-defined accessibility criteria and custom compliance frameworks

### Technical Infrastructure Enhancements

- **Performance Optimization**: Faster analysis algorithms with improved caching strategies
- **Microservices Architecture**: Distributed analysis system for enhanced scalability
- **Enhanced Caching**: Redis/database-backed caching with intelligent invalidation
- **GraphQL API**: More flexible query capabilities for complex data requirements
- **WebSocket Support**: Real-time analysis updates and collaborative features
- **Advanced Email Templates**: Rich HTML email reports with interactive elements

### Browser Extension Evolution

- **Firefox Compatibility**: Full cross-browser support with Firefox Add-ons distribution
- **Advanced Search Features**: Filtering, sorting, and custom accessibility criteria in search results
- **Offline Analysis**: Local accessibility analysis capabilities for improved privacy
- **Accessibility Insights Dashboard**: Comprehensive analytics and trending data visualization
- **User Customization**: Personalized accessibility priorities and scoring preferences

## 📝 License & Acknowledgments

### Project License

This project is part of the AIP Hackathon and follows the terms specified in the hackathon guidelines.

### Key Technologies

- **FastAPI**: High-performance web framework for building APIs
- **ConnectOnion**: AI agent framework for intelligent accessibility analysis
- **BeautifulSoup4**: Robust HTML parsing and DOM manipulation
- **Chrome Extensions API**: Browser integration for seamless user experience
- **OpenAI API**: Advanced language models for intelligent report generation

### WCAG Compliance

This system implements **WCAG 2.2 Level AA standards** with comprehensive analysis across all four foundational principles of accessibility.

---

**Last Updated**: September 2025  
**Version**: 3.0.0 - Intelligent Search Enhancement Release  
**WCAG Compliance**: 2.2 Level AA Standards  
**Browser Support**: Chrome (Manifest V3), Firefox compatibility planned  
**AI Framework**: ConnectOnion with OpenAI GPT integration
