#!/usr/bin/env python3
import pathlib
import re

REPO = "totkd/Assets"  # 自分のリポ名

ROOT = pathlib.Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

# ギャラリーに含めたい拡張子
patterns = ["*.png", "*.jpg", "*.jpeg"]


def list_images():
    imgs = []
    for pat in patterns:
        imgs.extend(ROOT.glob("**/" + pat))
    # .git や scripts などを除外したければここで filter
    imgs = [
        p for p in imgs
        if ".git" not in p.parts and ".github" not in p.parts and "scripts" not in p.parts
    ]
    # 名前順
    imgs = sorted(imgs, key=lambda p: p.as_posix().lower())
    return imgs


def chunk3(seq):
    buf = []
    for x in seq:
        buf.append(x)
        if len(buf) == 3:
            yield buf
            buf = []
    if buf:
        yield buf


def make_gallery_md(images, limit=None):
    if limit:
        images = images[-limit:]

    lines = []
    lines.append("### Latest Images\n")

    # 3つずつテーブル行を作る
    for group in chunk3(images):
        # 画像行
        row_imgs = ["|"]  # 先頭の |
        for p in group:
            rel = p.relative_to(ROOT).as_posix()
            url = f"https://raw.githubusercontent.com/{REPO}/main/{rel}"
            cell = (
                f'<a href="{url}">'
                f'<img src="{url}" width="220" />'
                f"</a>"
            )
            row_imgs.append(f" {cell} |")
        # 足りないセル(画像数が3で割り切れないとき)を埋める
        while len(row_imgs) < 4:  # 先頭の"|"込みで4 = 3セル
            row_imgs.append("  |")
        lines.append("".join(row_imgs))

        # 区切り行（最初のグループの時だけでもいいけど、見やすさ優先で毎回入れてもOK）
        # ここでは最初の1回だけ入れる
        if group is images[: len(group)]:
            lines.append("|---|---|---|")

        # URL/パス行
        row_meta = ["|"]
        for p in group:
            rel = p.relative_to(ROOT).as_posix()
            url = f"https://raw.githubusercontent.com/{REPO}/main/{rel}"
            cell = (
                f"`{url}`<br>"
                f"`{rel}`"
            )
            row_meta.append(f" {cell} |")
        while len(row_meta) < 4:
            row_meta.append("  |")
        lines.append("".join(row_meta))

    return "\n".join(lines).strip() + "\n"


def main():
    images = list_images()
    if not images:
        print("No images found, skipping.")
        return

    gallery = make_gallery_md(images, limit=30)  # 最新30枚だけ、とかにしてもOK

    text = README.read_text(encoding="utf-8")

    pattern = re.compile(
        r"(<!-- AUTO-GALLERY-START -->)(.*?)(<!-- AUTO-GALLERY-END -->)",
        re.DOTALL,
    )

    new_block = (
        "<!-- AUTO-GALLERY-START -->\n\n"
        + gallery
        + "\n<!-- AUTO-GALLERY-END -->"
    )

    if not pattern.search(text):
        raise SystemExit("Markers not found in README.md")

    new_text = pattern.sub(new_block, text)

    if new_text == text:
        print("README unchanged.")
        return

    README.write_text(new_text, encoding="utf-8")
    print("README updated.")


if __name__ == "__main__":
    main()
