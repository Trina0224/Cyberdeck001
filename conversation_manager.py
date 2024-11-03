# conversation_manager.py
from openai import OpenAI
import opencc
from typing import List, Dict, Callable
import base64
from tts_manager import TTSManager
import re

class ConversationManager:
    def __init__(self, api_key_path: str = "openai_key.txt"):
        self.converter = opencc.OpenCC('s2t')
        self.client = OpenAI(api_key=self.load_api_key(api_key_path))
        self.tts_manager = TTSManager(api_key_path)

        self.camera_images = {
            "camera1": "camera1.jpg",
            "camera2": "camera2.jpg"
        }
        
        self.conversation_history: List[Dict] = [
            {
                "role": "system",
                "content": """You are a knowledgeable female assistant with expertise in Japanese, 
                English, Chinese, Christianity, and Biblical studies. You can also analyze images 
                from two cameras. When asked about 'camera 1' or 'front camera', you'll analyze 
                the front view image. When asked about 'camera 2' or 'rear camera', you'll analyze 
                the rear view image. Please provide helpful and accurate responses for daily life 
                questions and image analysis. Maintain conversation context and provide responses 
                in the same language as the user's query."""
            }
        ]

    def load_api_key(self, filepath: str) -> str:
        try:
            with open(filepath, "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            raise Exception(f"API key file not found at {filepath}")

    def encode_image_to_base64(self, image_path: str) -> str:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            raise Exception(f"Image file not found: {image_path}")

    def add_message(self, role: str, content: str, image_path: str = None) -> None:
        if image_path:
            image_base64 = self.encode_image_to_base64(image_path)
            content_with_image = {
                "type": "text",
                "text": content
            }
            image_content = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            }
            self.conversation_history.append({
                "role": role,
                "content": [content_with_image, image_content]
            })
        else:
            self.conversation_history.append({"role": role, "content": content})


    def clear_history(self) -> None:
        self.conversation_history = [self.conversation_history[0]]
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.
        Returns 'ja' for Japanese, 'zh' for Chinese, 'en' for English
        """
        # Check for Japanese characters
        if re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text):
            return 'ja'
        # Check for Chinese characters
        elif re.search(r'[\u4E00-\u9FFF]', text):
            return 'zh'
        # Default to English
        return 'en'

    #def get_response(self, user_input: str) -> str:
    def get_response(self, user_input: str, status_callback: Callable[[str], None] = None) -> str:
        try:
            # Existing code for getting response
            image_path = None
            if "camera 1" in user_input.lower() or "front camera" in user_input.lower():
                image_path = self.camera_images["camera1"]
            elif "camera 2" in user_input.lower() or "rear camera" in user_input.lower():
                image_path = self.camera_images["camera2"]

            self.add_message("user", user_input, image_path)
            
            model = "gpt-4o-mini" if image_path else "gpt-4o"
            
            response = self.client.chat.completions.create(
                model=model,
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_response = response.choices[0].message.content
            self.add_message("assistant", assistant_response)
            
            # Detect language and convert to speech
            language = self.detect_language(assistant_response)
            # Start TTS conversion in background after displaying text
            self.tts_manager.text_to_speech(
                assistant_response,
                language,
                status_callback
            )
            #self.tts_manager.text_to_speech(assistant_response, language)
            
            return assistant_response

        except Exception as e:
            error_message = f"Error: {str(e)}"
            if status_callback:
                status_callback(error_message)
            return error_message

