# -*- coding: utf-8 -*-
"""Build the 10-tool portal: writes pages, css, sitemap."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import core
from pages_a import LOAN, DSR, PROP
from pages_b import RENT, SAVE, SALARY
from pages_c import SEVER, SUB, CGT

EXTRA_CSS = r"""
/* segmented bar (원금 vs 이자, 비용 비교, 가점 구성) */
.bar{display:flex; height:12px; border-radius:999px; overflow:hidden; background:#eef2f8; margin:2px 0 6px}
.bar span{display:block; height:100%; transition:width .25s ease}
.bar-p{background:#1b64da}
.bar-i{background:#9dc0f0}
.dot{display:inline-block; width:8px; height:8px; border-radius:2px; margin-right:4px; vertical-align:middle}
.dot-p{background:#1b64da}
.dot-i{background:#9dc0f0}
.bar-rows{margin:6px 0 4px}
.bar-row{display:flex; align-items:center; gap:9px; margin-bottom:7px; font-size:13px}
.bar-k{flex:none; width:62px; color:#4e5968; font-weight:600}
.bar-track{flex:1; height:10px; background:#eef2f8; border-radius:999px; overflow:hidden}
.bar-fill{display:block; height:100%; border-radius:999px; transition:width .25s ease}
.bar-v{flex:none; min-width:96px; text-align:right; font-weight:700; font-variant-numeric:tabular-nums; color:#0f2447; font-size:12.5px}
.fill-j{background:#1b64da}
.fill-w{background:#f0a24b}
.fill-s1{background:#1b64da}
.fill-s2{background:#37a17a}
.fill-s3{background:#b07cd6}
table.tbl tr.onrow td{background:#eef5ff; font-weight:700; color:#134fb0}
h3{scroll-margin-top:80px}
input[type=date]{font-family:inherit}
@media (max-width:520px){
  .bar-v{min-width:72px; font-size:11.5px}
  .bar-k{width:54px; font-size:12px}
}
"""


def main():
    core.write("assets/site.css", core.CSS + EXTRA_CSS)
    core.write("index.html", core.build_index())
    core.write("privacy.html", core.build_privacy())
    core.write("sitemap.xml", core.build_sitemap())
    for p in [LOAN, DSR, PROP, RENT, SAVE, SALARY, SEVER, SUB, CGT]:
        page = core.tool_page(p)
        core.write(p["slug"] + ".html", page)
    print("done")


if __name__ == "__main__":
    main()
