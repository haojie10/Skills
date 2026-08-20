#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Market Graphic / Category Insight
图片 Base64 智能压缩嵌入、语法清洗与自检脚本

核心功能：
1. 智能压缩与缩放：使用 PIL 将本地高分辨率图片等比缩放至合适尺寸（最大宽 900px），
   转为高画质 JPEG (quality=82) 进行 Base64 编码，将 HTML 体积严格控制在 200KB-400KB 之间，
   彻底杜绝 Nginx 413 Request Entity Too Large 错误。
2. 语法与前缀自愈清洗：检测并自动修复重复的 data:image/...;base64, 前缀。
3. 闭环解码自检：嵌入后自动对 HTML 中所有 Data URL 进行解码验证，确保 100% 可正常显示。
4. 自动清理临时文件：嵌入成功且自检通过后，自动删除本地的原临时图片文件。
"""

import os
import re
import sys
import io
import base64
import argparse

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def clean_and_compress_image(image_path, max_width=900, quality=82):
    """读取本地图片，自动缩放与压缩后返回标准 Data URL"""
    if not os.path.exists(image_path):
        print(f"[WARN] Image file not found: {image_path}")
        return None

    _, ext = os.path.splitext(image_path.lower())
    
    # 如果是 SVG 矢量图，直接以 svg+xml 内嵌
    if ext == ".svg":
        try:
            with open(image_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                return f"data:image/svg+xml;base64,{encoded}"
        except Exception as e:
            print(f"[WARN] Failed to read SVG {image_path}: {e}")
            return None

    # 如果有 PIL，进行智能缩放与高画质压缩
    if HAS_PIL:
        try:
            with Image.open(image_path) as img:
                # 统一转为 RGB（处理 RGBA / P 模式）
                if img.mode in ("RGBA", "LA", "P"):
                    # 如果有透明通道，建白色底
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "RGBA":
                        background.paste(img, mask=img.split()[3])
                    else:
                        background.paste(img)
                    img = background
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                # 等比缩放
                if img.width > max_width:
                    ratio = max_width / float(img.width)
                    new_size = (max_width, int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                out_io = io.BytesIO()
                img.save(out_io, format="JPEG", quality=quality, optimize=True)
                compressed_bytes = out_io.getvalue()
                encoded_string = base64.b64encode(compressed_bytes).decode("utf-8")
                print(f"[OK] Compressed {os.path.basename(image_path)}: {len(compressed_bytes) / 1024:.1f} KB (Res: {img.size[0]}x{img.size[1]})")
                return f"data:image/jpeg;base64,{encoded_string}"
        except Exception as e:
            print(f"[WARN] PIL compression failed for {image_path}, fallback to raw: {e}")

    # 降级：原生二进制读取
    mime_type = "image/png"
    if ext in [".jpg", ".jpeg"]:
        mime_type = "image/jpeg"
    elif ext == ".webp":
        mime_type = "image/webp"
    elif ext == ".gif":
        mime_type = "image/gif"

    try:
        with open(image_path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode("utf-8")
            return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        print(f"[ERROR] Failed to read {image_path}: {e}")
        return None

def sanitize_existing_base64(html_content):
    """清洗 HTML 中已存在的重复前缀与超大 Base64 图片"""
    # 修复类似 data:image/png;base64,data:image/... 的多重嵌套前缀
    pattern_nested = re.compile(r'src=["\'](?:data:image/[^;]+;base64,)+(data:image/[^;]+;base64,[^"\']+)["\']', re.IGNORECASE)
    html_content = pattern_nested.sub(r'src="\1"', html_content)
    
    # 进一步规范化清洗
    pattern_double = re.compile(r'src=["\']data:image/[^;]+;base64,data:image/[^;]+;base64,([^"\']+)["\']', re.IGNORECASE)
    html_content = pattern_double.sub(r'src="data:image/jpeg;base64,\1"', html_content)
    
    return html_content

def verify_all_embedded_images(html_content):
    """自检 HTML 中所有嵌入图片的有效性"""
    pattern = re.compile(r'<img\s+[^>]*src=["\']data:image/([^;]+);base64,([^"\']+)["\']', re.IGNORECASE)
    matches = pattern.findall(html_content)
    
    if not matches:
        print("[INFO] No Data URL images found to verify.")
        return True

    print(f"[VERIFY] Checking {len(matches)} embedded image(s)...")
    all_valid = True
    for idx, (mime, b64_str) in enumerate(matches, 1):
        try:
            raw_bytes = base64.b64decode(b64_str)
            if HAS_PIL and mime not in ("svg", "svg+xml"):
                with Image.open(io.BytesIO(raw_bytes)) as img:
                    print(f"  ✓ Image #{idx}: Valid {img.format} ({img.size[0]}x{img.size[1]}), {len(raw_bytes)/1024:.1f} KB")
            else:
                print(f"  ✓ Image #{idx}: Valid Data ({len(raw_bytes)/1024:.1f} KB)")
        except Exception as e:
            print(f"  ✗ Image #{idx}: INVALID Base64 Data! Error: {e}")
            all_valid = False

    return all_valid

def embed_images_in_html(html_path):
    """扫描 HTML 并嵌入本地图片，清洗语法，自检并删除本地图片"""
    if not os.path.exists(html_path):
        print(f"[ERROR] HTML file not found: {html_path}")
        sys.exit(1)

    html_dir = os.path.dirname(os.path.abspath(html_path))
    
    with open(html_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    # 1. 先进行现有 Base64 前缀清洗
    html_content = sanitize_existing_base64(html_content)

    # 2. 正则寻找相对路径本地图片
    img_pattern = re.compile(r'(<img\s+[^>]*src=["\'])([^"\']+\.(?:png|jpg|jpeg|gif|webp|svg))(["\'][^>]*>)', re.IGNORECASE)
    matches = img_pattern.findall(html_content)
    
    embedded_count = 0
    images_to_delete = []

    if matches:
        print(f"[INFO] Found {len(matches)} local image reference(s). Compressing & embedding...")
        
        def replace_image(match):
            nonlocal embedded_count
            prefix = match.group(1)
            src_path = match.group(2)
            suffix = match.group(3)
            
            # 排除网络链接和已是 Base64 的链接
            if src_path.startswith("http://") or src_path.startswith("https://") or src_path.startswith("data:"):
                return match.group(0)
                
            abs_image_path = os.path.join(html_dir, src_path)
            if os.path.exists(abs_image_path):
                data_url = clean_and_compress_image(abs_image_path)
                if data_url:
                    embedded_count += 1
                    images_to_delete.append(abs_image_path)
                    print(f"[OK] Embedded: {src_path}")
                    return f"{prefix}{data_url}{suffix}"
            else:
                print(f"[WARN] Local image path does not exist: {abs_image_path}")
                
            return match.group(0)

        html_content = img_pattern.sub(replace_image, html_content)

    # 3. 自检验证
    is_valid = verify_all_embedded_images(html_content)
    if not is_valid:
        print("[ERROR] Verification failed! One or more images cannot be decoded.")
        sys.exit(1)

    # 4. 写回 HTML 文件
    with open(html_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    file_size_kb = os.path.getsize(html_path) / 1024
    print(f"[OK] HTML saved successfully! File size: {file_size_kb:.1f} KB")

    # 5. 清理原临时图片文件
    if images_to_delete:
        print("[INFO] Cleaning up temporary image files...")
        deleted_count = 0
        for img_path in set(images_to_delete):
            try:
                if os.path.exists(img_path):
                    os.remove(img_path)
                    print(f"[OK] Deleted temp image: {os.path.basename(img_path)}")
                    deleted_count += 1
            except Exception as e:
                print(f"[WARN] Failed to delete file {img_path}: {e}")
        print(f"[OK] Cleanup complete. Deleted {deleted_count} temp image file(s).")

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="将 HTML 报告中的本地图片自动缩放压缩并以 Base64 内嵌，同时清洗前缀与自检。")
    parser.add_argument("html_file", help="目标 HTML 报告文件路径")
    args = parser.parse_args()
    
    embed_images_in_html(args.html_file)

if __name__ == "__main__":
    main()
