# YouTube Downloader - Quick Start Guide

## Quick Installation

1. Install Python 3.7+ from [python.org](https://www.python.org/downloads/)
2. Install FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
3. Run in terminal:
```bash
pip install -r requirements.txt
```

## Quick Setup

1. Make sure you're logged into YouTube in your browser
2. Check settings.json (created on first launch):
```json
{
    "cookies_from_browser": "chrome"  // Change to your browser if needed
}
```

## Quick Usage

1. Launch:
```bash
python c1.py
```

2. Download Video:
   - Paste YouTube URL
   - Select resolution
   - Click "Download"

3. Download Audio:
   - Paste YouTube URL
   - Select "Audio only"
   - Click "Download"

## Common Issues

- **No video resolutions?** → Make sure you're logged into YouTube
- **Download fails?** → Check your internet connection
- **"ffmpeg not found"?** → Add FFmpeg to system PATH

Need more help? See full README_EN.md 