import re
import os
import jsonlines

def mark_finish(file_name, total_num):
    with open(f"./done/{file_name}", "w") as f:
        f.write(str(total_num))
    return

def extract_text(input_str):
    """
    Extract and return the text inside and outside of parentheses.

    Parameters:
    - input_str: A string that includes text and parentheses.

    Returns:
    A tuple where the first element is a list of texts outside the parentheses,
    and the second element is a list of texts inside the parentheses.
    """

    pattern = re.compile(r'([^\(\)]+)(?:\((\d+)\))')
    match = pattern.search(input_str)
    
    text, number = match.groups()

    return text, number

def load_links(file_name):
    links = []
    if 'jsonl' in file_name:
        with jsonlines.open(f"{file_name}", "r") as reader:
            for item in reader:
                links.append(item)
    else:
        with open(f"./{file_name}", "r") as f:
            tmp = f.readlines()
        for t in tmp:
            links.append(t.replace('\n', ''))
    return links


def segment_restart():
    done_list = os.listdir('./done')

    category_dict = load_links('./chinaxiv_cate_link.jsonl')
    category_list = [item['cate'] for item in category_dict]
    restart_list = list(set(category_list) - set(done_list))

    return restart_list

