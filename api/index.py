import secrets
import base64
import json
import time
import requests
from flask import Flask, jsonify, request

VALID_PACKAGE = "com.DreamerTag.DreamRunners"
CERT_SHA256 = "SIMBATAG"

class GameInfo:
    def __init__(self):
        self.TitleId = "17EC5B"
        self.SecretKey = "AGR3BAHHJ8U3FEQISYWRPK15YDCG4I9A7NKCITBEFWMQ1D1POD"
        self.ApiKey = "OC|1240755245783649|5151fc00ae1300ccd7ca52445df60e35"

    def headers(self):
        return {
            "X-SecretKey": self.SecretKey,
            "Content-Type": "application/json"
        }

settings = GameInfo()
app = Flask(__name__)

current_nonces = {}
attested_users = {}

def verify_oculus_nonce(user_id, nonce):
    r = requests.post(
        "https://graph.oculus.com/user_nonce_validate",
        data={
            "access_token": settings.ApiKey,
            "user_id": user_id,
            "nonce": nonce
        }
    )
    return r.status_code == 200 and r.json().get("is_valid") is True


def verify_attestation_token(token):
    r = requests.get(
        "https://graph.oculus.com/platform_integrity/verify",
        params={
            "token": token,
            "access_token": settings.ApiKey
        }
    )
    return r.json()


def decode_claims(b64):
    b64 += "=" * (-len(b64) % 4)
    return json.loads(base64.urlsafe_b64decode(b64))


@app.route("/api/authenticate/attestation/getNonce", methods=["POST"])
def get_attestation_nonce():
    data = request.get_json(silent=True) or {}
    user_id = data.get("UserId")
    nonce = data.get("Nonce")

    if not user_id or not nonce:
        return jsonify({"error": "Missing UserId or Nonce"}), 400

    if not verify_oculus_nonce(user_id, nonce):
        return jsonify({"error": "Invalid Oculus nonce"}), 403

    challenge = secrets.token_urlsafe(16)
    current_nonces[user_id] = {
        "nonce": challenge,
        "ts": int(time.time())
    }

    return jsonify({"challenge_nonce": challenge}), 200


@app.route("/api/authenticate/attestation/verify", methods=["POST"])
def verify_attestation():
    data = request.get_json(silent=True) or {}
    user_id = data.get("UserId")
    token = data.get("AttestationToken")

    if not user_id or not token:
        return jsonify({"BanMessage": "Missing attestation data"}), 403

    if user_id not in current_nonces:
        return jsonify({"BanMessage": "Missing nonce session"}), 403

    result = verify_attestation_token(token)

    if not result.get("data"):
        return jsonify({"BanMessage": "Invalid attestation"}), 403

    entry = result["data"][0]
    if entry.get("message") != "success":
        return jsonify({"BanMessage": "Attestation failed"}), 403

    claims = decode_claims(entry["claims"])
    app_state = claims.get("app_state", {})
    device_state = claims.get("device_state", {})
    device_ban = claims.get("device_ban", {})

    if device_ban.get("is_banned"):
        return jsonify({"BanMessage": "Device banned"}), 403

    if app_state.get("package_id") != VALID_PACKAGE:
        return jsonify({"BanMessage": "Invalid package"}), 403

    if CERT_SHA256 not in (app_state.get("package_cert_sha256_digest") or ""):
        return jsonify({"BanMessage": "Invalid certificate"}), 403

    if device_state.get("device_integrity_state") != "Advanced":
        return jsonify({"BanMessage": "Untrusted device"}), 403

    attested_users[user_id] = {"claims": claims}
    return jsonify({"status": "OK"}), 200


@app.route("/api/PlayFabAuthentication", methods=["POST"])
def playfab_auth():
    data = request.get_json(silent=True) or {}
    oculus_id = data.get("OculusId")

    if not oculus_id:
        return jsonify({"BanMessage": "Missing OculusId"}), 403

    custom_id = "OCULUS" + oculus_id

    if oculus_id not in attested_users:
        return jsonify({"BanMessage": "No attestation"}), 403

    login = requests.post(
        f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithServerCustomId",
        headers=settings.headers(),
        json={
            "ServerCustomId": custom_id,
            "CreateAccount": True
        }
    )

    if login.status_code != 200:
        return jsonify(login.json()), 403

    d = login.json()["data"]

    return jsonify({
        "SessionTicket": d["SessionTicket"],
        "EntityToken": d["EntityToken"]["EntityToken"],
        "PlayFabId": d["PlayFabId"],
        "EntityId": d["EntityToken"]["Entity"]["Id"],
        "EntityType": d["EntityToken"]["Entity"]["Type"]
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1416, debug=True)
