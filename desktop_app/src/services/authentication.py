from public_api.api import UsersAPI
from public_api.shared_schemas import (
    UserCreate, UserUpdate, UserSanitizedWithRole, Token, Message, User
)

class AuthenticationService:
    def __init__(self, users_api: UsersAPI):
        self.users_api = users_api

    def login(self, email: str, password: str) -> Token:
        return self.users_api.login(email, password)

    def login_2fa(self, email: str, password: str, two_factor_code: str) -> Token:
        return self.users_api.login_2fa(email, password, two_factor_code)

    def register(self, user_data: UserCreate) -> User:
        return self.users_api.register(user_data)

    def reset_password(self, email: str) -> Message:
        return self.users_api.reset_password(email)

    def get_current_user(self) -> UserSanitizedWithRole:
        return self.users_api.get_current_user()

    def update_current_user(self, user_data: UserUpdate) -> User:
        return self.users_api.update_current_user(user_data)