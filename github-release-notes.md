# 🎉 Yomitoku-Web v0.1 - Initial Release

## 📝 Description

First public release of **Yomitoku-Web**, a modern web interface for the [Yomitoku](https://github.com/kotaro-kinoshita/yomitoku) Japanese OCR tool with integrated AI translation via Ollama.

## ✨ Key Features

### 🖥️ Web Interface
- Drag & drop file upload (PDF, PNG, JPG, TIFF, BMP)
- Real-time progress tracking with live logs (SSE)
- Multi-language support (French, English, Japanese)
- Responsive Bootstrap 5 UI

### 🌐 AI Translation
- Local translation via Ollama integration
- 6 specialized translation prompts:
  - Default (general purpose)
  - Manga (preserves style & cultural nuances)
  - Video Games (gaming terminology)
  - Famitsu (retro gaming magazines)
  - Technical (IT documentation)
  - Administrative (official documents)

### 📊 Job Management
- Unique job IDs with persistent storage
- Job history browser (`/jobs`)
- Direct file viewing in browser
- Background processing (up to 3 concurrent jobs)

### 🔧 Advanced Options
- Visualization generation
- Figure extraction
- Page merging
- Metadata filtering
- GPU/CUDA support

## 📋 Requirements

- Python 3.10+
- [Ollama](https://ollama.com/) (for translation feature)

## 🚀 Quick Start

```bash
git clone https://github.com/flelard/yomitoku-web.git
cd yomitoku-web
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run --host=0.0.0.0
```

Access at: `http://localhost:5000`

## 📦 What's Included

- Flask web application
- HTML/CSS/JS frontend
- Real-time log streaming (SSE)
- REST API endpoints
- Multi-format output (MD, HTML, JSON, CSV)

## ⚠️ Known Limitations

- Max file size: 50MB
- Ollama must be running locally for translation
- Thread-safe for up to 3 concurrent jobs

## 🙏 Credits

Built upon the excellent [Yomitoku](https://github.com/kotaro-kinoshita/yomitoku) project by **Kotaro Kinoshita**.

## 📄 License

CC BY-NC-SA 4.0 (same as original Yomitoku project)

---

**Note:** This is an initial release. Feedback and bug reports are welcome!
