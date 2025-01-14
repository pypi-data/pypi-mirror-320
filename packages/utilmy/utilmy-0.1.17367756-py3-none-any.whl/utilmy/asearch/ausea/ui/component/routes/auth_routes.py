from urllib.parse import quote_plus, urlencode
from flask import redirect, url_for, session

from utilmy import log
import os


def setup_auth_routes(app, oauth):
    @app.server.route("/callback", methods=["GET", "POST"])
    def callback():
        try:
            token = oauth.auth0.authorize_access_token()
            log("token", token)
            session["user"] = token
        except Exception as e:
            log("Token exchange failed", e)
            return redirect("/login")
        return redirect("/")

    @app.server.route("/logout")
    def logout():
        session.clear()
        return redirect(
            "https://" + app.server.config["AUTH0_DOMAIN"]
            + "/v2/logout?"
            + urlencode(
                {
                    "returnTo": url_for("/", _external=True),
                    "client_id": app.server.config["AUTH0_CLIENT_ID"],
                },
                quote_via=quote_plus,
            )
        )

    @app.server.route("/silent-auth")
    def silent_auth():
        base_url = os.getenv("BASE_URL")
        return oauth.auth0.authorize_redirect(
            redirect_uri=f"{base_url}/silent-callback",
            prompt='none'
        )

    @app.server.route("/silent-callback", methods=["GET", "POST"])
    def silent_callback():
        token = oauth.auth0.authorize_access_token()
        session["user"] = token
        return redirect("/")

    @app.server.route("/login")
    def login():
        base_url = os.getenv("BASE_URL")
        authentication = oauth.auth0.authorize_redirect(
            f"{base_url}/callback")
        log("test auth", authentication)
        return authentication
