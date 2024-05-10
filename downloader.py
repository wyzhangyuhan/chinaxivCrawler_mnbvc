import requests
import os
import time
import jsonlines
import argparse
import multiprocessing
import uuid
from multiprocessing import Process
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, TimeoutError

DOWNLOAD_INTERVAL = 0.5

global downloaded
global log_url

def link_downloader(url, save_path):
    """
    Download a PDF from a given URL and save it to the specified path.

    Parameters:
    - url: The URL of the PDF to download.
    - save_path: The file path where the PDF will be saved.
    """
    try:
        time.sleep(DOWNLOAD_INTERVAL)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        }

        # 发送GET请求
        response = requests.get(url, headers=headers)
        
        # 检查请求是否成功
        if response.status_code == 200:
            # 写入文件
            pdf_file_name = response.headers._store['content-disposition'][1]
            pdf_file_name = pdf_file_name.split('=')[-1]
            pdf_file_name = pdf_file_name.replace("\"", "")
            global downloaded
            if pdf_file_name in downloaded:
                print("已下载！")
                with jsonlines.open(f'{save_path}/log.jsonl', 'a') as file:
                    file.write({"url":url})
                return pdf_file_name
            
            with open(f'{save_path}/{pdf_file_name}', 'wb') as file:
                file.write(response.content)
            
            with jsonlines.open(f'{save_path}/log.jsonl', 'a') as file:
                file.write({"url":url})
            
            downloaded.add(pdf_file_name)
            return pdf_file_name
        else:
            print("文件下载失败，状态码：", response.status_code)
            return None
    except Exception as e:
        print(f"An error occurred: {e}")

def split_data(data, num_shards):
    # 将数据分割为 num_shards 个片段
    shard_size = len(data) // num_shards
    shards = [data[i:i + shard_size] for i in range(0, len(data), shard_size)]
    return shards

def build_segment(pdf_files, num_shards, save_path):
    data = []
    with jsonlines.open(f"{pdf_files}", "r") as reader:
        for item in reader:
            data.append(item)
            # file_downloader(item['link'][0], save_cate)
                
    return split_data(data, num_shards)

def file_downloader(link, save_path):
    with ThreadPoolExecutor(max_workers=1) as executor:
        # 提交下载文件的任务
        future = executor.submit(link_downloader, link, save_path)
        try:
            # 等待任务完成，设置超时时间为5分钟（300秒）
            filename = future.result(timeout=300)
            if filename:
                print(f'文件 {filename} 下载成功')
            else:
                print(f'链接{link}, 下载失败')
        except TimeoutError:
            print('下载操作超时，正在取消下载...')
            # 取消任务
            future.cancel()
            print('下载已取消')

def traverse_data(shard, save_path):
    global log_url
    for data in tqdm(shard, total=len(shard)):
        if data['link'][0] in log_url:
            continue
        file_downloader(data['link'][0], save_path)

def downloaded_recovery(save_path):

    already_downloaded = set()
    dealt_url=set()
    # 检查路径下的每一个文件和文件夹
    for filename in os.listdir(save_path):
        # 完整的文件路径
        full_path = os.path.join(save_path, filename)
        # 检查是否为文件且扩展名为.pdf
        if os.path.isfile(full_path) and filename.endswith('.pdf'):
            already_downloaded.add(filename)
    try:
        with jsonlines.open(f"{save_path}/log.jsonl", "r") as file:
            for item in file:
                dealt_url.add(item['url'])
    except:
        dealt_url=set()
    return already_downloaded, dealt_url

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='download pdf')
    parser.add_argument('--num_shard', default=1, type=int, help='Number of shards')
    parser.add_argument('--data_file', type=str, help='file path')
    parser.add_argument('--save_path', type=str, help='save file path')
    parser.add_argument('--recovery', default=True, type=bool, help='download_recovery')
    args = parser.parse_args()

    num_shards = args.num_shard
    file = args.data_file
    save_path = args.save_path
    recovery = args.recovery
    shards = build_segment(file, num_shards, save_path)

    try:
        cate_name = file.split('.')[0]
        cate_name = cate_name.split('/')[-1]
    except:
        print("文件名获取失败")
        cate_name = uuid.uuid4()
    save_cate = f"{save_path}/{cate_name}"
    if not os.path.exists(save_cate):
        os.mkdir(save_cate)
    save_path = save_cate

    global downloaded, log_url
    if recovery:
        downloaded, log_url=downloaded_recovery(save_path)
    else:
        downloaded, log_url=set(), set()
    print(downloaded)
    processes = []
    for shard in shards:
        p = Process(target=traverse_data, args=(shard,save_path))
        processes.append(p)
        p.start()

    # 等待所有进程完成
    for p in processes:
        p.join()

    print(f"finish downloading:{file}, save to {save_path}!\n")

if __name__ == "__main__":
    main()
    #"/home/zhangyuhan/python_project/chinaxivCrawler_mnbvc/pdf_links", "/mnt/matrix/zhangyuhan/zyh-data/chinaxiv"