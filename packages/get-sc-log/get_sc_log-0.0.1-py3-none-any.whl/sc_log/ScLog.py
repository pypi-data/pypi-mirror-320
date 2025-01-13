
import requests
import time
from datetime import datetime, timedelta
import json

def get_original_log(data):
    """默认查询最近15min,返回最原始的日记信息"""
    project = data["project"]
    logStore = data["logStore"]
    url = "https://xjp-logger-service-s-backend-sysop.inshopline.com/api/getLogs"
    headers = {"Content-Type": "application/json"}
    time_15_minutes_ago = datetime.now() - timedelta(minutes=15)
    timestamp_15_minutes_ago = int(time_15_minutes_ago.timestamp())
    start_time = timestamp_15_minutes_ago
    end_time = int(time.time())
    if "from" in data:
        start_time = data["from"]
    if "to" in data:
        end_time = data["to"]
    line = 2
    if "line" in data:
        line = data["line"]
    offset = 0
    if "offset" in data:
        offset = data["offset"]
    params = {"project": project, "logStore": logStore, "from": start_time, "to": end_time,"line":line,"offset":offset}
    if "query" in data:
        query = data["query"]
        params["query"] = query
    response = requests.get(url, params=params, headers=headers).json()
    return response


def get_msg_log(data):
    """处理返回的日记，"""
    response = get_original_log(data)
    logs = response["data"]["logs"]
    # print("logs",logs)
    m_contents = [log["mLogItem"]["mContents"] for log in logs]
    # print(json.dumps(m_contents))
    log_msg_list = []
    for cotent in m_contents:
        log_msg = {}
        for t in cotent:
            if t["mKey"]=="msg":
                log_msg["msg"] = t["mValue"]
            elif t["mKey"]=="traceId":
                log_msg["traceId"] = t["mValue"]
        log_msg_list.append(log_msg)
    return log_msg_list












if __name__=="__main__":
    data = {"project":"sl-aquaman-sl-user-center-sz","logStore":"sl-aquaman-sl-user-center_test"}
    data["query"] = "level : ERROR"
    log_msg = get_msg_log(data)
    print(log_msg)
