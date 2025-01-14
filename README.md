
# Pip Package Manager GUI

A GUI tool for managing Python packages using pip.

## Features

- View installed packages.
- Search and install packages from PyPI.
- Sort packages by name or size.
- Update or uninstall packages through a child window.
- Display information about packages
- Install from GitHub repositories
- Install from requirements.txt

## Installation

1. Clone the repository:
   ```bash
   pip install pipmanagergui
   ```

2. Run it on terminal:
   ```bash
   pipmanager
   ```
If any errors occur you can download the wheel manually [here](dist/pipmanagergui-0.1.1-py3-none-any.whl)

## Usage

- Click "Search Local Packages" to view installed packages.
- Use the search bar to find packages on PyPI.
- Double-click a package to update or uninstall it.

## Requirements

- Python 3.8+
- `requests`
- `tkinter`
## Changelog
### 0.1.0 (2025-01-06)
- Initial release.
### 0.1.1 (2025-01-06)
- Fixed bug.
- Released to pypi.
### 0.1.2 (2025-01-07)
- Added display info button that displays output of pip info.
- Fixed search function.
- Added installation date to double click menu.
- When searching for a pypi package author name is displayed
### 0.2.0 (2025-01-14)
- Resolved an issue regarding local search
- Added install from requirements.txt
- Added install from GitHub repository
- Added Update all button
## License

MIT License

