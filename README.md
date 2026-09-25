# fb2info

Simple FB2 thumbnailer for Linux desktop file managers.

Extracts cover images from FB2 (FictionBook) files and generates PNG thumbnails compatible with the [XDG Thumbnailer Cache specification](https://specifications.freedesktop.org/thumbnailer-spec/thumbnailer-spec-latest.html).

## Supported File Managers

- **Nautilus** (GNOME Files)
- **Caja** (MATE Files)
- **PCManFM** / **PCManFM-Qt**
- **Thunar** (Xfce)
- **Dolphin** (KDE)
- Any file manager that supports XDG thumbnailer spec

## Installation

1. Copy the thumbnailer entry:
   ```bash
   sudo cp fb2.thumbnailer /usr/share/thumbnailers/
   ```

2. Install the script:
   ```bash
   sudo cp fb2info.py /usr/bin/fb2info.py
   sudo chmod +x /usr/bin/fb2info.py
   ```

3. Install dependencies:
   ```bash
   # Debian/Ubuntu
   sudo apt install python3 python3-pil

   # Arch Linux
   sudo pacman -S python-pillow

   # Fedora
   sudo dnf install python3-pillow
   ```

4. Clear existing thumbnails (if needed):
   ```bash
   rm -rf ~/.cache/thumbnails/fail/gnome-thumbnail-factory/*
   ```

## How It Works

The thumbnailer searches for cover images in this priority order:

1. **FB2 coverpage structure** — looks up `<coverpage><image href="..."/>` → resolves the `href` to a `<binary>` element
2. **Fallback by ID** — searches `<binary id="cover.*">` elements
3. **Fallback by content-type** — searches `<binary content-type="image/*">` elements
4. **Fallback by extension** — searches `<binary content-type="..." id="*.jpg" or *.png">` elements

If no cover is found, it exits with status code `2` (no cover), which tells the file manager to display the default icon.

## Requirements

- Python 3.6+
- Pillow (Python Imaging Library)
- XML parsing (built-in `xml.etree.ElementTree`)

## Troubleshooting

### Thumbnails not showing

- Ensure the thumbnailer entry is in `/usr/share/thumbnailers/`
- Check that `python3` and `PIL` are installed
- Verify the MIME type: `file --mime-type book.fb2` should return `application/x-fictionbook+xml`
- Clear the thumbnail cache: `rm -rf ~/.cache/thumbnails/*`
- Restart the file manager

### Encoding issues (cp1251, windows-1251)

The script automatically normalizes `windows-1251` encoding declarations to `cp1251` for compatibility with `ElementTree`. UTF-8 BOM is also stripped if present.

### License

Distributed under [GNU General Public License v2](LICENSE).
