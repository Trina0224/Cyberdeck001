# dual_camera_gpt_app.py
import tkinter as tk
from tkinter import ttk, scrolledtext, font
from PIL import Image, ImageTk
import threading
import queue
from collections import deque
import datetime
import os
import sounddevice as sd
import numpy as np
from pydub import AudioSegment
from conversation_manager import ConversationManager
from camera_utils import CameraManager
import time
from pathlib import Path
import opencc

class DualCameraGPTApp:
    def __init__(self, master):
        self.master = master
        master.title("Dual Camera GPT Interface")
       
        # Initialize converter before other components
        self.converter = opencc.OpenCC('s2t')


        # Initialize recording state
        self.is_recording = False
        self.recording_thread = None
        self.audio_data = []
        self.sample_rate = 44100

        # Initialize command history
        self.command_history = deque(maxlen=10)
        self.history_index = 0
        
        # Set default font size for chat areas
        self.current_font_size = 12
        self.chat_font = font.Font(size=self.current_font_size)
        
        # Initialize preview update flags
        self.running = True
        
        ## Initialize cameras
        #self.setup_cameras()
        
        # Initialize the GPT conversation manager
        self.conversation_manager = ConversationManager()

        # Initialize cameras
        self.setup_cameras()
        
        # Pass camera references to conversation manager
        self.conversation_manager.set_cameras(self.picam1, self.picam2)

        # Bind Escape key
        self.master.bind('<Escape>', self.stop_audio)
        
        # Create main UI
        self.create_ui()
        
        # Start the preview loops in separate threads
        self.start_preview_threads()
        
        # Display welcome message
        self.display_welcome_message()

    def setup_cameras(self):
        try:
            self.picam1 = CameraManager.setup_camera(0)
            self.picam2 = CameraManager.setup_camera(1)
            print("Cameras initialized successfully")
        except Exception as e:
            print(f"Error setting up cameras: {e}")
    
    def create_ui(self):
        # Create main container
        self.main_container = ttk.Frame(self.master)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create font size control frame
        self.create_font_control()
        
        # Create frames for organization
        self.camera_frame = ttk.Frame(self.main_container)
        self.camera_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.chat_frame = ttk.Frame(self.main_container)
        self.chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Status label for processing feedback
        self.status_label = ttk.Label(
            self.main_container,
            text="",
            font=('Arial', 10, 'bold')  # Make status more visible
        )
        self.status_label.pack(fill=tk.X, padx=5)
        
        # Camera previews
        self.preview1_canvas = tk.Canvas(self.camera_frame, width=640, height=480)
        self.preview1_canvas.pack(side=tk.LEFT, padx=5)
        
        self.preview2_canvas = tk.Canvas(self.camera_frame, width=640, height=480)
        self.preview2_canvas.pack(side=tk.LEFT, padx=5)
        
        # Create a frame for chat display and input
        chat_container = ttk.Frame(self.chat_frame)
        chat_container.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for chat container
        chat_container.grid_columnconfigure(0, weight=1)
        chat_container.grid_rowconfigure(0, weight=1)
        chat_container.grid_rowconfigure(1, weight=0)  # Input row doesn't expand
        
        # Chat display with font settings
        self.chat_display = scrolledtext.ScrolledText(
            chat_container, 
            wrap=tk.WORD, 
            font=self.chat_font
        )
        self.chat_display.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Input frame
        self.input_frame = ttk.Frame(chat_container)
        self.input_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        
        # Configure input frame grid
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=0)
        
        # Chat input
        self.chat_input = ttk.Entry(
            self.input_frame,
            font=self.chat_font
        )
        self.chat_input.grid(row=0, column=0, sticky='ew')
        
        # Button frame
        self.button_frame = ttk.Frame(self.input_frame)
        self.button_frame.grid(row=0, column=1, sticky='e', padx=(5, 0))
        
        # Record button (New) - Using tk.Button instead of ttk.Button for color support
        self.record_button = tk.Button(
            self.button_frame,
            text="Record",
            command=self.toggle_recording,
            relief=tk.RAISED,  # Add relief to make it more visible
            width=8,  # Set a fixed width
            bg='light gray',
            activebackground='gray'
        )
        self.record_button.pack(side=tk.LEFT, padx=2)


        # Buttons
        self.send_button = ttk.Button(
            self.button_frame, 
            text="Send", 
            command=self.handle_input
        )
        self.send_button.pack(side=tk.LEFT, padx=2)
        
        self.exit_button = ttk.Button(
            self.button_frame, 
            text="Exit", 
            command=self.exit_program
        )
        self.exit_button.pack(side=tk.LEFT, padx=2)
        
        # Bind keys
        self.chat_input.bind("<Return>", lambda e: self.handle_input())
        self.chat_input.bind("<Up>", self.handle_up_key)
        self.chat_input.bind("<Down>", self.handle_down_key)
        
        # New keyboard shortcuts
        # Bind to both the main window and chat_input to ensure they work regardless of focus
        for widget in (self.master, self.chat_input):
            widget.bind('r', lambda e: self.toggle_recording())
            widget.bind('R', lambda e: self.toggle_recording())
            widget.bind('s', lambda e: self.handle_input())
            widget.bind('S', lambda e: self.handle_input())
            widget.bind('e', lambda e: self.exit_program())
            widget.bind('E', lambda e: self.exit_program())

        # Update button text to show shortcuts
        self.record_button.configure(text="Record (R)")
        self.send_button.configure(text="Send (S)")
        self.exit_button.configure(text="Exit (E)")


    def create_font_control(self):
        # Create frame for font size control
        font_control_frame = ttk.Frame(self.main_container)
        font_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Label for the slider
        font_label = ttk.Label(
            font_control_frame,
            text="Chat Text Size:"
        )
        font_label.pack(side=tk.LEFT, padx=5)
        
        # Create the slider
        self.font_size_var = tk.IntVar(value=self.current_font_size)
        self.font_slider = ttk.Scale(
            font_control_frame,
            from_=12,
            to=24,
            orient=tk.HORIZONTAL,
            variable=self.font_size_var,
            command=self.update_font_size
        )
        self.font_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Display current font size
        self.font_size_label = ttk.Label(
            font_control_frame,
            text=str(self.current_font_size)
        )
        self.font_size_label.pack(side=tk.LEFT, padx=5)

    def update_font_size(self, *args):
        new_size = self.font_size_var.get()
        self.current_font_size = new_size
        self.chat_font.configure(size=new_size)
        self.font_size_label.configure(text=str(new_size))
        
        # Update font for both chat display and input area
        self.chat_display.configure(font=self.chat_font)
        self.chat_input.configure(font=self.chat_font)
        
        # Adjust chat display height based on font size
        # This helps maintain the input area visibility
        base_height = 20  # Base height for font size 12
        adjusted_height = max(10, int(base_height * (12 / new_size)))  # Minimum height of 10
        self.chat_display.configure(height=adjusted_height)
        
        # Force update of the display
        self.master.update_idletasks()


    def handle_up_key(self, event):
        if len(self.command_history) > 0:
            if self.history_index < len(self.command_history):
                self.history_index += 1
                self.chat_input.delete(0, tk.END)
                self.chat_input.insert(0, self.command_history[-self.history_index])

    def handle_down_key(self, event):
        if self.history_index > 0:
            self.history_index -= 1
            self.chat_input.delete(0, tk.END)
            if self.history_index > 0:
                self.chat_input.insert(0, self.command_history[-self.history_index])

    def display_welcome_message(self):
        welcome_message = """Welcome! I'm your AI assistant. I can help you with questions in English, Japanese, Chinese, 
and particularly with topics related to Christianity and the Bible.

I can analyze images from two cameras - just mention 'camera 1' or 'camera 2' in your question.
Type 'quit', 'exit', or 'bye' to end the program, or use the Exit button.

Keyboard shortcuts:
R - Toggle Recording
S - Send Message
E - Exit Program

Esc - Stop GPT's talking.

How can I help you today?
"""
        self.chat_display.insert(tk.END, welcome_message)
        self.chat_display.see(tk.END)

    def start_preview_threads(self):
        self.preview_queue1 = queue.Queue()
        self.preview_queue2 = queue.Queue()
        
        threading.Thread(
            target=self.capture_preview_loop,
            args=(self.picam1, self.preview_queue1, 1),
            daemon=True
        ).start()
        
        threading.Thread(
            target=self.capture_preview_loop,
            args=(self.picam2, self.preview_queue2, 2),
            daemon=True
        ).start()
        
        self.update_preview_canvases()

    def capture_preview_loop(self, camera, preview_queue, camera_num):
        while self.running:
            try:
                frame = camera.capture_array("lores")
                # Convert directly to PIL Image with correct color format
                image = Image.fromarray(frame, 'RGBA').convert('RGB')
                photo = ImageTk.PhotoImage(image)
                preview_queue.put(photo)
            except Exception as e:
                print(f"Error capturing preview from camera {camera_num}: {e}")
            self.master.after(10)


    def update_preview_canvases(self):
        try:
            if not self.preview_queue1.empty():
                photo1 = self.preview_queue1.get_nowait()
                self.preview1_canvas.create_image(0, 0, anchor=tk.NW, image=photo1)
                self.preview1_canvas.image = photo1
            
            if not self.preview_queue2.empty():
                photo2 = self.preview_queue2.get_nowait()
                self.preview2_canvas.create_image(0, 0, anchor=tk.NW, image=photo2)
                self.preview2_canvas.image = photo2
        except Exception as e:
            print(f"Error updating preview canvases: {e}")
        
        if self.running:
            self.master.after(10, self.update_preview_canvases)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.master.update_idletasks()

    def handle_input(self):
        user_input = self.chat_input.get().strip()
        if not user_input:
            return
        
        # Add to command history
        self.command_history.append(user_input)
        self.history_index = 0
        
        # Clear input field
        self.chat_input.delete(0, tk.END)
        
        # Display user input
        self.chat_display.insert(tk.END, f"\nYou: {user_input}\n")
        self.chat_display.see(tk.END)
        
        # Check for exit commands
        if user_input.lower() in ['quit', 'exit', 'bye']:
            self.exit_program()
            return
        
        # Check if we need to capture from either camera
        if "camera 1" in user_input.lower() or "front camera" in user_input.lower():
            self.update_status("Processing image from Camera 1... Please wait.")
            image_path = CameraManager.capture_and_convert(self.picam1, 1)
        elif "camera 2" in user_input.lower() or "rear camera" in user_input.lower():
            self.update_status("Processing image from Camera 2... Please wait.")
            image_path = CameraManager.capture_and_convert(self.picam2, 2)
        
        # Get response from GPT
        response = self.conversation_manager.get_response(
            user_input,
            status_callback=self.update_status
        )
        
        # Display assistant response before TTS starts
        self.chat_display.insert(tk.END, f"\nAssistant: {response}\n")
        self.chat_display.see(tk.END)

        
        # Clear status
        self.update_status("")

    def cleanup(self):
        self.running = False
        if hasattr(self, 'picam1'):
            self.picam1.stop()
            self.picam1.close()
        if hasattr(self, 'picam2'):
            self.picam2.stop()
            self.picam2.close()

    def exit_program(self):
        self.cleanup()
        self.master.quit()
        self.master.destroy()
    

    def toggle_recording(self):
        if not self.is_recording:
            # Start recording
            self.is_recording = True
            self.record_button.configure(bg='red', activebackground='dark red')
            self.update_status("Recording audio...")
            self.audio_data = []
            self.recording_thread = threading.Thread(target=self.record_audio)
            self.recording_thread.start()
        else:
            # Stop recording
            self.is_recording = False
            self.record_button.configure(bg='light gray', activebackground='gray')
            self.update_status("Processing audio...")
            if self.recording_thread:
                self.recording_thread.join()
            self.save_and_transcribe_audio()

    def record_audio(self):
        """Record audio in chunks while is_recording is True."""
        try:
            with sd.InputStream(channels=1, samplerate=self.sample_rate, dtype='float32') as stream:
                while self.is_recording:
                    audio_chunk, _ = stream.read(self.sample_rate)
                    self.audio_data.append(audio_chunk)
        except Exception as e:
            print(f"Error recording audio: {e}")
            self.update_status(f"Error recording audio: {e}")
            self.is_recording = False
            self.master.after(0, lambda: self.record_button.configure(
                bg='light gray', 
                activebackground='gray'
            ))

    def save_and_transcribe_audio(self):
        """Save recorded audio to MP3 and transcribe it."""
        try:
            if not self.audio_data:
                self.update_status("No audio recorded")
                return

            # Combine all audio chunks
            combined_audio = np.concatenate(self.audio_data)
            
            # Convert to AudioSegment
            audio_segment = AudioSegment(
                (combined_audio * 32767).astype(np.int16).tobytes(),
                frame_rate=self.sample_rate,
                sample_width=2,
                channels=1
            )
            
            # Save as MP3
            output_path = Path("/tmp") / f"recording_{int(time.time())}.mp3"
            audio_segment.export(str(output_path), format="mp3")
            
            # Transcribe audio
            self.update_status("Transcribing audio...")
            with open(output_path, "rb") as audio_file:
                transcription = self.conversation_manager.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            # Convert to traditional Chinese if needed and display
            transcribed_text = self.converter.convert(transcription.text)
            self.chat_input.insert(0, transcribed_text)
            self.update_status("")
            
            # Clean up
            if output_path.exists():
                os.remove(output_path)

            # Automatically trigger send after a short delay (to ensure UI is updated)
            self.master.after(100, self.handle_input) #delay 100ms to trigger the Send button

            
        except Exception as e:
            print(f"Error processing audio: {e}")
            self.update_status(f"Error processing audio: {e}")


    def stop_audio(self, event=None):
        """
        Stop audio playback when Escape is pressed.
        """
        try:
            self.conversation_manager.tts_manager.stop_playback()
            self.update_status("")
        except Exception as e:
            print(f"Error stopping audio: {e}")
            self.update_status("Error stopping audio")
    
        # Ensure the UI remains responsive
        self.master.update()
