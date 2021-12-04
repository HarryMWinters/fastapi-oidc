# Example with keycloak

## Setup your realm

1. Start up keycloak with `docker-compose up` (the fastapi app will crash since
   we do not have a realm yet).
2. Log into keycloak at http://localhost:8080 with username/password `admin/admin`.
3. Create a realm `my-realm`. This will set your `openid_connect_url` to `http://localhost:8080/auth/realms/my-realm/.well-known/openid-configuration`
   and your issuer to `http://localhost:8080/auth/realms/my-realm`.
4. Allow implicit flow (in order for login in interactive docs to work).
5. Create a user and add credentials (password).

## Login into docs with your credentials

1. Kill app and then restart with `docker-compose up`.
2. Go to `http://localhost:8000/docs` and login with your credentials by
   clicking `authorize` in the top right corner.
