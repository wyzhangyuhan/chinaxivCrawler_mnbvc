# chinaxiv全量爬虫

一个简单的脚本实现chinaxiv网站全量论文数据爬虫。
爬虫规则为先按类别爬取，后根据时间遍历所有文章下载链接。并将下载链接保存至pdf_links文件夹中。

## 启动命令
```bash
python chinaixv_crawl.py
```

## 输出格式
```json
{
    "link": ["..."],    //下载链接
    "title": "xxx",     //论文标题
    "author": "xxx"     //作者信息
}
```