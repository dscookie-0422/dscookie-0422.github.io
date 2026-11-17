# -*- coding: utf-8 -*-
"""연말정산 계산기 JS를 quickjs로 실행해 기대값과 대조한다(브라우저 없이 로직 검증).

로컬 Chromium이 시스템 라이브러리 부재로 뜨지 않는 환경에서도 계산 로직을 검증하기 위한 보조 테스트.
`python3 _build/test_logic_quickjs.py`
"""
import json
import os
import re
import sys

import quickjs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_site import exp_yet  # noqa: E402  (기대값은 동일 미러 사용)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "tools", "year-end-tax-calculator.html")

PRELUDE = r"""
var __els = {};
function __el(id){
  if(!__els[id]) __els[id] = {id:id, value:'', textContent:'', innerHTML:'', checked:false,
                              tagName:'DIV', style:{}};
  return __els[id];
}
var document = {
  getElementById: __el,
  querySelectorAll: function(){ return {forEach:function(){}}; }
};
"""

DRIVER = r"""
function __run(v){
  var ids = ['gross','deps','kids','cc','chk','mkt','tr','pension','irp','rent','jeonse',
             'insurance','medical','donation','prepaid'];
  for(var k=0;k<ids.length;k++){ __el(ids[k]).value = (v[ids[k]]===undefined? '' : String(v[ids[k]])); }
  __el('married').checked = !!v.married;
  calcYearEnd();
  return {
    main: __el('r-main').textContent,
    label: __el('r-main-label').textContent,
    sub: __el('r-main-sub').textContent,
    base: __el('r-base').textContent,
    tax: __el('r-tax').textContent,
    credit: __el('r-credit').textContent,
    fin: __el('r-final').textContent,
    prepaid: __el('r-prepaid').textContent,
    card: __el('r-card').textContent,
    cardUse: __el('r-card-use').textContent,
    penUse: __el('r-pen-use').textContent,
    penCredit: __el('r-c-pen').textContent,
    kidCredit: __el('r-c-kid').textContent,
    rentCredit: __el('r-c-rent').textContent,
    std: __el('r-c-std').textContent,
    note: __el('yt-note').innerHTML,
    simNow: __el('sim-now').textContent,
    simNext: __el('sim-next').textContent,
    simDelta: __el('sim-delta').textContent,
    simRows: __el('sim-body').innerHTML
  };
}
"""


def num(text):
    """'1,026,200원' / '−12,500,000원' / '350만' → 숫자(만원 단위는 10000 곱하지 않고 그대로)."""
    t = str(text).replace(",", "").replace("−", "").replace("-", "")
    m = re.findall(r"\d+(?:\.\d+)?", t)
    return float(m[0]) if m else 0.0


def main():
    html = open(PAGE, encoding="utf-8").read()
    scripts = re.findall(r"<script>\n(.*?)\n</script>", html, re.S)
    assert scripts, "inline script not found"
    page_js = scripts[-1]
    assert "function calcYearEnd" in page_js, "calculator script not found"

    ctx = quickjs.Context()
    ctx.eval(PRELUDE + page_js + DRIVER)

    base = {"gross": 5500, "deps": 2, "kids": 1, "cc": 1800, "chk": 600, "mkt": 0, "tr": 0,
            "pension": 200, "irp": 0, "rent": 0, "jeonse": 0, "insurance": 0, "medical": 0,
            "donation": 0, "married": False, "prepaid": ""}

    scenarios = [
        # (이름, 입력 dict, 기대 계산 인자)
        ("기본값", {}, dict(gross=55000000)),
        ("총급여 7,000만", {"gross": 7000}, dict(gross=70000000)),
        ("총급여 3,000만", {"gross": 3000}, dict(gross=30000000)),
        ("총급여 1.2억", {"gross": 12000}, dict(gross=120000000)),
        ("자녀 0명", {"kids": 0}, dict(gross=55000000, kids=0)),
        ("자녀 3명", {"kids": 3}, dict(gross=55000000, kids=3)),
        ("부양가족 4명", {"deps": 4}, dict(gross=55000000, deps=4)),
        ("연금저축 900만", {"pension": 900}, dict(gross=55000000, pension=9000000)),
        ("연금저축 600 + IRP 500", {"pension": 600, "irp": 500}, dict(gross=55000000, pension=6000000, irp=5000000)),
        ("월세 1,200만", {"rent": 1200}, dict(gross=55000000, rent=12000000)),
        ("총급여 9,000만 + 월세 1,000만", {"gross": 9000, "rent": 1000},
         dict(gross=90000000, rent=10000000)),
        ("카드 문턱 미달", {"cc": 500, "chk": 200}, dict(gross=55000000, cc=5000000, chk=2000000)),
        ("전통시장·대중교통", {"mkt": 200, "tr": 150}, dict(gross=55000000, mkt=2000000, tr=1500000)),
        ("보험·의료비·기부금", {"insurance": 100, "medical": 300, "donation": 50},
         dict(gross=55000000, insurance=1000000, medical=3000000, donation=500000)),
        ("결혼세액공제", {"married": True}, dict(gross=55000000, marriage=True)),
        ("전세대출 원리금 500만", {"jeonse": 500}, dict(gross=55000000, jeonse=5000000)),
        ("결정세액 0원", {"gross": 2800, "deps": 1, "kids": 0, "pension": 900},
         dict(gross=28000000, deps=1, kids=0, pension=9000000)),
        ("기납부세액 직접 입력", {"prepaid": 300}, dict(gross=55000000)),
    ]

    fails = []
    for name, over, kwargs in scenarios:
        v = dict(base)
        v.update(over)
        out = json.loads(ctx.eval("JSON.stringify(__run(%s))" % json.dumps(v, ensure_ascii=False)))
        exp = exp_yet(**kwargs)

        def close(a, b, tol=3):
            return abs(a - b) <= tol

        checks = [
            ("과세표준", num(out["base"]), exp["base"]),
            ("산출세액", num(out["tax"]), exp["tax"]),
            ("세액공제", num(out["credit"]), exp["credit"]),
            ("결정세액", num(out["fin"]), exp["final"]),
            ("카드공제", num(out["card"]), exp["card"]),
        ]
        if "prepaid" not in over:
            checks.append(("기납부세액", num(out["prepaid"]), exp["prepaid"]))
            checks.append(("환급액", num(out["main"]), abs(exp["refund"])))
        else:
            checks.append(("기납부세액(입력)", num(out["prepaid"]), 3000000))
            checks.append(("환급액(입력)", num(out["main"]), abs(3000000 - exp["final"])))

        bad = [(k, got, want) for k, got, want in checks if not close(got, want)]
        print(("FAIL " if bad else "ok   ") + name + " | 환급 " + out["main"] +
              " · 결정세액 " + out["fin"] + " · 카드 " + out["card"])
        if bad:
            fails.append((name, bad))

    # 시뮬레이션·표준세액공제 등 표시값 점검
    v = dict(base)
    v.update({})
    out = json.loads(ctx.eval("JSON.stringify(__run(%s))" % json.dumps(v, ensure_ascii=False)))
    extra = []
    if "자동 적용" not in out["std"]:
        extra.append(("표준세액공제", out["std"]))
    if out["simRows"].count("<tr>") != 5:
        extra.append(("시뮬레이션 행 수", out["simRows"].count("<tr>")))
    if "+" not in out["simDelta"] and "−" not in out["simDelta"]:
        extra.append(("시뮬레이션 증감", out["simDelta"]))
    if "350만" not in out["cardUse"]:
        extra.append(("카드 한도 표시", out["cardUse"]))
    if extra:
        fails.append(("표시값", extra))

    print()
    if fails:
        print("== FAIL ==")
        for name, bad in fails:
            print(name, bad)
        sys.exit(1)
    print("== PASS: %d 시나리오 전부 일치 ==" % len(scenarios))


if __name__ == "__main__":
    main()
