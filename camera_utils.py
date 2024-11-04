# camera_utils.py
from picamera2 import Picamera2
from PIL import Image
import datetime
import os

class CameraManager:
    @staticmethod
    def setup_camera(camera_num: int) -> Picamera2:
        camera = Picamera2(camera_num=camera_num)
        
        preview_config = {
            "format": "XBGR8888",  # Using XRGB8888 format for correct color
            "size": (640, 480)
        }
        
        camera_config = camera.create_preview_configuration(
            main={"size": (3280, 2464), "format": "XBGR8888"},  # Using XRGB8888 for main capture too
            lores=preview_config
        )
        
        camera.configure(camera_config)
        camera.start()
        return camera

    @staticmethod
    def capture_and_convert(camera: Picamera2, camera_num: int) -> str:
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        final_path = f"camera{camera_num}.jpg"
        
        try:
            # Capture image directly as RGB format
            image_array = camera.capture_array()
            
            # Convert to PIL Image
            img = Image.fromarray(image_array, 'RGBA').convert('RGB')  # Convert XRGB to RGB
            
            # Resize to maintain aspect ratio, fitting within 683x512
            img = img.resize((683, 512), Image.Resampling.LANCZOS)
            
            # Calculate the coordinates for cropping the center 512x512 area
            left = (683 - 512) // 2
            top = 0
            right = left + 512
            bottom = 512
            img = img.crop((left, top, right, bottom))
            
            # Save as JPEG
            img.save(final_path, "JPEG", quality=90)
            
            return final_path
            
        except Exception as e:
            print(f"Error in image processing: {e}")
            return None

