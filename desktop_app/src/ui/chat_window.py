import traceback

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                               QLineEdit, QPushButton, QTextEdit, QMessageBox,
                               QSplitter, QWidget, QComboBox)

from public_api.api import APIClient


class ChatDialog(QDialog):
    def __init__(self, api_client: APIClient, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.current_chat_id = None
        self.all_users = []
        self.current_user = self.get_current_user()
        if self.current_user:
            self.init_ui()
            self.load_users()
            self.load_chats()
        else:
            QMessageBox.critical(self, "Error", "Should be authenticated!")
            self.close()

    def init_ui(self):
        self.setWindowTitle("Chat")
        self.setMinimumSize(600, 400)

        layout = QHBoxLayout(self)

        # Left side
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.chat_list = QListWidget()
        self.chat_list.itemClicked.connect(self.load_chat)
        left_layout.addWidget(self.chat_list)

        self.user_combo = QComboBox()
        self.user_combo.setEditable(True)
        self.user_combo.setInsertPolicy(QComboBox.NoInsert)
        left_layout.addWidget(self.user_combo)

        new_chat_button = QPushButton("New Chat")
        new_chat_button.clicked.connect(self.start_new_chat)
        left_layout.addWidget(new_chat_button)

        delete_chat_button = QPushButton("Delete Chat")
        delete_chat_button.clicked.connect(self.delete_chat)
        left_layout.addWidget(delete_chat_button)

        # Right side
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        right_layout.addWidget(self.chat_area)

        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        right_layout.addLayout(input_layout)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        layout.addWidget(splitter)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_current_chat)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds

    def get_current_user(self):
        try:
            return self.api_client.get("/users/me")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get current user data: {str(e)}")
            return None

    def load_users(self):
        try:
            response = self.api_client.get("/users")
            self.all_users = [user for user in response if user['id'] != self.current_user['id']]
            self.update_user_combo()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")

    def update_user_combo(self):
        self.user_combo.clear()
        for user in self.all_users:
            self.user_combo.addItem(f"{user['username']} ({user['email']})", userData=user['id'])

    def load_chats(self):
        try:
            response = self.api_client.get("/chat")
            chats = response.get("chats", [])
            self.chat_list.clear()
            for chat in chats:
                other_user = chat["user1"] if chat["user2"]["id"] == self.current_user['id'] else chat["user2"]
                self.chat_list.addItem(f"{other_user['username']} (ID: {chat['id']})")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load chats: {str(e)}")

    def load_chat(self, item):
        chat_id = int(item.text().split("ID: ")[-1].strip(")"))
        self.current_chat_id = chat_id
        self.refresh_current_chat()

    def refresh_current_chat(self):
        if self.current_chat_id:
            try:
                response = self.api_client.get(f"/chat/{self.current_chat_id}/messages")
                messages = response.get("messages", [])
                self.chat_area.clear()
                for message in messages:
                    sender = "You" if message["sender_id"] == self.current_user['id'] else "Other"
                    self.chat_area.append(f"{sender}: {message['content']}")
            except Exception as e:
                error_msg = f"Failed to load messages: {str(e)}\n\n{traceback.format_exc()}"
                print(error_msg)  # Log the error
                QMessageBox.critical(self, "Error", error_msg)

    def send_message(self):
        if not self.current_chat_id:
            QMessageBox.warning(self, "Warning", "Please select a chat first.")
            return
        message = self.message_input.text()
        if message:
            try:
                self.api_client.post(f"/chat/{self.current_chat_id}/messages", json={"content": message})
                self.message_input.clear()
                self.refresh_current_chat()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to send message: {str(e)}")

    def start_new_chat(self):
        selected_user_id = self.user_combo.currentData()
        if not selected_user_id:
            QMessageBox.warning(self, "Warning", "Please select a valid user.")
            return

        existing_chat = self.find_existing_chat(selected_user_id)
        if existing_chat:
            QMessageBox.warning(self, "Warning", f"A chat with {existing_chat} already exists.")
            return

        try:
            response = self.api_client.post("/chat", json={"user2_id": selected_user_id})
            self.load_chats()
            QMessageBox.information(self, "Success", "New chat started successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start new chat: {str(e)}")

    def find_existing_chat(self, user_id):
        try:
            response = self.api_client.get("/chat")
            chats = response.get("chats", [])
            for chat in chats:
                if chat["user1"]["id"] == user_id or chat["user2"]["id"] == user_id:
                    other_user = chat["user1"] if chat["user2"]["id"] == self.current_user['id'] else chat["user2"]
                    return other_user["username"]
        except Exception as e:
            print(f"Error checking chats: {str(e)}")
        return None

    def delete_chat(self):
        if not self.current_chat_id:
            QMessageBox.warning(self, "Warning", "Please select a chat first.")
            return
        reply = QMessageBox.question(self, "Delete Chat", "Are you sure you want to delete this chat?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.api_client.delete(f"/chat/{self.current_chat_id}")
                self.load_chats()
                self.chat_area.clear()
                self.current_chat_id = None
                QMessageBox.information(self, "Success", "Chat deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete chat: {str(e)}")
