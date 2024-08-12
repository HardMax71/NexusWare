from .client import APIClient


class UsersAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def login(self, email, password):
        data = {
            "grant_type": "password",  # This is required and should be "password"
            "username": email,
            "password": password,
        }
        headers = {"content-type": "application/x-www-form-urlencoded"}

        response = self.client.post("/users/login", data=data, headers=headers)
        access_token = response.get("access_token")

        if access_token:
            self.client.set_token(access_token)

        return response

    def register(self, user_data):
        return self.client.post("/users/register", json=user_data)

    def reset_password(self, email):
        return self.client.post("/users/reset_password", json={"email": email})

    def get_current_user(self):
        return self.client.get("/users/me")

    def update_current_user(self, user_data):
        return self.client.put("/users/me", json=user_data)

    def get_users(self, skip=0, limit=100):
        return self.client.get("/users/", params={"skip": skip, "limit": limit})

    def create_user(self, user_data):
        return self.client.post("/users/", json=user_data)

    def get_user(self, user_id):
        return self.client.get(f"/users/{user_id}")

    def update_user(self, user_id, user_data):
        return self.client.put(f"/users/{user_id}", json=user_data)

    def delete_user(self, user_id):
        return self.client.delete(f"/users/{user_id}")

    def get_roles(self, skip=0, limit=100):
        return self.client.get("/users/roles", params={"skip": skip, "limit": limit})

    def get_role(self, role_id):
        return self.client.get(f"/users/roles/{role_id}")

    def update_role(self, role_id, role_data):
        return self.client.put(f"/users/roles/{role_id}", json=role_data)

    def delete_role(self, role_id):
        return self.client.delete(f"/users/roles/{role_id}")

    def create_permission(self, permission_data):
        return self.client.post("/users/permissions", json=permission_data)

    def get_permissions(self, skip=0, limit=100):
        return self.client.get("/users/permissions", params={"skip": skip, "limit": limit})
