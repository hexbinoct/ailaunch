# Ideas

Backlog of things we might want to build later. Not commitments — entries here are candidates to discuss.

## 1. Git status indicator next to each path

When the picker renders, for each entry that is inside a git repo, show a small git glyph plus a status badge similar to what zsh prompt themes (powerlevel10k, agnoster, etc.) display:

- A git icon (e.g. `` from a Nerd Font, or a plain `git:` if no Nerd Font available)
- Current branch name
- Dirty/clean marker (`*` for uncommitted changes, ` ` for clean)
- Optional ahead/behind counts vs upstream (`↑2 ↓1`)

Example row:

```
1   ~/code/acme-web    main *↑1   3h ago
```

**Open questions:**
- Performance: shelling out to `git` for every entry on every render could be slow with 50 paths. Cache results, or run async, or only resolve when the row is visible/selected.
- Detection: walk up from the path looking for `.git`, or just `git -C <path> rev-parse` and check exit code.
- Non-git paths: skip the column entirely or pad with spaces for alignment.
- Nerd Font fallback: detect terminal capability or just make it configurable.
