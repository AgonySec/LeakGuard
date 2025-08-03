from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import json
import time
import random

from .utils import save_excel_or_json, user_agents, read_file

headers = {
    "Host": "api.haveibeenbreached.com",
    "User-Agent": random.choice(user_agents),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://haveibeenbreached.com/",
    "Origin": "https://haveibeenbreached.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Modev": "cors",
    "Sec-Fetch-Site": "same-site",
    "Te": "trailers"
}

email_leak_columns = ['邮箱信息', '泄露次数', '泄露情报']


# 检测邮件是否泄露
def check_leak(email_addr):
    url = "https://api.haveibeenbreached.com/?contact=" + email_addr
    print(f"[+]正在检查邮箱：{email_addr} 的泄露情况...")
    # 最多重放次数
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)

            # 检查请求是否成功
            if response.status_code == 200:
                # 获取响应的文本内容
                content = response.text
                # 检查响应内容是否为空
                if content == '[]':
                    print(f"第{attempt + 1}次检测中，邮箱: {email_addr} 不存在泄露")
                    time.sleep(1)
                else:
                    # 将JSON字符串转换为Python列表
                    data = json.loads(content)
                    # 泄露次数
                    array_size = len(data)
                    names = []
                    for item in data:
                        name = item.get("Name")
                        names.append(name)
                    print(
                        f"第{attempt + 1}次检测中，邮箱: {email_addr} 存在泄露！泄露次数为：{array_size}，具体泄露情报已写入result目录下的txt文件中。跳转下个邮箱...")
                    time.sleep(1)
                    return [email_addr, array_size, names]
            else:
                print(f"[+]请求失败，状态码：{response.status_code}")
                if attempt < max_retries - 1:
                    print(f"[+]尝试重新请求，尝试次数：{attempt + 1}/{max_retries}")
                    time.sleep(1)  # 等待1秒后重试
        except requests.RequestException as e:
            print(f"[+]请求异常：{e}")
            if attempt < max_retries - 1:
                print(f"[+]尝试重新请求，尝试次数：{attempt + 1}/{max_retries}")
                time.sleep(1)  # 等待1秒后重试
    return [email_addr, 0, []]  # 如果没有泄露，返回默认值


def check_one_email(email, output_file, mode):
    print(f"[+]开始检测邮箱：{email}")
    result = check_leak(email)
    results = [result] if result[1] > 0 else []  # 只有存在泄露时才添加到结果中
    save_excel_or_json(results, email_leak_columns, output_file, mode)


# 单线程批量处理邮件，准确率99%
def batch_process_emails_for(email_file, output_file, modes):
    print("[+]开始批量检测邮箱：")
    emails_addr = read_file(email_file)

    results = []
    leak_count = 0

    for email in emails_addr:
        result = check_leak(email)
        if result[1] > 0:  # 如果有泄露记录
            results.append(result)
            leak_count += 1

    save_excel_or_json(results, email_leak_columns, output_file, modes)
    print(f"[+]批量检测结束，总共检测{len(emails_addr)}个邮箱，存在泄露邮箱的总数为：{leak_count}")
