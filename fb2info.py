#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import base64
import xml.etree.ElementTree as ET
from PIL import Image
from io import BytesIO
from urllib.request import url2pathname


def save_cover(cover_raw, output_file, size):
    try:
        cover_decoded = base64.b64decode(cover_raw)
        cover = Image.open(BytesIO(cover_decoded))
        cover.thumbnail((size, size), Image.Resampling.LANCZOS)
        cover.save(output_file, "PNG")
        return True
    except Exception as e:
        print(e)
        return False


def get_cover_id(root):
    cover_page = root.find('.//description/title-info/coverpage/image')
    if cover_page is None:
        cover_page = root.find('.//{*}description/{*}title-info/{*}coverpage/{*}image')
    if cover_page is None:
        cover_page = root.find('.//body/image')
    if cover_page is None:
        cover_page = root.find('.//{*}body/{*}image')
    if cover_page is None or cover_page.attrib is None:
        return None
    cover_id = None
    for k, v in cover_page.attrib.items():
        if v and len(v) > 0 and k.endswith('href'):
            cover_id = v[1:]
            break
    return cover_id


def try_without_cover_id(root, output_file, size):
    # fallback: look for cover by id attribute
    for i in root.iter():
        if (i.tag.split('}')[1] == 'binary') and ('id' in i.attrib) and (i.attrib['id'].split('.')[0] == 'cover'):
            print("Found by cover attribute")
            if save_cover(i.text, output_file, size):
                return True
    # fallback: look for any image
    for i in root.iter():
        if (i.tag.split('}')[1] == 'binary') and ('content-type' in i.attrib) and (i.attrib['content-type'].split('/')[0] == 'image'):
            print("Found by image type")
            if save_cover(i.text, output_file, size):
                return True
    # fallback: look for jpg/png by content-type id
    for i in root.iter():
        if (i.tag.split('}')[1] == 'binary') and ('content-type' in i.attrib) and ('id' in i.attrib) and (i.attrib['id'].split('.')[1].lower() in ['jpg', 'png']):
            print("Found by image type")
            if save_cover(i.text, output_file, size):
                return True
    return False


def main():
    if len(sys.argv) < 3:
        print('Not enough actual parameters')
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    size = int(sys.argv[3]) if len(sys.argv) > 3 else 256

    if input_file.startswith('file://'):
        input_file = url2pathname(input_file).split('file://')[1]

    with open(input_file, 'rb') as f:
        raw = f.read()

    # Strip UTF-8 BOM if present
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]

    # Normalize 'windows-1251' (hyphen) to 'cp1251' (underscore)
    # so ElementTree can recognize the encoding declaration
    raw = raw.replace(b'windows-1251', b'cp1251')

    root = ET.parse(BytesIO(raw)).getroot()

    cover_id = get_cover_id(root)
    if cover_id:
        for i in root.iter():
            if (i.tag.split('}')[1] == 'binary') and ('id' in i.attrib) and (i.attrib['id'] == cover_id):
                print(f"Found by coverpage = #{cover_id}")
                if save_cover(i.text, output_file, size):
                    sys.exit(0)

    if not try_without_cover_id(root, output_file, size):
        print('No cover inside')
        sys.exit(2)


if __name__ == '__main__':
    main()
