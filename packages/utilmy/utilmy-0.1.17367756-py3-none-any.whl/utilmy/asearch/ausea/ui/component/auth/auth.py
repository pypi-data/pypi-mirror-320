from authlib.integrations.flask_client import OAuth
from flask_cors import CORS

oauth = None


def setup_auth(app):
    global oauth
    oauth = OAuth(app)
    oauth.register(
        "auth0",
        client_id=app.server.config['AUTH0_CLIENT_ID'],
        client_secret=app.server.config['AUTH0_CLIENT_SECRET'],
        client_kwargs={"scope": "openid profile email"},
        server_metadata_url=f'https://{app.server.config["AUTH0_DOMAIN"]}/.well-known/openid-configuration',
    )
    return oauth

def setup_CORS(app):
    server = app.server
    CORS(server, resources={r"/*": {"origins": "*"}})
