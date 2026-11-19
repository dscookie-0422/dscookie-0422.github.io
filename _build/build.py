# -*- coding: utf-8 -*-
"""Build the 11-tool portal: writes pages, css, sitemap."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import core
from pages_a import LOAN, DSR, PROP
from pages_b import RENT, SAVE, SALARY
from pages_c import SEVER, SUB, CGT
from pages_d import YET

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
/* 연말정산: 입력 구역 소제목, 시뮬레이션 비교 카드 */
.field-sub{font-size:12px; font-weight:800; color:#8b97a8; letter-spacing:.05em; margin:20px 0 10px; padding-top:14px; border-top:1px dashed var(--line)}
.field-sub.first{margin-top:4px; padding-top:0; border-top:0}
.sim{display:grid; grid-template-columns:1fr 1fr; gap:9px; margin:0 0 12px}
.sim-card{border:1px solid var(--line); border-radius:12px; padding:11px 12px 12px; background:#fbfcfe; min-width:0}
.sim-card span{display:block; font-size:11.5px; font-weight:700; color:var(--muted); margin-bottom:3px; line-height:1.4}
.sim-card strong{display:block; font-size:16.5px; font-weight:800; color:var(--navy); font-variant-numeric:tabular-nums; letter-spacing:-.01em; white-space:nowrap}
.sim-card em{display:block; font-style:normal; font-size:11.5px; font-weight:700; color:var(--muted); margin-top:3px; line-height:1.4}
.sim-card.up{background:#f2f8ff; border-color:#cbdcf8}
.sim-card.up strong{color:var(--blue-d)}
.sim-card.up em{color:var(--blue-d)}
table.sim-tbl{min-width:0; font-size:12.5px}
table.sim-tbl th,table.sim-tbl td{padding:8px 9px}
table.sim-tbl td:first-child{white-space:normal; line-height:1.45}
table.sim-tbl td:last-child{color:var(--blue-d); font-weight:700}
.kv-note{color:#9aa7ba; font-weight:500; font-size:12px}
@media (max-width:520px){
  .sim-card strong{font-size:14.5px}
  .sim-card span{font-size:10.5px}
}
@media (max-width:520px){
  .bar-v{min-width:72px; font-size:11.5px}
  .bar-k{width:54px; font-size:12px}
}
/* 본문 표: 문장이 들어가는 칸은 줄바꿈 + 왼쪽 정렬 */
table.tbl.txt{min-width:560px}
table.tbl.txt th,table.tbl.txt td{white-space:normal; text-align:left}
table.tbl.txt td{line-height:1.55; vertical-align:top}
/* 좁은 화면에서는 문장 표를 한 줄씩 쌓아 읽기 좋게 */
@media (max-width:600px){
  table.tbl.txt{min-width:0; display:block}
  table.tbl.txt thead{display:none}
  table.tbl.txt tbody,table.tbl.txt tr,table.tbl.txt td{display:block; width:auto}
  table.tbl.txt tr{padding:11px 13px; border-bottom:1px solid #eef1f6}
  table.tbl.txt tr:last-child{border-bottom:0}
  table.tbl.txt tbody tr:nth-child(even){background:#fcfdff}
  table.tbl.txt td{border:0; padding:0 0 3px; font-size:13px}
  table.tbl.txt td:first-child{font-weight:800; color:var(--navy); font-size:14px}
  table.tbl.txt td:nth-child(2){font-weight:700; color:var(--blue-d); font-variant-numeric:normal}
  table.tbl.txt td:last-child{color:#4e5968; font-size:12.5px; line-height:1.6}
}
.hint-mobile{display:none; font-size:12px; color:var(--muted); margin:0 0 14px}
@media (max-width:600px){.hint-mobile{display:block}}
/* 사례 카드 (연말정산 3가지 케이스) */
.cases{display:grid; gap:12px; margin:0 0 18px}
@media(min-width:720px){.cases{grid-template-columns:repeat(3,1fr)}}
.case{border:1px solid var(--line); border-radius:14px; padding:15px 16px 14px; background:#fbfcfe; min-width:0}
.case .who{display:inline-block; font-size:11.5px; font-weight:800; color:var(--blue-d); background:var(--sky); border-radius:999px; padding:3px 10px; margin-bottom:9px}
.case h3{margin:0 0 8px; font-size:15px; line-height:1.45; color:var(--navy)}
.case p{font-size:13.5px; margin:0 0 10px; color:#4e5968; line-height:1.6}
.case dl{display:grid; grid-template-columns:1fr auto; gap:4px 8px; margin:0; font-size:12.5px}
.case dt{color:var(--muted); min-width:0}
.case dd{margin:0; text-align:right; font-weight:700; font-variant-numeric:tabular-nums; white-space:nowrap}
.case .res{display:flex; justify-content:space-between; align-items:baseline; gap:8px; margin-top:11px; padding-top:10px; border-top:1px dashed var(--line)}
.case .res span{font-size:12px; font-weight:700; color:var(--muted)}
.case .res b{font-size:16px; font-weight:800; color:var(--blue-d); font-variant-numeric:tabular-nums}
@media (max-width:520px){.case .res b{font-size:15px}}
"""


def main():
    core.write("assets/site.css", core.CSS + EXTRA_CSS)
    core.write("index.html", core.build_index())
    core.write("privacy.html", core.build_privacy())
    core.write("sitemap.xml", core.build_sitemap())
    for p in [LOAN, DSR, PROP, RENT, SAVE, SALARY, SEVER, SUB, CGT, YET]:
        page = core.tool_page(p)
        core.write(p["slug"] + ".html", page)
    print("done")


if __name__ == "__main__":
    main()
