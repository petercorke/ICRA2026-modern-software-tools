#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


MOBILE_SCRIPT_RE = re.compile(
    r"\s*<script[^>]*\bdata-icra-mobile-navigation\b[^>]*>.*?</script>\s*",
    re.DOTALL,
)

EARLY_SLIDE_SCRIPT_RE = re.compile(
    r'\s*<script>\s*document\.addEventListener\("DOMContentLoaded", \(\) => \{'
    r'\s*const slides = Array\.from\(document\.querySelectorAll\("\.container"\)\);'
    r".*?</script>\s*",
    re.DOTALL,
)

PRESENTERM_NAV_RE = re.compile(
    r"\s*<script>\s*let originalWidth\s*=\s*(?P<width>\d+)\s*;"
    r"\s*let originalHeight\s*=\s*(?P<height>\d+)\s*;.*?</script>\s*",
    re.DOTALL,
)

CONTAINER_ACTIVE_RE = re.compile(r"\s*\.container\.active\s*\{.*?\}\s*", re.DOTALL)
CONTAINER_RE = re.compile(r"(?P<head>\.container\s*\{)(?P<body>.*?)(?P<tail>\n\s*\})", re.DOTALL)
BODY_WIDTH_RE = re.compile(r"(?:^|[;\n])\s*width:\s*(?P<width>\d+)px\s*;")
BODY_HEIGHT_RE = re.compile(r"(?:^|[;\n])\s*height:\s*(?P<height>\d+)px\s*;")


def replace_or_insert_display(css_body: str) -> str:
    if re.search(r"\bdisplay\s*:", css_body):
        return re.sub(r"\bdisplay\s*:\s*[^;]+;", "display: none;", css_body, count=1)

    lines = css_body.splitlines()
    if len(lines) > 1:
        lines.insert(1, "                    display: none;")
        return "\n".join(lines)

    return css_body + "\n                    display: none;"


def patch_container_css(html: str) -> str:
    html = CONTAINER_ACTIVE_RE.sub("\n", html)

    def replace_container(match: re.Match[str]) -> str:
        body = replace_or_insert_display(match.group("body"))
        active = "\n\n        .container.active {\n            display: flex;\n        }"
        return f"{match.group('head')}{body}{match.group('tail')}{active}"

    patched, count = CONTAINER_RE.subn(replace_container, html, count=1)
    if count != 1:
        raise ValueError("Could not find a .container CSS block to patch")

    return patched


def infer_slide_size(html: str) -> tuple[int, int]:
    style_match = re.search(r"body\s*\{(?P<body>.*?)\}", html, re.DOTALL)
    if style_match:
        body_css = style_match.group("body")
        width_match = BODY_WIDTH_RE.search(body_css)
        height_match = BODY_HEIGHT_RE.search(body_css)
        if width_match and height_match:
            return int(width_match.group("width")), int(height_match.group("height"))

    presenterm_match = PRESENTERM_NAV_RE.search(html)
    if presenterm_match:
        return int(presenterm_match.group("width")), int(presenterm_match.group("height"))

    return 666, 444


def navigation_script(width: int, height: int) -> str:
    return f"""<script data-icra-mobile-navigation>
document.addEventListener("DOMContentLoaded", () => {{
    const originalWidth = {width};
    const originalHeight = {height};
    const slides = Array.from(document.querySelectorAll(".container"));
    let current = 0;
    let startX = 0;
    let startY = 0;

    function clamp(index) {{
        return Math.max(0, Math.min(index, slides.length - 1));
    }}

    function scaleToViewport() {{
        const widthScale = document.documentElement.clientWidth / originalWidth;
        const heightScale = document.documentElement.clientHeight / originalHeight;
        const scale = Math.min(2, widthScale, heightScale);
        const offsetX = Math.max(0, (document.documentElement.clientWidth - originalWidth * scale) / 2);
        document.body.style.transform = `translateX(${{offsetX}}px) scale(${{scale}})`;
    }}

    function showSlide(index) {{
        if (!slides.length) return;

        current = clamp(index);
        slides.forEach((slide, i) => {{
            slide.classList.toggle("active", i === current);
        }});
    }}

    function nextSlide() {{
        showSlide(current + 1);
    }}

    function prevSlide() {{
        showSlide(current - 1);
    }}

    document.addEventListener("keydown", (event) => {{
        if (event.key === "ArrowRight" || event.key === "PageDown" || event.key === " ") {{
            event.preventDefault();
            nextSlide();
        }} else if (event.key === "ArrowLeft" || event.key === "PageUp") {{
            event.preventDefault();
            prevSlide();
        }} else if (event.key === "Home") {{
            event.preventDefault();
            showSlide(0);
        }} else if (event.key === "End") {{
            event.preventDefault();
            showSlide(slides.length - 1);
        }}
    }});

    document.addEventListener("touchstart", (event) => {{
        if (!event.changedTouches.length) return;

        startX = event.changedTouches[0].clientX;
        startY = event.changedTouches[0].clientY;
    }}, {{ passive: true }});

    document.addEventListener("touchend", (event) => {{
        if (!event.changedTouches.length) return;

        const endX = event.changedTouches[0].clientX;
        const endY = event.changedTouches[0].clientY;
        const dx = endX - startX;
        const dy = endY - startY;

        if (Math.abs(dx) < 50 || Math.abs(dx) <= Math.abs(dy)) return;
        if (dx < 0) nextSlide();
        else prevSlide();
    }}, {{ passive: true }});

    document.addEventListener("click", (event) => {{
        if (event.defaultPrevented || event.button !== 0) return;
        if (event.metaKey || event.ctrlKey || event.altKey || event.shiftKey) return;
        if (event.target.closest("a, button, input, textarea, select, label")) return;

        if (event.clientX > window.innerWidth / 2) nextSlide();
        else prevSlide();
    }});

    window.addEventListener("resize", scaleToViewport);

    scaleToViewport();
    showSlide(0);
}});
</script>"""


def patch_html(html: str) -> str:
    width, height = infer_slide_size(html)

    html = MOBILE_SCRIPT_RE.sub("", html)
    html = EARLY_SLIDE_SCRIPT_RE.sub("", html)
    html = PRESENTERM_NAV_RE.sub("", html)
    html = patch_container_css(html)

    script = navigation_script(width, height)
    patched, count = re.subn(r"\s*</body>", "\n\n" + script + "\n</body>", html, count=1)
    if count != 1:
        raise ValueError("Could not find a </body> tag for script insertion")

    return patched


def main() -> None:
    parser = argparse.ArgumentParser(description="Post-process a presenterm HTML export.")
    parser.add_argument("html", type=Path)
    args = parser.parse_args()

    source = args.html.read_text(encoding="utf-8")
    patched = patch_html(source)
    args.html.write_text(patched, encoding="utf-8")
    print(f"Post-processed {args.html}")


if __name__ == "__main__":
    main()
