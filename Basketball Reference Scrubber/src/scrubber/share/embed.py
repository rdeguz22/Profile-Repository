from __future__ import annotations

from html import escape


def iframe_embed(
    permalink_url: str, width: int = 680, height: int = 420, title: str = "Basketball Reference Scrubber"
) -> str:
    return (
        f'<iframe src="{escape(permalink_url, quote=True)}" '
        f'width="{width}" height="{height}" '
        f'style="border:0;border-radius:12px;overflow:hidden;" '
        f'title="{escape(title, quote=True)}" loading="lazy"></iframe>'
    )


def image_embed(image_url: str, link_url: str | None = None, alt: str = "Basketball Reference Scrubber view") -> str:
    img_tag = f'<img src="{escape(image_url, quote=True)}" alt="{escape(alt, quote=True)}" style="max-width:100%;border-radius:12px;" />'
    if link_url:
        return f'<a href="{escape(link_url, quote=True)}">{img_tag}</a>'
    return img_tag


def markdown_embed(permalink_url: str, image_url: str | None = None, alt: str = "Basketball Reference Scrubber view") -> str:
    if image_url:
        return f"[![{alt}]({image_url})]({permalink_url})"
    return f"[{alt}]({permalink_url})"
