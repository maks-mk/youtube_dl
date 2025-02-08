---
title: YouTube Downloader
description: A program for downloading videos and audio from YouTube with a user-friendly graphical interface
author: Your Name
version: 1.0.0
license: MIT
language: English
tags:
  - youtube
  - downloader
  - python
  - gui
  - video
  - audio
requirements:
  - Python 3.7+
  - FFmpeg
  - Web browser
dependencies:
  - yt-dlp>=2023.12.30
  - pyperclip>=1.8.2
  - pyinstaller>=6.3.0
---

# YouTube Downloader

A program for downloading videos and audio from YouTube with a user-friendly graphical interface.

## Requirements

1. Python 3.7 or higher
2. FFmpeg (must be installed and available in system PATH)
3. Browser with YouTube authorization (Chrome, Firefox, Edge, Opera, Brave, or Safari)
4. Stable internet connection

## Installation

1. Install Python from the [official website](https://www.python.org/downloads/)

2. Install FFmpeg:
   - Windows: 
     1. Download FFmpeg from the [official website](https://ffmpeg.org/download.html)
     2. Extract the archive
     3. Add the bin folder path to the system PATH variable
     4. Verify that ffmpeg.exe is accessible via command line

3. Install required Python packages:
```bash
pip install -r requirements.txt
```

## Configuration

1. On first launch, the program will create a `settings.json` file with default settings
2. You can modify the settings by editing the `settings.json` file:
```json
{
    "download_mode": "video",
    "last_resolution": "720p",
    "cookies_from_browser": "chrome"
}
```

Available values for `cookies_from_browser`:
- "chrome" - Google Chrome
- "firefox" - Mozilla Firefox
- "edge" - Microsoft Edge
- "opera" - Opera
- "brave" - Brave Browser
- "safari" - Safari (macOS only)
- "chromium" - Chromium

**Important**: 
- You must be logged into YouTube in the selected browser
- It's recommended to use the browser where you regularly use YouTube

## Important Authentication Note

Before using the program:

1. Sign in to your YouTube account in the browser:
   - Open YouTube
   - Click "Sign In" in the top right corner
   - Sign in to your Google account
   - Make sure you can watch videos without captcha

2. Specify the correct browser in settings.json:
   ```json
   {
       "download_mode": "video",
       "last_resolution": "720p",
       "cookies_from_browser": "chrome"  // Specify your browser
   }
   ```

3. Ensure that:
   - The browser is installed in the default location
   - You are logged into YouTube in this browser
   - The browser is not in incognito mode
   - You have permissions to read the browser profile

If the problem persists:
1. Try using a different browser
2. Make sure you regularly use YouTube in this browser
3. Clear browser cookies, sign in to YouTube again, and wait a few minutes
4. Try watching a few videos in the browser before using the program

## Usage

1. Launch the program:
```bash
python c1.py
```

2. Insert YouTube video URL:
   - Copy the video URL from your browser
   - Paste it into the URL field (you can use the "Paste URL" button)

3. Select download mode:
   - "Video" - for downloading videos
   - "Audio only" - for downloading in MP3 format

4. If "Video" mode is selected:
   - Click "Update list" to get available resolutions
   - Select desired resolution from the dropdown list

5. Click "Download"

6. Wait for the download to complete:
   - For videos, progress will be shown separately for video and audio
   - For audio, overall progress will be shown
   - With slow internet, the program automatically retries downloads

7. After completion, the file will be saved in the same folder as the program

## Troubleshooting

1. "ffmpeg.exe is not installed":
   - Ensure FFmpeg is installed and added to PATH
   - Verify that ffmpeg.exe is accessible via command line
   - Restart the program

2. "Sign in to confirm you're not a bot":
   - Make sure you're logged into YouTube in the selected browser
   - Check the `cookies_from_browser` setting in settings.json
   - Try using a different browser
   - Ensure you regularly use YouTube in this browser

3. "Failed to get video resolutions":
   - Check your internet connection
   - Ensure the video URL is correct
   - Try updating the resolution list

4. "Read timed out" or other network errors:
   - Check your internet connection stability
   - The program will automatically retry downloads
   - For frequent errors, try using a VPN
   - Try downloading the video later

## Notes

- The program saves files in the format:
  - Video: `[video title]_[resolution].mp4`
  - Audio: `[video title]_audio.mp3`
- When attempting to download a file with an existing name, the program will ask for overwrite permission
- All actions are logged to `download.log`
- The program uses browser cookies to bypass YouTube restrictions
- Settings are saved between program launches
- For network issues, the program automatically makes up to 10 retry attempts

## Program Files

- `c1.py` - main program file
- `requirements.txt` - dependencies list
- `settings.json` - settings file
- `ytdl.ico` - application icon
- `download.log` - log file

## Creating EXE File (optional)

You can create an executable file using PyInstaller:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Create the EXE file:
```bash
pyinstaller --onefile --windowed --icon=ytdl.ico c1.py
```

3. The finished EXE file will be located in the dist folder 