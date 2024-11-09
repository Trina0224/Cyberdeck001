# Cyberdeck001 Setup Guide

## Initial Setup

1. Create a file named `openai_key.txt` in the working directory.
2. Paste your OpenAI API key into `openai_key.txt`.  
3. For Claude, create a new file called `anthropic_key.txt` and paste the key into it.  
4. For Gemini, create a new file named `google_key.txt` and paste the key into it.  

## Requirements  
(--break-system-packages may need, if no virtual env. )  

```bash  
pip install -r requirements.txt  
```  
  
If you would like to have the exactlly reversions I am using:  
  
```bash  
pip install -r requirements_fix.txt  
```  

Somehthing you may need to install:  

```bash  
# For Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y \
    python3-tk \
    portaudio19-dev \
    python3-pil.imagetk
```  


## Running the Program

Run the following command to start the program:
```bash
python main.py
```

## Hardware Requirements

1. **Raspberry Pi 5**  
   - Recommended for use with dual cameras.  
   - Alternatively, you can use a Raspberry Pi 4 with a USB camera or modify the code to use a single camera.
2. **HDMI Output**
3. **Audio Device**  
   - A USB-to-speaker + MIC dongle (or separate dongles).
   - Compatible audio shields or gloves can also be used.

## Known Issues

1. ~~Incorrect color rendering in the outputs of both cameras.~~
2. Basic GUI design, which may affect the user experience.
3. Keyboard shortcuts, if focuse on input-box, the shortcuts are not working.  
4. Package list.  

## Release Info  
v0.5.0  It's a full function chat Interface and only support chatGPT.  

## Models  
OpenAI:  gpt-4o-mini, gpt-4o  
Claude:  claude-3-5-sonnet-20241022  
Gemini:  gemini-1.5-flash  
Grok:  grok-demo  (Released on Nov/04th/2024, image support will be released later. No python lib required.)



