<div align="center">
  <h1>🍯 Bear Blog Skill</h1>
  <p><b>通过智能体或轻量 Python 命令行管理 Bear Blog。</b></p>
  <p><a href="README.md">English</a> · <b>简体中文</b> · <a href="README.zh-TW.md">繁體中文</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a></p>
  <p>
    <a href="https://docs.bearblog.dev/api/"><img src="https://img.shields.io/badge/API-official-green" alt="Official Bear Blog API"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="Python 3.9+"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License"></a>
  </p>
</div>

面向 **Codex、Claude Code 及兼容工具** 的 Agent Skill，内置可独立使用的 [Bear Blog API](https://docs.bearblog.dev/api/) Python 客户端。

本项目仅使用 [Bear Blog 官方公开 API](https://docs.bearblog.dev/api/)，不使用私有协议、未公开接口或非官方平台能力。搜索与批量编辑通过组合官方接口完成。

- 创建、编辑、发布、定时发布和删除文章或页面。
- 更新首页、导航、CSS 及 API 支持的博客设置。
- 查询草稿与定时文章，获取完整正文，导出 API 可读内容。

## 使用条件

需要 Python 3.9+ 和 **Bear Blog 付费方案**。**只有付费博客才能生成 API Key**，入口为 **后台 → Settings → API**。即使使用自定义域名，也填写原始 Bear 子域名。运行脚本只依赖 Python 标准库，支持 macOS 和 Linux。

## 安装

使用 [Skills CLI](https://github.com/vercel-labs/skills)，需要 Node.js/npm 和 Git：

```bash
npx skills add somkanel/bearblog-skill --skill bearblog -a codex claude-code -g
```

`-a` 后只保留使用的智能体名称；去掉 `-g` 可安装到当前项目。安装后开启新会话。

<details>
<summary>手动安装</summary>

```bash
git clone https://github.com/somkanel/bearblog-skill.git
```

克隆仓库，将完整的 `skills/bearblog` 目录复制到对应位置。替换已有技能前，先保留自定义修改。

| 智能体 | 用户级技能目录 |
| --- | --- |
| Codex | `~/.agents/skills/bearblog` |
| Claude Code | `~/.claude/skills/bearblog` |

</details>

## 配置

在终端中将 `SKILL_DIR` 设置为实际安装目录。Codex 默认全局安装可使用：

```bash
SKILL_DIR="$HOME/.agents/skills/bearblog"
python3 "$SKILL_DIR/scripts/bearblog.py" configure
python3 "$SKILL_DIR/scripts/bearblog.py" get-blog
```

Claude Code 使用 `~/.claude/skills/bearblog`；在仓库克隆目录中使用 `./skills/bearblog`。配置命令询问子域名，并隐藏输入 API Key，随后保存到 `~/.config/bearblog/config.json`，POSIX 权限为 `0600`。`get-blog` 只验证访问，不修改博客。

自动化运行时，通过环境变量**同时提供** `BEARBLOG_API_KEY` 和 `BEARBLOG_SUBDOMAIN`，优先级高于配置文件。全局参数 `--config PATH` 可选择其他配置。不要把密钥放进提示词、命令历史或仓库。

## 使用

在 Codex 中：

```text
$bearblog 列出全部草稿和定时发布的文章。
$bearblog 根据 ./article.md 创建草稿，并添加 notes 标签。
$bearblog 将标题为“Hello”的草稿安排在 2027 年 12 月 1 日欧洲巴黎时间 09:00 发布。
```

Claude Code 将 `$bearblog` 替换为 `/bearblog`。说明目标内容和预期改动，定时发布时注明时区。搜索和批量编辑由智能体顺序调用接口完成。

## 组成

| 组件 | 用途 |
| --- | --- |
| [SKILL.md](skills/bearblog/SKILL.md) | 智能体指引和操作路由 |
| [scripts/bearblog.py](skills/bearblog/scripts/bearblog.py) | 无第三方运行依赖的 API 客户端与命令行 |
| [scripts/test_bearblog.py](skills/bearblog/scripts/test_bearblog.py) | 使用本地 HTTP 服务的离线测试 |
| [references/api.md](skills/bearblog/references/api.md) | 接口、字段、分页与限制 |
| [references/workflows.md](skills/bearblog/references/workflows.md) | 发布、批量编辑、导出和故障恢复示例 |
| [agents/openai.yaml](skills/bearblog/agents/openai.yaml) | Codex 展示信息 |

## 独立命令行

不使用智能体也能运行同一客户端。以下命令沿用前面设置的 `SKILL_DIR`。

```bash
python3 "$SKILL_DIR/scripts/bearblog.py" list-posts --status draft --all
python3 "$SKILL_DIR/scripts/bearblog.py" create-post --data draft.json
python3 "$SKILL_DIR/scripts/bearblog.py" export --output export.json
```

| 命令 | 用途 |
| --- | --- |
| `list-posts --all` | 列出文章，支持 `--status`、`--is-page`、`--page` 和 `--all` |
| `get-post UID` | 读取单篇文章及正文 |
| `create-post --data draft.json` | 创建文章，默认为草稿 |
| `update-post UID --data patch.json` | 编辑、发布或定时发布文章 |
| `delete-post UID` | 永久删除文章或页面 |
| `get-blog` | 读取博客设置 |
| `update-blog --data settings.json` | 只修改提交的设置字段 |
| `export --output export.json` | 导出设置及全部文章的完整正文 |

`draft.json` 示例：

```json
{"title":"Hello from Bear Blog","content":"A **Markdown** draft.","tags":["notes"]}
```

更新时只提交需要修改的字段。`--data -` 从标准输入读取 JSON。例如，`{"publish":true}` 发布文章，`{"publish":false}` 转为草稿。定时发布需要 `publish:true` 和带时区的未来 `published_date`。全部可写字段见 [API 参考](skills/bearblog/references/api.md)。

## 行为与限制

- 覆盖官方文档的全部 7 个接口。新文章默认为草稿，修改与删除使用稳定的 `uid`。
- 列表每页 20 条且不含正文。导出会逐篇获取详情，不包含媒体文件，不是一致性快照，也没有一键恢复；已有导出文件不会被覆盖。
- 服务端限制为每分钟 60 次请求。每个客户端实例控制请求间隔，429 最多重试两次，遵守 `Retry-After`，累计自动等待不超过 60 秒；跨进程需协调总速率。
- 网络失败或 5xx 后不自动重试写入，应先读回核对。请求发送至官方 API 主机，并拒绝重定向。
- 公开 API 没有媒体上传、统计或订阅者接口。本地配置为明文，由文件权限保护；JSON 导出可能包含私人草稿。

## 开发

```bash
python3 -m unittest discover -s skills/bearblog/scripts -p 'test_*.py' -v
```

测试无需 API Key，也不访问真实博客。命令行帮助与错误消息使用英语。欢迎提交翻译改进和问题反馈。

## 许可

采用 [MIT](LICENSE) 许可。本项目独立维护，与 Bear Blog 无隶属关系。
