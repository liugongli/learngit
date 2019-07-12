import pymysql


def get_user(userid: int):
    """
    获取用户信息
    :param userid: 短信平台userid
    :return:
    """
    conn = pymysql.connect(host='rds110h078ky1dvmyq7n127.mysql.rds.aliyuncs.com',
                           user='canal',
                           password='Canal#2019',
                           db='s3main',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                select * from sms_accounts where id={userid}
            """)
            return cursor.fetchone()
    finally:
        conn.close()
