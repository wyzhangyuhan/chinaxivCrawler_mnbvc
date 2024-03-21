import requests
import re
import os
import time
import jsonlines
from tqdm import tqdm
from bs4 import BeautifulSoup
from utils import extract_text, mark_finish, load_links, segment_restart

TIME_INTERVAL = 0.5
global session
session=requests.Session()
def get_html_from_url(url):
    global session
    time.sleep(TIME_INTERVAL)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",  # Do Not Track Request Header
        "Connection": "keep-alive"
    }
    response = session.get(url, headers=headers)

    # 确保请求成功
    if response.status_code == 200:
        # 获取页面HTML内容
        html_text = response.text
        return html_text  # 或者进行其他的处理
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    
    return ""

def get_chinaxiv_category(html_text):

    cate_link = []
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_text, 'html.parser')

    # 找到所有的<div class="box part1">标签
    divs = soup.find_all('div', class_='box part1')

    # 从这些<div>标签中提取所有的<a>标签
    a_tags = []
    for div in divs:
        a_tags.extend(div.find_all('a'))

    # 打印提取的<a>标签
    for a in a_tags:
        tmp_dict = dict()
        tmp_dict['link'] = "https://chinaxiv.org" + a["href"]
        tmp_cate, _ = extract_text(a.text)
        tmp_dict['cate'] = tmp_cate
        cate_link.append(tmp_dict)
        print(f'URL: {a["href"]}, Text: {tmp_cate}')

    return cate_link

def get_time_link(html_text):
    time_links = []
    dedup_set = set()
    soup = BeautifulSoup(html_text, 'html.parser')

    # 找到ID为ulfieid1的<ul>标签
    ul_tag = soup.find('ul', id='ulfield1')

    # 从这个<ul>标签中提取所有的<a>标签
    a_tags = ul_tag.find_all('a') if ul_tag else []

    # 打印提取的<a>标签链接
    for a in a_tags:
        time_links.append("https://chinaxiv.org" + a["href"])
        print(f'URL: {a["href"]}')

    for tmp_link in time_links:
        dedup_set.add(tmp_link)
    
    return list(dedup_set)

def get_download_link(html_text):
    pdf_links = []

   
    soup = BeautifulSoup(html_text, 'html.parser')

    list_div = soup.find('div', class_='list')
    li_tags = list_div.find_all('li')
    
    for li in li_tags:
        pdf_dict = {}
        a_tag = li.find_all('a')
        download_links = ["https://chinaxiv.org" + a['href'] for a in a_tag if "下载全文" in a.text]

        h3_tags = li.find_all('h3')
        for h3_tag in h3_tags:
            title = h3_tag.text
        
        author_tags = li.find_all('div', class_='name')
        for author_tag in author_tags:
            author = author_tag.text
        
        pdf_dict['link'] = download_links
        pdf_dict['title'] = title
        pdf_dict['author'] = author
        
        pdf_links.append(pdf_dict)

    return pdf_links

def chinaxiv_empty(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')

    # 查找所有<span>标签
    span_tags = soup.find_all('span')

    # 判断是否存在符合条件的<span>标签
    found = any("没有查找" in span.text for span in span_tags)

    # 打印结果
    if found:
        return True
    else:
        return False

def get_start_url(html_text, raw_url):
    soup = BeautifulSoup(html_text, 'html.parser')

    # 查找所有class为"last"的<a>标签
    a_tags = soup.find_all('a', class_='last')

    # 从这些<a>标签中筛选出文本包含"尾页"的链接
    last_page_links = [a['href'] for a in a_tags if "尾页" in a.text]

    question_mark_index = raw_url.find('?')

    # 如果找到'?'，则替换它及其后面的内容；否则，直接附加新的查询字符串
    if question_mark_index != -1:
        # 替换原始URL中'?'及其后面的所有内容
        new_url = raw_url[:question_mark_index] + last_page_links[0]
    
    match = re.search(r'Page=(\d+)', new_url)

    # 检查是否找到匹配项并提取值
    last_page_value = match.group(1) if match else None
    
    new_current_page=0
    traverse_url = re.sub(r'(Page=)\d+', r'\g<1>{}'.format(new_current_page), new_url)
    return traverse_url, last_page_value

def traverse_category_link(url):
    pdf_links = []

    
    page_text = get_html_from_url(url)
    traverse_url, page_nums = get_start_url(page_text, url)
    match = re.search(r'pageId=(\d+)', traverse_url)
    if match:
        pageId = match.group(1)
    traverse_url = f'https://chinaxiv.org/user/search.htm?pageId={pageId}&setId=recordList&currentPage=0'
    page_nums = int(page_nums)
    for idx in range(page_nums):

        traverse_url = re.sub(r'(Page=)\d+', r'\g<1>{}'.format(idx), traverse_url)
        page_text = get_html_from_url(traverse_url)
        if not chinaxiv_empty(page_text):
            pdf_links += get_download_link(page_text)
            # pdf_links = list(set(pdf_links))
        else:
            return pdf_links
        
    return pdf_links

def save_stage_link_res(links, file_name):
    with open(f"{file_name}", "w") as f:
        for link in links:
            f.write(link+'\n')

def save_dict_res(file_name, pdf_res):
    # pdf_res = list(set(pdf_res))
    with jsonlines.open(f"{file_name}", "w") as writer:
        for item in pdf_res:
            writer.write(item)

if __name__ == "__main__":

    if os.path.exists("./chinaxiv_cate_link.jsonl"):
        cate_links = load_links("./chinaxiv_cate_link.jsonl")
    else:
        index = "https://chinaxiv.org/home.htm"
        html_text = get_html_from_url(index)
        cate_links = get_chinaxiv_category(html_text)
        save_dict_res("./chinaxiv_cate_link.jsonl", cate_links)

    time_links_files = os.listdir("./time_links")
    
    if len(time_links_files) != len(cate_links):
        for idx, link in enumerate(cate_links):
            html_text = get_html_from_url(link['link'])
            time_links = get_time_link(html_text)
            save_stage_link_res(time_links, f"./time_links/{link['cate']}.txt")

    
    crawl_list = segment_restart()
    print(crawl_list)

    for idx, file in tqdm(enumerate(crawl_list), total=len(crawl_list)):
        pdf_links = []
        time_links = load_links(f"./time_links/{file}.txt")

        #final
        for link in time_links:
            if link is None or len(link) < 5:
                break
            tmp = traverse_category_link(link)
            if tmp is not None:
                pdf_links += tmp
        save_dict_res(f"./pdf_links/{file}.jsonl", pdf_links)
        mark_finish(file, len(pdf_links))

