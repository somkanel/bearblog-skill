<div align="center">
  <h1>Bear Blog Skill</h1>
  <p><b>Gérez Bear Blog avec un agent ou un petit outil Python en ligne de commande.</b></p>
  <p><a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.es.md">Español</a> · <b>Français</b> · <a href="README.de.md">Deutsch</a></p>
  <p>
    <a href="https://github.com/somkanel/bearblog-skill/actions/workflows/checks.yml"><img src="https://github.com/somkanel/bearblog-skill/actions/workflows/checks.yml/badge.svg" alt="Checks"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="Python 3.9+"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License"></a>
  </p>
</div>

Un Agent Skill pour **Codex, Claude Code et les outils compatibles**, avec un client Python autonome pour l’[API Bear Blog](https://docs.bearblog.dev/api/).

- Créez, modifiez, publiez, programmez et supprimez des articles ou des pages.
- Mettez à jour l’accueil, la navigation, le CSS et les paramètres pris en charge.
- Consultez les brouillons et publications programmées, récupérez le texte intégral et exportez les données accessibles par l’API.

## Prérequis

Python 3.9+, un blog Bear avec une offre payante et une clé générée dans **tableau de bord → Settings → API**. Utilisez le sous-domaine Bear d’origine, même avec un domaine personnalisé. Les scripts utilisent uniquement la bibliothèque standard de Python et prennent en charge macOS et Linux.

## Installation

Avec [Skills CLI](https://github.com/vercel-labs/skills), Node.js/npm et Git :

```bash
npx skills add somkanel/bearblog-skill --skill bearblog -a codex claude-code -g
```

Après `-a`, conservez uniquement l’agent utilisé. Omettez `-g` pour une installation dans le projet. Ouvrez une nouvelle conversation après l’installation.

<details>
<summary>Installation manuelle</summary>

```bash
git clone https://github.com/somkanel/bearblog-skill.git
```

Clonez le dépôt et copiez le dossier complet `skills/bearblog` à l’emplacement approprié. Conservez vos personnalisations avant de remplacer une installation existante.

| Agent | Dossier des compétences utilisateur |
| --- | --- |
| Codex | `~/.agents/skills/bearblog` |
| Claude Code | `~/.claude/skills/bearblog` |

</details>

## Configuration

Dans un terminal, définissez `SKILL_DIR` avec le chemin d’installation. Pour une installation globale par défaut de Codex :

```bash
SKILL_DIR="$HOME/.agents/skills/bearblog"
python3 "$SKILL_DIR/scripts/bearblog.py" configure
python3 "$SKILL_DIR/scripts/bearblog.py" get-blog
```

Pour Claude Code, utilisez `~/.claude/skills/bearblog` ; dans un clone du dépôt, utilisez `./skills/bearblog`. La commande demande le sous-domaine et une clé saisie de façon masquée, puis enregistre `~/.config/bearblog/config.json` avec les droits POSIX `0600`. `get-blog` vérifie l’accès sans modifier le blog.

Pour l’automatisation, fournissez **les deux** variables `BEARBLOG_API_KEY` et `BEARBLOG_SUBDOMAIN` dans l’environnement. Elles sont prioritaires sur le fichier de configuration. L’option globale `--config PATH` sélectionne un autre fichier. Ne placez pas de clé dans les instructions à l’agent, l’historique du shell ou le dépôt.

## Utilisation

Dans Codex :

```text
$bearblog Liste tous les brouillons et les articles programmés.
$bearblog Crée un brouillon à partir de ./article.md avec le tag notes.
$bearblog Programme le brouillon intitulé Hello pour le 1er décembre 2027 à 09:00 Europe/Paris.
```

Dans Claude Code, remplacez `$bearblog` par `/bearblog`. Précisez le contenu, les modifications et le fuseau horaire pour une publication programmée. L’agent effectue les recherches et modifications par lots avec des appels séquentiels à l’API.

## Composants

| Composant | Rôle |
| --- | --- |
| [SKILL.md](skills/bearblog/SKILL.md) | Instructions de l’agent et choix des opérations |
| [scripts/bearblog.py](skills/bearblog/scripts/bearblog.py) | Client API et CLI sans dépendances externes |
| [scripts/test_bearblog.py](skills/bearblog/scripts/test_bearblog.py) | Tests hors ligne avec un serveur HTTP local |
| [references/api.md](skills/bearblog/references/api.md) | Points d’accès, champs, pagination et limites |
| [references/workflows.md](skills/bearblog/references/workflows.md) | Exemples de publication, modification par lots, export et reprise |
| [agents/openai.yaml](skills/bearblog/agents/openai.yaml) | Métadonnées d’affichage de Codex |

## CLI autonome

Le même client fonctionne sans agent. Utilisez le `SKILL_DIR` défini plus haut.

```bash
python3 "$SKILL_DIR/scripts/bearblog.py" list-posts --status draft --all
python3 "$SKILL_DIR/scripts/bearblog.py" create-post --data draft.json
python3 "$SKILL_DIR/scripts/bearblog.py" export --output export.json
```

| Commande | Action |
| --- | --- |
| `list-posts --all` | Liste les articles ; accepte `--status`, `--is-page`, `--page` et `--all` |
| `get-post UID` | Récupère un article et son contenu |
| `create-post --data draft.json` | Crée un brouillon par défaut |
| `update-post UID --data patch.json` | Modifie, publie ou programme un article |
| `delete-post UID` | Supprime définitivement un article ou une page |
| `get-blog` | Lit les paramètres du blog |
| `update-blog --data settings.json` | Met à jour uniquement les paramètres fournis |
| `export --output export.json` | Exporte les paramètres et le contenu intégral de tous les articles |

Exemple de `draft.json` :

```json
{"title":"Hello from Bear Blog","content":"A **Markdown** draft.","tags":["notes"]}
```

Pour une mise à jour, transmettez uniquement les champs à modifier. `--data -` lit le JSON sur l’entrée standard. `{"publish":true}` publie et `{"publish":false}` remet en brouillon. La programmation exige `publish:true` et un `published_date` futur avec fuseau horaire. Consultez les champs dans la [référence API](skills/bearblog/references/api.md).

## Comportement et limites

- Couvre les sept points d’accès documentés. Les nouveaux articles sont des brouillons par défaut ; utilisez l’`uid` stable pour modifier ou supprimer.
- Les listes contiennent 20 éléments par page, sans leur contenu. L’export lit chaque article, omet les fichiers multimédias et ne constitue ni un instantané cohérent ni une restauration en une commande. Les fichiers existants ne sont pas écrasés.
- Le service autorise 60 requêtes par minute. Chaque client espace les requêtes et réessaie les réponses 429 au maximum deux fois, selon `Retry-After`, dans une limite de 60 secondes d’attente cumulée. Coordonnez le débit entre processus.
- Les écritures ne sont pas relancées automatiquement après une erreur réseau ou une réponse 5xx. Relisez le résultat avant de réessayer. Seul l’hôte officiel de l’API est utilisé ; les redirections sont refusées.
- L’API documentée ne propose pas d’envoi de médias, de statistiques ou de gestion des abonnés. La configuration locale est en clair, protégée par les droits d’accès. Les exports JSON peuvent contenir des brouillons privés.

## Développement

```bash
python3 -m unittest discover -s skills/bearblog/scripts -p 'test_*.py' -v
```

Les tests ne nécessitent aucune clé et n’accèdent pas aux blogs réels. L’aide et les erreurs de la CLI sont en anglais. Les corrections de traduction et signalements de bugs sont les bienvenus.

## Licence

[MIT](LICENSE). Projet indépendant, sans affiliation avec Bear Blog.
