from .base import Base


class Auth(Base):
    #
    # Authentication
    #

    def sign_in(self, email, password):
        return self._client.request(
            "post",
            "/auth/sign_in",
            json={"email": email, "password": password},
        )

    def sign_up(
        self,
        email,
        first_name,
        last_name,
        phone_country_code,
        phone_number,
        password=None,
    ):
        return self._client.request(
            "post",
            "/auth/sign_up",
            json={
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
                "phone_country_code": phone_country_code,
                "phone_number": phone_number,
            },
        )

    def refresh_token(self):
        return self._client.request("post", "/auth/token/refresh")

    def revoke_token(self):
        return self._client.request("delete", "/auth/revoke")

    def revoke_all_tokens(self):
        return self._client.request("delete", "/auth/revoke_all")

    #
    # Users
    #

    def validate_user(self, token):
        return self._client.request(
            "get",
            "/users/activate",
            params={"token": token},
        )

    def deactivate_user(self, user_id):
        return self._client.request("post", f"/users/deactivate?id={user_id}")

    def user_by_id(self, user_id):
        return self._client.request("get", f"/users/id/{user_id}")

    def user_by_email(self, email):
        return self._client.request("get", f"/users/email/{email}")

    def me(self, **kwargs):
        return self._client.request("get", "/users/me", params=kwargs)

    def users_by_tenant(self, **kwargs):
        return self._client.request("get", "/users/tenant", params=kwargs)

    def update_user(self, user_id, **kwargs):
        return self._client.request("patch", f"/users/{user_id}", json=kwargs)

    def delete_user_by_id(self, user_id):
        return self._client.request("delete", f"/users/{user_id}")

    def reset_user_password(self, email):
        return self._client.request(
            "post", "/auth/password/reset", json={"email": email}
        )

    def update_user_password(self, token, password):
        return self._client.request(
            "patch",
            "/auth/password/update",
            json={"token": token, "password": password},
        )

    #
    # Tenants
    #

    def create_tenant(
        self,
        tenant_type,
        email,
        master_contract,
        volume_pricing,
        sales_contact,
        contact_country_code,
        siret,
        iban,
    ):
        return self._client.request(
            "post",
            "/tenants",
            json={
                "type": tenant_type,
                "email": email,
                "master_contract": master_contract,
                "volume_pricing": volume_pricing,
                "sales_contact": sales_contact,
                "contact_country_code": contact_country_code,
                "siret": siret,
                "iban": iban,
            },
        )

    def iban_validation(self, iban):
        return self._client.request(
            "get", f"/tenants/iban_validation?iban={iban}"
        )

    def tenant_by_id(self, tenant_id):
        return self._client.request("get", f"/tenants/{tenant_id}")

    def select_tenant(self, uuid):
        return self._client.request("post", f"/tenants/{uuid}/select")

    def current_tenant(self):
        return self._client.request("get", "/tenants/current")

    def tenant_by_user_token(self, **kwargs):
        return self._client.request("get", "/tenants", params=kwargs)

    def update_tenant(self, tenant_id, **kwargs):
        return self._client.request(
            "patch",
            f"/tenants/{tenant_id}",
            json=kwargs,
        )

    def delete_tenant_by_id(self, tenant_id):
        return self._client.request("delete", f"/tenants/{tenant_id}")

    def add_tenant_user(
        self,
        tenant_id,
        email,
        password,
        first_name,
        last_name,
        phone_country_code,
        phone_number,
    ):
        return self._client.request(
            "post",
            f"/tenants/{tenant_id}/users",
            json={
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
                "phone_country_code": phone_country_code,
                "phone_number": phone_number,
            },
        )
