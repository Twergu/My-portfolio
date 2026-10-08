"""Run PDF extraction in a separate process so slow files can be terminated."""

import json
import sys
import traceback

from pypdf import PdfReader


def extract(path):
    reader = PdfReader(path, strict=False)
    if reader.is_encrypted:
        raise ValueError("PDF 已加密，请先解密后再上传。")
    if not 1 <= len(reader.pages) <= 200:
        raise ValueError("每份 PDF 需为 1–200 页，请拆分后上传。")
    pages = []
    total = 0
    empty = []
    for number, page in enumerate(reader.pages, 1):
        content = page.get_contents()
        if content and len(content.get_data()) > 12 * 1024 * 1024:
            raise ValueError(f"第 {number} 页内容过于复杂，请简化 PDF 后重试。")
        text = (page.extract_text() or "").replace("\x00", "").strip()
        total += len(text)
        if total > 1_000_000:
            raise ValueError("文档文字超过 100 万字符，请拆分上传。")
        if not text:
            empty.append(number)
        pages.append({"page": number, "text": text})
    if not any(p["text"] for p in pages):
        raise ValueError("未提取到文字。这可能是扫描版 PDF，请先进行 OCR 文字识别。")
    return {"pages": pages, "empty_pages": empty}


if __name__ == "__main__":
    try:
        print(json.dumps(extract(sys.argv[1]), ensure_ascii=True))
    except ValueError as exc:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"error": str(exc)}, ensure_ascii=True))
        sys.exit(1)
    except Exception:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"error": "PDF 无法解析，文件可能损坏或使用了不支持的格式。"}, ensure_ascii=True))
        sys.exit(1)
