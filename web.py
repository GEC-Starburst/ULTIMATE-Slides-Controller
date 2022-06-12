from functools import wraps
from secrets import token_urlsafe
import sys

from pyngrok import conf, ngrok

import keyboard
from flask import Flask, g, flash, jsonify, request, url_for, redirect, render_template

app = Flask(__name__)
app.secret_key = token_urlsafe(64)

# global session token
session_token = None

# Ngrok public url
public_url = None

def localhost_only(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.remote_addr != "127.0.0.1" or "ngrok" in request.headers["Host"]:
            return redirect(url_for("session"), 301)
        return f(*args, **kwargs)
    return decorated

def required_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.auth_type == "bearer":
            return render_template("error.html", page="Error", error="Unknown token format!"), 406

        if not g.token_verified:
            return render_template("error.html", page="Error", error="Invalid session token!"), 403

        return f(*args, **kwargs)
    return decorated

@app.before_request
def parse_token():
    auth_type, *payload = request.headers.get("Authorization", "").split(" ")

    g.auth_type = auth_type.lower()
    g.token_verified = "".join(payload) == session_token

@app.route("/")
@localhost_only
def index():
    if session_token:
        share_url = f"{public_url}{url_for('session', token=session_token)}"
        return render_template("index.html", page="Host", token=session_token, share_url=share_url)
    else:
        return render_template("index.html", page="Host", token=None, share_url=None)

@app.route("/session/create")
@localhost_only
def create_session():
    global session_token

    session_token = token_urlsafe(16)
    flash("Session created successfully!")
    return redirect(url_for("index"))

@app.route("/session/end")
@localhost_only
def end_session():
    global session_token

    session_token = None
    flash("Session has ended!")
    return redirect(url_for("index"))

@app.route("/status")
def status():
    return jsonify(session_token is not None and g.token_verified)

@app.route("/s/<token>")
@app.route("/s", defaults={"token": None}, methods=["GET", "POST"])
def session(token):
    if not token:
        if request.method == "GET":
            return render_template("control.html", page="Control", token=None)
        else:
            if request.form.get("token"):
                return redirect(url_for("session", token=request.form.get("token")))
            else:
                return  render_template("error.html", page="Error", error="No token!"), 400
    elif token != session_token:
        return render_template("error.html", page="Error", error="Invalid session token!"), 403

    return render_template("control.html", page="Control", token=token)

@app.route("/action")
@required_token
def slides_control():
    action = request.args.get("action")

    if action == "left":
        keyboard.send("left")
    elif action == "right":
        keyboard.send("right")
    else:
        return "Invalid action", 400

    return "", 204


if __name__ == "__main__":
    if len(sys.argv) == 2:
        conf.get_default().auth_token = sys.argv[1]

    http_tunnel = ngrok.connect(5000)
    public_url = http_tunnel.public_url

    print("*"*30)
    print("[Web Slides Control] Welcome to Web Slide Control!")
    print("[Web Slides Control] To setup a session, go to http://localhost:5000/")
    print(f"[Web Slides Control] To let others control your slides, share the link: {public_url}")
    print("*"*30)

    app.run("127.0.0.1", port=5000, debug=False)
    
    

