import sys
import pyperclip
import keyboard
import pyttsx3
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QHBoxLayout, QComboBox
from PyQt5.QtCore import Qt

class TTSWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_tts_engine()
        self.init_ui()
        
        # Register hotkey
        keyboard.add_hotkey('ctrl+alt+f8', self.read_clipboard, suppress=True)
        
        print("Initialization complete - Copy text and press Ctrl+Alt+F8 to read it")

    def setup_tts_engine(self):
        """Initialize the text-to-speech engine"""
        try:
            self.engine = pyttsx3.init("sapi5")
            self.voices = self.engine.getProperty('voices')
            print(f"Found {len(self.voices)} voices")
            
            # Print detailed voice information
            for voice in self.voices:
                print(f"Voice ID: {voice.id}")
                print(f"Voice Name: {voice.name}")
                print(f"Voice Languages: {voice.languages}")
                print("-" * 50)
            
            # Set default voice
            if self.voices:
                self.engine.setProperty('voice', self.voices[0].id)
                print(f"Set default voice: {self.voices[0].name}")
            else:
                print("No voices found")
            
            # Set default rate
            self.engine.setProperty('rate', 400)
        except Exception as e:
            print(f"Error initializing TTS engine: {str(e)}")
            self.voices = []

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('Text to Speech Tool')
        self.setGeometry(100, 100, 400, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create status label
        self.status_label = QLabel("Ready - Copy text and press Ctrl+Alt+F8 to read it")
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
        self.speed_slider.setMinimum(100)
        self.speed_slider.setMaximum(1000)
        self.speed_slider.setValue(400)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(100)
        self.speed_slider.valueChanged.connect(self.update_speed)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_slider)
        layout.addLayout(speed_layout)
        
        # Create speed value label
        self.speed_value_label = QLabel(f"Speed: {self.speed_slider.value()}")
        layout.addWidget(self.speed_value_label)
        
        # Create test button
        self.test_button = QPushButton("Test Speech")
        self.test_button.clicked.connect(self.test_speech)
        layout.addWidget(self.test_button)

    def update_language_list(self):
        """Update the language dropdown with available voices"""
        self.lang_combo.clear()
        self.voice_map = {}
        
        # Define known voice genders
        female_voices = ['zira', 'hazel', 'hedda', 'female']
        
        for voice in self.voices:
            # Print raw voice data for debugging
            print(f"\nProcessing voice:")
            print(f"ID: {voice.id}")
            print(f"Name: {voice.name}")
            
            # Determine language based on voice properties
            voice_id_lower = voice.id.lower()
            voice_name_lower = voice.name.lower()
            
            # Check for German voices
            if any(german_id in voice_id_lower for german_id in ['german', 'deutsch', 'de-de', 'de_']):
                lang = 'German'
            else:
                lang = 'English'
            
            # Add gender information
            if any(female_name in voice_name_lower for female_name in female_voices):
                gender = '(Female)'
            else:
                gender = '(Male)'
            
            voice_label = f"{lang} {gender}"
            
            # Only add if we don't already have this exact voice type
            if voice_label not in self.voice_map:
                self.voice_map[voice_label] = voice
                self.lang_combo.addItem(voice_label)
                print(f"Added voice: {voice_label} - {voice.name}")
            
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

    def update_speed(self):
        """Update the speech rate based on slider value"""
        speed = self.speed_slider.value()
        self.speed_value_label.setText(f"Speed: {speed}")
        self.engine.setProperty('rate', speed)
        print(f"Speech rate updated to: {speed}")

    def test_speech(self):
        """Test the text-to-speech with current settings"""
        self.engine.say("This is a test of the text to speech system. Das ist ein Test!")
        self.engine.runAndWait()

    def read_clipboard(self):
        """Read text from clipboard using text-to-speech"""
        try:
            # Get text from clipboard
            text = pyperclip.paste().strip()
            
            if text:
                print(f"\nReading text: {text[:100]}{'...' if len(text) > 100 else ''}")
                self.status_label.setText("Reading text...")
                self.engine.say(text)
                self.engine.runAndWait()
                self.status_label.setText("Ready - Copy text and press Ctrl+Alt+F8 to read it")
            else:
                print("No text in clipboard")
                self.status_label.setText("No text in clipboard!")
        except Exception as e:
            print(f"Error reading clipboard: {str(e)}")
            self.status_label.setText("Error reading clipboard!")

def main():
    app = QApplication(sys.argv)
    window = TTSWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
