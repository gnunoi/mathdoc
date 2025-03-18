import requests

url = "https://sms.aliyuncs.com"
params = {
    "RegionId": "cn-hangzhou",
    "PhoneNumbers": "your_phone_number",
    "SignName": "your_sign_name",
    "TemplateCode": "your_template_code",
    "TemplateParam": "{\"code\":\"123456\"}"
}
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}
response = requests.post(url, data=params, headers=headers)
print(response.json())