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

## 文件结构

```
- chinaxiv
-- done                 # 爬虫已完成标识
-- pdf_links            # 每个类型的论文链接
-- time_links           # 爬虫中间结果，方便中间恢复
-- chinaixv_crawl.py    # 主函数
-- utils.py             # 一些小函数
```

## 功能

- 全量爬虫；爬取chinaxiv的全量论文数据代码
- 断点恢复；爬取过程按类别为一进度，按类别断点恢复