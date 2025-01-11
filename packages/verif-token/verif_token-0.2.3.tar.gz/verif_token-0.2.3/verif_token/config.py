import os

KEYCLOAK_URL = os.environ['KEYCLOAK_URL']
API_NAME = os.environ['API_NAME']

if not KEYCLOAK_URL:
    raise RuntimeError("KEYCLOAK_URL environment variables are required.")
if not API_NAME:
    raise RuntimeError("API_NAME environment variable is required.")
