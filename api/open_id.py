from flask import Flask, request, jsonify
import requests

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
            "authority": "prod-api.reward.ff.garena.com",
            "method": "GET",
            "path": "/redemption/api/auth/inspect_token/",
            "scheme": "https",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "access-token": access_token,
            "user-agent": "Mozilla/5.0"
        }

        uid_res = requests.get(uid_url, headers=uid_headers)
        uid_data = uid_res.json()
        uid = uid_data.get("uid")

        if not uid:
            return jsonify({"error": "Failed to extract UID"}), 400

        # Step 2: open_id fetch
        openid_url = "https://shop2game.com/api/auth/player_id_login"
        openid_headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        payload = {"app_id": 100067, "login_id": str(uid)}

        openid_res = requests.post(openid_url, headers=openid_headers, json=payload)
        openid_data = openid_res.json()
        open_id = openid_data.get("open_id")

        if not open_id:
            return jsonify({"error": "Failed to extract open_id"}), 500

        return jsonify({"uid": uid, "open_id": open_id})

    except Exception as e:
        return jsonify({"error": "Exception occurred", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
