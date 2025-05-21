import os
import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QMessageBox, QListWidget,
    QDialog, QDialogButtonBox, QFormLayout, QTabWidget, QSplitter
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QSize
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette
from app.encryption import EncryptionHandler
from app.resources import get_app_icon


class AddPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Password Entry")
        self.resize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                border-radius: 10px;
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("e.g. Gmail, Facebook, etc.")
        form_layout.addRow("Title:", self.title_edit)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Your username or email")
        form_layout.addRow("Username:", self.username_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Your password")
        form_layout.addRow("Password:", self.password_edit)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Additional notes (optional)")
        form_layout.addRow("Notes:", self.notes_edit)
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_entry_data(self):
        return {
            "title": self.title_edit.text(),
            "username": self.username_edit.text(),
            "password": self.password_edit.text(),
            "notes": self.notes_edit.toPlainText()
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.encryption_handler = EncryptionHandler()
        self.master_password = None
        self.data_file = "encrypted_passwords.dat"
        self.password_entries = []
        self.current_entry_index = -1
        
        self.setWindowTitle("Secure Password Manager")
        self.resize(900, 600)
        self.setWindowIcon(get_app_icon())
        
        # Set modern style
        self.setup_style()
        
        # Initialize UI
        self.init_ui()
    
    def setup_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                padding: 4px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #e6f0ff;
                color: #2a66c8;
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QLabel {
                font-size: 14px;
            }
        """)
        
        # Set custom font
        font = self.font()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.setFont(font)
    
    def init_ui(self):
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Password login section (initially visible)
        self.login_widget = QWidget()
        login_layout = QVBoxLayout(self.login_widget)
        login_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel("Secure Password Manager")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPointSize(24)
        font.setBold(True)
        title_label.setFont(font)
        login_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Enter your master password to unlock your passwords")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.addWidget(subtitle_label)
        
        login_layout.addSpacing(30)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter master password")
        self.password_input.setMinimumWidth(300)
        self.password_input.setMaximumWidth(400)
        login_layout.addWidget(self.password_input, 0, Qt.AlignmentFlag.AlignCenter)
        
        login_button = QPushButton("Unlock")
        login_button.setMinimumWidth(200)
        login_button.setMaximumWidth(200)
        login_button.clicked.connect(self.authenticate)
        login_layout.addWidget(login_button, 0, Qt.AlignmentFlag.AlignCenter)
        
        login_layout.addSpacing(20)
        
        create_new_button = QPushButton("Create New Password File")
        create_new_button.setMinimumWidth(200)
        create_new_button.setMaximumWidth(200)
        create_new_button.clicked.connect(self.create_new_password_file)
        login_layout.addWidget(create_new_button, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Main app interface (initially hidden)
        self.app_widget = QWidget()
        self.app_widget.setVisible(False)
        app_layout = QVBoxLayout(self.app_widget)
        
        # Create splitter for list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel with list of password entries
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        list_label = QLabel("Saved Passwords")
        font = list_label.font()
        font.setBold(True)
        list_label.setFont(font)
        left_layout.addWidget(list_label)
        
        self.entry_list = QListWidget()
        self.entry_list.currentRowChanged.connect(self.on_entry_selected)
        left_layout.addWidget(self.entry_list)
        
        # Buttons for managing entries
        buttons_layout = QHBoxLayout()
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_password_entry)
        buttons_layout.addWidget(add_button)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_password_entry)
        self.edit_button.setEnabled(False)
        buttons_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_password_entry)
        self.delete_button.setEnabled(False)
        buttons_layout.addWidget(self.delete_button)
        
        left_layout.addLayout(buttons_layout)
        
        # Right panel with password details
        right_panel = QWidget()
        self.right_layout = QVBoxLayout(right_panel)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        
        details_label = QLabel("Password Details")
        font = details_label.font()
        font.setBold(True)
        details_label.setFont(font)
        self.right_layout.addWidget(details_label)
        
        # Form for viewing password details
        form_layout = QFormLayout()
        
        self.title_label = QLabel("")
        form_layout.addRow("Title:", self.title_label)
        
        self.username_label = QLabel("")
        form_layout.addRow("Username:", self.username_label)
        
        self.password_container = QWidget()
        password_layout = QHBoxLayout(self.password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        self.password_label = QLineEdit("")
        self.password_label.setReadOnly(True)
        self.password_label.setEchoMode(QLineEdit.EchoMode.Password)
        self.toggle_password_btn = QPushButton("Show")
        self.toggle_password_btn.setFixedWidth(80)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.password_label)
        password_layout.addWidget(self.toggle_password_btn)
        form_layout.addRow("Password:", self.password_container)
        
        self.notes_label = QTextEdit("")
        self.notes_label.setReadOnly(True)
        form_layout.addRow("Notes:", self.notes_label)
        
        self.right_layout.addLayout(form_layout)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 600])  # Initial sizes
        
        app_layout.addWidget(splitter)
        
        # Logout button
        logout_button = QPushButton("Lock")
        logout_button.clicked.connect(self.lock_application)
        app_layout.addWidget(logout_button, 0, Qt.AlignmentFlag.AlignRight)
        
        # Add widgets to main layout
        main_layout.addWidget(self.login_widget)
        main_layout.addWidget(self.app_widget)
    
    def authenticate(self):
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, "Error", "Please enter a password")
            return
        
        # Check if the data file exists
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    encrypted_data = f.read()
                
                # Try to decrypt the data
                decrypted_data = self.encryption_handler.decrypt_data(encrypted_data, password)
                if decrypted_data:
                    self.master_password = password
                    self.password_entries = json.loads(decrypted_data)
                    self.update_entry_list()
                    self.show_app_interface()
                else:
                    QMessageBox.warning(self, "Error", "Incorrect password or corrupted data file")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open password file: {str(e)}")
        else:
            # For new files, we require password confirmation
            reply = QMessageBox.question(
                self,
                "Confirm Password",
                "No existing password file found. Would you like to create a new one with the entered password?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.master_password = password
                self.password_entries = []
                self.save_data()
                self.show_app_interface()
            else:
                self.password_input.clear()
                self.password_input.setFocus()
    
    def create_new_password_file(self):
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, "Error", "Please enter a master password")
            return
        
        # Ask for password confirmation
        confirm_dialog = QDialog(self)
        confirm_dialog.setWindowTitle("Confirm Master Password")
        confirm_dialog.setMinimumWidth(300)
        layout = QVBoxLayout(confirm_dialog)
        
        layout.addWidget(QLabel("Please confirm your master password:"))
        confirm_input = QLineEdit()
        confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(confirm_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(confirm_dialog.accept)
        buttons.rejected.connect(confirm_dialog.reject)
        layout.addWidget(buttons)
        
        if confirm_dialog.exec() == QDialog.DialogCode.Accepted:
            if confirm_input.text() != password:
                QMessageBox.warning(self, "Error", "Passwords do not match!")
                return
            
            if os.path.exists(self.data_file):
                # Ask for confirmation before overwriting
                reply = QMessageBox.question(
                    self,
                    "Overwrite Existing File",
                    "This will overwrite your existing password file. Are you sure?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.No:
                    return
            
            self.master_password = password
            self.password_entries = []
            self.save_data()
            self.show_app_interface()
    
    def show_app_interface(self):
        # Animate transition
        self.login_widget.setVisible(False)
        self.app_widget.setVisible(True)
        
        # Clear password field
        self.password_input.clear()
        
        # Animation for the app interface
        self.app_widget_animation = QPropertyAnimation(self.app_widget, b"geometry")
        self.app_widget_animation.setDuration(500)
        self.app_widget_animation.setStartValue(QRect(0, self.height(), self.width(), self.height()))
        self.app_widget_animation.setEndValue(QRect(0, 0, self.width(), self.height()))
        self.app_widget_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.app_widget_animation.start()
    
    def update_entry_list(self):
        self.entry_list.clear()
        for entry in self.password_entries:
            self.entry_list.addItem(entry["title"])
    
    def on_entry_selected(self, index):
        self.current_entry_index = index
        
        if index >= 0 and index < len(self.password_entries):
            entry = self.password_entries[index]
            self.title_label.setText(entry["title"])
            self.username_label.setText(entry["username"])
            self.password_label.setText(entry["password"])
            self.notes_label.setText(entry["notes"])
            
            # Enable edit and delete buttons
            self.edit_button.setEnabled(True)
            self.delete_button.setEnabled(True)
        else:
            self.clear_details()
    
    def clear_details(self):
        self.title_label.setText("")
        self.username_label.setText("")
        self.password_label.setText("")
        self.notes_label.setText("")
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
    
    def add_password_entry(self):
        dialog = AddPasswordDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            entry_data = dialog.get_entry_data()
            self.password_entries.append(entry_data)
            self.update_entry_list()
            self.save_data()
    
    def edit_password_entry(self):
        if self.current_entry_index < 0:
            return
        
        current_entry = self.password_entries[self.current_entry_index]
        dialog = AddPasswordDialog(self)
        dialog.title_edit.setText(current_entry["title"])
        dialog.username_edit.setText(current_entry["username"])
        dialog.password_edit.setText(current_entry["password"])
        dialog.notes_edit.setText(current_entry["notes"])
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            entry_data = dialog.get_entry_data()
            self.password_entries[self.current_entry_index] = entry_data
            self.update_entry_list()
            self.entry_list.setCurrentRow(self.current_entry_index)
            self.save_data()
    
    def delete_password_entry(self):
        if self.current_entry_index < 0:
            return
        
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete '{self.password_entries[self.current_entry_index]['title']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.password_entries[self.current_entry_index]
            self.update_entry_list()
            self.current_entry_index = -1
            self.clear_details()
            self.save_data()
    
    def toggle_password_visibility(self):
        if self.password_label.echoMode() == QLineEdit.EchoMode.Password:
            self.password_label.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_btn.setText("Hide")
        else:
            self.password_label.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_btn.setText("Show")
    
    def save_data(self):
        if not self.master_password:
            return
        
        try:
            json_data = json.dumps(self.password_entries)
            encrypted_data = self.encryption_handler.encrypt_data(json_data, self.master_password)
            
            with open(self.data_file, "w") as f:
                f.write(encrypted_data)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not save data: {str(e)}")
    
    def lock_application(self):
        # Animation for hiding app interface
        self.app_widget_animation = QPropertyAnimation(self.app_widget, b"geometry")
        self.app_widget_animation.setDuration(500)
        self.app_widget_animation.setStartValue(QRect(0, 0, self.width(), self.height()))
        self.app_widget_animation.setEndValue(QRect(0, self.height(), self.width(), self.height()))
        self.app_widget_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.app_widget_animation.finished.connect(self.show_login_interface)
        self.app_widget_animation.start()
        
        # Clear sensitive data
        self.master_password = None
        self.password_entries = []
        self.current_entry_index = -1
        self.clear_details()
    
    def show_login_interface(self):
        self.app_widget.setVisible(False)
        self.login_widget.setVisible(True)
        
        # Animation for showing login interface
        self.login_widget_animation = QPropertyAnimation(self.login_widget, b"geometry")
        self.login_widget_animation.setDuration(500)
        self.login_widget_animation.setStartValue(QRect(0, -self.height(), self.width(), self.height()))
        self.login_widget_animation.setEndValue(QRect(0, 0, self.width(), self.height()))
        self.login_widget_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.login_widget_animation.start() 