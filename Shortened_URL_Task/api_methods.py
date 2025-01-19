import dbApi
import hashlib
from config import base_url
from datetime import datetime
from config import database_conn_info
from werkzeug.security import check_password_hash


def get_shorten_url(org_url, expiry_hours, password):
    if not org_url:
        return {"error": "Missing Required Field", "message": "Missing URL value", "field": "URL"}
    short_url = hashlib.sha256(org_url.encode()).hexdigest()[:6]
    shorten_url = f"{base_url}{short_url}"
    resp = dbApi.insert_data(database_conn_info, org_url, shorten_url, expiry_hours, password)
    return resp


def redirect_org_url(short_url, password, ip_address):
    id, org_url, expiry, hashed_password = dbApi.get_data(database_conn_info, short_url)
    if not org_url:
        return {"error": "Invalid URL", "message": "Short URL does not exist", "field": "short_url"}

    curr_time = datetime.now()
    if curr_time > expiry:
        return {"error": "Expired URL", "message": "Short URL has expired", "field": "expiry_hour"}
    
    if hashed_password and not check_password_hash(hashed_password, password):
        return {"error": "Invalid Password", "message": "Incorrect Password", "field": "password"}
    
    dbApi.update_access_count(database_conn_info, id)
    dbApi.insert_log_access_table(database_conn_info, short_url, ip_address)

    return org_url


if __name__ == "__main__":
    # org_url = "https://www.naukri.com/mnjuser/homepage"
    # org_url = "https://github.com/SaurabhSingh86/Case-Study/blob/main/Python%20Project/Food_hub_orders_Project.html"
    # short_url = "https://short.ly/0a4c98"
    # expiry_hours = 24
    # password = "abc@123"
    # resp = get_shorten_url(org_url, expiry_hours, password)
    # resp = redirect_org_url(short_url, password)
    # print(resp)
    pass