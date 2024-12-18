import sys
import pyperclip
import keyboard
import pyttsx3
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QHBoxLayout, QComboBox
from PyQt5.QtCore import Qt, QEvent
import win32gui
import win32api
import win32con
import win32clipboard
from ctypes import windll, create_unicode_buffer
import time
import threading

# Custom event for updating status from another thread
class StatusUpdateEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    
    def __init__(self, status_text):
        super().__init__(self.EVENT_TYPE)
        self.status_text = status_text

class TTSWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_tts_engine()  # Setup TTS engine first
        self.init_ui()  # Then initialize UI
        self.last_clipboard_content = self.get_clipboard_content()
        self.is_processing = False  # Add lock to prevent multiple processing
        self.speech_thread = None  # Thread for speech
        self.should_stop = False  # Flag to control speech stopping
        
        # Register global hotkey (F8)
        keyboard.on_press_key("F8", self.handle_hotkey, suppress=True)
        # Register stop hotkey (Ctrl+Alt+F8)
        keyboard.add_hotkey('ctrl+alt+f8', self.stop_speech, suppress=True)
        
        print("Initialization complete - press F8 to read highlighted text, Ctrl+Alt+F8 to stop")

    def setup_tts_engine(self):
        """Initialize the text-to-speech engine"""
        try:
            self.engine = pyttsx3.init()
            self.voices = self.engine.getProperty('voices')
            print(f"Found {len(self.voices)} voices")
            
            # Set default voice (will be updated when language changes)
            if self.voices:
                self.engine.setProperty('voice', self.voices[0].id)
                print(f"Set default voice: {self.voices[0].name}")
            else:
                print("No voices found")
            
            # Set default rate
            self.engine.setProperty('rate', 300)
        except Exception as e:
            print(f"Error initializing TTS engine: {str(e)}")
            self.voices = []  # Set empty list if initialization fails

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('Text to Speech Tool')
        self.setGeometry(100, 100, 400, 200)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create status label
        self.status_label = QLabel("Ready - Press F8 to read text")
        layout.addWidget(self.status_label)
        
        # Create language selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Language:")
        self.lang_combo = QComboBox()
        self.update_language_list()
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)
        
        # Create speed control slider
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speed:")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(50)
        self.speed_slider.setMaximum(400)
        self.speed_slider.setValue(300)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(50)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_slider)
        layout.addLayout(speed_layout)
        
        # Create speed value label
        self.speed_value_label = QLabel("Speed: 400")
        layout.addWidget(self.speed_value_label)
        
        # Create test button
        self.test_button = QPushButton("Test Speech")
        self.test_button.clicked.connect(self.test_speech)
        layout.addWidget(self.test_button)

    def update_language_list(self):
        """Update the language dropdown with available voices"""
        self.lang_combo.clear()
        self.voice_map = {}  # Map to store language name to voice object
        
        for voice in self.voices:
            # Extract language from voice name
            if 'german' in voice.name.lower():
                lang = 'German'
            else:
                lang = 'English'
                
            # Add gender information
            if 'female' in voice.name.lower():
                lang += ' (Female)'
            else:
                lang += ' (Male)'
                
            self.voice_map[lang] = voice
            self.lang_combo.addItem(lang)
            
        # If no voices found, add default
        if self.lang_combo.count() == 0:
            self.lang_combo.addItem('English (Default)')

    def on_language_changed(self, index):
        """Handle language selection change"""
        selected_lang = self.lang_combo.currentText()
        if selected_lang in self.voice_map:
            voice = self.voice_map[selected_lang]
            self.engine.setProperty('voice', voice.id)
            print(f"Changed voice to: {selected_lang}")

    def get_clipboard_content(self):
        """Get current clipboard content"""
        try:
            win32clipboard.OpenClipboard()
            try:
                return win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            except:
                return ""
            finally:
                win32clipboard.CloseClipboard()
        except:
            return ""

    def set_clipboard_content(self, text):
        """Set clipboard content"""
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            return True
        except:
            return False

    def update_speed(self):
        """Update the speech rate based on slider value"""
        speed = self.speed_slider.value()
        self.speed_value_label.setText(f"Speed: {speed}")
        self.engine.setProperty('rate', speed)

    def test_speech(self):
        """Test the text-to-speech with current settings"""
        self.engine.stop()  # Stop any ongoing speech
        speed = self.speed_slider.value()
        self.engine.setProperty('rate', speed)
        self.engine.say("This is a test of the text to speech system. Das ist ein Test!")
        self.engine.runAndWait()

    def handle_hotkey(self, event):
        """Handle the global hotkey press"""
        # Ignore key release events and prevent multiple processing
        if event.event_type == 'up' or self.is_processing:
            return
            
        print("\n=== Hotkey Debug ===")
        print(f"Hotkey pressed: {event}")
        
        self.is_processing = True  # Set processing lock
            
        try:
            # Save current window focus
            current_window = win32gui.GetForegroundWindow()
            print(f"Current window handle: {current_window}")
            
            # Fixed delay to let keys be released naturally
            print("Waiting brief delay before copying")
            time.sleep(0.3)  # 300ms delay
            
            print("Simulating Ctrl+C using Win32 API")
            # Simulate Ctrl+C using Win32 API
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)  # Ctrl down
            win32api.keybd_event(ord('C'), 0, 0, 0)  # C down
            time.sleep(0.05)  # Brief delay between press and release
            win32api.keybd_event(ord('C'), 0, win32con.KEYEVENTF_KEYUP, 0)  # C up
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up
            
            # Wait a bit for the clipboard to update
            time.sleep(0.2)
            
            # Get the current clipboard content
            current_content = self.get_clipboard_content()
            print(f"Current clipboard length: {len(current_content) if current_content else 0}")
            
            if current_content:  # If we have any content, read it
                print("Reading clipboard content")
                self.read_clipboard_text(current_window)
            else:
                print("No content found in clipboard")
                
        except Exception as e:
            print(f"Error in hotkey handler: {str(e)}")
        finally:
            self.is_processing = False  # Release processing lock
                
        print("=== End Hotkey Debug ===\n")

    def speak_text_thread(self, text):
        """Run text-to-speech in a separate thread"""
        try:
            # Create a new engine instance for this thread
            thread_engine = pyttsx3.init()
            # Copy properties from main engine
            thread_engine.setProperty('rate', self.engine.getProperty('rate'))
            thread_engine.setProperty('voice', self.engine.getProperty('voice'))
            
            def onWord(name, location, length):
                # Check if we should stop
                if self.should_stop:
                    thread_engine.stop()
                    return
            
            # Connect word callback
            thread_engine.connect('started-word', onWord)
            
            # Speak the text
            thread_engine.say(text)
            thread_engine.runAndWait()
            
            # Update status if we completed normally (not stopped)
            if not self.should_stop:
                # Use invokeMethod to safely update UI from another thread
                QApplication.instance().postEvent(self, StatusUpdateEvent("Ready - Press F8 to read text"))
            
        except Exception as e:
            print(f"Error in speech thread: {str(e)}")
        finally:
            self.speech_thread = None
            self.should_stop = False

    def read_clipboard_text(self, previous_window):
        """Read the text from clipboard using text-to-speech"""
        print("\n--- Clipboard Debug ---")
        try:
            text = self.get_clipboard_content().strip()
            print(f"Clipboard text length: {len(text)}")
            if text:
                print("Text found, starting speech")
                self.status_label.setText("Reading text... (Ctrl+Alt+F8 to stop)")
                
                # Stop any existing speech thread
                self.stop_speech()
                
                # Start new speech thread
                self.should_stop = False
                self.speech_thread = threading.Thread(target=self.speak_text_thread, args=(text,))
                self.speech_thread.daemon = True  # Make thread daemon so it exits when main program exits
                self.speech_thread.start()
                
            else:
                print("No text found in clipboard")
                self.status_label.setText("No text selected!")
                self.status_label.setText("Ready - Press F8 to read text")
        except Exception as e:
            print(f"Error in read_clipboard_text: {str(e)}")
            self.status_label.setText(f"Error: {str(e)}")
            self.status_label.setText("Ready - Press F8 to read text")
        print("--- End Clipboard Debug ---\n")
        
        # Restore previous window focus
        try:
            if previous_window:
                win32gui.SetForegroundWindow(previous_window)
        except Exception:
            pass

    def stop_speech(self):
        """Stop any ongoing speech"""
        try:
            if self.speech_thread and self.speech_thread.is_alive():
                self.should_stop = True
                self.speech_thread.join(timeout=1)  # Wait for thread to finish
                self.status_label.setText("Speech stopped - Ready")
                print("Speech stopped by user")
        except Exception as e:
            print(f"Error stopping speech: {str(e)}")

    def event(self, event):
        if event.type() == StatusUpdateEvent.EVENT_TYPE:
            self.status_label.setText(event.status_text)
            return True
        return super().event(event)

def main():
    app = QApplication(sys.argv)
    window = TTSWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
