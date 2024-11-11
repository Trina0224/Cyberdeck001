# Introduction

This Python GUI program allows users to interact with ChatGPT, Claude, Gemini, Grok, and Perplexity. You can ask ChatGPT, Claude, and Gemini to capture and analyze images from two connected cameras. As ChatGPT, Claude, Gemini, and Grok lack built-in online search capabilities, Perplexity has been integrated for this function. The system can call on Perplexity for support when necessary, not only for interaction but also for search tasks.

The program enables these AI models to request an online search by generating `{"Online Search": "xxxx"}`. This command prompts Perplexity to perform the search and relay the results back to the requesting AI. Additionally, the models can interact with the cameras using the command `{"Camera": "1 or 2"}`.

# Cyberdeck001 Setup Guide

## Initial Setup

1. Create a file named `openai_key.txt` in the project directory and paste your OpenAI API key into it.
2. Create a file named `anthropic_key.txt` for Claude and add your API key.
3. For Gemini, create `google_key.txt` and paste the API key into it.
4. For Perplexity, create `perplexity_key.txt` and include the API key.

## Requirements

(Use `--break-system-packages` if not using a virtual environment)

```bash
pip install -r requirements.txt
```

To use the exact package versions:

```bash
pip install -r requirements_fix.txt
```

### Additional Dependencies

For Debian/Ubuntu systems, run the following:

```bash
sudo apt-get update
sudo apt-get install -y \
    python3-tk \
    portaudio19-dev \
    python3-pil.imagetk
```

## Running the Program

To start the program, use the command:

```bash
python main.py
```

## Hardware Requirements

1. **Raspberry Pi 5**  
   - Recommended for dual-camera usage.
   - Alternatively, a Raspberry Pi 4 can be used with a USB camera, or the code can be modified for single-camera use.
2. **HDMI Output**
3. **Audio Device**  
   - USB-to-speaker + MIC dongle or separate audio input/output dongles.
   - Compatible audio shields or gloves can also be used.

## Known Issues

1. ~~Color rendering issues with both camera outputs.~~
2. Basic GUI design that may impact user experience.
3. Keyboard shortcuts do not work when the input box is focused.
4. ~~Incomplete package list.~~

## Release Information

**v0.5.0**: Fully functional chat interface supporting only ChatGPT.

## Models

- **OpenAI**: `gpt-4o-mini`, `gpt-4o`
- **Claude**: `claude-3-5-sonnet-20241022`
- **Gemini**: `gemini-1.5-flash`
- **Grok**: `grok-demo` (Released Nov 4, 2024; image support to be released. No additional Python libraries required.)
- **Perplexity**: `llama-3.1-sonar-large-128k-online`  
