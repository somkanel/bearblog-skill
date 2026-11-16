<div align="center">
  <h1>Bear Blog Skill</h1>
  <p><b>透過 AI 代理或輕量 Python 命令列管理 Bear Blog。</b></p>
  <p><a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a> · <b>繁體中文</b> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a></p>
  <p>
    <a href="https://github.com/somkanel/bearblog-skill/actions/workflows/checks.yml"><img src="https://github.com/somkanel/bearblog-skill/actions/workflows/checks.yml/badge.svg" alt="Checks"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="Python 3.9+"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License"></a>
  </p>
</div>

適用於 **Codex、Claude Code 與相容工具** 的 Agent Skill，內附可獨立使用的 [Bear Blog API](https://docs.bearblog.dev/api/) Python 用戶端。

- 建立、編輯、發佈、排程發佈及刪除文章或頁面。
- 更新首頁、導覽列、CSS 與 API 支援的部落格設定。
- 查詢草稿與排程文章、取得完整內文，匯出 API 可讀取的內容。

## 使用需求

需要 Python 3.9+、已升級的 Bear Blog，以及在 **後台 → Settings → API** 產生的金鑰。即使使用自訂網域，也請填寫原始 Bear 子網域。執行程式只需 Python 標準函式庫，支援 macOS 和 Linux。

## 安裝

使用 [Skills CLI](https://github.com/vercel-labs/skills)，需要 Node.js/npm 和 Git：

```bash
npx skills add somkanel/bearblog-skill --skill bearblog -a codex claude-code -g
```

`-a` 後只保留使用的代理工具名稱；移除 `-g` 可安裝至目前專案。安裝後開啟新對話。

<details>
<summary>手動安裝</summary>

```bash
git clone https://github.com/somkanel/bearblog-skill.git
```

複製儲存庫，將完整的 `skills/bearblog` 目錄複製到對應位置。取代既有技能前，請保留自訂修改。

| 代理工具 | 使用者技能目錄 |
| --- | --- |
| Codex | `~/.agents/skills/bearblog` |
| Claude Code | `~/.claude/skills/bearblog` |

</details>

## 設定

在終端機將 `SKILL_DIR` 設為實際安裝目錄。Codex 預設全域安裝可使用：

```bash
SKILL_DIR="$HOME/.agents/skills/bearblog"
python3 "$SKILL_DIR/scripts/bearblog.py" configure
python3 "$SKILL_DIR/scripts/bearblog.py" get-blog
```

Claude Code 使用 `~/.claude/skills/bearblog`；在儲存庫目錄中使用 `./skills/bearblog`。設定指令會詢問子網域，並以隱藏輸入讀取 API Key，儲存至 `~/.config/bearblog/config.json`，POSIX 權限為 `0600`。`get-blog` 只驗證存取權，不修改部落格。

自動化執行時，透過環境變數**同時提供** `BEARBLOG_API_KEY` 和 `BEARBLOG_SUBDOMAIN`，其優先順序高於設定檔。全域參數 `--config PATH` 可選擇其他設定檔。不要將金鑰放入提示詞、指令歷史或儲存庫。

## 使用

在 Codex 中：

```text
$bearblog 列出所有草稿與排程發佈的文章。
$bearblog 依照 ./article.md 建立草稿，並加上 notes 標籤。
$bearblog 將標題為「Hello」的草稿排程於 2027 年 12 月 1 日歐洲巴黎時間 09:00 發佈。
```

Claude Code 請將 `$bearblog` 改為 `/bearblog`。說明目標內容與預期修改，排程發佈時註明時區。搜尋與批次編輯由代理依序呼叫 API 完成。

## 組成

| 元件 | 用途 |
| --- | --- |
| [SKILL.md](skills/bearblog/SKILL.md) | 代理操作指引與路由 |
| [scripts/bearblog.py](skills/bearblog/scripts/bearblog.py) | 無第三方執行依賴的 API 用戶端與命令列 |
| [scripts/test_bearblog.py](skills/bearblog/scripts/test_bearblog.py) | 使用本機 HTTP 服務的離線測試 |
| [references/api.md](skills/bearblog/references/api.md) | 端點、欄位、分頁與限制 |
| [references/workflows.md](skills/bearblog/references/workflows.md) | 發佈、批次編輯、匯出與錯誤復原範例 |
| [agents/openai.yaml](skills/bearblog/agents/openai.yaml) | Codex 顯示資訊 |

## 獨立命令列

不透過代理也能使用相同用戶端。以下指令沿用前面設定的 `SKILL_DIR`。

```bash
python3 "$SKILL_DIR/scripts/bearblog.py" list-posts --status draft --all
python3 "$SKILL_DIR/scripts/bearblog.py" create-post --data draft.json
python3 "$SKILL_DIR/scripts/bearblog.py" export --output export.json
```

| 指令 | 用途 |
| --- | --- |
| `list-posts --all` | 列出文章，支援 `--status`、`--is-page`、`--page` 和 `--all` |
| `get-post UID` | 讀取單篇文章與內文 |
| `create-post --data draft.json` | 建立文章，預設為草稿 |
| `update-post UID --data patch.json` | 編輯、發佈或排程文章 |
| `delete-post UID` | 永久刪除文章或頁面 |
| `get-blog` | 讀取部落格設定 |
| `update-blog --data settings.json` | 只更新提交的設定欄位 |
| `export --output export.json` | 匯出設定與所有文章的完整內文 |

`draft.json` 範例：

```json
{"title":"Hello from Bear Blog","content":"A **Markdown** draft.","tags":["notes"]}
```

更新時只提交要修改的欄位。`--data -` 從標準輸入讀取 JSON。例如，`{"publish":true}` 發佈文章，`{"publish":false}` 轉為草稿。排程需要 `publish:true` 與含時區的未來 `published_date`。全部可寫入欄位請見 [API 參考](skills/bearblog/references/api.md)。

## 行為與限制

- 涵蓋官方文件的全部 7 個端點。新文章預設為草稿，修改與刪除使用固定的 `uid`。
- 清單每頁 20 筆且不含內文。匯出會逐篇取得詳細內容，不含媒體檔案，不是具一致性的快照，也沒有一鍵還原；既有匯出檔案不會被覆寫。
- 服務端限制每分鐘 60 次請求。每個用戶端實例控制請求間隔，429 最多重試兩次，遵守 `Retry-After`，累計自動等待最多 60 秒；多個程序需協調總速率。
- 網路錯誤或 5xx 後不自動重試寫入，應先重新讀取確認。請求僅傳送至官方 API 主機，並拒絕重新導向。
- 公開 API 沒有媒體上傳、統計或訂閱者端點。本機設定為明文，以檔案權限保護；JSON 匯出可能包含私人草稿。

## 開發

```bash
python3 -m unittest discover -s skills/bearblog/scripts -p 'test_*.py' -v
```

測試不需要 API Key，也不存取真實部落格。命令列說明與錯誤訊息使用英語。歡迎提供翻譯修正與問題回報。

## 授權

採用 [MIT](LICENSE) 授權。本專案獨立維護，與 Bear Blog 無隸屬關係。
