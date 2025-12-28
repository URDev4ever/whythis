<h1 align="center">whythis</h1>

<h3 align="center">whythis is a small CLI tool that lets you attach human explanations to files on your system.</h3>

It answers one simple question:

> **Why does this file exist?**

Instead of guessing months later why `fix_final_v2_REAL.sh` or `temp_patch.py` exists, you can ask `whythis`.

---

## What it does

- Stores explanations **outside** your projects (no file modification)
- Tracks files by **absolute path + SHA256 hash**
- Detects when files are **moved**, **deleted**, or **modified**
- Works with any file type
- Lightweight, local, and dependency-free

All metadata is stored locally in:

```

~/.whythis/db.json

````

---

## Installation

Clone the repository and run the installer:

```bash
git clone https://github.com/URDev4ever/whythis.git
cd whythis
chmod +x installer.sh
sudo ./installer.sh install
````

This installs `whythis` globally (default: `/usr/local/bin`).

To uninstall:

```bash
sudo ./installer.sh uninstall
```

> The database in `~/.whythis/` is preserved by default.

---

## Basic usage

### Add an explanation

```bash
whythis add script.sh "Temporary workaround for prod issue"
```
> [ ! ] Make sure to use the quotation marks (" ") for it to work.

With tags:

```bash
whythis add script.sh "Hotfix for API bug" --tags prod,hotfix
```
> [ ! ] WITHOUT spaces ("--tags tag1 tag2" won't work, correct format: "--tags tag1,tag2").
---

### Ask why a file exists

```bash
whythis why script.sh
```

Example output:

```
📄 script.sh
❓ Why: Temporary workaround for prod issue
👤 By: YourUser
🕒 Added: 2025-12-25 18:40
📁 Original location: /home/user/project
🔒 Hash verification: OK
```

---

### List all explained files

```bash
whythis list
```

Filter by tags:

```bash
whythis list --tags prod
```

---

### Search explanations

```bash
whythis search prod
```

Searches in:

* explanations
* file paths
* tags

---

### Edit an explanation

```bash
whythis edit script.sh --explanation "Permanent fix after refactor"
```

Update tags:

```bash
whythis edit script.sh --tags refactor,cleanup
```

---

### Remove an explanation

```bash
whythis rm script.sh
```

Works even if the file was moved (hash-based match).

---

## How it works (technical overview)

* Files are indexed by **absolute path**
* Each entry stores a **SHA256 hash**
* If a file is moved, `whythis` finds it via hash comparison
* If a file is modified, a warning is shown
* If a file is deleted, the explanation is still accessible

No filesystem metadata, no git hooks, no file changes.

---

## Data format

Example entry in `~/.whythis/db.json`:

```json
{
  "/home/user/project/script.sh": {
    "why": "Temporary workaround for prod issue",
    "created_at": "2025-12-25T18:40:00",
    "author": "YourUser",
    "hash": "sha256:abcd1234...",
    "cwd": "/home/user/project",
    "tags": ["prod", "hotfix"]
  }
}
```

---

## Requirements

* Python 3.8+
* Linux / macOS (Windows via WSL or manual install)

No external Python dependencies.

---

## Status

Early version.
The tool is functional but intentionally minimal.

Future ideas:

* git context (commit / branch)
* relink command for moved files
* JSON / plain output modes

---
Made with <3 by URDev.
