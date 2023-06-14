from pathlib import Path

import markdown
from nonebot import logger, require

from .config import config

require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender.data_source import (  # noqa: E402
    TEMPLATES_PATH,
    env,
    get_new_page,
    read_tpl,
)


RES_PATH = Path(__file__).parent / "res"
ADDITIONAL_CSS = (RES_PATH / "additional.css").read_text(encoding="u8")
ADDITIONAL_HTML = (RES_PATH / "additional.html").read_text(encoding="u8")


async def text_to_img(text: str) -> bytes:
    template = env.get_template("text.html")
    content = await template.render_async(
        text=text,
        css="\n".join([await read_tpl("text.css"), ADDITIONAL_CSS]),
    )

    async with get_new_page(
        viewport={"width": config.IMG_MAX_WIDTH, "height": 1000}
    ) as page:
        await page.goto(f"file://{TEMPLATES_PATH}")
        await page.set_content(content, wait_until="networkidle")

        text_element = await page.query_selector(".text")
        assert text_element

        return await text_element.screenshot(type="png")


# 个人微调
async def md_to_img(md: str) -> bytes:
    logger.debug(md)

    md = markdown.markdown(
        md,
        extensions=[
            "pymdownx.tasklist",
            "tables",
            "fenced_code",
            "codehilite",
            "mdx_math",
            "pymdownx.tilde",
        ],
        extension_configs={"mdx_math": {"enable_dollar_delimiter": True}},
    )
    logger.debug(md)

    # if "math/tex" in md:
    katex_css = await read_tpl("katex/katex.min.b64_fonts.css")
    katex_js = await read_tpl("katex/katex.min.js")
    mathtex_js = await read_tpl("katex/mathtex-script-type.min.js")
    extra = (
        f"{ADDITIONAL_HTML}\n"
        f'<style type="text/css">{katex_css}</style>\n'
        f"<script defer>{katex_js}</script>\n"
        f"<script defer>{mathtex_js}</script>\n"
    )

    css = "\n".join(
        [
            await read_tpl("github-markdown-light.css"),
            await read_tpl("pygments-default.css"),
            ADDITIONAL_CSS,
        ],
    )
    template = env.get_template("markdown.html")
    content = await template.render_async(md=md, css=css, extra=extra)

    async with get_new_page(
        viewport={"width": config.IMG_MAX_WIDTH, "height": 1000}
    ) as page:
        await page.goto(f"file://{TEMPLATES_PATH}")
        await page.set_content(content, wait_until="networkidle")

        article = await page.query_selector("article")
        assert article

        return await article.screenshot(type="png")
