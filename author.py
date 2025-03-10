import ntplib
from threading import Thread
from datetime import datetime
from time import sleep

class author():
    def __init__(self, magic_date="2025-12-31"):
        self.magic_date = magic_date
        self.authorization = None
        self.GetNetTimeInThread(self.HandleAuthorization)

    def GetNetTime(self):
        servers = ['ntp.aliyun.com', 'time.hicloud.com', 'ntp.ntsc.ac.cn',
                   'ntp.tuna.tsinghua.edu.cn']
        ntp_client = ntplib.NTPClient()
        for server in servers:
            try:
                # 请求NTP服务器（这里使用 'pool.ntp.org' 作为示例）
                response = ntp_client.request('ntp.aliyun.com')
                # 获取并返回网络时间
                utc_time = datetime.fromtimestamp(response.tx_time)
                tz_time = utc_time.astimezone()
                local_date = tz_time.strftime("%Y-%m-%d")
                local_time = tz_time.strftime("%Y-%m-%d %H:%M:%S")
                print("{}: {}".format(server, local_time))
                return local_date
            except Exception as e:
                print(f"Error fetching NTP time: {e}")
        return None


    def GetNetTimeInThread(self, callback):
        def wrapper():
            callback(self.GetNetTime())
        Thread(target=wrapper).start()

    # 回调函数
    def HandleAuthorization(self, net_time):
        if net_time and net_time > self.magic_date:
            print("软件超过使用期, 请联系软件作者")
            self.authorization = False

if __name__ == "__main__":
    a = author("2025-03-08")
    while True:
        if a.authorization is None:
            sleep(1)
        elif a.authorization:
            print("软件授权有效")
            break;
        else:
            print("软件授权无效")
            break;
