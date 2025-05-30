import requests

url = "https://api.github.com/repos/gnunoi/mathdoc/releases"
params = {"per_page": 100}  # 每页最多可用100条
all_releases = []

page = 1
while True:
    params["page"] = page
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"请求失败，状态码：{response.status_code}")
        break
    
    releases = response.json()
    if not releases:
        break  # 如果没有更多 Release，则退出循环
    
    all_releases.extend(releases)
    page += 1

# 打印所有版本及发布时间
for release in all_releases:
    print(f"版本：{release['tag_name']}, 发布时间：{release['published_at']}")
