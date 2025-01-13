# Changelog

## 0.2.x
### 0.2.1
- Insert exif to image file (i.e. without changing the file).

### 0.2.0
- Now spaces in rename string are replaces with `_`.
- version check of `optima35`, incase pip did not update it.
- Sorting entries from exif file.

### 0.2.0-a1
- Main UI received a facelift.
- Added a new experimental preview window to display an image and show how changing values affects it.
- Programm now warns for potential overwrite of existing files.

## 0.1.x
### 0.1.1
- Update metadata, preview, readme, bump in version for pip

### 0.1.0
- Preserved the current working GUI by pinning `optima35` to a specific version for guaranteed compatibility.

## 0.0.x
### 0.0.4-a2
- Adding __version__ to `__init__.py` so version is automaticly updated in program as well as pypi.

### 0.0.4-a1
- Refactored project structure, moving all code to the `src` directory.
- Adjusted imports and setup to accommodate the new folder structure.
- Skipped version numbers to `.4` due to PyPI versioning constraints (testing purposes).

### 0.0.1 - Initial UI-Focused Release
- Forked from OPTIMA35.
- Removed core OPTIMA35 files to focus exclusively on UI components.
- Integrated OPTIMA35 functionality via the pip package.
- Ensured both TUI and GUI modes operate seamlessly.
- Revised the README for improved clarity and structure.
