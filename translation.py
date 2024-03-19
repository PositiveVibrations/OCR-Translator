from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PIL import Image
import easyocr
from googletrans import Translator
import configparser
import sys

class LanguageSelectionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Language Selection')
        self.setWindowOpacity(0.3)  # Set window opacity to 80%
        self.setMinimumWidth(300)   # Set minimum width to prevent widgets from being compressed

        self.settings_file = 'settings.ini'

        # Load default and translated languages from file
        self.default_language, self.translated_language = self.load_languages()

        from_label = QLabel('From:')
        to_label = QLabel('To:')

        self.default_combo = QComboBox()
        self.default_combo.addItems(['English', 'French', 'German', 'Spanish', 'Italian'])
        self.default_combo.setCurrentText(self.default_language)
        self.default_combo.currentIndexChanged.connect(self.update_default_language)

        self.translated_combo = QComboBox()
        self.translated_combo.addItems(['English', 'French', 'German', 'Spanish', 'Italian'])
        self.translated_combo.setCurrentText(self.translated_language)
        self.translated_combo.currentIndexChanged.connect(self.update_translated_language)

        layout = QHBoxLayout()
        layout.addWidget(from_label)
        layout.addWidget(self.default_combo)
        layout.addWidget(to_label)
        layout.addWidget(self.translated_combo)

        # Set layout alignment to the top
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        # Load window position and size from settings file
        self.load_window_settings()

        # Create a label for displaying the screenshot
        self.screenshot_label = QLabel(self)
        self.screenshot_label.setGeometry(0, 100, 800, 600)

        # Create a timer to update the screenshot
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_screenshot)
        self.timer.start(1000)  # Update every second

        # Initialize OCR and translator
        self.reader = easyocr.Reader(['en'], gpu=True)
        self.translator = Translator()

        # Add button to start OCR and translation
        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_translation)
        self.start_button.setEnabled(True)  

        # Add start button below language selection
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        layout.addLayout(button_layout)

    def start_translation(self):
        # Read the screenshot area coordinates from the settings file
        settings = configparser.ConfigParser()
        settings.read('settings.ini')
        x1 = settings.getint('Window', 'x')
        y1 = settings.getint('Window', 'y')+110
        x2 = settings.getint('Window', 'width') + x1
        y2 = settings.getint('Window', 'height') + y1

        # Read the screenshot of the selected area
        screenshot = QApplication.primaryScreen().grabWindow(QApplication.desktop().winId(), x1, y1, x2 - x1, y2 - y1)
        screenshot.save('screenshot.png', 'png')

        # Perform OCR
        image = Image.open('screenshot.png')
        text_list = self.reader.readtext('screenshot.png')

        # Combine all text into one paragraph
        paragraph = ' '.join([text_info[1] for text_info in text_list])

        # Translate the combined text
        translation = self.translator.translate(paragraph, src='es', dest='en')
        print(f'Original Text: {paragraph}')
        print(f'Translation: {translation.text}')

    def update_screenshot(self):
        pass  # This method will be called every second to update the screenshot label

    def load_languages(self):
        config = configparser.ConfigParser()
        config.read(self.settings_file)
        default_language = config.get('Settings', 'default_language', fallback='English')
        translated_language = config.get('Settings', 'translated_language', fallback='English')
        return default_language, translated_language

    def save_languages(self):
        config = configparser.ConfigParser()
        config.read(self.settings_file)
        if 'Settings' not in config:
            config['Settings'] = {}
        config['Settings']['default_language'] = self.default_combo.currentText()
        config['Settings']['translated_language'] = self.translated_combo.currentText()
        with open(self.settings_file, 'w') as configfile:
            config.write(configfile)

    def update_default_language(self, index):
        self.save_languages()

    def update_translated_language(self, index):
        self.save_languages()

    def load_window_settings(self):
        config = configparser.ConfigParser()
        config.read(self.settings_file)
        try:
            x = config.getint('Window', 'x')
            y = config.getint('Window', 'y')
            width = config.getint('Window', 'width')
            height = config.getint('Window', 'height')
            self.setGeometry(x, y, width, height)
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass

    def save_window_settings(self):
        config = configparser.ConfigParser()
        config['Window'] = {
            'x': str(self.x()),
            'y': str(self.y()),
            'width': str(self.width()),
            'height': str(self.height())
        }
        with open(self.settings_file, 'w') as configfile:
            config.write(configfile)

    def moveEvent(self, event):
        self.save_window_settings()
        super().moveEvent(event)

    def resizeEvent(self, event):
        self.save_window_settings()
        super().resizeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    language_selection_widget = LanguageSelectionWidget()
    language_selection_widget.show()

    sys.exit(app.exec_())
