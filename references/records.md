# 校订正文记录

`export-word --input FILE` 接受 JSON 数组，最小示例：

```json
[
  {
    "account_id": "douyin-public:example",
    "account_name": "示例博主",
    "id": "example-work-id",
    "url": "https://www.douyin.com/video/example-work-id",
    "type": "video",
    "published_at": "2026-01-01",
    "likes": 501,
    "comments": 20,
    "favorites": 30,
    "shares": 10,
    "title": "示例标题",
    "body": "这里填写基于实际来源核对的完整正文。",
    "recognition_review": "machine_unreviewed"
  }
]
```

示例作品ID只是占位符，不能用于真实采集。已人工确认的正文也不要伪装成脚本自动审核；在交付说明中报告真实复核范围。未知统计用 null，点赞尚未核验的作品不得混进达标清单。缩写点赞需保留 likes_display 与 likes_exact=false，不能虚构精确数。

原数据在 WORK/data/collect.sqlite3；脚本 videos 输出状态和载荷，Service/Store 可按参数化查询读取完整记录。校订记录应保留 account_id、id、来源、原始证据，并备份旧正文。按用户日期筛选 published_at 后再导出数组。提供JSON只生成新文档，不会自动覆盖数据库或线上文档。
