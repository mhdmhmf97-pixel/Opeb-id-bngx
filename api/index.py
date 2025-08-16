from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

@app.route('/open_id', methods=['GET'])
def fetch_open_id():
    access_token = request.args.get('access_token')
    if not access_token:
        return jsonify({"error": "Missing access_token"}), 400

    try:
        # Step 1: UID Fetch
        uid_url = "https://prod-api.reward.ff.garena.com/redemption/api/auth/inspect_token/"
        uid_headers = {
            "accept": "application/json",
            "access-token": access_token,
            "user-agent": "Mozilla/5.0"
        }

        uid_res = requests.get(uid_url, headers=uid_headers, timeout=10)
        uid_data = uid_res.json()
        uid = uid_data.get("uid")
        if not uid:
            return jsonify({"error": "Failed to extract UID"}), 400

        # Step 2: open_id fetch with retry (up to 20s)
        openid_url = "https://shop2game.com/api/auth/player_id_login"
        openid_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        payload = {"app_id": 100067, "login_id": str(uid)}

        open_id = None
        start_time = time.time()
        while time.time() - start_time < 20:
            res = requests.post(openid_url, headers=openid_headers, json=payload, timeout=10)
            data = res.json()
            open_id = data.get("open_id")
            if open_id:
                break
            time.sleep(1)  # انتظر ثانية قبل المحاولة مرة أخرى

        if not open_id:
            return jsonify({"error": "Failed to extract open_id"}), 500

        return jsonify({"uid": uid, "open_id": open_id})

    except Exception as e:
        return jsonify({"error": "Exception occurred", "details": str(e)}), 500
