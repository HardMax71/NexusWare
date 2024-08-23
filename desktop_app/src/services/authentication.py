from public_api.api import UsersAPI
from public_api.shared_schemas import (
    UserCreate, UserUpdate, UserSanitized, Token, Message
)


class AuthenticationService:
    def __init__(self, users_api: UsersAPI):
        self.users_api = users_api

    def login(self, username: str, password: str) -> Token:
        return self.users_api.login(username, password)

    def login_2fa(self, username: str, password: str, two_factor_code: str) -> Token:
        return self.users_api.login_2fa(username, password, two_factor_code)

    def register(self, user_data: UserCreate) -> UserSanitized:
        return self.users_api.register(user_data)

    def reset_password(self, email: str) -> Message:
        return self.users_api.reset_password(email)

    def refresh_token(self) -> Token:
        return self.users_api.refresh_token()

    def get_current_user(self) -> UserSanitized:
        return self.users_api.get_current_user()

    def update_current_user(self, user_data: UserUpdate) -> UserSanitized:
        return self.users_api.update_current_user(user_data)

    def change_password(self, current_password: str, new_password: str) -> Message:
        return self.users_api.change_password(current_password, new_password)
