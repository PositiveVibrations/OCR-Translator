from PyQt5.QtWidgets import QTextEdit, QApplication, QWidget, QLabel, QComboBox, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect
from PyQt5.QtGui import QPixmap, QPainter, QPen, QGuiApplication, QIcon
from PIL import Image
import easyocr
from googletrans import Translator, LANGUAGES
import pyautogui
import configparser
import sys
import os


class LanguageSelectionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Snip Translator')
        self.setWindowOpacity(1.0)  # Set window opacity to 100%
        self.setMinimumWidth(600)   # Set minimum width to prevent widgets from being compressed

        self.settings_file = 'settings.ini'

        # Load default and translated languages from file
        self.default_language, self.translated_language = self.load_languages()

        from_label = QLabel('From:')
        to_label = QLabel('To:')
        self.original_text_edit = QTextEdit(self)
        self.original_text_edit.setGeometry(0, 400, 800, 200)
        self.original_text_edit.setReadOnly(True)  # Make it read-only
        self.original_text_edit.setLineWrapMode(QTextEdit.WidgetWidth)  # Wrap text at widget width
        self.original_text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # Show vertical scrollbar
        self.original_text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hide horizontal scrollbar

        self.translated_text_edit = QTextEdit(self)
        self.translated_text_edit.setGeometry(0, 600, 800, 200)
        self.translated_text_edit.setReadOnly(True)
        self.translated_text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        self.translated_text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.translated_text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Get a list of all language codes and names
        language_codes = list(LANGUAGES.keys())
        language_names = list(LANGUAGES.values())

        self.default_combo = QComboBox()
        self.default_combo.addItems(language_names)
        self.default_combo.setCurrentText(self.default_language)
        self.default_combo.currentIndexChanged.connect(self.update_default_language)

        self.translated_combo = QComboBox()
        self.translated_combo.addItems(language_names)
        self.translated_combo.setCurrentText(self.translated_language)
        self.translated_combo.currentIndexChanged.connect(self.update_translated_language)

        # Initialize snipping widget
        self.snipping_widget = SnippingWidget(self.default_language, self.translated_language)

        layout = QHBoxLayout()  # Create layout here
        layout.addWidget(from_label)
        layout.addWidget(self.default_combo)
        layout.addWidget(to_label)
        layout.addWidget(self.translated_combo)
        layout.addWidget(self.snipping_widget)  # Add snipping widget to layout

        # Set layout alignment to the top
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        # Load window position and size from settings file
        self.load_window_settings()

        # Create a label for displaying the snipped image
        self.screenshot_label = QLabel(self)
        self.screenshot_label.setGeometry(0, 100, 800, 600)
        self.update_screenshot()  # Load initial image
        

        # Create a timer to update the screenshot and translate using start_translation method
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_screenshot)
        #self.timer.timeout.connect(self.start_translation)

        
       

        self.timer.start(1000)  # Update every second

        # Initialize OCR and translator
        self.reader = easyocr.Reader(['en'])
        self.translator = Translator()

        # Add button to start OCR and translation
        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_translation)
        self.start_button.setEnabled(True)  

        # Add button to snip area
        self.snip_button = QPushButton('Snip Area', self)
        self.snip_button.clicked.connect(self.snip_area)

        # Add Chat button
        self.chat_button = QPushButton('Chat', self)
        self.chat_button.clicked.connect(self.open_chat_bar)

        # Add buttons below language selection
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.snip_button)
        button_layout.addWidget(self.chat_button)
        layout.addLayout(button_layout)

        # Initialize snipping widget
        self.snipping_widget = SnippingWidget(self.default_language, self.translated_language)

        self.snipping_widget.hide()

    def take_screenshot(self, start_x, start_y, end_x, end_y):
        settings = configparser.ConfigParser()
        settings.read('settings.ini')
        settings['Window'] = {
            'x': str(start_x),
            'y': str(start_y),
            'width': str(end_x - start_x),
            'height': str(end_y - start_y)
        }
        with open('settings.ini', 'w') as configfile:
            settings.write(configfile)

    def snip_area(self):
      
    # Reset begin and end points
        self.snipping_widget.begin = None
        self.snipping_widget.end = None

        # Show the snipping widget
        self.snipping_widget.show()

    def start_translation(self):
        # Read the screenshot area coordinates from the settings file
        settings = configparser.ConfigParser()
        settings.read('settings.ini')
        x1 = settings.getint('Snip', 'x1')
        y1 = settings.getint('Snip', 'y1')
        x2 = settings.getint('Snip', 'x2')
        y2 = settings.getint('Snip', 'y2')
        
        settings = configparser.ConfigParser()
        settings.read('settings.ini')
        x1 = settings.getint('Snip', 'x1')
        y1 = settings.getint('Snip', 'y1')
        x2 = settings.getint('Snip', 'x2')
        y2 = settings.getint('Snip', 'y2')
        #read in default language
        default_language = self.default_combo.currentText()
        #read in translated language
        translated_language = self.translated_combo.currentText()

        # Read the screenshot of the selected area
        screenshot = QApplication.primaryScreen().grabWindow(QApplication.desktop().winId(), x1, y1, x2 - x1, y2 - y1)
        screenshot.save('snip.png', 'png')

        # Perform OCR
        image = Image.open('snip.png')
        text_list = self.reader.readtext('snip.png')

        # Combine all text into one paragraph
        paragraph = ' '.join([text_info[1] for text_info in text_list])

        # Translate the combined text
        translation = self.translator.translate(paragraph, src=translated_language, dest=default_language)
        original_text = paragraph
        translated_text = translation.text
        self.original_text_edit.setPlainText(f'Original Text: {original_text}')
        self.translated_text_edit.setPlainText(f'Translated Text: {translated_text}')

    def update_screenshot(self):
        
        screenshot_path = 'snip.png'
        if os.path.exists(screenshot_path):
            pixmap = QPixmap(screenshot_path)
            self.screenshot_label.setPixmap(pixmap)
            self.screenshot_label.adjustSize()
            self.screenshot_label.show()
            # Resize the window to fit the screenshot and double the height for the text but set a minimal width to like 400
            self.resize(max(pixmap.width(), 900), pixmap.height() + 600)

            # Align the image to the top of the window but 100 down to make space for the text
            self.screenshot_label.setGeometry(0, 100, pixmap.width(), pixmap.height())
            #resize the text box to fit the window BUT MIN IS 800

            self.original_text_edit.setGeometry(0, pixmap.height() + 100, max(pixmap.width(), 800), 200)
            self.translated_text_edit.setGeometry(0, pixmap.height() + 300, max(pixmap.width(), 800), 200)
            

            

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
        config.read(self.settings_file)
        try:
            if (
                config.getint('Window', 'x') == self.x() and
                config.getint('Window', 'y') == self.y() and
                config.getint('Window', 'width') == self.width() and
                config.getint('Window', 'height') == self.height()
            ):
                return  # No need to save if the position and size haven't changed
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass

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
        config.read(self.settings_file)
        try:
            if (
                config.getint('Window', 'x') == self.x() and
                config.getint('Window', 'y') == self.y() and
                config.getint('Window', 'width') == self.width() and
                config.getint('Window', 'height') == self.height()
            ):
                return  # No need to save if the position and size haven't changed
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass

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
    def open_chat_bar(self):
        #wait for the next point the user clicks using pyautogui and store the x and y coordinates to the settings.ini without distubing the other things Store it as Chat
        settings = configparser.ConfigParser()
        while True:
            # Wait for a click event
            pyautogui.click()
            x,y = pyautogui.position()

            
            # Store the position in settings.ini
            settings.read('settings.ini')
            settings['Chat'] = {
                'x': str(x),
                'y': str(y)
            }
            with open('settings.ini', 'w') as configfile:
                settings.write(configfile)
            break




        if not hasattr(self, 'chat_bar'):
            self.chat_bar = QTextEdit(self)
            self.chat_bar.setGeometry(0, self.height() - 200, self.width(), 200)
            self.chat_bar.setPlaceholderText('Type your message here...')
            self.chat_bar.show()
            self.chat_bar.textChanged.connect(self.handle_text_changed)

    def handle_text_changed(self):
        # Implement handling text changes in the chat bar
        if hasattr(self, 'chat_bar'):
            text = self.chat_bar.toPlainText()
            if text.strip() and text.endswith('\n'):
                self.send_message(text.strip())
                self.chat_bar.clear()

    def send_message(self, message):
        # Implement sending message functionality
        print(f"Sending message: {message}")
        # Process the message (translate, send, etc.)
        #click on the chat bar
        settings = configparser.ConfigParser()
        settings.read('settings.ini')
        x = settings.getint('Chat', 'x')
        y = settings.getint('Chat', 'y')

        #translate the message using the translated language selected From the in gui 
        translated_language = self.translated_combo.currentText()
        default_language = self.default_combo.currentText()
        translation = self.translator.translate(message, src=default_language, dest=translated_language)
        message = translation.text

        pyautogui.click(x, y)
        #type the message at a normal speed
        pyautogui.typewrite(message, interval=0.1)
        pyautogui.press('enter')







class SnippingWidget(QWidget):
    def __init__(self, default_language, translated_language):
        super().__init__()
        self.default_language = default_language
        self.translated_language = translated_language
        self.setWindowTitle('Snipping Tool')
        self.setGeometry(0, 0, QApplication.desktop().screenGeometry().width(), QApplication.desktop().screenGeometry().height())
        self.setWindowOpacity(0.5) # Set transparency level
        self.setMouseTracking(True)
        self.begin = None
        self.end = None
        self.settings_file = 'settings.ini'
        self.load_settings()

        self.label = QLabel('Select Area', self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 0, self.width(), self.height())
        self.label.setStyleSheet('font-size: 24px; color: white;')

        self.showFullScreen()

    def paintEvent(self, event):
        if self.begin is None or self.end is None:
            return

        qp = QPainter(self)
        qp.setPen(QPen(Qt.red, 2))
        qp.drawRect(QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        if self.begin is None or self.end is None:
            self.begin = event.pos()
            self.end = event.pos()
            self.update()

    def mouseMoveEvent(self, event):
        if self.begin is not None:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.begin is not None:
            self.end = event.pos()
            self.close()
            self.capture_snip()



    def capture_snip(self):
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())

        screenshot = QGuiApplication.primaryScreen().grabWindow(
            QApplication.desktop().winId(), x1, y1, x2 - x1, y2 - y1
        )
        screenshot.save('snip.png', 'png')
        print('Screenshot saved as snip.png')

        self.save_coordinates(x1, y1, x2, y2)

        # Display the snipped image
        pixmap = QPixmap('snip.png')
        self.label.setPixmap(pixmap)
        self.label.setGeometry(0, 0, x2 - x1, y2 - y1)  # Set geometry relative to SnippingWidget
        self.label.show()
        

    def save_coordinates(self, x1, y1, x2, y2):
        config = configparser.ConfigParser()
        config.read(self.settings_file)
        if 'Snip' not in config:
            config['Snip'] = {}
        config['Snip']['x1'] = str(x1)
        config['Snip']['y1'] = str(y1)
        config['Snip']['x2'] = str(x2)
        config['Snip']['y2'] = str(y2)
        with open(self.settings_file, 'w') as configfile:
            config.write(configfile)

    def load_coordinates(self):
        config = configparser.ConfigParser()
        config.read(self.settings_file)
        if 'Snip' in config:
            coords = config['Snip']
            self.begin = QPoint(int(coords['x1']), int(coords['y1']))
            self.end = QPoint(int(coords['x2']), int(coords['y2']))

    def save_settings(self):
        config = configparser.ConfigParser()
        config['Settings'] = {
            'default_language': self.default_language,
            'translated_language': self.translated_language
        }
        with open(self.settings_file, 'w') as configfile:
            config.write(configfile)

    def load_settings(self):
        config = configparser.ConfigParser()
        config.read(self.settings_file)
        if 'Settings' in config:
            settings = config['Settings']
            self.default_language = settings.get('default_language', 'English')
            self.translated_language = settings.get('translated_language', 'English')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = LanguageSelectionWidget()
    widget.show()
    sys.exit(app.exec_())