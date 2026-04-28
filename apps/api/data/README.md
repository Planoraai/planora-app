# data/

Local, non-secret data assets.

| Sub-folder | Phase | Contents |
|---|---|---|
| `kb/` | 3 | Curated travel knowledge base (markdown / JSON) ingested into the vector DB |
| `cache/` | 2 | (gitignored) On-disk cache when Redis is unavailable |
| `runs/` | 7 | (gitignored) Persisted run-state snapshots for replay |

Add new KB sources as plain markdown files under `data/kb/<country>/`.
