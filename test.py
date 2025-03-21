import os
import sys
import requests
import subprocess
import time


def download_new_version(url, save_path):
    """
    下载新版本的EXE文件
    :param url: 新版本EXE文件的下载链接
    :param save_path: 保存新版本EXE文件的路径
    """
    response = requests.get(url, stream=True)
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def start_subprocess(exe_path):
    """
    启动子进程运行EXE文件
    :param exe_path: EXE文件的路径
    :return: 子进程对象
    """
    return subprocess.Popen([exe_path])


def main():
    # 假设新版本EXE文件的下载链接和保存路径
    new_version_url = "https://mathdoc.top/mathdoc.exe"
    new_version_path = "/Users/paul/Desktop/mathdoc.exe"

    # 当前运行的EXE文件路径
    current_exe_path = sys.argv[0]
    print(current_exe_path)

    # 下载新版本EXE文件
    print(new_version_url, new_version_path)
    download_new_version(new_version_url, new_version_path)

    # 启动子进程运行新版本EXE文件
    sub_process = start_subprocess(new_version_path)

    # 退出主进程
    sys.exit()

    # 子进程在后台运行，等待主进程退出后覆盖旧EXE文件
    # 这里需要确保子进程在主进程退出后有足够的权限覆盖旧EXE文件
    # 可以通过在子进程中稍作等待，确保主进程已完全退出
    time.sleep(2)

    # 覆盖旧EXE文件
    os.replace(new_version_path, current_exe_path)

    # 退出子进程
    sub_process.terminate()


if __name__ == "__main__":
    main()