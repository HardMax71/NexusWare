from desktop_app.src.api import UsersAPI


class AuthenticationService:
    def __init__(self, users_api: UsersAPI):
        self.users_api = users_api

    def login(self, email, password):
        return self.users_api.login(email, password)

    def register(self, user_data):
        return self.users_api.register(user_data)

    def reset_password(self, email):
        return self.users_api.reset_password(email)

    def get_current_user(self):
        return self.users_api.get_current_user()

    def update_current_user(self, user_data):
        return self.users_api.update_current_user(user_data)