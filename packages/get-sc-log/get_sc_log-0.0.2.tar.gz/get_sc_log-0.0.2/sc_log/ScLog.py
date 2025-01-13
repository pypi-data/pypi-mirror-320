import re

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
    time_15_minutes_ago = datetime.now() - timedelta(minutes=60)
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

def get_http_data(http_data):
    fields = {}
    patterns = {
        'method': r'method:\s*(\w+)',
        'uri': r'uri:\s*(.+)',
        'requestHeader': r'requestHeader:\s*(\{.*?\})',
        'requestParams': r'requestParams:\s*(\{.*?\})',
        'requestBody': r'requestBody:\s*(\{.*?\})',
        'responseCode': r'responseCode:\s*(\d+)',
        'responseHeader': r'responseHeader:\s*(\{.*?\})',
        'responseBody': r'responseBody:\s*(\{.*?\})'
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, http_data, re.DOTALL)
        if match:
            fields[key] = match.group(1).strip()
    # print("fields",fields)
    # 对 JSON 字符串进行解析
    # fields['requestHeader'] = json.loads(fields['requestHeader'])
    # fields['requestParams'] = json.loads(fields['requestParams'])
    # fields['requestBody'] = json.loads(fields['requestBody'])
    # fields['responseHeader'] = json.loads(fields['responseHeader'])
    # fields['responseBody'] = json.loads(fields['responseBody'])
    return fields


if __name__=="__main__":
    data = {"project":"sl-aquaman-sl-user-center-sz","logStore":"sl-aquaman-sl-user-center_test"}
    data["query"] = 'eca14bb46e127d070cc928dcb7133284 and http and msg: "completed." and msg: open_host and msg: jobs '
    log_msg = get_msg_log(data)
    # print(log_msg)
    for i in log_msg:
        # print(json.dumps(i))
        # print(i["msg"])
        fields = get_http_data(i["msg"])
        # print(fields)
        # print(fields["method"])
        # print(fields["uri"])
        # print("requestHeader",fields["requestHeader"])
        # print("requestParams",fields["requestParams"])
        # print("requestBody",fields["requestBody"])
        # print("responseCode",fields["responseCode"])
        # print("responseHeader",fields["responseHeader"])
        # print("responseBody",fields["responseBody"])


