import arrow
import pymysql
import accounts


account_map = {
    204497: ['18874415793'],
    202844: ['18874415793'],
    202843: ['18874415793'],
    202842: ['18874415793'],
    202839: ['18874415793'],
    204469: ['18874415793'],
    202838: ['18874415793'],
    204473: ['18874415793'],
    204526: ['18874415793'],
    204527: ['18874415793'],
    204525: ['18874415793'],
    203400: ['18874415793'],
}


def alert_to_dingtalk(content, atMobiles, url="https://oapi.dingtalk.com/robot/send?access_"
                                              "token=282c30d5ee85576c3b9b07b245bee96fe81711487108076f85c57cd51d7524d3"):
    """
    发送信息到钉钉机器人
    :return:
    """
    import requests

    body = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    if atMobiles:
        body['at'] = {}
        body['at']['atMobiles'] = atMobiles
    resp = requests.post(url, json=body)
    print(resp.content)


def yx_user_statistics(conn):
    """
    统计营销用户的发送情况, 只要有发送,立刻告警
    :return:
    """
    with conn.cursor() as cursor:
        today = arrow.now().format('YYYYMMDD')
        sql = f"""
            SELECT userid, count(id) c from sended_{today}
            where CREATETIME >= DATE_ADD(now(),interval -30 minute)
            and userid in (
            204497,
            202844,
            202843,
            202842,
            202839,
            204469,
            203400,
            204473
            )
            GROUP BY userid
            having count(id) >= 1
        """
        cursor.execute(sql)
        data = cursor.fetchall()
        for row in data:
            phone = account_map[row['userid']]
            account = accounts.get_user(row['userid'])
            alert_to_dingtalk(f"{row['userid']} [{account['SIGNCODE']}]有信息提交 请关注! 目前已经提交{row['c']}个手机号码", phone)


def hy_user_statistics(conn):
    """
    统计行业用户发送情况, 若过去两分钟内失败率或者未知率100% 告警
    :param conn: 数据库连接对象
    :return:
    """

    today = arrow.now().format('YYYYMMDD')
    sql = f"""
    select userid, total, success, unknown, (total-success-unknown) fail from (
            SELECT userid, count(id) total, 
            sum(if(RETURN_STATUS='DELIVRD', 1, 0)) success, 
            sum(if(RETURN_STATUS is null, 1, 0)) unknown
            from sended_{today}
            where CREATETIME BETWEEN DATE_ADD(now(),interval -4 minute) and DATE_ADD(now(),interval -2 minute)
            and userid in (
            202838,
            204526,
            204527,
            204525
            )
            GROUP BY userid
            ) t
    """
    with conn.cursor() as cursor:
        cursor.execute(sql)
        data = cursor.fetchall()
        pattern = 'YYYY-MM-DD HH:mm:ss'
        begin = arrow.now().replace(minutes=-4).format(pattern)
        end = arrow.now().replace(minutes=-2).format(pattern)
        for row in data:
            phone = account_map[row['userid']]
            account = accounts.get_user(row['userid'])
            if row['fail'] == row['total']:
                # 失败率100%
                alert_to_dingtalk(f"{row['userid']} [{account['SIGNCODE']}]在{begin}到{end}期间失败率100%, 共{row['total']}个号码", phone)
            if row['unknown'] == row['total']:
                # 未知率100%
                alert_to_dingtalk(f"{row['userid']} [{account['SIGNCODE']}]在{begin}到{end}期间未知率100%, 共{row['total']}个号码", phone)


def ce_shi():
    print('我还活着！')


if __name__ == '__main__':
    conn = pymysql.connect(host='rds64hblrr5lg14i18rz198.mysql.rds.aliyuncs.com',
                           user='canal',
                           password='Canal#2019',
                           db='s4backup',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

    import schedule
    # 每30分钟执行一次
    schedule.every(30).minutes.do(yx_user_statistics, conn)

    # 每2分钟执行一次
    schedule.every(2).minutes.do(hy_user_statistics, conn)

    # 每1分钟执行一次
    schedule.every(1).minutes.do(ce_shi)

    # 每1分钟执行一次
    schedule.every(5).minutes.do(alert_to_dingtalk, f'网络异常', ['18874415793'])

    while True:
        try:
            schedule.run_pending()
            import time
            time.sleep(1)
        except Exception as e:
            url = "https://oapi.dingtalk.com/robot/send?access_" \
                  "token=282c30d5ee85576c3b9b07b245bee96fe81711487108076f85c57cd51d7524d3"
            alert_to_dingtalk(f'网络异常 {e}', ['18874415793'], url=url)
            time.sleep(120)
