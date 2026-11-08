# 运行与兼容性

Skill 根目录包含 `SKILL.md`、`scripts/`、`src/`、`config.example.json`，安装时必须保留整个目录。仅复制说明文件不能运行采集。

## 宿主能力

| 宿主条件 | 能完成的工作 |
| --- | --- |
| 支持 Skill 发现、Python、文件读写、可见浏览器 | 按完整流程执行 |
| 不识别 Skill 格式，但支持读取仓库、运行程序和浏览器 | 读取根目录 SKILL.md 后执行同一流程 |
| 只能上传文件、没有浏览器或本地执行 | 在现有能力内处理上传素材；不能凭仓库链接安装采集工具 |
| 无图形显示的远程服务器 | 可以导出已有稿件；实采需要可供用户验证的浏览器环境 |

不以助手品牌判断能力，不承诺所有产品版本都支持一键安装。豆包、DeepSeek 等普通聊天入口能否执行，取决于具体客户端是否开放本地工具。

## 启动命令

Windows 通常用 `python`，macOS/Linux 通常用 `python3`。推荐 Python 3.12，程序要求3.10以上。命令中的 ROOT/WORK/URL/N 是占位符，需替换为真实路径和参数，勿原样运行。

```text
python ROOT/scripts/collect.py capabilities
python ROOT/scripts/collect.py bootstrap --dry-run
python ROOT/scripts/collect.py bootstrap --models --browser chromium
```

bootstrap 仅补充缺失的依赖；环境不完整时创建仓库 `.venv`，不修改全局包。输出 `result.python` 是后续使用的解释器；不要改回另一个未安装依赖的 Python。浏览器与模型下载需要网络，已有文件可复用。可选 `--model large-v3-turbo`，较大模型更耗资源，先让用户知情。

Chromium 由 Playwright 准备；Chrome/Edge 使用用户已安装的浏览器。Linux 可能还缺浏览器系统库，按 Playwright 的明确错误处理，不自动执行需要系统权限的安装。Mac 环境已做代码适配，但尚未在真实 Mac 上完成端到端采集验证，不宣称所有芯片和系统版本都已支持。

```text
python ROOT/scripts/collect.py --workspace WORK setup --profile URL --min-likes 500 --browser chromium
python ROOT/scripts/collect.py --workspace WORK login
python ROOT/scripts/collect.py --workspace WORK organize
python ROOT/scripts/collect.py --workspace WORK status
python ROOT/scripts/collect.py --workspace WORK videos
python ROOT/scripts/collect.py --workspace WORK browser-backfill --max-scrolls 30 --max-details 100
python ROOT/scripts/collect.py --workspace WORK process --retry
python ROOT/scripts/collect.py --workspace WORK export-word
```

重复账号用多个 `--profile` 参数，严格大于加 `--strict`。工作目录保存 config.json、data、exports；模型保存在 Skill 根目录的 models，准备后配置记录绝对路径。默认生成 `.docx`，不安装或启动 WPS/Word。

login 需要交互式终端；等待用户手动完成登录，不能自动提交验证码。无法提供可见浏览器时请说明阻碍，不用无头模式假装完成登录。
