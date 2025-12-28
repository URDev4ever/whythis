#!/usr/bin/env python3
"""
whythis - Local metadata database for files with human explanations
Created by URDev
"""

import os
import sys
import json
import hashlib
import argparse
from datetime import datetime
from pathlib import Path, PurePath
import time
import shutil
from typing import Dict, Any, Optional, List

class WhyThisDB:
    def __init__(self):
        self.home = Path.home()
        self.config_dir = self.home / ".whythis"
        self.db_file = self.config_dir / "db.json"
        self.lock_file = self.config_dir / ".lock"
        self._ensure_config()
        
    def _ensure_config(self):
        """Create config directory and empty database if needed"""
        self.config_dir.mkdir(exist_ok=True)
        if not self.db_file.exists():
            self._write_db({})
            
    def _acquire_lock(self):
        """Simple file-based lock to prevent concurrent writes"""
        timeout = 10
        start = time.time()
        while self.lock_file.exists():
            if time.time() - start > timeout:
                raise Exception("Timeout waiting for lock")
            time.sleep(0.1)
        self.lock_file.touch()
        
    def _release_lock(self):
        """Release file lock"""
        if self.lock_file.exists():
            self.lock_file.unlink()
            
    def _read_db(self) -> Dict[str, Any]:
        """Read database with lock handling"""
        if not self.db_file.exists():
            return {}
            
        with open(self.db_file, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def _write_db(self, data: Dict[str, Any]):
        """Write database with lock handling"""
        self._acquire_lock()
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        finally:
            self._release_lock()
            
    def compute_hash(self, filepath: Path) -> str:
        """Compute SHA256 hash of file content"""
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return f"sha256:{hasher.hexdigest()}"
        except (OSError, IOError):
            return "unknown"
            
    def resolve_path(self, path_str: str) -> Path:
        """Resolve absolute path, handling symlinks"""
        path = Path(path_str).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.resolve()
        
    def add(self, filepath: Path, explanation: str, author: str = None, tags: List[str] = None):
        """Add or update explanation for a file"""
        if not filepath.exists():
            print(f"✗ File not found: {filepath}")
            sys.exit(1)
            
        abs_path = str(self.resolve_path(filepath))
        file_hash = self.compute_hash(filepath)
        
        db = self._read_db()
        
        entry = {
            "why": explanation,
            "created_at": datetime.now().isoformat(),
            "author": author or os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
            "hash": file_hash,
            "cwd": str(Path.cwd()),
            "tags": tags or []
        }
        
        db[abs_path] = entry
        self._write_db(db)
        print(f"✓ Added explanation for: {filepath.name}")
        
    def why(self, filepath: Path, verbose: bool = True) -> Optional[Dict[str, Any]]:
        """Get explanation for a file"""
        abs_path = str(self.resolve_path(filepath))
        
        if not filepath.exists():
            print(f"⚠ File not found (may have been deleted): {filepath}")
            abs_path = None
            
        db = self._read_db()
        
        entry = None
        moved_from = None
        
        if abs_path and abs_path in db:
            entry = db[abs_path]
        else:
            current_hash = self.compute_hash(filepath) if filepath.exists() else None
            
            for path, e in db.items():
                if e.get("hash") == current_hash:
                    entry = e
                    moved_from = path
                    break
                    
        if not entry:
            if verbose:
                print(f"✗ No explanation found for: {filepath}")
            return None
            
        if verbose:
            self._display_entry(filepath, entry, moved_from)
            
        return entry
        
    def _display_entry(self, filepath: Path, entry: Dict[str, Any], moved_from: str = None):
        """Display entry in human-readable format"""
        created = datetime.fromisoformat(entry["created_at"])
        file_exists = filepath.exists()
        
        print(f"\n📄 {filepath.name}")
        print(f"❓ Why: {entry['why']}")
        print(f"👤 By: {entry['author']}")
        print(f"🕒 Added: {created.strftime('%Y-%m-%d %H:%M')}")
        
        if moved_from and moved_from != str(filepath):
            print(f"📦 Moved from: {moved_from}")
        elif entry.get("cwd"):
            print(f"📁 Original location: {entry['cwd']}")
            
        if file_exists:
            current_hash = self.compute_hash(filepath)
            if current_hash != entry.get("hash"):
                print("⚠ File modified since explanation was added")
            elif entry.get("hash") != "unknown":
                print("🔒 Hash verification: OK")
                
        if entry.get("tags"):
            print(f"🏷 Tags: {', '.join(entry['tags'])}")
            
        print()
        
    def list_all(self, filter_tags: List[str] = None):
        """List all files with explanations"""
        db = self._read_db()
        
        if not db:
            print("No explanations found")
            return
            
        for path, entry in db.items():
            filepath = Path(path)
            exists = filepath.exists()
            
            if filter_tags:
                entry_tags = entry.get("tags", [])
                if not any(tag in entry_tags for tag in filter_tags):
                    continue
                    
            status = "✓" if exists else "✗"
            print(f"{status} {filepath.name}")
            print(f"  Why: {entry['why'][:80]}{'...' if len(entry['why']) > 80 else ''}")
            if entry.get("tags"):
                print(f"  Tags: {', '.join(entry['tags'])}")
            print()
            
    def search(self, query: str):
        """Search in explanations and tags"""
        db = self._read_db()
        query = query.lower()
        found = False
        
        for path, entry in db.items():
            if (query in entry["why"].lower() or 
                query in path.lower() or
                any(query in tag.lower() for tag in entry.get("tags", []))):
                
                self._display_entry(Path(path), entry)
                found = True
                
        if not found:
            print(f"No results for: {query}")
            
    def edit(self, filepath: Path, explanation: str = None, tags: List[str] = None):
        """Edit explanation or tags for a file"""
        entry = self.why(filepath, verbose=False)
        
        if not entry:
            print(f"✗ No existing explanation for: {filepath}")
            return
            
        db = self._read_db()
        abs_path = str(self.resolve_path(filepath))
        
        if abs_path not in db:
            for path, e in db.items():
                if e.get("hash") == entry.get("hash"):
                    abs_path = path
                    break
                    
        if explanation:
            db[abs_path]["why"] = explanation
        if tags is not None:
            db[abs_path]["tags"] = tags
            
        db[abs_path]["updated_at"] = datetime.now().isoformat()
        self._write_db(db)
        print(f"✓ Updated explanation for: {filepath.name}")
        
    def remove(self, filepath: Path):
        """Remove explanation for a file"""
        abs_path = str(self.resolve_path(filepath))
        db = self._read_db()
        
        if abs_path in db:
            del db[abs_path]
            self._write_db(db)
            print(f"✓ Removed explanation for: {filepath.name}")
        else:
            entry = self.why(filepath, verbose=False)
            if entry:
                for path, e in db.items():
                    if e.get("hash") == entry.get("hash"):
                        del db[path]
                        self._write_db(db)
                        print(f"✓ Removed explanation for: {filepath.name}")
                        return
            print(f"✗ No explanation found for: {filepath}")

def main():
    parser = argparse.ArgumentParser(
        description="whythis - Add human explanations to files",
        epilog="Created by URDev"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    add_parser = subparsers.add_parser("add", help="Add explanation for a file")
    add_parser.add_argument("file", help="File to explain")
    add_parser.add_argument("explanation", help="Human explanation")
    add_parser.add_argument("--author", help="Author name")
    add_parser.add_argument("--tags", help="Comma-separated tags")
    
    why_parser = subparsers.add_parser("why", help="Show explanation for a file")
    why_parser.add_argument("file", help="File to query")
    
    list_parser = subparsers.add_parser("list", help="List all explained files")
    list_parser.add_argument("--tags", help="Filter by comma-separated tags")
    
    search_parser = subparsers.add_parser("search", help="Search in explanations")
    search_parser.add_argument("query", help="Search query")
    
    edit_parser = subparsers.add_parser("edit", help="Edit explanation")
    edit_parser.add_argument("file", help="File to edit")
    edit_parser.add_argument("--explanation", help="New explanation")
    edit_parser.add_argument("--tags", help="New comma-separated tags")
    
    rm_parser = subparsers.add_parser("rm", help="Remove explanation")
    rm_parser.add_argument("file", help="File to remove")
    
    args = parser.parse_args()
    db = WhyThisDB()
    
    try:
        if args.command == "add":
            tags = args.tags.split(",") if args.tags else []
            db.add(Path(args.file), args.explanation, args.author, tags)
            
        elif args.command == "why":
            db.why(Path(args.file))
            
        elif args.command == "list":
            filter_tags = args.tags.split(",") if args.tags else None
            db.list_all(filter_tags)
            
        elif args.command == "search":
            db.search(args.query)
            
        elif args.command == "edit":
            tags = args.tags.split(",") if args.tags else None
            db.edit(Path(args.file), args.explanation, tags)
            
        elif args.command == "rm":
            db.remove(Path(args.file))
            
    except KeyboardInterrupt:
        print("\n✗ Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
