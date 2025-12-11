#!/usr/bin/env python3
"""
Script to update imports after restructuring backend
"""

import os
import re
from pathlib import Path


def update_imports_in_file(file_path: Path, old_import: str, new_import: str):
    """Update imports in a single file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Update the import
        updated_content = content.replace(old_import, new_import)

        if content != updated_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
            print(f"✅ Updated {file_path}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def main():
    """Update all imports in backend"""
    backend_dir = Path("backend/src")

    # Import mappings
    import_mappings = [
        ("from .cache import", "from ..services.cache import"),
        ("from .constants import", "from ..utils.constants import"),
        ("from .gemini_service import", "from ..services.gemini_service import"),
        ("from .mocks import", "from ..utils.mocks import"),
        ("from .models import", "from ..models.models import"),
        ("from .search_clients import", "from ..services.search_clients import"),
        ("from .observability import", "from ..services.observability import"),
        ("from .db import", "from ..utils.db import"),
    ]

    # Update all Python files
    for py_file in backend_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        for old_import, new_import in import_mappings:
            update_imports_in_file(py_file, old_import, new_import)


if __name__ == "__main__":
    main()
