# catalog

Catalog and repository for components of the Enterprise Knowledge
Graph.

## Python

This repo uses **Python 3.14.2+** (see `pyproject.toml`) and **uv**.

```bash
uv sync
```

## Use case mindmaps & metadata

- Use case Markdown files under `docs/use-case/**/index.md` must
  include frontmatter with `title`, `description`, `keywords`, and
  `parents`. Allowed `parents` values: `..` (direct parent directory)
  or absolute `/use-case/...` for cross-tree “used by” parents.
  Siblings cannot be parents; the build will fail if encountered.

- During `uv run mkdocs serve|build`, `docs/main.py` normalizes
  frontmatter (deriving missing fields from H1 and first paragraph),
  builds the use case graph, and regenerates collision-free PlantUML
  mindmaps under `docs/diagrams/src/`, overwriting stale use-case
  mindmaps.
- To regenerate mindmaps and frontmatter outside MkDocs:

  ```bash
  cd docs && python3 - <<'PY'
  from main import _build_graph, _write_pumls
  graph = _build_graph()
  _write_pumls(graph)
  print(f"Processed {len(graph)} use cases")
  PY
  ```

- Each parent shown in a mindmap includes all its children; multiple
  parents are supported (primary rendered first).

## Copyright and Attribution

```text
Copyright (c) 2026 EDMCouncil Inc., d/b/a Enterprise Data Management Association ("EDMA")
Copyright (c) 2026 agnos.ai UK Ltd
```

This work is licensed under a
[Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).

When using or sharing this content, please provide attribution to:

- EDMCouncil Inc., d/b/a Enterprise Data Management Association
  ("EDMA")
- agnos.ai UK Ltd

## Initiative

This is an initiative of:

- [agnos.ai UK Ltd](https://agnos.ai)
- [Object Management Group](https://omg.org) (OMG)
  [Enterprise Knowledge Graph Forum](https://ekgf.org) (EKGF)

The content of this repository is published as
https://catalog.ekgf.org
