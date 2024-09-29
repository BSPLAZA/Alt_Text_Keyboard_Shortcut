
# Alt Text Generator with AutoHotkey and Python

## Overview

This project provides a convenient way to generate alt text descriptions for highlighted content, whether text or images, using a keyboard shortcut (`Ctrl + Alt + C`). The highlighted content is copied to the clipboard and then processed via OpenAI's GPT-4 API to generate concise alt text. The result is automatically placed back into the clipboard.

## Features
- **AutoHotkey Integration**: Binds `Ctrl + Alt + C` to copy the highlighted content and trigger a Python script.
- **Alt Text Generation**: Uses OpenAI’s GPT-4 API to generate accurate and concise alt text.
- **Text and Image Support**: Works with both text and image content, creating alt descriptions for either.

## How It Works
1. The user highlights text or an image.
2. Press `Ctrl + Alt + C` to copy the content.
3. The content is processed using OpenAI’s GPT-4 API.
4. The generated alt text is copied to the clipboard.

## Prerequisites

### Software
- **Git**: Version control software.
  - [Download Git](https://git-scm.com/download/win)
- **Python 3.x**: Programming language used for the script.
  - [Download Python](https://www.python.org/downloads/)
- **AutoHotkey**: Used to bind `Ctrl + Alt + C` to trigger both the copy operation and the Python script.
  - [Download AutoHotkey](https://www.autohotkey.com/)

### Python Libraries
You need the following Python packages:
- **openai**: For accessing the GPT-4 API.
- **pyperclip**: For managing clipboard operations.
- **Pillow**: For handling image data.
- **pywin32**: For accessing Windows clipboard functions.
- **keyboard**: To simulate keypresses in Python.

To install the required dependencies, run:
```bash
pip install openai pyperclip Pillow pywin32 keyboard
```

## Setup

### Step 1: AutoHotkey Script
1. Install AutoHotkey from the link provided above.
2. Create a new `.ahk` file with the following content:

```ahk
^!c::  ; Ctrl + Alt + C
Send ^c  ; Copy highlighted content
Sleep 500  ; Wait for clipboard to update
Run, pythonw "C:\path	o\your\main.py"  ; Run your Python script
return
```

3. Save the file and double-click it to run.

### Step 2: Python Script
1. Create the `main.py` file with the following logic:
```python
import asyncio
import os
import pyperclip
from PIL import Image, ImageGrab
from openai import OpenAIError, OpenAI
from dotenv import load_dotenv
import base64
from io import BytesIO
import win32clipboard  # Access clipboard content
import keyboard  # To simulate Ctrl+C for copying

# Load environment variables
load_dotenv()

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Simulate Ctrl+C to copy highlighted content
def simulate_copy():
    keyboard.press_and_release('ctrl+c')

# Get plain text from clipboard
def get_clipboard_text():
    try:
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
            return win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()

# Convert the image to base64
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Generate alt text using GPT-4
async def get_description(text=None, image=None):
    try:
        if image:
            base64_image = encode_image(image)
            response = await asyncio.to_thread(client.chat.completions.create,
                                               model="gpt-4o",
                                               messages=[{"role": "system", "content": "Provide concise alt text."},
                                                         {"role": "user", "content": f"Describe this image: {base64_image}"}])
            return response.choices[0].message.content.strip()

        elif text:
            response = await asyncio.to_thread(client.chat.completions.create,
                                               model="gpt-4o",
                                               messages=[{"role": "system", "content": "Provide concise alt text."},
                                                         {"role": "user", "content": f"Describe this text: {text}"}])
            return response.choices[0].message.content.strip()

    except OpenAIError as e:
        print(f"Error: {e}")
        return None

# Process clipboard content
async def process_clipboard():
    simulate_copy()
    text, image = get_clipboard_content()
    if text or image:
        description = await get_description(text, image)
        if description:
            pyperclip.copy(description)

if __name__ == "__main__":
    asyncio.run(process_clipboard())
```

### Step 3: Environment Setup
1. Set up your `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

### Step 4: Add to GitHub
1. Initialize Git in your project folder:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of alt text generator"
   ```
2. Create a repository on GitHub and push the changes:
   ```bash
   git remote add origin https://github.com/yourusername/your-repo.git
   git push -u origin master
   ```

## Usage
1. Select or highlight content (text or image).
2. Press `Ctrl + Alt + C` to copy the content and generate alt text.
3. The alt text is automatically copied to your clipboard.

## Dependencies
- **AutoHotkey**: To create the shortcut trigger for both copy and Python script execution.
- **Python 3.x**
- **OpenAI Python Library**
- **pyperclip**
- **Pillow**
- **pywin32**
- **keyboard**
