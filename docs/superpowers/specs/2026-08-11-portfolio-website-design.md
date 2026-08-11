# Portfolio Website Design

## Purpose

A personal portfolio website that serves two goals: credible enough for
recruiters/hiring managers evaluating data work, and a running build log the
user keeps updating as they add projects. It showcases the projects in the
`data-portfolio` repo (starting with `01-analytics-pipeline-duckdb`) plus an
about/background section and contact links.

## Repo

New, separate repo: `mhajiyev-portfolio-website`, at
`C:\Users\mhajiyev\projects\mhajiyev-portfolio-website`. Kept independent from
`data-portfolio` so that repo stays focused purely on the data projects
themselves.

## Tech stack

**MkDocs + Material for MkDocs theme.**

- Python-based, managed with `uv` (consistent with the numbered projects'
  tooling), Python 3.14+.
- Content authored in Markdown; navigation defined in `mkdocs.yml`.
- Material theme provides search, light/dark mode toggle, tags, and a blog
  plugin (`mkdocs-material` built-in blog) — all out of the box, no custom
  theming required.
- `mkdocs build` emits plain static HTML into `site/` — no backend, no
  server-side logic, deploys as static files.

Rejected alternatives:
- **Pelican** — also Python and blog-first, but achieving a comparably
  polished, docs-style look means owning more Jinja2 templating directly.
  More upfront work for no benefit given the desired clean docs aesthetic.
- **Hand-rolled Jinja2 + build script** — full control, but rebuilds
  theme/CSS/search/nav from scratch. Overkill for a portfolio site.

## Repo structure

```
mhajiyev-portfolio-website/
├── docs/                       # Markdown content (MkDocs convention)
│   ├── index.md                # Home
│   ├── about.md                # About/background
│   ├── projects/
│   │   ├── index.md            # Projects listing/index
│   │   └── 01-analytics-pipeline-duckdb.md
│   ├── blog/
│   │   └── posts/               # Write-ups, grows over time
│   └── contact.md              # Static links (email, LinkedIn, GitHub)
├── mkdocs.yml                  # Site config, nav, theme, plugins
├── pyproject.toml              # uv-managed deps (mkdocs, mkdocs-material)
├── uv.lock
├── .python-version
├── netlify.toml                # Build command + publish dir for Netlify
└── README.md
```

## Content/pages

- **Home** — brief intro + featured/recent projects.
- **About** — background, skills, experience relevant to data work.
- **Projects** — index page listing each numbered project from
  `data-portfolio`; each project gets its own page with a description, tech
  stack, and links out to the code/notebook on GitHub (no notebook embedding
  — this site links to the source repo rather than rendering `.ipynb`
  output directly).
- **Blog** — longer-form write-ups (what was built, why, what was learned).
  Starts empty/sparse and grows as new posts are added.
- **Contact** — static links only: email, LinkedIn, GitHub. No contact form,
  no backend.

## Deployment

- Site repo pushed to GitHub, connected to Netlify for continuous deploy.
- Netlify build command: `mkdocs build`. Publish directory: `site/`.
- Every push to `main` triggers an automatic Netlify deploy.
- Local development: `uv run mkdocs serve` for live-reloading preview.

## Out of scope

- Notebook rendering (`.ipynb` → page) — explicitly deferred; write-ups are
  hand-written prose instead.
- Contact form / form backend (e.g. Netlify Forms) — static links only for
  now.
- Custom visual design/branding — using Material's default clean docs theme
  rather than a bespoke look.
