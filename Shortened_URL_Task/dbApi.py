import mysql.connector
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash



def get_connection(database_conn_info):
    host_name, user_name, passw_name, db_name = database_conn_info.split('#')
    conn = mysql.connector.connect(host=host_name, user=user_name, passwd=passw_name, database=db_name, charset="utf8")
    cur = conn.cursor()
    return conn, cur


def insert_data(database_conn_info, org_url, shorten_url, expiry_hours, password):
    resp = {}
    conn, cur = get_connection(database_conn_info)
    exp = datetime.now() + timedelta(hours=int(expiry_hours))
    pass_sql = "insert into url_info_table(original_url, short_url, expiration_timestamp, hashed_password) values ('{}', '{}', '{}', '{}');"
    i_sql = "insert into url_info_table(original_url, short_url, expiration_timestamp) values ('{}', '{}', '{}');"
    try:
        if password:
            cur.execute(pass_sql.format(org_url, shorten_url, exp, generate_password_hash(password)))
        else:
            cur.execute(i_sql.format(org_url, shorten_url, exp))
            
        resp = {"status": "success", "message": "URL shortened successfully", "short_url": shorten_url}
    except mysql.connector.IntegrityError as err:
        resp = {"error": "Duplicate entry", "message": "URL already exist", "short_url": shorten_url}
    finally:
        conn.commit()
        cur.close()
        conn.close()
    return resp


def get_data(database_conn_info, short_url):
    conn, cur = get_connection(database_conn_info)
    sql = """select id, original_url, expiration_timestamp, hashed_password from url_info_table where short_url like '{}';"""
    pattern = f'%{short_url}%'
    cur.execute(sql.format(pattern))
    res = cur.fetchone()
    cur.close()
    conn.close()
    if res: return res[0], res[1], res[2], res[3]
    return "", "", "", ""

def update_access_count(database_conn_info, id):
    conn, cur = get_connection(database_conn_info)
    up_sql = "update url_info_table set accessed_count= accessed_count + 1 where id = {};"
    cur.execute(up_sql.format(id))
    conn.commit()
    cur.close()
    conn.close()
    return

def insert_log_access_table(database_conn_info, short_url, ip_address):
    conn, cur = get_connection(database_conn_info)
    up_sql = "insert into access_logs_table (short_url, ip_address) values('{}', '{}')"
    cur.execute(up_sql.format(short_url, ip_address))
    conn.commit()
    cur.close()
    conn.close()
    return

def get_analytics_info(database_conn_info, short_url):
    conn, cur = get_connection(database_conn_info)
    response = []
    sql = "select access_time, ip_address from access_logs_table where short_url = '{}';"
    cur.execute(sql.format(short_url))
    res = cur.fetchall()
    cur.close()
    conn.close()
    if res:
        for access_time, ip_address in res:
            response.append({"access_time": access_time, "ip_address": ip_address})
    return response

if __name__ == "__main__":
    from config import database_conn_info
    print(get_connection(database_conn_info))