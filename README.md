# chinaxiv全量爬虫

一个简单的脚本实现chinaxiv网站全量论文数据爬虫。
爬虫规则为先按类别爬取，后根据时间遍历所有文章下载链接。并将下载链接保存至pdf_links文件夹中。

## 启动命令
```bash
python chinaixv_crawl.py # 链接爬取程序，若已有上一版本结果，需清空done, pdf_links, time_links这三个文件夹重新运行。

python downloader.py --num_shard={一个文件需要几个进程下载} --data_file=chinaxivCrawler_mnbvc/pdf_links/安全科学技术.jsonl --save_path={存放的文件夹}
```

## 输出格式
```json
{
    "link": ["..."],    //下载链接
    "title": "xxx",     //论文标题
    "author": "xxx"     //作者信息
}
```

## 文件结构

```
- chinaxiv
-- done                 # 爬虫已完成标识
-- pdf_links            # 每个类型的论文链接
-- time_links           # 爬虫中间结果，方便中间恢复
-- chinaixv_crawl.py    # 主函数
-- utils.py             # 一些小函数
-- downloader.py        # 对爬取到的论文链接进行下载
```

## 功能

- 全量爬虫；爬取chinaxiv的全量论文数据代码
- 断点恢复；爬取过程按类别为一进度，按类别断点恢复

## 结果预览
- 文件下载
![文件下载结果](/docs/downloading.png)

- 下载好的文件
![文件下载目录](/docs/saved_pdf.png)