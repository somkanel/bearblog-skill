<div align="center">
  <h1>Bear Blog Skill</h1>
  <p><b>エージェントや小さなPython CLIでBear Blogを管理。</b></p>
  <p><a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a> · <b>日本語</b> · <a href="README.ko.md">한국어</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a></p>
  <p>
    <a href="https://github.com/somkanel/bearblog-skill/actions/workflows/checks.yml"><img src="https://github.com/somkanel/bearblog-skill/actions/workflows/checks.yml/badge.svg" alt="Checks"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="Python 3.9+"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License"></a>
  </p>
</div>

**Codex、Claude Code、および互換ツール**向けのAgent Skill。[Bear Blog API](https://docs.bearblog.dev/api/) 用のPythonクライアントは単独でも使えます。

- 記事やページの作成、編集、公開、予約公開、削除。
- ホームページ、ナビゲーション、CSS、対応するブログ設定の更新。
- 下書きや予約記事の一覧、本文の取得、APIで取得可能なデータのエクスポート。

## 必要なもの

Python 3.9+、アップグレード済みのBear Blog、**管理画面 → Settings → API** で発行したAPIキーが必要です。独自ドメインを使っていても、元のBearサブドメインを指定します。実行時はPython標準ライブラリのみを使い、macOSとLinuxに対応します。

## インストール

[Skills CLI](https://github.com/vercel-labs/skills) を使います。Node.js/npmとGitが必要です。

```bash
npx skills add somkanel/bearblog-skill --skill bearblog -a codex claude-code -g
```

`-a` の後には使用するエージェントだけを指定します。`-g` を省くとプロジェクト内にインストールします。完了後に新しい会話を開いてください。

<details>
<summary>手動インストール</summary>

```bash
git clone https://github.com/somkanel/bearblog-skill.git
```

リポジトリをクローンし、`skills/bearblog` ディレクトリ全体を対応する場所にコピーします。既存のスキルを置き換える前に、独自の変更を保存してください。

| エージェント | ユーザー用スキルディレクトリ |
| --- | --- |
| Codex | `~/.agents/skills/bearblog` |
| Claude Code | `~/.claude/skills/bearblog` |

</details>

## 設定

ターミナルで `SKILL_DIR` にインストール先を設定します。Codexの標準的なグローバルインストールの場合：

```bash
SKILL_DIR="$HOME/.agents/skills/bearblog"
python3 "$SKILL_DIR/scripts/bearblog.py" configure
python3 "$SKILL_DIR/scripts/bearblog.py" get-blog
```

Claude Codeでは `~/.claude/skills/bearblog`、クローンしたリポジトリ内では `./skills/bearblog` を指定します。設定コマンドはサブドメインと非表示入力のAPIキーを受け取り、`~/.config/bearblog/config.json` にPOSIX権限 `0600` で保存します。`get-blog` はブログを変更せずに接続を確認します。

自動実行では、環境変数 `BEARBLOG_API_KEY` と `BEARBLOG_SUBDOMAIN` を**両方**設定します。環境変数は設定ファイルより優先されます。グローバル引数 `--config PATH` で別のファイルを指定できます。キーをプロンプト、シェル履歴、リポジトリに残さないでください。

## 使い方

Codexの例：

```text
$bearblog 下書きと予約公開の記事をすべて一覧表示して。
$bearblog ./article.md から下書きを作成し、notes タグを付けて。
$bearblog 「Hello」という下書きを 2027 年 12 月 1 日 09:00、Europe/Paris の時刻で予約公開して。
```

Claude Codeでは `$bearblog` を `/bearblog` に置き換えます。対象と変更内容を伝え、予約時にはタイムゾーンを指定します。検索や一括編集は、エージェントがAPIを順番に呼び出して行います。

## 構成

| 構成要素 | 役割 |
| --- | --- |
| [SKILL.md](skills/bearblog/SKILL.md) | エージェント向けの指示と操作の選択 |
| [scripts/bearblog.py](skills/bearblog/scripts/bearblog.py) | 外部パッケージ不要のAPIクライアントとCLI |
| [scripts/test_bearblog.py](skills/bearblog/scripts/test_bearblog.py) | ローカルHTTPサーバーによるオフラインテスト |
| [references/api.md](skills/bearblog/references/api.md) | エンドポイント、フィールド、ページ分割、制限 |
| [references/workflows.md](skills/bearblog/references/workflows.md) | 公開、一括編集、エクスポート、復旧の例 |
| [agents/openai.yaml](skills/bearblog/agents/openai.yaml) | Codexの表示メタデータ |

## 単独のCLI

エージェントなしでも同じクライアントを使えます。以下では設定済みの `SKILL_DIR` を使います。

```bash
python3 "$SKILL_DIR/scripts/bearblog.py" list-posts --status draft --all
python3 "$SKILL_DIR/scripts/bearblog.py" create-post --data draft.json
python3 "$SKILL_DIR/scripts/bearblog.py" export --output export.json
```

| コマンド | 操作 |
| --- | --- |
| `list-posts --all` | 記事一覧。`--status`、`--is-page`、`--page`、`--all` に対応 |
| `get-post UID` | 本文を含む記事の取得 |
| `create-post --data draft.json` | 記事の作成。既定は下書き |
| `update-post UID --data patch.json` | 記事の編集、公開、予約公開 |
| `delete-post UID` | 記事やページの完全削除 |
| `get-blog` | ブログ設定の取得 |
| `update-blog --data settings.json` | 指定した設定のみ更新 |
| `export --output export.json` | 設定と全記事の本文をエクスポート |

`draft.json` の例：

```json
{"title":"Hello from Bear Blog","content":"A **Markdown** draft.","tags":["notes"]}
```

更新時は変更するフィールドだけを渡します。`--data -` は標準入力からJSONを読み取ります。`{"publish":true}` で公開し、`{"publish":false}` で下書きに戻します。予約公開には `publish:true` とタイムゾーン付きの未来の `published_date` が必要です。全フィールドは [APIリファレンス](skills/bearblog/references/api.md) を参照してください。

## 動作と制限

- 公式文書の 7 つのエンドポイントをすべてカバーします。新規記事の既定は下書きで、編集や削除には変わらない `uid` を使います。
- 一覧は 1 ページ 20 件で本文を含みません。エクスポートは記事ごとに本文を取得します。メディアファイル、一貫したスナップショット、ワンコマンド復元は含まれません。既存ファイルは上書きしません。
- サービスの上限は毎分 60 リクエストです。クライアントは送信間隔を空け、429 は `Retry-After` に従い最大 2 回再試行します。自動待機は合計 60 秒までです。複数プロセスでは合計レートの調整が必要です。
- 通信失敗や 5xxの後に書き込みを自動再試行しません。先に読み戻して確認してください。送信先は公式APIホストに限定し、リダイレクトを拒否します。
- 公開APIにメディアアップロード、解析、購読者用のエンドポイントはありません。設定はファイル権限で保護した平文です。JSONエクスポートには非公開の下書きが含まれることがあります。

## 開発

```bash
python3 -m unittest discover -s skills/bearblog/scripts -p 'test_*.py' -v
```

テストにAPIキーは不要で、実際のブログにはアクセスしません。CLIのヘルプとエラーは英語です。翻訳の修正や不具合報告を歓迎します。

## ライセンス

[MIT](LICENSE)。Bear Blogとは提携していない独立したプロジェクトです。
