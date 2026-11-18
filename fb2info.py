#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import base64
import xml.etree.ElementTree as ET
from PIL import Image
from io import BytesIO
from urllib.request import url2pathname


def local_name(tag):
    """Return local tag name without namespace."""
    return tag.rsplit('}', 1)[-1]


def save_cover(cover_raw, output_file, size):
    try:
        cover_decoded = base64.b64decode(cover_raw)
        cover = Image.open(BytesIO(cover_decoded))
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.LANCZOS
        cover.thumbnail((size, size), resample)
        cover.save(output_file, "PNG")
        return True
    except Exception as e:
        print(f"save_cover: {e}", file=sys.stderr)
        return False


def find_by_path(root, path):
    """Find element by local-name path, e.g. 'description/title-info/coverpage/image'."""
    parts = path.split('/')
    candidates = [root]
    for part in parts:
        next_candidates = []
        for c in candidates:
            for child in c:
                if local_name(child.tag) == part:
                    next_candidates.append(child)
        candidates = next_candidates
        if not candidates:
            return None
    return candidates[0] if candidates else None


def get_cover_id(root):
    cover_page = find_by_path(root, 'description/title-info/coverpage/image')
    if cover_page is None:
        # fallback: body/image (прямой потомок body)
        body = find_by_path(root, 'body')
        if body is not None:
            for child in body:
                if local_name(child.tag) == 'image':
                    cover_page = child
                    break
    if cover_page is None:
        return None
    for k, v in cover_page.attrib.items():
        if v and k.endswith('href'):
            return v[1:] if v.startswith('#') else v
    return None


def try_without_cover_id(root, output_file, size):
    # 1) cover by id attribute
    for i in root.iter():
        if local_name(i.tag) == 'binary' and i.attrib.get('id', '').split('.')[0] == 'cover':
            print("Found by cover attribute")
            if save_cover(i.text, output_file, size):
                return True
    # 2) any image by content-type
    for i in root.iter():
        if local_name(i.tag) == 'binary' and i.attrib.get('content-type', '').split('/')[0] == 'image':
            print("Found by image type")
            if save_cover(i.text, output_file, size):
                return True
    # 3) jpg/png by id
    for i in root.iter():
        if local_name(i.tag) != 'binary':
            continue
        id_parts = i.attrib.get('id', '').split('.')
        if len(id_parts) > 1 and id_parts[1].lower() in ('jpg', 'png'):
            print("Found by image id")
            if save_cover(i.text, output_file, size):
                return True
    return False


def main():
    if len(sys.argv) < 3:
        print('Not enough actual parameters', file=sys.stderr)
        return 1

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    try:
        size = max(1, int(sys.argv[3])) if len(sys.argv) > 3 else 256
    except ValueError:
        print(f"Invalid size: {sys.argv[3]}", file=sys.stderr)
        return 1

    if input_file.startswith('file://'):
        input_file = url2pathname(input_file)  # уже без 'file://'

    with open(input_file, 'rb') as f:
        raw = f.read()

    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]

    # Заменяем только в XML declaration (до первого '?>')
    head, sep, tail = raw.partition(b'?>')
    if b'windows-1251' in head:
        raw = head.replace(b'windows-1251', b'cp1251') + sep + tail

    root = ET.parse(BytesIO(raw)).getroot()

    cover_id = get_cover_id(root)
    if cover_id:
        for i in root.iter():
            if local_name(i.tag) == 'binary' and i.attrib.get('id') == cover_id:
                print(f"Found by coverpage = #{cover_id}")
                if save_cover(i.text, output_file, size):
                    return 0

    if not try_without_cover_id(root, output_file, size):
        print('No cover inside', file=sys.stderr)
        return 2

    return 0


if __name__ == '__main__':
    sys.exit(main())
