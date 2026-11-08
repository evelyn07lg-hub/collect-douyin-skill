# 配置与导出

先 setup 创建 WORK/config.json。需要配置时生成 UTF-8 JSON，再运行：

```text
python ROOT/scripts/collect.py --workspace WORK configure --settings /absolute/path/settings.json
```

以下为可选设置示例，文件路径必须替换为用户实际文件；不用的字段删除，不要将示例路径写入配置：

```json
{
  "browser": "chromium",
  "document_format": {
    "font": "宋体", "body_size": 10.5, "heading_size": 14,
    "line_spacing": 1, "article_gap": 10.5,
    "account_page_break": true, "inherit_existing": true
  },
  "word_export": {"base_document": "/absolute/path/existing.docx", "output_dir": "exports"},
  "proofreading": {"reference_path": "/absolute/path/reference.docx"},
  "collection": {"image_mode": "published_copy", "include_homepage_coauthored": true}
}
```

格式字号单位为pt；字体应为用户设备已安装字体。image_mode 可选 `published_copy`（发布文案）或 `ocr`（图片文字）。继承旧文档时默认继承正文样式，需要完全用新格式则 inherit_existing=false。基础文档生成新副本，保留原文件。

参考稿支持 `.docx`、UTF-8 `.txt` 和 `.md`。云参考库需要明确配置 reference_url/reference_title/reference_path，且先验证登录与下载来源；没有权限时不要随意替换参考库。自定义确认词可通过 proofreading.reviewed_replacements 与 asr_vocabulary 配置，结构沿用源码，不能未经确认全局替换词语。

configure 合并已有配置并备份；不要把本人账号或共享链接写进仓库模板。无需改变门槛或账号时不要重新 setup。
