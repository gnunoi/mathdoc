import requests


def check_carrier_by_phone(phone_number):
    # 使用 ip138 的查询服务
    url = f"https://ip138.com/mobile.asp?mobile={phone_number}&action=mobile/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # 解析返回的 HTML 页面，提取运营商信息
            if "移动" in response.text:
                return "移动"
            elif "联通" in response.text:
                return "联通"
            elif "电信" in response.text:
                return "电信"
            else:
                return "未知运营商"
        else:
            return "查询失败"
    except Exception as e:
        return f"查询出错：{e}"


# 示例使用
phone_number = input("请输入手机号码：")
carrier = check_carrier_by_phone(phone_number)
print(f"该手机号码属于：{carrier}")