import asyncio
import os
import pyperclip
from PIL import Image, ImageGrab
from openai import OpenAIError, OpenAI
from dotenv import load_dotenv
import base64
from io import BytesIO
import ctypes  # To use the Windows API to perform copy action
import win32clipboard  # Access clipboard content
import time

# Load environment variables
load_dotenv()

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to perform copy action using Windows API via ctypes
def perform_copy_action():
    print("Performing copy action using Windows API.")
    user32 = ctypes.windll.user32
    user32.keybd_event(0x11, 0, 0, 0)  # Ctrl key down (0x11 is the virtual-key code for Ctrl)
    user32.keybd_event(0x43, 0, 0, 0)  # C key down (0x43 is the virtual-key code for 'C')
    user32.keybd_event(0x43, 0, 2, 0)  # C key up
    user32.keybd_event(0x11, 0, 2, 0)  # Ctrl key up
    time.sleep(0.5)  # Ensure clipboard has time to update

# Function to get plain text from clipboard
def get_clipboard_text():
    try:
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
            data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            return data
        else:
            print("Clipboard does not contain text.")
            return None
    finally:
        win32clipboard.CloseClipboard()

# Function to convert the image to base64 string
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")  # Save the image as PNG format
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# API interaction to generate concise descriptions
async def get_description(text=None, image=None):
    try:
        if image:
            print("Image detected in clipboard.")
            base64_image = encode_image(image)  # Convert image to base64

            # Send the image to GPT-4o API
            response = await asyncio.to_thread(client.chat.completions.create,
                                               model="gpt-4o",  # Hypothetical model with vision capability
                                               messages=[
                                                   {"role": "system", "content": "You are a helpful assistant that provides concise summaries of images for alt text in just one to two sentence. Do not include the words image of or image of this."},
                                                   {"role": "user", "content": [
                                                       {"type": "text", "text": "Please describe the content of this image. Be concise."},
                                                       {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                                                   ]}
                                               ],
                                               max_tokens=100)

            return response.choices[0].message.content.strip()

        elif text:
            print("Text detected in clipboard.")
            # Handle text-only input
            response = await asyncio.to_thread(client.chat.completions.create,
                                               model="gpt-4o",
                                               messages=[
                                                   {"role": "system", "content": "You are a helpful assistant that provides concise summaries of text for alt text in just one to two sentences. Make sure to limit your response to only alt text for the content. If there's too much content, just try to give a concise summary in one sentence."},
                                                   {"role": "user", "content": f"Provide a one to two sentence description of the following text: {text}"}
                                               ],
                                               max_tokens=100)

            return response.choices[0].message.content.strip()

        else:
            return None

    except OpenAIError as e:
        print(f"An error occurred with OpenAI API: {e}")
        return None

# Function to retrieve clipboard content
def get_clipboard_content():
    try:
        image = ImageGrab.grabclipboard()  # Capture the image from the clipboard
        text = get_clipboard_text()  # Capture the text from the clipboard

        if image:
            print("Image found in clipboard.")
            return None, image  # Return the image if found
        elif text:
            print("Text found in clipboard.")
            return text, None  # Return the text if found
        else:
            print("Clipboard is empty or content not supported.")
            return None, None
    except Exception as e:
        print(f"Error accessing clipboard: {e}")
        return None, None

# Main logic to process clipboard content
async def process_clipboard():
    perform_copy_action()  # Perform copy action using Windows API
    text, image = get_clipboard_content()  # Get clipboard content directly
    if text or image:
        # Send content to the OpenAI API for description
        description = await get_description(text=text, image=image)
        if description:
            pyperclip.copy(description)  # Copy the generated description to the clipboard
            print(f"Alt text generated and copied to clipboard: {description}")
        else:
            print("Failed to generate alt text.")
    else:
        print("No valid content found in clipboard.")

def main():
    # Automatically copy content and process it
    print("Processing highlighted content...")
    asyncio.run(process_clipboard())  # Create a new event loop for processing

if __name__ == "__main__":
    main()
