# Text-to-Speech Tool

A simple yet powerful Windows application that converts highlighted text to speech using Windows' built-in text-to-speech engine. This tool allows you to quickly listen to any text you select on your screen with a simple keyboard shortcut.

## Features

- **Global Hotkey**: Press `Ctrl+Alt+Minus` to read any highlighted text
- **Adjustable Speech Speed**: Control the reading speed from 50 to 300 words per minute
- **Always-on-Top Window**: Easy access to controls while using other applications
- **Test Function**: Verify speech settings with a test button
- **Status Updates**: Visual feedback for all operations
- **Window Focus Management**: Automatically returns focus to your original window

## Planned Features

### Voice Customization
- Support for multiple voice engines with better quality
- Language selection:
  - English (Male/Female voices)
  - German (Male/Female voices)
- Voice quality improvements using enhanced TTS engines

### Controls Enhancement
- GUI buttons for basic controls:
  - Start Speaking button
  - Stop Speaking button
- Toggle speech with F8:
  - First press: Start speaking
  - Second press: Stop speaking immediately
- Visual indication of speaking status
- Single-key operation:
  - F8 shortcut automatically copies selected text and reads it out
  - No need for manual copying before pressing F8
  - Maintains clipboard state after operation

### Additional Improvements
- Language auto-detection for automatic voice selection
- Save voice and language preferences
- Keyboard shortcuts for quick language switching
- Progress indicator for long text passages

## Installation

1. Create a Python environment (Python 3.10 recommended):
```bash
conda create -n text_to_speech_env python=3.10
conda activate text_to_speech_env
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python tts_app.py
```

2. The tool window will appear and stay on top of other windows.

3. To use the text-to-speech function:
   - Highlight any text in any application
   - Press `Ctrl+Alt+Minus`
   - The text will be read aloud using the current speed settings

4. Adjust speech settings:
   - Use the slider to change the speech rate
   - Click "Test Speech" to verify the current settings
   - Changes take effect immediately

## Controls

- **Speed Slider**: Adjust the reading speed (50-300 words per minute)
- **Test Speech Button**: Play a test message with current settings
- **Global Hotkey**: `Ctrl+Alt+Minus` to read highlighted text
- **Status Label**: Shows current status and any error messages

## Requirements

- Windows operating system
- Python 3.10 or later
- Required Python packages (see requirements.txt):
  - PyQt5
  - keyboard
  - pyperclip
  - pyttsx3
  - pywin32

## Troubleshooting

1. **No Text Being Read**:
   - Ensure text is properly highlighted
   - Check if Windows text-to-speech is enabled
   - Verify your system's audio is working

2. **Hotkey Not Working**:
   - Ensure no other application is using the same hotkey
   - Try running the application as administrator
   - Check if keyboard library is properly installed

3. **Window Focus Issues**:
   - Make sure you have necessary permissions
   - No other application is blocking window focus changes

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
