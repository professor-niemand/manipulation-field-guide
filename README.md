# Manipulation Field Guide

A free, open field guide to recognising and defusing manipulation: how it works, how to spot it, and how to respond safely.

**Read it, download it and take the quiz:** https://professor-niemand.github.io/manipulation-field-guide/

## What is in this repository

| Path | What it is |
|---|---|
| `content/` | The guide, one Markdown file per page. **This is where you change wording.** |
| `site.yaml` | Site title, subtitle, contact email, quiz address, "Leave site" destination, and the optional Ko-fi link. |
| `changelog.yaml` | The list of updates. The top entry sets the version and "last updated" date shown on every page. |
| `templates/`, `static/` | Page layout, styling and the small script (theme button, search, quick exit, help filter). No tracking, no outside resources. |
| `build.py` | Turns all of the above into the website in `docs/`. |
| `docs/` | The finished site, served by GitHub Pages, plus the PDF and the quiz library (`.xlsx`). |
| `LICENSE` | Full text of CC BY-SA 4.0, which covers the guide and the quiz library. |
| `LICENSE-CODE` | MIT licence, which covers `build.py`, `templates/` and `static/`. |

## Licence

The guide and the quiz library are licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). You may share and adapt them, including commercially, if you credit them to professor-niemand and release your changes under the same licence. Quotations and cited research remain their authors' own. The site code is MIT (see `LICENSE-CODE`).

## About this guide

It is a teaching guide, not therapy, legal or professional advice. It was written with the help of AI models, and the "About" page says what was and was not checked. Helpline numbers should be confirmed before you rely on them.

## Found a mistake?

Email contentnobody@protonmail.com with a source and it will be corrected.

## Changing the site

One-time setup (installs three small libraries for your user only):

```
pip install --user markdown pyyaml jinja2
```

1. Edit the page in `content/`. Each technique starts with a heading such as `### 1.1.1 Gaslighting {#gaslighting}`. The part in braces is its permanent ID: do not change IDs, because links people have saved rely on them. Keep labels such as `**Protective Response:**` exactly as they are, since the site uses them to colour the boxes.
2. Add an entry at the top of `changelog.yaml` with the new version, the date and what changed.
3. Run `python3 build.py`. It rebuilds `docs/` and lists anything to check.
4. Commit and push. GitHub Pages republishes `docs/` within a few minutes.

The PDF and the quiz library in `docs/` are snapshots. If you change the text of a technique, update them too, and note it in `changelog.yaml`.
