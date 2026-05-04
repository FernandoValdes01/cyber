import base64
import hashlib
import hmac
import json
import os
import smtplib
import ssl
import time
from email.message import EmailMessage

from flask import Flask, jsonify, request
from ldap3 import ALL, BASE, MODIFY_REPLACE, Connection, Server, Tls


app = Flask(__name__)


LDAP_URL = os.getenv("LDAP_URL", "ldaps://ldap.cyber.lab:636")
LDAP_BASE_DN = os.getenv("LDAP_BASE_DN", "dc=cyber,dc=lab")
LDAP_ADMIN_DN = os.getenv("LDAP_ADMIN_DN", f"cn=admin,{LDAP_BASE_DN}")
LDAP_ADMIN_PASSWORD = os.getenv("LDAP_ADMIN_PASSWORD", "")
LDAP_CA_CERT_PATH = os.getenv("LDAP_CA_CERT_PATH", "/run/secrets/ca.crt")

TOKEN_SECRET_KEY = os.getenv("TOKEN_SECRET_KEY", "")
TOKEN_EXPIRATION_MINUTES = int(os.getenv("TOKEN_EXPIRATION_MINUTES", "15"))

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "")
SMTP_USE_STARTTLS = os.getenv("SMTP_USE_STARTTLS", "true").lower() == "true"
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "false").lower() == "true"

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8080"))


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def make_reset_token(uid: str) -> str:
    payload = {
        "uid": uid,
        "exp": int(time.time()) + TOKEN_EXPIRATION_MINUTES * 60,
    }
    payload_raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = _b64url(payload_raw)
    signature = hmac.new(TOKEN_SECRET_KEY.encode("utf-8"), payload_b64.encode("ascii"), hashlib.sha256).digest()
    return f"{payload_b64}.{_b64url(signature)}"


def verify_reset_token(token: str):
    try:
        payload_b64, sig_b64 = token.split(".", 1)
        expected_sig = hmac.new(TOKEN_SECRET_KEY.encode("utf-8"), payload_b64.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(expected_sig, _b64url_decode(sig_b64)):
            return None, "invalid_signature"
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None, "expired"
        uid = payload.get("uid")
        if not uid:
            return None, "invalid_payload"
        return uid, None
    except Exception:
        return None, "invalid_token"


def generate_ssha(password: str) -> str:
    salt = os.urandom(8)
    digest = hashlib.sha1(password.encode("utf-8") + salt).digest()
    return "{SSHA}" + base64.b64encode(digest + salt).decode("ascii")


def ldap_connection() -> Connection:
    tls = Tls(validate=ssl.CERT_REQUIRED, ca_certs_file=LDAP_CA_CERT_PATH)
    server = Server(LDAP_URL, use_ssl=True, tls=tls, get_info=ALL)
    conn = Connection(server, user=LDAP_ADMIN_DN, password=LDAP_ADMIN_PASSWORD, auto_bind=True)
    ensure_directory_structure(conn)
    return conn


def user_dn(uid: str) -> str:
    return f"uid={uid},ou=people,{LDAP_BASE_DN}"


def ensure_directory_structure(conn: Connection):
    if not conn.search(LDAP_BASE_DN, "(objectClass=*)", search_scope=BASE, attributes=["objectClass"]):
        conn.add(
            LDAP_BASE_DN,
            ["top", "dcObject", "organization"],
            {
                "dc": LDAP_BASE_DN.split(",", 1)[0].split("=", 1)[1],
                "o": os.getenv("LDAP_ORGANISATION", "Aseguridad Lab"),
            },
        )

    people_dn = f"ou=people,{LDAP_BASE_DN}"
    if not conn.search(people_dn, "(objectClass=*)", search_scope=BASE, attributes=["objectClass"]):
        conn.add(people_dn, ["organizationalUnit"], {"ou": "people"})


def send_reset_email(to_email: str, reset_link: str):
    if not SMTP_HOST or not SMTP_FROM:
        return False

    msg = EmailMessage()
    msg["Subject"] = "Recuperacion de cuenta"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg.set_content(f"Usa este enlace para recuperar tu cuenta (expira en {TOKEN_EXPIRATION_MINUTES} min):\n{reset_link}")

    if SMTP_USE_SSL:
        try:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
                if SMTP_USERNAME and SMTP_PASSWORD:
                    smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
                smtp.send_message(msg)
            return True
        except Exception:
            return False

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            if SMTP_USE_STARTTLS:
                smtp.starttls()
            if SMTP_USERNAME and SMTP_PASSWORD:
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception:
        return False


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/users")
def create_user():
    data = request.get_json(force=True)
    uid = data.get("uid")
    cn = data.get("cn")
    sn = data.get("sn")
    mail = data.get("mail")
    password = data.get("password")

    if not all([uid, cn, sn, mail, password]):
        return jsonify({"error": "uid, cn, sn, mail y password son obligatorios"}), 400

    dn = user_dn(uid)
    attrs = {
        "objectClass": ["inetOrgPerson", "organizationalPerson", "person", "top"],
        "uid": uid,
        "cn": cn,
        "sn": sn,
        "mail": mail,
        "userPassword": generate_ssha(password),
    }

    conn = ldap_connection()
    ok = conn.add(dn, attributes=attrs)
    if not ok:
        if conn.result.get("result") == 68:
            return jsonify({"error": "usuario ya existe"}), 409
        return jsonify({"error": conn.result}), 400
    return jsonify({"message": "usuario creado", "dn": dn}), 201


@app.get("/users/<uid>")
def get_user(uid):
    conn = ldap_connection()
    conn.search(user_dn(uid), "(objectClass=inetOrgPerson)", attributes=["uid", "cn", "sn", "mail"])
    if not conn.entries:
        return jsonify({"error": "usuario no encontrado"}), 404
    e = conn.entries[0]
    return jsonify({
        "uid": str(e.uid),
        "cn": str(e.cn),
        "sn": str(e.sn),
        "mail": str(e.mail),
    })


@app.put("/users/<uid>")
def update_user(uid):
    data = request.get_json(force=True)
    changes = {}
    for attr in ["cn", "sn", "mail"]:
        if attr in data:
            changes[attr] = [(MODIFY_REPLACE, [data[attr]])]
    if "password" in data:
        changes["userPassword"] = [(MODIFY_REPLACE, [generate_ssha(data["password"])])]
    if not changes:
        return jsonify({"error": "sin cambios"}), 400

    conn = ldap_connection()
    ok = conn.modify(user_dn(uid), changes)
    if not ok:
        return jsonify({"error": conn.result}), 400
    return jsonify({"message": "usuario actualizado"})


@app.delete("/users/<uid>")
def delete_user(uid):
    conn = ldap_connection()
    ok = conn.delete(user_dn(uid))
    if not ok:
        return jsonify({"error": conn.result}), 400
    return jsonify({"message": "usuario eliminado"})


@app.post("/login")
def login():
    data = request.get_json(force=True)
    uid = data.get("uid")
    password = data.get("password")

    if not uid or not password:
        return jsonify({"error": "uid y password son obligatorios"}), 400

    tls = Tls(validate=ssl.CERT_REQUIRED, ca_certs_file=LDAP_CA_CERT_PATH)
    server = Server(LDAP_URL, use_ssl=True, tls=tls, get_info=ALL)
    conn = Connection(server, user=user_dn(uid), password=password, auto_bind=False)

    if not conn.bind():
        return jsonify({"error": "credenciales invalidas"}), 401

    return jsonify({"message": "login correcto", "uid": uid})


@app.post("/password-recovery/request")
def request_recovery():
    data = request.get_json(force=True)
    uid = data.get("uid")
    if not uid:
        return jsonify({"error": "uid es obligatorio"}), 400

    conn = ldap_connection()
    conn.search(user_dn(uid), "(objectClass=inetOrgPerson)", attributes=["mail"])
    if not conn.entries:
        return jsonify({"error": "usuario no encontrado"}), 404

    mail = str(conn.entries[0].mail)
    token = make_reset_token(uid)
    reset_link = f"http://localhost:{APP_PORT}/password-recovery/confirm?token={token}"
    sent = send_reset_email(mail, reset_link)

    if not sent:
        return jsonify({
            "message": "smtp no configurado, enlace generado para prueba local",
            "token": token,
            "reset_link": reset_link,
        })

    return jsonify({"message": "enlace de recuperacion enviado"})


@app.route("/password-recovery/confirm", methods=["GET", "POST"])
def confirm_recovery():
    if request.method == "GET":
        token = request.args.get("token", "")
        return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Recuperar contraseña</title>
  <style>
    body {{ font-family: sans-serif; max-width: 560px; margin: 40px auto; padding: 0 16px; }}
    input {{ width: 100%; padding: 10px; margin: 8px 0 16px; box-sizing: border-box; }}
    button {{ padding: 10px 16px; }}
    code {{ word-break: break-all; }}
  </style>
</head>
<body>
  <h1>Recuperar contraseña</h1>
  <p>Token recibido:</p>
  <p><code>{token}</code></p>
  <form method="post">
    <input type="hidden" name="token" value="{token}">
    <label for="new_password">Nueva contraseña</label>
    <input id="new_password" name="new_password" type="password" required>
    <button type="submit">Actualizar contraseña</button>
  </form>
</body>
</html>"""

    data = request.get_json(silent=True) or request.form or {}
    token = data.get("token")
    new_password = data.get("new_password")
    if not token or not new_password:
        return jsonify({"error": "token y new_password son obligatorios"}), 400

    uid, err = verify_reset_token(token)
    if err:
        return jsonify({"error": err}), 400

    conn = ldap_connection()
    ok = conn.modify(user_dn(uid), {"userPassword": [(MODIFY_REPLACE, [generate_ssha(new_password)])]})
    if not ok:
        return jsonify({"error": conn.result}), 400

    return jsonify({"message": "contrasena actualizada"})


if __name__ == "__main__":
    if not TOKEN_SECRET_KEY:
        raise RuntimeError("TOKEN_SECRET_KEY no configurada")
    app.run(host=APP_HOST, port=APP_PORT)
