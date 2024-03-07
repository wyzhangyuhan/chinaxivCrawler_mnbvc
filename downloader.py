import requests
import os
import time
import jsonlines
from tqdm import tqdm

DOWNLOAD_INTERVAL = 0.5

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
            with open(f'{save_path}/{pdf_file_name}', 'wb') as file:
                file.write(response.content)
        else:
            print("文件下载失败，状态码：", response.status_code)
    except Exception as e:
        print(f"An error occurred: {e}")


def traverse_pdf_link(pdf_foler, save_path):
    pdf_files = os.listdir(pdf_foler)
    for file in tqdm(pdf_files, total=len(pdf_files)):
        with jsonlines.open(f"{pdf_foler}/{file}", "r") as reader:
            cate_name = file.split('.')[0]
            save_cate = f"{save_path}/{cate_name}"
            if not os.path.exists(save_cate):
                os.mkdir(save_cate)
            for item in reader:
                link_downloader(item['link'][0], save_cate)

if __name__ == "__main__":
    traverse_pdf_link("/home/zhangyuhan/python_project/chinaxivCrawler_mnbvc/pdf_links", "/mnt/matrix/zhangyuhan/zyh-data/chinaxiv")