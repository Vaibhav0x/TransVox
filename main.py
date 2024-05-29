from PyQt5 import QtWidgets,QtCore
from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal,QUrl,QTimer
from PyQt5.QtWidgets import QMessageBox, QApplication, QFileDialog, QMainWindow,QSlider,QDialog,QListWidgetItem
from PyQt5.QtGui import QIcon
from spellchecker import SpellChecker
from langdetect import detect
import googletrans
import sys
import os
import gtts
from gtts import gTTS
import pyttsx3
from googletrans import Translator, LANGUAGES
import shutil
import speech_recognition as sr
from pydub import AudioSegment
import pygame
from multiprocessing import Process
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import datetime
import resources
import sys
import re
import os
from database import *
from System_log import login_assets_qrc

# Email validation regex pattern
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

def check_ui_files():
    required_files = [r'System_log\login.ui', r'System_log\create.ui', r'Ui\main.ui']
    for file in required_files:
        if not os.path.isfile(file):
            raise FileNotFoundError(f"Required UI file '{file}' not found.")

class LoginWindow(QtWidgets.QDialog):
    def __init__(self):
        super(LoginWindow, self).__init__()
        uic.loadUi(r'System_log\login.ui', self)
        self.setWindowTitle("Login System")
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.login_btn.clicked.connect(self.handle_login)
        self.new_acc_btn.clicked.connect(self.open_create_account_window)
        self.forgot_btn.clicked.connect(self.open_reset_credentials_window)   
        
        self.show_btn.clicked.connect(self.toggle_password_visibility)
        
        self.password_visible = False
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)  # Set password field to hide text by default

        self.cancel_btn.clicked.connect(self.Confirm_Close)

    def Confirm_Close(self):
        reply=QMessageBox().question(self,"Warning","Do you want to Exit",QMessageBox.Yes| QMessageBox.No)
        if reply==QMessageBox.Yes:
            self.close()

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if verify_user(username, password):
            self.open_main_window(username)
        else:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Invalid username or password')
        self.close()

    def open_create_account_window(self):
        self.create_account_window = CreateAccountWindow()
        self.create_account_window.show()
        # self.close()

    def open_reset_credentials_window(self):
        self.reset_credentials_window = ResetCredentialsWindow()
        self.reset_credentials_window.show()
        # self.close()

    def open_main_window(self, username):
        self.main_window = MainWindow(username)
        self.main_window.show()
        self.close()

    def toggle_password_visibility(self):
        if self.password_visible:
            self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
            self.show_btn.setIcon(QIcon(r"System_log/login_assets/eye.png"))
            # self.show_password_btn.setText("Show Password")
        else:
            self.password_input.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.show_btn.setIcon(QIcon(r"System_log/login_assets/hidden.png"))
            # self.show_password_btn.setText("Hide Password")
        self.password_visible = not self.password_visible

class CreateAccountWindow(QtWidgets.QDialog):
    def __init__(self):
        super(CreateAccountWindow, self).__init__()
        uic.loadUi(r'System_log\create.ui', self)
        self.setWindowTitle("Create Account")
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint & ~QtCore.Qt.WindowContextHelpButtonHint)

        self.create_acc_btn.clicked.connect(self.handle_create_account)
        self.cancel_btn.clicked.connect(self.Confirm_Close)

    def Confirm_Close(self):
        reply=QMessageBox().question(self,"Create Account","You Doesn't want to Create Account",QMessageBox.Yes| QMessageBox.No)
        if reply==QMessageBox.Yes:
            self.close()

    def handle_create_account(self):
        full_name = self.user_name_input.text()
        email = self.user_email_input.text()
        username = self.user_username_input.text()
        password = self.user_password_input.text()
        # Validate email format
        if not re.match(EMAIL_REGEX, email):
            QtWidgets.QMessageBox.warning(self, 'Error', 'Invalid email format')
            return
        
        create_user(full_name, email, username, password)
        QtWidgets.QMessageBox.information(self, 'Success', 'Account created successfully')
        self.open_login_window()

    def open_login_window(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

class ResetCredentialsWindow(QtWidgets.QDialog):
    def __init__(self):
        super(ResetCredentialsWindow, self).__init__()
        uic.loadUi(r'System_log\create.ui', self)
        self.setWindowTitle("Reset Account Info")
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.create_acc_btn.setText("Forgot")
        self.create_acc_btn.clicked.connect(self.handle_reset_credentials)
        self.label1.setText("Enter Old Username:")
        self.user_name_input.setPlaceholderText("Enter old username")
        self.cancel_btn.clicked.connect(self.Confirm_Close)
        # self.label2.setText(":")
        # self.fullNameInput.setPlaceholderText("Enter old username")

    def Confirm_Close(self):
        reply=QMessageBox().question(self,"Reset Credentials","You doesn't want to reset the password and username",QMessageBox.Yes| QMessageBox.No)
        if reply==QMessageBox.Yes:
            self.close()

    def handle_reset_credentials(self):
        old_username = self.user_name_input.text()
        email = self.user_email_input.text()
        new_username = self.user_username_input.text()
        new_password = self.user_password_input.text()

        # Validate email format
        if not re.match(EMAIL_REGEX, email):
            QtWidgets.QMessageBox.warning(self, 'Error', 'Invalid email format')
            return

        if update_user_credentials(old_username, email, new_username, new_password):
            QtWidgets.QMessageBox.information(self, 'Success', 'Credentials reset successfully')
            self.close()
        else:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Invalid email or old username')

    def open_login_window(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()


class AdminLoginWindow(QtWidgets.QDialog):
    def __init__(self):
        super(AdminLoginWindow, self).__init__()
        uic.loadUi(r'System_log\login.ui', self)

        self.login_btn.clicked.connect(self.handle_admin_login)
        self.new_acc_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.close)

    def handle_admin_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Assuming admin credentials are hardcoded for simplicity
        if username == "admin" and password == "admin":
            self.open_admin_main_window()
        else:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Invalid admin credentials')

    def open_admin_main_window(self):
        self.admin_main_window = AdminMainWindow()
        self.admin_main_window.show()
        self.close()

class AdminMainWindow(QtWidgets.QDialog):
    def __init__(self):
        super(AdminMainWindow, self).__init__()
        uic.loadUi(r'System_log\admin.ui', self)

        self.del_btn.clicked.connect(self.handle_delete_user)
        self.populate_user_list()
        self.cancel_btn.clicked.connect(self.close)

    def populate_user_list(self):
        self.userListWidget.clear()
        users = get_all_users()
        for user in users:
            self.userListWidget.addItem(f"ID: {user[0]}, Username: {user[3]}, Email: {user[2]}")

    def handle_delete_user(self):
        selected_item = self.userListWidget.currentItem()
        if selected_item:
            user_info = selected_item.text()
            user_id = int(user_info.split(",")[0].split(":")[1].strip())
            delete_user(user_id)
            self.populate_user_list()
        else:
            QtWidgets.QMessageBox.warning(self, 'Error', 'No user selected')
    
class VoiceSettingsDialog(QDialog):
    accepted = pyqtSignal(str,int, int, int)
    def __init__(self,engine,parent=None):
        super().__init__()
        uic.loadUi(r'Ui\Setting_Dialog.ui',self)
        self.setWindowTitle("Voice Settings")
        self.setWindowIcon(QIcon(r'resources\text_speech.png'))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # remove the ? mark from title bar
        self.engine = engine
        self.cancel_btn.clicked.connect(self.reject)
        self.generate_btn.clicked.connect(self.generate_voice)

        self.reset_btn.clicked.connect(self.resetChanges)

        # Add sliders for pitch and volume
        self.pitch_slider.setMinimum(0)
        self.pitch_slider.setMaximum(200)
        self.pitch_slider.setValue(150)
        self.pitch_slider.valueChanged.connect(self.pitch_slider_func)
        self.pitch_edit.textChanged.connect(self.pitch_changed)

        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(200)
        self.volume_slider.setValue(90)
        self.volume_slider.valueChanged.connect(self.volume_slider_func)
        self.volume_edit.textChanged.connect(self.volume_changed)

        self.rate_slider.setMinimum(0)  # Adjust min and max as needed
        self.rate_slider.setMaximum(200)
        self.rate_slider.setValue(100)   # Adjust default value as needed
        self.rate_slider.valueChanged.connect(self.rate_slider_func)
        self.rate_edit.textChanged.connect(self.rate_changed)
    
    def generate_voice(self):
        pitch = self.pitch_slider.value()
        rate = self.rate_slider.value()
        volume = self.volume_slider.value()
        gender = "female" if self.engine.getProperty('voice').endswith("ZIRA_11.0") else "male"  # Determine gender from current voice
        self.accepted.emit(gender, pitch, rate, volume)  # Emit 'gender' along with other settings
        self.close()
        QMessageBox().information(self,"Voice Generated","Successfully Audio Generated")

    def pitch_slider_func(self,value):
        self.pitch_edit.setText(str(value))

    def volume_slider_func(self,value):
        self.volume_edit.setText(str(value))

    def rate_slider_func(self,value):
        self.rate_edit.setText(str(value))

    def pitch_changed(self, text):
        try:
            value = int(text)
            if value >= self.pitch_slider.minimum() and value <= self.pitch_slider.maximum():
                self.pitch_slider.setValue(value)
        except ValueError:
            pass

    def volume_changed(self, text):
        try:
            value = int(text)
            if value >= self.volume_slider.minimum() and value <= self.volume_slider.maximum():
                self.volume_slider.setValue(value)
        except ValueError:
            pass
    
    def rate_changed(self, text):
        try:
            value = int(text)
            if value >= self.rate_slider.minimum() and value <= self.rate_slider.maximum():
                self.rate_slider.setValue(value)
        except ValueError:
            pass

    def resetChanges(self):
        # Reset sliders to their initial values
        self.pitch_slider.setValue(150)  # Set initial value for high slider
        self.volume_slider.setValue(90)   # Set initial value for low slider
        self.rate_slider.setValue(100) # Set initial value for gamma slider

        # Emit a signal to notify the main window to reset the image
        self.accepted.emit('default',150, 90, 100)  # Emit signal with initial values

class MainWindow(QMainWindow):
    def __init__(self,username):
        super().__init__()
        uic.loadUi(os.path.abspath(r'Ui/main.ui'), self)    # Load UI
        self.setWindowTitle("TransVox:Transcription System")
        self.setWindowIcon(QIcon(r'resources\main_logo.webp'))
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()

        self.username = username
        '''
        Stacked Widget connections with Main Menu buttons
        '''
        self.home_btn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0)) 
        self.text_translator_btn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1)) 
        self.voice_text_btn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2)) 
        self.text_voice_btn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))

        '''
        Text translator buttons 
        '''
        self.lang_combobox.addItems(LANGUAGES.values())
        self.lang_combobox.currentIndexChanged.connect(self.updateSelectedLanguage)
        self.search_edit.textChanged.connect(self.updateLanguageList)
        self.language_list.addItems(LANGUAGES.values())
        self.language_list.itemClicked.connect(self.updateSelectedLanguage)
        self.translate_btn.clicked.connect(self.translateText)
        self.speak_btn.clicked.connect(self.speakTranslatedText)
        self.user_text.textChanged.connect(self.onTextChanged)
        self.suggestions_list.itemClicked.connect(self.onSuggestionClicked)

        '''
        Connect the Action Bar with their respective slots 
        '''
        self.actionTranslateExpress.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.actionVoice_to_Text.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(2)) 
        self.actionText_to_Voice.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(3))
        
        # self.actionVoice_Setting.triggered.connect(self.open_voice_settings_dialog)

        '''
        Voice to text button widget connections
        '''
        self.open_btn.clicked.connect(self.open_file)
        self.play_btn.clicked.connect(self.play_audio)
        # self.pause_btn.clicked.connect(self.pause_audio)
        self.reset_file_btn.clicked.connect(self.reset_file)

        self.text_slider = QSlider(Qt.Horizontal)
        self.text_slider.setMinimum(0)
        self.text_slider.setMaximum(100)
        self.text_slider.sliderMoved.connect(self.sliderMoved)
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)

        self.generate_text_btn.clicked.connect(self.transcribe_audio)
        self.save_text_btn.clicked.connect(self.save_transcription)
        
        '''
        Language Buttons connect with stacked widget
        '''
        self.english_btn.clicked.connect(lambda: self.stackedWidget_2.setCurrentIndex(0)) 
        self.hindi_btn.clicked.connect(lambda: self.stackedWidget_2.setCurrentIndex(1))

        # self.david_btn.clicked.connect(self.generate_male_voice)
        # self.zira_btn.clicked.connect(self.open_voice_settings_dialog)
        self.david_btn.clicked.connect(lambda: self.open_voice_settings_dialog("male"))  # Connect to male voice
        self.zira_btn.clicked.connect(lambda: self.open_voice_settings_dialog("female"))  # Connect to female voice
        '''
        Create an instance of the VoiceSettingDialog
        '''
        self.voice_settings_dialog = VoiceSettingsDialog(self.engine)
        self.voice_settings_dialog.accepted.connect(self.generate_voice) 

        self.download_btn.clicked.connect(self.download_voice)
        self.play_pause_btn.clicked.connect(self.play_ai_voice)
        self.timer.timeout.connect(self.updateVoiceTime)

        self.play_btn.setEnabled(False)
        self.generate_text_btn.setEnabled(False)
        self.save_text_btn.setEnabled(False)
        self.media_player = QMediaPlayer()
        
        self.output_filename = None
        self.language_list.clear()

        # Add items with associated data
        for lang_code, lang_name in googletrans.LANGUAGES.items():
            item = QListWidgetItem(lang_name)
            item.setData(Qt.UserRole, lang_code)  # Set the language code as data for the item
            self.language_list.addItem(item)

        self.actionSystem_Log.triggered.connect(self.show_system_logs)
        self.actionUser_Account.triggered.connect(self.open_admin_login)
        log_user_activity(self.username, "Logged in")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Close Confirmation',
                                               'Do you want to close the application?',
                                               QMessageBox.Yes | QMessageBox.No,
                                               QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def show_system_logs(self):
        self.window=QDialog()
        uic.loadUi(r"System_log\system_logs.ui",self.window)
        self.window.setWindowTitle("System Logs")
        logs = get_user_logs()
        for log in logs:
            self.window.listWidget.addItem(f"User: {log[0]}, Time: {log[1]}, Data: {log[2]}")
        self.window.close_btn.clicked.connect(self.window.close)
        self.window.exec_()
    
    def open_admin_login(self):
        self.admin_login_window = AdminLoginWindow()
        self.admin_login_window.show()

    '''
    ----------------------------Text Translator Widget Functionalities-------------------------
    '''
    def updateLanguageList(self):
        try:
            search_text = self.search_edit.text().lower()
            filtered_languages = [lang for lang in LANGUAGES.values() if search_text in lang.lower()]
            self.language_list.clear()
            self.language_list.addItems(filtered_languages)

            # Update dropdown selection if only one item matches the search
            if len(filtered_languages) == 1:
                self.lang_combobox.setCurrentText(filtered_languages[0])
        except Exception as e:
            print("update lang exception:",e)

    def updateSelectedLanguage(self, item=None):
        try:
            if isinstance(item, QListWidgetItem):
                selected_language = item.text()
                self.search_edit.setText(selected_language)
            elif isinstance(item, int):
                selected_language = self.lang_combobox.currentText()
                self.search_edit.setText(selected_language)
            else:
                QMessageBox().warning(self,'Warning',f'Invalid item type passed to updateSelectedLanguage:{type(item)}')
        except Exception as e:
            print("Exception in update selected lang:",e)

    def onTextChanged(self):
        try:
            user_input_text = self.user_text.toPlainText()
            cursor = self.user_text.textCursor()
            self.cursor_position = cursor.position()  # Update cursor position

            # Get word at cursor position
            text_before_cursor = user_input_text[:self.cursor_position]
            last_word_start = text_before_cursor.rfind(' ') + 1
            last_word = text_before_cursor[last_word_start:]

        # Detect language of the text
       
            language = detect(user_input_text)
            self.input_lang_label.setText(f'Detected Language: {LANGUAGES[language]}')
        except:
            language = 'unknown'

        # Spell check last word if the detected language is English
        try:
            if language == 'en':
                if last_word and last_word.isalpha():  # Only check if the word is alphabetic
                    spell = SpellChecker()
                    misspelled = spell.unknown([last_word])

                    # Display suggestions if misspelled
                    if misspelled:
                        suggestions = spell.candidates(last_word)
                        self.suggestions_list.clear()
                        self.suggestions_list.addItems(suggestions)
                    else:
                        self.suggestions_list.clear()
            else:
                self.suggestions_list.clear()
        except Exception as e:
            print("Exception in onText Changed:",e)

    def onSuggestionClicked(self, item):
        try:
            suggestion = item.text()
            cursor = self.user_text.textCursor()
            cursor_position = cursor.position()

            # Get word at cursor position
            user_input_text = self.user_text.toPlainText()
            text_before_cursor = user_input_text[:cursor_position]
            last_word_start = text_before_cursor.rfind(' ') + 1
            last_word = text_before_cursor[last_word_start:]

            # Spell check last word
            spell = SpellChecker()
            misspelled = spell.unknown([last_word])

            # Replace misspelled word with suggestion
            if misspelled and last_word:
                corrected_text = user_input_text[:cursor_position - len(last_word)] + suggestion + user_input_text[cursor_position:]
                self.user_text.setText(corrected_text)
        except Exception as e:
            print("Exception in Suggestions:",e)


    def translateText(self):
        try:
            user_input_text = self.user_text.toPlainText()
            target_language = self.search_edit.text()

            # Check if the target language is valid
            if target_language not in LANGUAGES.values():
                # print("Invalid destination language:", target_language)
                QMessageBox().warning(self,'Warning',f'Invalid Language Detection {target_language}')
                return
            if not user_input_text:
                QMessageBox().warning(self,'Warning','First Input the text')
                return
            # Translate text
            translator = Translator()
            translated = translator.translate(user_input_text, dest=target_language)
            translated_text = translated.text

            self.output_text.setText(translated_text)
        except Exception as e:
            print('Exception in translate text:',e)

    def speakTranslatedText(self):
        try:
            translated_text = self.output_text.toPlainText()
            target_language = self.search_edit.text()
            target_language_code = self.getLanguageCode(target_language)

            if not translated_text:
                QMessageBox.warning(self, 'Warning', 'Please translate the text first.')
                return
            
            if target_language_code is None:
                QMessageBox.warning(self, 'Warning', 'Invalid target language.')
                return
            # Speak translated text
            audio_process = Process(target=play_translated_audio, args=(translated_text, target_language_code))
            audio_process.start()
        except Exception as e:
            print("Exception in speak text:",e)
        
    def getLanguageCode(self, language_name):
        try:
            for code, name in googletrans.LANGUAGES.items():
                if name.lower() == language_name.lower():
                    return code
            return None
        except Exception as e:
            print("Exception in get language:",e)


    '''
    -----------------------Voice to Text Transcribe Widget Functionalities---------------------------------------------
    '''
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.mp3 *.mp4 *.ogg)")
        if filename:
            self.audio_file=filename
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            self.audio_label.setText(os.path.basename(filename))  # Display the filename in the label
            self.play_btn.setEnabled(True)
            self.generate_text_btn.setEnabled(True)

    def transcribe_audio(self):
        if hasattr(self, 'audio_file'):
            # Convert MP3 to WAV
            wav_file = 'converted_audio.wav'
            audio = AudioSegment.from_mp3(self.audio_file)
            audio.export(wav_file, format="wav")

            # Disable main window interaction while progress dialog is open
            self.setEnabled(False)

            # Transcribe the WAV file
            with sr.AudioFile(wav_file) as source:
                audio_data = self.recognizer.record(source)
                try:
                    self.transcription = self.recognizer.recognize_google(audio_data)
                    self.text_edit.setText(self.transcription)
                    # progress_dialog.close()  # Close the progress dialog
                    QMessageBox().information(self, "Transcription Saved", "File Successfully Transcribed")
                except sr.UnknownValueError:
                    QMessageBox().information(self, "Could not understand the audio")
                except sr.RequestError as e:
                    QMessageBox().warning(self, "Error", f"Error: {e}")

            # Enable main window interaction after progress dialog is closed
            self.setEnabled(True)
            self.save_text_btn.setEnabled(True)
            # Remove the temporary WAV file
            os.remove(wav_file)
        else:
            QMessageBox().information(self, "No Audio file selected")


    def save_transcription(self):
        if not hasattr(self, 'transcription'):
            QMessageBox().warning(self,"No transcription to save")
            return
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Text files (*.txt)")
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setDefaultSuffix('txt')
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                with open(file_path, 'w') as f:
                    f.write(self.transcription)
                QMessageBox().information(self, "Transcription saved", f"Transcription saved to: {file_path}")

    def play_audio(self):
        if not self.audio_file:
            return
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.timer.stop()  # Stop the timer when playback is paused
            self.text_slider.setValue(0)  # Reset the slider position
            self.text_slider_label.setText('00:00')  # Reset the label time
            self.play_btn.setIcon(QIcon(r'resources\play.png'))
        else:
            self.media_player.play()
            self.timer.start() 
            self.play_btn.setIcon(QIcon(r'resources\pause.png'))


    def reset_file(self):
        reply=QMessageBox.question(self,"Warning","Do you want to reset the transcription and file",QMessageBox.Yes | QMessageBox.No)
        if reply==QMessageBox.Yes:
            self.audio_file = None
            self.audio_label.setText(".wav file")
            self.text_edit.setText("")
            self.play_btn.setIcon(QIcon(r'resources\play.png')) 
            self.media_player.pause()
            self.play_btn.setEnabled(False) 
            self.save_text_btn.setEnabled(False)
            self.generate_text_btn.setEnabled(False)

    def sliderMoved(self, position):
        # You can implement seeking functionality here
        self.media_player.setPosition(position * 1000)
    

    def updateTime(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            # Simulated music playback progress
            self.text_slider.setValue(self.text_slider.value() + 1)
            elapsed_seconds = self.text_slider.value()
            elapsed_minutes = elapsed_seconds // 60
            elapsed_seconds %= 60
            self.text_slider_label.setText('{:02d}:{:02d}'.format(elapsed_minutes, elapsed_seconds))
        else:
            # Reset slider and label when music playback reaches the end
            self.text_slider.setValue(0)
            self.text_slider_label.setText('00:00')
            self.play_btn.setIcon(QIcon(r'resources\play.png'))

    # def voice_setting(self):
    #     try:
    #         dialog = VoiceSettingsDialog(self.engine)
    #         dialog.generate_btn.setEnabled(False)
    #         dialog.exec_()
    #     except Exception as e:
    #         QMessageBox().warning(self,f"Warning{'You can not set at this point'}:{e}")

    def open_voice_settings_dialog(self, gender):
        dialog = VoiceSettingsDialog(self.engine)
        dialog.accepted.connect(lambda pitch, rate, volume: self.generate_voice(gender, pitch, rate, volume))  # Pass gender to the accepted signal
        self.voice_settings_dialog.finished.connect(self.voice_generated_msg)
        dialog.exec_()

    def voice_generated_msg(self):
        QMessageBox.information(self,'Voice Generated','Voice successfully generated')
    
    def update_voice_properties(self, pitch, volume, rate):
        # Update pyttsx3 engine properties based on the slider values
        self.engine.setProperty('pitch', pitch)
        self.engine.setProperty('volume', volume / 100)  # Convert volume to a float between 0 and 1
        self.engine.setProperty('rate', rate)

    '''
    ----------------------------Text to Voice Transcribe Widget Functionalities-------------------------------------------
    '''
    def generate_voice(self, gender, pitch, rate, volume):
        text = self.input_text.toPlainText()
        if text:
            if gender == 'male':
                voice_name = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0'
                output_filename = f'output_male_{datetime.now().strftime("%Y%m%d_%H%M%S")}.wav'
            elif gender == 'female':
                voice_name = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0'
                output_filename = f'output_female_{datetime.now().strftime("%Y%m%d_%H%M%S")}.wav'

            # Set voice property            
            self.engine.setProperty('voice', voice_name)
            self.engine.setProperty('pitch', pitch)
            self.engine.setProperty('volume', volume / 100)
            self.engine.setProperty('rate', rate)
            
            # Save to file in WAV format
            self.engine.save_to_file(text, output_filename)
            self.engine.runAndWait()

            # Convert WAV to MP3
            output_mp3_filename = output_filename.replace(".wav", ".mp3")
            audio = AudioSegment.from_wav(output_filename)
            audio.export(output_mp3_filename, format="mp3")

            # Move MP3 file to "Mp3 Voices" folder
            dest_folder = "Mp3 output"
            os.makedirs(dest_folder, exist_ok=True)
            shutil.move(output_mp3_filename, os.path.join(dest_folder, output_mp3_filename))

            # Remove the generated WAV file
            os.remove(output_filename)

            # Store the generated filename
            self.output_filename = os.path.join(dest_folder, output_mp3_filename)

    # def generate_male_voice(self):
    #     rate = self.engine.getProperty('rate')   # Get the current speaking rate
    #     self.engine.setProperty('rate', rate - 10)   # Decrease the rate by 50 (adjust as needed)
    #     self.generate_voice('male')
    #     QMessageBox.information(self, "Voice Generated", "David voice generated successfully.")
    

    # def generate_female_voice(self,pitch,rate,volume):
    #     rate = self.engine.getProperty('rate')   # Get the current speaking rate
    #     self.engine.setProperty('rate', rate - 30)   # Decrease the rate by 50 (adjust as needed)
    #     self.generate_voice('female')
    #     QMessageBox.information(self, "Voice Generated", "Zira voice generated successfully.")

    def play_ai_voice(self):
            pygame.mixer.init()
            if self.output_filename:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load(self.output_filename)
                    pygame.mixer.music.play()
                    self.timer.start()  # Start the timer
                    self.play_pause_btn.setIcon(QIcon(r'resources\pause.png'))
                else:
                    pygame.mixer.music.stop()
                    self.timer.stop()  # Stop the timer
                    self.timer_label.setText('00:00')
                    self.play_pause_btn.setIcon(QIcon(r'resources\play.png'))
    
    def updateVoiceTime(self):
        pygame.mixer.init()
        if pygame.mixer.music.get_busy():
            # Simulated voice playback progress
            self.voice_slider.setValue(self.voice_slider.value() + 1)
            elapsed_seconds = self.voice_slider.value()
            elapsed_minutes = elapsed_seconds // 60
            elapsed_seconds %= 60
            self.timer_label.setText('{:02d}:{:02d}'.format(elapsed_minutes, elapsed_seconds))
        else:
            # Reset slider and label when voice playback reaches the end
            self.voice_slider.setValue(0)
            self.timer_label.setText('00:00')
            self.play_pause_btn.setIcon(QIcon(r'resources\play.png'))

    
    def download_voice(self):
    # Prompt the user to choose the location to save the voice file
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Voice File", "", "Audio Files (*.mp3)")

        if fileName:
            try:
                # Read the contents of the generated voice file
                with open(self.output_filename, 'rb') as f:
                    voice_data = f.read()
                # Write the voice data to the selected file
                with open(fileName, 'wb') as f2:
                    f2.write(voice_data)
                QMessageBox.information(self, "Download Complete", "Voice file downloaded successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to download voice file: {str(e)}")


def play_translated_audio(text, target_language):
# Generate the translated audio file
    audio_filename = "translated_audio.mp3"
    translated_audio = gtts.gTTS(text, lang=target_language)
    translated_audio.save(audio_filename)

    # Initialize the audio mixer
    pygame.mixer.init()
    pygame.mixer.music.load(audio_filename)
    pygame.mixer.music.play()

    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

if __name__ == '__main__':
    check_ui_files()
    setup_database()
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_()) 