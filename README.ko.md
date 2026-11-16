<div align="center">
  <h1>Bear Blog Skill</h1>
  <p><b>에이전트 또는 작은 Python CLI로 Bear Blog를 관리하세요.</b></p>
  <p><a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a> · <a href="README.ja.md">日本語</a> · <b>한국어</b> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a></p>
  <p>
    <a href="https://github.com/somkanel/bearblog-skill/actions/workflows/checks.yml"><img src="https://github.com/somkanel/bearblog-skill/actions/workflows/checks.yml/badge.svg" alt="Checks"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="Python 3.9+"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License"></a>
  </p>
</div>

**Codex, Claude Code 및 호환 도구**를 위한 Agent Skill입니다. [Bear Blog API](https://docs.bearblog.dev/api/)용 Python 클라이언트는 단독으로도 사용할 수 있습니다.

- 게시물과 페이지를 만들고 편집, 게시, 예약 게시, 삭제합니다.
- 홈페이지, 탐색 링크, CSS와 API가 지원하는 블로그 설정을 변경합니다.
- 초안과 예약 게시물을 조회하고 전체 본문 및 API로 읽을 수 있는 데이터를 내보냅니다.

## 요구 사항

Python 3.9+, 업그레이드된 Bear Blog, **대시보드 → Settings → API**에서 발급한 키가 필요합니다. 사용자 지정 도메인을 쓰더라도 원래 Bear 하위 도메인을 입력합니다. 실행 시 Python 표준 라이브러리만 사용하며 macOS와 Linux를 지원합니다.

## 설치

[Skills CLI](https://github.com/vercel-labs/skills)를 사용합니다. Node.js/npm과 Git이 필요합니다.

```bash
npx skills add somkanel/bearblog-skill --skill bearblog -a codex claude-code -g
```

`-a` 뒤에는 사용하는 에이전트만 남기세요. `-g`를 빼면 현재 프로젝트에 설치됩니다. 설치 후 새 대화를 여세요.

<details>
<summary>수동 설치</summary>

```bash
git clone https://github.com/somkanel/bearblog-skill.git
```

저장소를 복제하고 `skills/bearblog` 디렉터리 전체를 해당 위치에 복사하세요. 기존 스킬을 교체하기 전에 사용자 지정 내용을 보관하세요.

| 에이전트 | 사용자 스킬 디렉터리 |
| --- | --- |
| Codex | `~/.agents/skills/bearblog` |
| Claude Code | `~/.claude/skills/bearblog` |

</details>

## 설정

터미널에서 `SKILL_DIR`을 설치 경로로 설정합니다. Codex의 기본 전역 설치 예시:

```bash
SKILL_DIR="$HOME/.agents/skills/bearblog"
python3 "$SKILL_DIR/scripts/bearblog.py" configure
python3 "$SKILL_DIR/scripts/bearblog.py" get-blog
```

Claude Code는 `~/.claude/skills/bearblog`, 저장소 복제본에서는 `./skills/bearblog`를 사용합니다. 설정 명령은 하위 도메인과 화면에 표시되지 않는 API 키를 입력받아 `~/.config/bearblog/config.json`에 POSIX 권한 `0600`으로 저장합니다. `get-blog`는 블로그를 변경하지 않고 접근을 확인합니다.

자동화에서는 환경 변수 `BEARBLOG_API_KEY`와 `BEARBLOG_SUBDOMAIN`을 **모두** 제공하세요. 환경 변수가 설정 파일보다 우선합니다. 전역 옵션 `--config PATH`로 다른 파일을 선택할 수 있습니다. 키를 프롬프트, 셸 기록, 저장소에 넣지 마세요.

## 사용

Codex 예시:

```text
$bearblog 모든 초안과 예약 게시물을 나열해 줘.
$bearblog ./article.md로 초안을 만들고 notes 태그를 붙여 줘.
$bearblog 제목이 Hello인 초안을 2027년 12월 1일 09:00 Europe/Paris 시간으로 예약 게시해 줘.
```

Claude Code에서는 `$bearblog`를 `/bearblog`로 바꾸세요. 대상과 변경 내용을 설명하고 예약 게시 시 시간대를 지정하세요. 검색과 일괄 편집은 에이전트가 API를 순서대로 호출해 수행합니다.

## 구성

| 구성 요소 | 역할 |
| --- | --- |
| [SKILL.md](skills/bearblog/SKILL.md) | 에이전트 지침 및 작업 선택 |
| [scripts/bearblog.py](skills/bearblog/scripts/bearblog.py) | 외부 패키지 없이 실행하는 API 클라이언트와 CLI |
| [scripts/test_bearblog.py](skills/bearblog/scripts/test_bearblog.py) | 로컬 HTTP 서버를 사용하는 오프라인 테스트 |
| [references/api.md](skills/bearblog/references/api.md) | 엔드포인트, 필드, 페이지 나누기 및 제한 |
| [references/workflows.md](skills/bearblog/references/workflows.md) | 게시, 일괄 편집, 내보내기 및 복구 예시 |
| [agents/openai.yaml](skills/bearblog/agents/openai.yaml) | Codex 표시 메타데이터 |

## 독립 CLI

에이전트 없이도 같은 클라이언트를 사용할 수 있습니다. 아래 명령은 앞서 설정한 `SKILL_DIR`을 사용합니다.

```bash
python3 "$SKILL_DIR/scripts/bearblog.py" list-posts --status draft --all
python3 "$SKILL_DIR/scripts/bearblog.py" create-post --data draft.json
python3 "$SKILL_DIR/scripts/bearblog.py" export --output export.json
```

| 명령 | 작업 |
| --- | --- |
| `list-posts --all` | 게시물 목록. `--status`, `--is-page`, `--page`, `--all` 지원 |
| `get-post UID` | 본문을 포함한 게시물 조회 |
| `create-post --data draft.json` | 게시물 생성, 기본값은 초안 |
| `update-post UID --data patch.json` | 게시물 편집, 게시 또는 예약 |
| `delete-post UID` | 게시물이나 페이지 영구 삭제 |
| `get-blog` | 블로그 설정 조회 |
| `update-blog --data settings.json` | 제공한 설정만 변경 |
| `export --output export.json` | 설정과 모든 게시물의 전체 본문 내보내기 |

`draft.json` 예시:

```json
{"title":"Hello from Bear Blog","content":"A **Markdown** draft.","tags":["notes"]}
```

업데이트할 때는 바꿀 필드만 전달하세요. `--data -`는 표준 입력에서 JSON을 읽습니다. `{"publish":true}`로 게시하고 `{"publish":false}`로 초안으로 되돌립니다. 예약에는 `publish:true`와 시간대가 포함된 미래의 `published_date`가 필요합니다. 전체 필드는 [API 참조](skills/bearblog/references/api.md)를 확인하세요.

## 동작과 제한

- 문서에 명시된 7개 API 엔드포인트를 모두 지원합니다. 새 게시물은 기본적으로 초안이며, 편집과 삭제에는 변하지 않는 `uid`를 사용합니다.
- 목록은 페이지당 20개이며 본문이 없습니다. 내보내기는 개별 상세 조회로 본문을 가져옵니다. 미디어 파일, 일관된 스냅샷, 한 번의 명령으로 복원하는 기능은 포함하지 않습니다. 기존 파일은 덮어쓰지 않습니다.
- 서비스 제한은 분당 60회입니다. 클라이언트는 요청 간격을 두고 429 발생 시 `Retry-After`를 따라 최대 두 번 재시도합니다. 자동 대기는 총 60초까지입니다. 여러 프로세스의 합산 속도는 별도로 조정해야 합니다.
- 네트워크 실패나 5xx 이후 쓰기를 자동 재시도하지 않습니다. 먼저 다시 읽어 결과를 확인하세요. 공식 API 호스트로만 요청하며 리디렉션은 거부합니다.
- 공개 API에는 미디어 업로드, 분석, 구독자 엔드포인트가 없습니다. 로컬 설정은 파일 권한으로 보호되는 평문입니다. JSON 내보내기에는 비공개 초안이 포함될 수 있습니다.

## 개발

```bash
python3 -m unittest discover -s skills/bearblog/scripts -p 'test_*.py' -v
```

테스트에는 API 키가 필요 없고 실제 블로그에 접근하지 않습니다. CLI 도움말과 오류 메시지는 영어입니다. 번역 개선과 버그 제보를 환영합니다.

## 라이선스

[MIT](LICENSE). Bear Blog와 제휴하지 않은 독립 프로젝트입니다.
