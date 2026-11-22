#!/usr/bin/env python3
"""Build the Manipulation Field Guide website.

Usage:  python3 build.py
Needs:  pip install --user markdown pyyaml jinja2
Input:  site.yaml, changelog.yaml, content/*.md, templates/, static/
Output: docs/  (GitHub Pages serves this folder; other files in docs/ are left alone)
"""
import re, sys, shutil, urllib.parse
from pathlib import Path
import markdown, yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"
OUT.mkdir(exist_ok=True)
warnings = []

site = yaml.safe_load((ROOT / "site.yaml").read_text(encoding="utf-8"))
changelog = yaml.safe_load((ROOT / "changelog.yaml").read_text(encoding="utf-8"))
latest = changelog[0]
fmt = lambda d: f"{d.day} {d.strftime('%B %Y')}"
VERSION, UPDATED = str(latest["version"]), fmt(latest["date"])
for e in changelog: e["date_text"] = fmt(e["date"])
for k in ("contact_email", "exit_url", "quiz_url", "repo_url"):
    if not (site.get(k) or "").strip(): warnings.append(f"site.yaml: {k} is empty")
KOFI = (site.get("kofi_url") or "").strip()

env = Environment(loader=FileSystemLoader(str(ROOT / "templates")), autoescape=select_autoescape(["html"]))
env.filters["urlencode"] = lambda s: urllib.parse.quote(str(s), safe="")

def new_md():
    return markdown.Markdown(extensions=["extra", "sane_lists", "toc"], extension_configs={"toc": {"permalink": False}})

def slug(s):
    s = re.sub(r"\([^)]*\)", "", s).lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def tokens(t):
    for k, v in {"%%QUIZ_URL%%": site["quiz_url"], "%%PDF%%": site["pdf_file"], "%%XLSX%%": site["xlsx_file"],
                 "%%AUTHOR%%": site["author"], "%%REPO_URL%%": site["repo_url"], "%%KOFI%%": KOFI,
                 "%%VERSION%%": VERSION, "%%UPDATED%%": UPDATED}.items():
        t = t.replace(k, v)
    return t

# ---- help topics (for cross-links) ----
help_md = (ROOT / "content" / "get-help.md").read_text(encoding="utf-8")
HELP = {m.group(1): m.group(2) for m in re.finditer(r"^## (.*?) \{#([a-z0-9-]+)\}", help_md, re.M)}

def linkify_help(t):
    def see(m):
        parts = [p.strip() for p in m.group(1).split(",")]
        out = []
        for p in parts:
            if p in HELP: out.append(f"[{p}](get-help.html#{HELP[p]})")
            else: warnings.append(f"unknown help topic in a Caution: {p}"); out.append(p)
        return "See [Where to get help](get-help.html): " + ", ".join(out) + "."
    t = re.sub(r"See “Where to get help”: ([^\n]*?)\.(?=\s|$)", see, t)
    t = re.sub(r"(?<!\[)“Where to get help”", "[“Where to get help”](get-help.html)", t)
    return t

def read_page(name):
    raw = (ROOT / "content" / name).read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    if not m: sys.exit(f"{name}: missing front matter")
    return yaml.safe_load(m.group(1)), tokens(linkify_help(m.group(2)))

def inline(md, s):
    h = md.convert(s); md.reset()
    return re.sub(r"^<p>(.*)</p>$", r"\1", h.strip(), flags=re.S)

def plain(s):
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    return re.sub(r"[*_`]", "", s)

def first_sentence(s, n=135):
    s = plain(s).strip()
    m = re.match(r"(.+?[.!?])(\s|$)", s)
    out = m.group(1) if m else s
    if len(out) > n: out = out[:n].rsplit(" ", 1)[0].rstrip(",;:—-") + "…"
    return out

# ---- techniques ----
LABELS = [(r"Definition", "def"), (r"Variants", "var"), (r"Example(?: \([^)]*\))?", "eg"),
          (r"Protective Response", "resp"), (r"What helps", "resp"), (r"Reflection prompts", "refl"),
          (r"Caution", "caution"), (r"Did you know\?", "dyk")]
LABEL_RE = re.compile(r"^\*{2,3}(" + "|".join(l for l, _ in LABELS) + r"):?\*{2,3}\s*(.*)$", re.S)

def parse_techniques(text):
    md = new_md()
    cats, cat, grp, tech, buf = [], None, None, None, []
    intro_lines = []
    def flush():
        nonlocal buf
        body = "\n".join(buf).strip(); buf = []
        if not body: return
        if tech is not None:
            for para in re.split(r"\n\s*\n", body):
                para = para.strip()
                m = LABEL_RE.match(para)
                if not m:
                    warnings.append(f"technique {tech['name']}: paragraph without label: {para[:40]}"); continue
                label, rest = m.group(1), m.group(2)
                cls = next(c for l, c in LABELS if re.fullmatch(l, label))
                tech["blocks"].append({"label": label if label.endswith("?") else label + ":", "cls": cls, "raw": rest, "html": inline(md, rest)})
        elif grp is not None: grp["intro"].append(body)
        elif cat is not None: cat["intro"].append(body)
        else: intro_lines.append(body)
    for line in text.split("\n"):
        m1 = re.match(r"^# (\d) (.*)$", line); m2 = re.match(r"^## (\d\.\d) (.*)$", line)
        m3 = re.match(r"^### (\d\.\d\.\d) (.*?) \{#([a-z0-9-]+)\}$", line)
        if m1:
            flush(); tech = grp = None
            cat = {"num": int(m1.group(1)), "title": m1.group(2), "intro": [], "groups": []}; cats.append(cat)
        elif m2:
            flush(); tech = None
            grp = {"title": m2.group(2), "intro": [], "techniques": []}; cat["groups"].append(grp)
        elif m3:
            flush()
            tech = {"number": m3.group(1), "name": m3.group(2), "id": m3.group(3), "blocks": [], "cat": cat["num"]}
            grp["techniques"].append(tech)
        else: buf.append(line)
    flush()
    for c in cats:
        c["intro_html"] = md.convert("\n\n".join(c["intro"])); md.reset()
        c["blurb"] = first_sentence(c["intro"][0]) if c["intro"] else ""
        c["count"] = 0
        for g in c["groups"]:
            g["title"] = g["title"]
            g["intro_html"] = md.convert("\n\n".join(g["intro"])); md.reset()
            for t in g["techniques"]:
                c["count"] += 1
                d = next((b for b in t["blocks"] if b["cls"] == "def"), None)
                t["teaser"] = first_sentence(d["raw"]) if d else ""
                t["search"] = plain(" ".join([t["name"]] + [b["raw"] for b in t["blocks"]])).lower().replace('"', "'")
    return cats, "\n\n".join(intro_lines)

# ---- render ----
nav_items = [("index", "Home"), ("start-here", "Start here"), ("techniques", "Techniques"), ("bigger-picture", "Bigger picture"),
             ("defend-yourself", "Defend yourself"), ("get-help", "Get help"), ("quiz", "Quiz"), ("downloads", "Downloads"), ("about", "About")]
if KOFI: nav_items.append(("support", "Support"))
nav = [{"slug": s, "label": l, "href": f"{s}.html"} for s, l in nav_items]
ctx = {"site": site, "nav": nav, "version": VERSION, "updated": UPDATED}
written = []
def emit(name, html):
    (OUT / name).write_text(html, encoding="utf-8"); written.append(name)

def render(tpl, slug_, **kw):
    page = kw.pop("page", {}) ; page.setdefault("slug", slug_)
    return env.get_template(tpl).render(page=page, **ctx, **kw)

# techniques page first (feeds home)
meta, ttext = read_page("techniques.md")
cats, intro = parse_techniques(ttext)
md = new_md()
az = sorted([t for c in cats for g in c["groups"] for t in g["techniques"]], key=lambda t: t["name"].lower())
n_tech = len(az)
if n_tech != 51: warnings.append(f"expected 51 techniques, found {n_tech}")
emit("techniques.html", render("techniques.html", "techniques", page=meta, cats=cats, az=az, intro=plain(intro)))
emit("index.html", render("home.html", "index", page={"title": site["title"], "summary": site["subtitle"]}, cats=cats))

for name, slug_ in [("start-here.md", "start-here"), ("bigger-picture.md", "bigger-picture"), ("defend-yourself.md", "defend-yourself"),
                    ("about.md", "about"), ("sources.md", "sources"), ("quiz.md", "quiz"), ("downloads.md", "downloads")]:
    meta, text = read_page(name)
    md = new_md(); html = md.convert(text)
    emit(f"{slug_}.html", render("page.html", slug_, page=meta, content=html))

# help page with UK / anywhere filter
meta, text = read_page("get-help.md")
text = re.sub(r"\n(\*\*UK:\*\*)", r"\n\n\1", text)
md = new_md(); html = md.convert(text)
html = html.replace("<p><strong>Anywhere:</strong>", '<p class="h-any"><strong>Anywhere:</strong>').replace("<p><strong>UK:</strong>", '<p class="h-uk"><strong>UK:</strong>')
filt = ('<div class="filter" id="help-filter" hidden role="group" aria-label="Show help lines for">'
        '<button type="button" class="btn small" data-mode="all" aria-pressed="true">All</button>'
        '<button type="button" class="btn small" data-mode="uk" aria-pressed="false">UK</button>'
        '<button type="button" class="btn small" data-mode="any" aria-pressed="false">Anywhere else</button></div>')
first_h2 = html.find("<h2")
html = html[:first_h2] + filt + html[first_h2:]
emit("get-help.html", render("page.html", "get-help", page=meta, content=html))

if KOFI:
    meta, text = read_page("support.md"); md = new_md()
    emit("support.html", render("page.html", "support", page=meta, content=md.convert(text)))

# updates
body = []
for e in changelog:
    body.append(f"<h2>Version {e['version']}, {e['date_text']}</h2><ul>" + "".join(f"<li>{c}</li>" for c in e["changes"]) + "</ul>")
emit("updates.html", render("page.html", "updates", page={"title": "Updates", "summary": f"Latest version: {VERSION}, updated {UPDATED}."}, content="".join(body)))

emit("404.html", render("page.html", "404", page={"title": "Page not found", "summary": "That page does not exist."},
     content='<p>Try the <a href="index.html">home page</a> or the <a href="techniques.html">techniques</a>.</p>'))

for f in ("style.css", "site.js"): shutil.copy(ROOT / "static" / f, OUT / f)
(OUT / ".nojekyll").touch()
for old in OUT.glob("*.html"):
    if old.name not in written: old.unlink(); warnings.append(f"removed stale {old.name}")
print(f"Built {len(written)} pages, {n_tech} techniques, version {VERSION}, updated {UPDATED}.")
for w in warnings: print("CHECK:", w)
