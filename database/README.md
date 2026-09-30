# R Theory database dump — 2026-09-30

Per-table SQL dumps of `rtheory.db` (SQLite), zipped and split for upload.

## Contents
11 tables: theorems, status_codes, theorem_deps, prose, prose_theorems,
prose_chunks, desmos_graphs, embeddings, prose_embeddings, terms, changelog.

## Reassemble
```sh
cat rtheory-tables.zip.part-* > rtheory-tables.zip
unzip rtheory-tables.zip
```
Then load any table, e.g.:
```sh
sqlite3 my.db < tables/theorems.sql
```
Vector blobs are stored as `X'...'` hex literals (little-endian float32, 768 dims, nomic-embed-text).
