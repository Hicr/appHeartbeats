#!/usr/bin/python3
# import pymysql

from datetime import datetime
from datetime import timedelta
from datetime import timezone

import uuid
import dmPython
from apscheduler.schedulers.blocking import BlockingScheduler
# new
import requests


# 时区
SHA_TZ = timezone(
    timedelta(hours=8),
    name='Asia/Shanghai',
)

# 指向数据库 mysql版本
MYSQL_PARAMS = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "app",
    "charset": "utf8",
    "tableName":"app_keepalive"
}

# 指向数据库 dm版本
DM_PARAMS = {
    "host": "127.0.0.1",
    "port": 5237,
    "user": "root",
    "password": "root",
    "schema": "root"
}

# 应用信息
APP_LIST = [
    {
        "appName":"系统1",
        "appCode":"app1",
        "appDesc":"系统1",
        "appUrl":"http://127.0.0.1:28084/v2/api-docs",
        "appIp":"127.0.0.1",
        "appPort":"28084"
    },
    {
        "appName": "系统2",
        "appCode": "app2",
        "appDesc": "系统2",
        "appUrl": "http://127.0.0.1:28083/v2/api-docs",
        "appIp": "127.0.0.1",
        "appPort": "28083"
    }
]

# 插入数据列表
INSTER_APP_LIST = []

# 心跳检测间隔时间 (min)
TIME_INTERVAL = 15
# 应用超时时间
TIME_OUT = 5

# 插入数据
def insertInfo(logData):
    print("开始批量插入检测数据 当前时间为", nowTime())
    conn = dmPython.connect(
        user=DM_PARAMS["user"],
        password=DM_PARAMS["password"],
        server=DM_PARAMS["host"],
        port=DM_PARAMS["port"]
    )
    cursor = conn.cursor()
    sql = "INSERT INTO \""+ DM_PARAMS["schema"] + "\".\"OTHER_APP_KEEPALIVE" +"\" ( \"id\", \"app_name\", \"app_code\", \"app_desc\", \"app_url\", \"app_ip\", \"app_port\", \"app_state\", \"connect_time\", \"message\" ) VALUES (?,?,?,?,?,?,?,?,?,?)"

    try:
        cursor.executemany(sql,logData)
        conn.commit()
    except Exception as e:
        print("插入异常：" , e)
        conn.rollback()

    cursor.close()
    conn.close()
    # conn = pymysql.connect(host=MYSQL_PARAMS["host"],
    #                        port=MYSQL_PARAMS["port"],
    #                        user=MYSQL_PARAMS["user"],
    #                        password=MYSQL_PARAMS["password"],
    #                        database=MYSQL_PARAMS["database"],
    #                        charset=MYSQL_PARAMS["charset"])
    #
    # cursor = conn.cursor()
    # sql = "INSERT INTO `"+ MYSQL_PARAMS["tableName"] +"` ( `id`, `app_name`, `app_code`, `app_desc`, `app_url`, `app_ip`, `app_port`, `app_state`, `connect_time` , `message`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    #
    # try:
    #     cursor.executemany(sql,logData)
    #     conn.commit()
    # except Exception as e:
    #     print("插入异常：" , e)
    #     conn.rollback()
    # cursor.close()
    # conn.close()
    print("批量插入检测数据完毕 当前时间为", nowTime())
    return None

def nowTime():
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    beijing_now = utc_now.astimezone(SHA_TZ)
    # print(beijing_now.strftime('%H_%M_%S'))
    # print(beijing_now.strftime('%Y-%m-%d %H:%M:%S'))
    # print(beijing_now,'111', beijing_now.time())
    # print(beijing_now.date(), beijing_now.tzname())
    return beijing_now.strftime('%Y-%m-%d %H:%M:%S')

# 测试连接
def testConn():
    print("========== 触发心跳检测 时间为", nowTime(), " ==========")
    global INSTER_APP_LIST
    # print("当前待插入数量" , len(INSTER_APP_LIST))
    for app in APP_LIST:
        try:
            r = requests.get(app.get("appUrl"),timeout=TIME_OUT)
            if(r.status_code == 200):
                print("当前" + app.get("appName") + "应用响应状态码为：" + str(r.status_code), "心跳检测正常")
                INSTER_APP_LIST.append([str(uuid.uuid4()),app.get("appName"),app.get("appCode"),app.get("appDesc"),app.get("appUrl"),app.get("appIp"),app.get("appPort"),'成功',nowTime(),''])
            else:
                print("当前" + app.get("appName") + "应用响应状态码为：" + str(r.status_code), "心跳检测发现异常")
                INSTER_APP_LIST.append([str(uuid.uuid4()),app.get("appName"),app.get("appCode"),app.get("appDesc"),app.get("appUrl"),app.get("appIp"),app.get("appPort"),'连接异常',nowTime(),'连接状态码为'+str(r.status_code)])
        except requests.exceptions.RequestException as e:
            print(app.get("appName") + "拒绝连接！心跳检测发现异常", e)
            INSTER_APP_LIST.append([str(uuid.uuid4()),app.get("appName"),app.get("appCode"),app.get("appDesc"),app.get("appUrl"),app.get("appIp"),app.get("appPort"),'连接超时',nowTime(),str(e)])
    insertInfo(INSTER_APP_LIST)
    INSTER_APP_LIST = []
    print("========== 心跳检测完毕 时间为", nowTime(), " ==========")
    return None

# 定时任务
def autoJob():
    s = BlockingScheduler()
    # 初始化定时任务 每15分钟测似一次
    s.add_job(testConn, 'interval', seconds=TIME_INTERVAL * 60)
    try:
        s.start()
    except KeyboardInterrupt:
        s.shutdown()
        print("========== 停止心跳检测 ==========")


if __name__ == '__main__':
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    print("========== 心跳检测开始 ==========")
    print("========== 开始时间为", nowTime(), " ==========")
    print("========== 当前配置心跳检测间隔时间为每", TIME_INTERVAL , "分钟一次==========")
    # 定时任务执行心跳检测
    autoJob()
    print("========== 心跳检测停止 ==========")