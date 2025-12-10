# 🎯 Competition Monitor

> Desktop application for competitor website analysis with AI-powered insights

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-orange.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 Overview

Competition Monitor is a powerful desktop application that helps you analyze competitor websites using automated web scraping and AI-powered analysis. Built with modern Python technologies, it provides real-time insights into competitor products, pricing, and design strategies.

## ✨ Features

- 🤖 **AI-Powered Analysis** - OpenAI Vision API integration for screenshot analysis
- 🌐 **Web Scraping** - Selenium-based headless Chrome parsing
- 📊 **History Tracking** - Automatic logging of all analysis requests
- 🎨 **Modern UI** - Clean PyQt6 desktop interface
- ⚡ **Concurrent Processing** - Semaphore-based request limiting
- 📦 **Portable Build** - Single .exe file distribution

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI + Uvicorn |
| **Desktop UI** | PyQt6 |
| **Web Scraping** | Selenium WebDriver |
| **AI Analysis** | OpenAI GPT-4 Vision |
| **Build Tool** | PyInstaller |
| **Language** | Python 3.10+ |

## 🚀 Quick Start

### Windows (Recommended)

```bash
# 1. Install dependencies
install.bat

# 2. Configure .env file
copy .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Run application
start.bat
```

### Manual Installation

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
pip install -r desktop/requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 4. Run application
python start_dev.py
```

## 📚 Documentation

- 🇷🇺 [Русская документация](README_RU.md) - Complete Russian documentation
- 🚀 [Quick Start Guide](QUICKSTART_RU.md) - Get started in 5 minutes
- 🧪 [Testing Guide](TESTING.md) - Testing and debugging
- 📝 [Changelog](CHANGELOG.md) - Recent changes and improvements

## 📦 Building Executable

```bash
# Build .exe file
python build.py

# Or use batch file
build.bat
```

Output: `dist/competitionmonitor.exe` (~50-150 MB)

**Requirements for .exe:**
- ✅ Windows 10/11
- ✅ Google Chrome installed
- ✅ .env file with OPENAI_API_KEY

## 🔧 Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_PROXY=http://user:pass@ip:port  # Optional
```

See [.env.example](.env.example) for all available options.

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/parsedemo` | GET | Parse competitor website |
| `/analyze` | POST | Analyze screenshot with AI |
| `/docs` | GET | Interactive API documentation |

## 🧪 Testing

```bash
# Check dependencies
python check_dependencies.py

# Run integration tests
set TESTING=True
pytest tests/test_integration.py -v

# Test API manually
curl http://127.0.0.1:8000/health
```

## 📁 Project Structure

```
competition-monitor/
├── backend/              # FastAPI backend
│   ├── services/        # Business logic
│   ├── models/          # Data models
│   └── main.py          # API entry point
├── desktop/             # PyQt6 desktop app
│   ├── main.py          # UI entry point
│   ├── api_client.py    # HTTP client
│   └── styles.py        # UI styles
├── tests/               # Test suite
├── .env.example         # Environment template
├── start_dev.py         # Development launcher
├── build.py             # Build script
└── *.bat                # Windows batch files
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| ModuleNotFoundError | Run `python check_dependencies.py` |
| Chrome not found | Install Google Chrome |
| Connection refused | Ensure backend is running on port 8000 |
| API key error | Check `.env` file configuration |

See [TESTING.md](TESTING.md) for detailed troubleshooting guide.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Desktop UI framework
- [Selenium](https://www.selenium.dev/) - Web automation
- [OpenAI](https://openai.com/) - AI analysis capabilities

## 📞 Support

- 📖 [Documentation](README_RU.md)
- 🐛 [Issue Tracker](https://github.com/yourusername/competition-monitor/issues)
- 💬 [Discussions](https://github.com/yourusername/competition-monitor/discussions)

---

Made with ❤️ by [Your Name]
