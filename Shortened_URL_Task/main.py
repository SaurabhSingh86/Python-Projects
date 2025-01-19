from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from config import database_conn_info
import api_methods
import dbApi


app = Flask(__name__)
CORS(app)


@app.route("/shorten", methods=["POST"])
def shorten():
    data_dict = request.get_json()
    org_url = data_dict.get("URL", "")
    expiry_hours = data_dict.get("expiry_hour", "")
    if not expiry_hours:
        expiry_hours = 24
    password = data_dict.get("password", "")
    response = api_methods.get_shorten_url(org_url, expiry_hours, password)
    return jsonify(response)


@app.route("/<short_url>", methods=["GET"])
def redirect_org_url(short_url):
    data_dict = request.get_json()
    password = data_dict.get("password", "")
    ip_address = request.remote_addr
    response = api_methods.redirect_org_url(short_url, password, ip_address)
    if "error" in response:
        return jsonify(response)
    return redirect(response)


@app.route("/analytics/<short_url>", methods=["GET"])
def analytics(short_url):
    response = dbApi.get_analytics_info(database_conn_info, short_url)
    return jsonify({"accessed_count": len(response), "log": response})


if __name__ == "__main__":
    app.run(debug=True)