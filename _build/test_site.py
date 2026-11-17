# -*- coding: utf-8 -*-
"""Verify the 11-tool portal: console errors, links, calculations, responsive layout."""
import http.server
import json
import re
import os
import socketserver
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8765
SHOTS = os.path.join(os.path.dirname(ROOT), "..", "handoffs", "🧮-11호-웹툴-연말정산-환급-계산기-제작-배포", "shots")

FAIL = []
OK = []


def check(cond, msg, extra=""):
    if cond:
        OK.append(msg)
    else:
        FAIL.append(msg + (" | " + str(extra) if extra else ""))


def pnum(text):
    v = "".join(ch for ch in text if ch.isdigit() or ch == "-")
    return float(v) if v not in ("", "-") else 0.0


def digits(text):
    """원 금액 표기('3억 6,015만 136원' 또는 '153,000원')를 숫자로."""
    t = text.replace(",", "").strip()
    if not t:
        return 0.0
    if "억" in t or "만" in t:
        total = 0.0
        for m in re.finditer(r"(\d+)억", t):
            total += int(m.group(1)) * 100000000
        for m in re.finditer(r"(\d+)만", t):
            total += int(m.group(1)) * 10000
        for m in re.finditer(r"(\d+)원", t):
            total += int(m.group(1))
        return -total if t.strip().startswith("-") or "-" in t.split("억")[0] else total
    return pnum(t)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, *a):
        pass


def serve():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        httpd.serve_forever()


# ---------------------------------------------------------------- expectations
def exp_monthly(P, rate, months):
    i = rate / 100 / 12
    return P * i / (1 - (1 + i) ** -months)


def exp_maxloan(annual_room, rate, years):
    i = rate / 100 / 12
    n = years * 12
    m = annual_room / 12
    return m * (1 - (1 + i) ** -n) / i


def exp_salary(annual, nontax_m, family, kids):
    nonTaxYear = nontax_m * 12
    taxable = annual - nonTaxYear
    base_m = taxable / 12
    np_base = min(max(base_m, 400000), 6370000)
    np = np_base * 0.0475
    hi = base_m * 0.03595
    ltc = hi * 0.1314
    ei = base_m * 0.009
    ins = np + hi + ltc + ei
    gross = taxable

    def ded(g):
        if g <= 5e6: return g * .7
        if g <= 15e6: return 3.5e6 + (g - 5e6) * .4
        if g <= 45e6: return 7.5e6 + (g - 15e6) * .15
        if g <= 100e6: return 12e6 + (g - 45e6) * .05
        return 14.75e6 + (g - 100e6) * .02

    wage = max(0, gross - ded(gross))
    taxbase = max(0, wage - 1.5e6 * (1 + family) - np * 12 - (hi + ltc) * 12 - 130000)
    br = [(14e6, .06, 0), (50e6, .15, 1.26e6), (88e6, .24, 5.76e6), (150e6, .35, 15.44e6),
          (300e6, .38, 19.94e6), (500e6, .40, 25.94e6), (1e9, .42, 35.94e6), (9e18, .45, 65.94e6)]
    calc = 0
    for lim, r, d in br:
        if taxbase <= lim:
            calc = max(0, taxbase * r - d)
            break
    credit = calc * .55 if calc <= 1.3e6 else 715000 + (calc - 1.3e6) * .3
    cap = 740000 if gross <= 33e6 else 660000 if gross <= 70e6 else 500000 if gross <= 120e6 else 200000
    credit = min(credit, cap) + kids * 150000
    decided = max(0, calc - credit)
    month_tax = decided / 12 + decided * .1 / 12
    return annual / 12 - ins - month_tax


def exp_severance(work_days, wage3, m3days):
    daily = wage3 / m3days
    return daily * 30 * (work_days / 365), daily


def exp_yet(gross, deps=2, kids=1, cc=18000000, chk=6000000, mkt=0, tr=0,
            pension=2000000, irp=0, rent=0, jeonse=0, insurance=0, medical=0, donation=0,
            marriage=False):
    """2026년 귀속 연말정산 미러 계산(페이지 JS와 동일 순서)."""
    BR = [(14000000, .06, 0), (50000000, .15, 1260000), (88000000, .24, 5760000),
          (150000000, .35, 15440000), (300000000, .38, 19940000), (500000000, .40, 25940000),
          (1000000000, .42, 35940000), (float("inf"), .45, 65940000)]

    def prog(b):
        b = int(b // 1)
        if b <= 0:
            return 0
        for lim, r, d in BR:
            if b <= lim:
                return max(0, b * r - d)

    def earned(g):
        if g <= 5000000: return g * .7
        if g <= 15000000: return 3500000 + (g - 5000000) * .4
        if g <= 45000000: return 7500000 + (g - 15000000) * .15
        if g <= 100000000: return 12000000 + (g - 45000000) * .05
        return min(20000000, 14750000 + (g - 100000000) * .02)

    m = gross / 12
    np_ = min(max(m, 400000), 6370000) * .0475 * 12
    hi = m * .03595 * 12
    hicare = hi + hi * .1314
    ed = earned(gross)
    inc = max(0, gross - ed)
    personal = 1500000 * deps

    limit = (3000000 if gross <= 70000000 else 2500000) + min(2, kids) * (500000 if gross <= 70000000 else 250000)
    floor = gross * .25
    if cc + chk + mkt + tr <= 0:
        cardded = 0
    else:
        gd = cc * .15 + chk * .30 + mkt * .40 + tr * .40
        if cc >= floor: cut = floor * .15
        elif cc + chk >= floor: cut = cc * .15 + (floor - cc) * .30
        else: cut = cc * .15 + chk * .30 + max(0, floor - cc - chk) * .40
        raw = max(0, gd - cut)
        over = max(0, raw - limit)
        extra = min(over, mkt * .40 + tr * .40, 3000000 if gross <= 70000000 else 2000000)
        cardded = min(raw, limit) + extra
    house = min(jeonse, 4000000) * .40
    base = int(max(0, inc - (personal + np_ + hicare + cardded + house)) // 1000 * 1000)
    tax = prog(base)

    def work_credit(t, g):
        if t <= 0: return 0
        c = t * .55 if t <= 1300000 else 715000 + (t - 1300000) * .3
        cap = 740000 if g <= 33000000 else 660000 if g <= 70000000 else 500000 if g <= 120000000 else 200000
        return min(c, cap)

    kc = 0 if kids <= 0 else 250000 if kids == 1 else 550000 if kids == 2 else 550000 + (kids - 2) * 400000
    prate = .15 if gross <= 55000000 else .12
    pb = min(pension, 6000000)
    pa = pb + min(irp, max(0, 9000000 - pb))
    ins = min(insurance, 1000000) * .12
    med = min(max(0, medical - gross * .03), 7000000 * max(1, deps - 1)) * .15
    don = min(donation, 10000000) * .15 + max(0, donation - 10000000) * .30
    special = ins + med + don
    rentcr = 0
    if gross <= 80000000 and rent > 0:
        rentcr = min(rent, 10000000) * (.17 if gross <= 55000000 else .15)
    if special + rentcr < 130000:
        special = 130000
        rentcr = 0
    mar = 500000 if marriage else 0
    credit = min(work_credit(tax, gross) + kc + pa * prate + special + rentcr + mar, tax)
    final = max(0, tax - credit)
    estbase = int(max(0, inc - 1500000 * deps - np_ - hicare - 130000) // 1000 * 1000)
    est_tax = prog(estbase)
    prepaid = max(0, est_tax - work_credit(est_tax, gross))
    return {"card": cardded, "limit": limit, "base": base, "tax": tax, "credit": credit,
            "final": final, "prepaid": prepaid, "refund": prepaid - final, "pen": pa * prate,
            "rent": rentcr, "kid": kc}


def main():
    t = threading.Thread(target=serve, daemon=True)
    t.start()

    from playwright.sync_api import sync_playwright

    base = f"http://127.0.0.1:{PORT}/"
    pages = ["index.html", "privacy.html"] + [s + ".html" for s in [
        "tools/loan-interest", "tools/dsr-calculator", "tools/property-tax-fee",
        "tools/rent-vs-jeonse", "tools/savings-calculator", "tools/salary-calculator",
        "tools/severance-calculator", "tools/subscription-score", "tools/capital-gains-tax",
        "tools/year-end-tax-calculator"]]

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
        page = ctx.new_page()
        errors = []
        page.on("console", lambda m: errors.append(("console", m.type, m.text)) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(("pageerror", str(e))))

        # ---- every page: load, console clean, meta, nav, links
        for path in pages:
            errors.clear()
            resp = page.goto(base + path, wait_until="load")
            check(resp.status == 200, f"{path}: HTTP 200", resp.status)
            check(not errors, f"{path}: 콘솔 에러 0건", errors)
            title = page.title()
            check(len(title) > 8, f"{path}: title", title)
            check(page.locator('link[rel="canonical"]').count() == 1, f"{path}: canonical", "")
            check(page.locator('meta[name="description"]').count() == 1, f"{path}: description", "")
            ads = page.eval_on_selector_all(
                'script[src*="adsbygoogle.js"]', "els => els.map(e => e.getAttribute('src'))")
            check(any("ca-pub-6285965398350241" in (a or "") for a in ads),
                  f"{path}: 애드센스 스크립트", ads)
            gtag = page.eval_on_selector_all(
                'script[src*="googletagmanager.com/gtag/js"]', "els => els.map(e => e.getAttribute('src'))")
            check(any("G-T4MEBSL2R8" in (a or "") for a in gtag), f"{path}: GA4 태그", gtag)
            check(page.evaluate("typeof window.gtag === 'function'"), f"{path}: gtag 함수 정의", "")
            check(page.locator('meta[property="og:title"]').count() == 1, f"{path}: og:title", "")
            navs = page.locator("header nav.tool-nav a")
            if path != "privacy.html":
                check(navs.count() == 11, f"{path}: 상단 11개 내비", navs.count())
            foot = page.locator("footer .footer-links a")
            check(foot.count() == 11, f"{path}: 하단 11개 내비", foot.count())
            # no horizontal overflow at desktop
            ow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            check(ow <= 2, f"{path}: 가로 넘침 없음(desktop)", ow)

        # ---- tool-page navigation links resolve
        tool_pages = [s for s in pages if s.startswith("tools/")]
        for path in tool_pages:
            page.goto(base + path, wait_until="load")
            hrefs = page.eval_on_selector_all(
                "header nav.tool-nav a, footer .footer-links a, .related a.card",
                "els => els.map(e => e.getAttribute('href'))")
            bad = []
            for h in set(hrefs):
                if not h:
                    continue
                if h.startswith("http"):
                    r = page.request.get(h)
                    if r.status != 200:
                        bad.append((h, r.status))
                else:
                    r = page.request.get(base + "tools/" + h)
                    if r.status != 200:
                        bad.append((h, r.status))
            check(not bad, f"{path}: 내비·관련 링크 전부 200", bad)
            check(len(set(hrefs)) == 11, f"{path}: 11개 도구 링크 모두 존재", len(set(hrefs)))

        # ---- portal cards point to the 10 tools
        page.goto(base + "index.html", wait_until="load")
        cards = page.eval_on_selector_all("a.tool-card", "els => els.map(e => e.getAttribute('href'))")
        check(len(cards) == 11, "index: 도구 카드 11개", len(cards))
        check(cards[0].startswith("https://dscookie-0422.github.io/web-ad/"), "index: 1번 기존 툴 연결", cards[0])
        check(all(c.startswith("tools/") for c in cards[1:]), "index: 2~11번 tools/ 링크", cards[1:])
        check(cards[-1] == "tools/year-end-tax-calculator.html", "index: 11번 연말정산 카드", cards[-1])

        # ---- portal screenshot
        os.makedirs(SHOTS, exist_ok=True)
        page.goto(base + "index.html", wait_until="load")
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(SHOTS, "portal-desktop.png"), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(300)
        page.screenshot(path=os.path.join(SHOTS, "portal-mobile.png"), full_page=True)
        ow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
        check(ow <= 2, "index.html: 가로 넘침 없음(mobile 390)", ow)
        page.set_viewport_size({"width": 1440, "height": 1000})

        # ---- internal link resolution
        page.goto(base + "index.html", wait_until="load")
        hrefs = page.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href'))")
        internal = sorted({h for h in hrefs if h and not h.startswith(("http", "#", "mailto"))})
        for h in internal:
            r = page.request.get(base + h)
            check(r.status == 200, f"link {h}: 200", r.status)

        # ---- loan interest
        errors.clear()
        page.goto(base + "tools/loan-interest.html", wait_until="load")
        got = digits(page.locator("#r-main").inner_text())
        exp = exp_monthly(3e8, 4.0, 360)
        check(abs(got - exp) < 2, "loan: 원리금균등 월납입 3억/4%/30년", (got, round(exp)))
        ti = digits(page.locator("#r-total-int").inner_text())
        check(abs(ti - (exp * 360 - 3e8)) < 5000, "loan: 총이자 ≈ 월납입×360−원금", (ti, round(exp*360-3e8)))
        check(page.locator("#year-body tr").count() == 30, "loan: 연도별 30행", page.locator("#year-body tr").count())
        page.fill("#rate", "0")
        page.wait_for_timeout(150)
        check(abs(digits(page.locator("#r-main").inner_text()) - 3e8 / 360) < 2, "loan: 0% 이자 방어", page.locator("#r-main").inner_text())
        page.fill("#rate", "4")
        page.select_option("#method", "principal")
        page.wait_for_timeout(150)
        exp_p = 3e8 / 360 + 3e8 * 0.04 / 12
        check(abs(digits(page.locator("#r-main").inner_text()) - exp_p) < 5, "loan: 원금균등 첫달", (page.locator("#r-main").inner_text(), round(exp_p)))
        page.select_option("#method", "bullet")
        page.wait_for_timeout(150)
        check(abs(digits(page.locator("#r-main").inner_text()) - 1e6) < 5, "loan: 만기일시 월이자", page.locator("#r-main").inner_text())
        page.select_option("#method", "graduated")
        page.wait_for_timeout(150)
        grad = digits(page.locator("#r-main").inner_text())
        check(0 < grad < exp, "loan: 체증식 첫해 < 원리금균등", (grad, round(exp)))
        page.select_option("#method", "equal")
        page.fill("#grace", "2")
        page.wait_for_timeout(200)
        check(abs(digits(page.locator("#r-main").inner_text()) - 1e6) < 2,
              "loan: 거치 2년 첫달은 이자만", page.locator("#r-main").inner_text())
        check(abs(digits(page.locator("#r-last").inner_text()) - exp_monthly(3e8, 4, 360 - 24)) < 3,
              "loan: 거치 후 월납입 336개월 재계산", (page.locator("#r-last").inner_text(), round(exp_monthly(3e8, 4, 336))))
        check("거치기간 월 이자" in page.locator("#r-main-label").inner_text(),
              "loan: 거치 라벨", page.locator("#r-main-label").inner_text())
        check(not errors, "loan: 콘솔 에러 0건", errors)
        page.fill("#grace", "0")

        # ---- dsr
        errors.clear()
        page.goto(base + "tools/dsr-calculator.html", wait_until="load")
        check("7.00%" in page.locator("#r-judged").inner_text(), "dsr: 심사금리 4%+3%", page.locator("#r-judged").inner_text())
        check("+3.00%p" in page.locator("#r-stress").inner_text(), "dsr: 스트레스 가산", page.locator("#r-stress").inner_text())
        lim = digits(page.locator("#r-main").inner_text())
        exp_lim = exp_maxloan(6e7 * 0.4, 7.0, 30)
        check(abs(lim - exp_lim) < 20000, "dsr: 한도 (6천만/수도권 변동)", (lim, round(exp_lim)))
        # 기존 신용대출 3천만 추가 → 여력 감소
        page.fill("#c-bal", "3000")
        page.wait_for_timeout(200)
        lim2 = digits(page.locator("#r-main").inner_text())
        check(lim2 < lim, "dsr: 신용대출 추가 시 한도 감소", (lim, lim2))
        # 규제 한도 초과 시 0원 안내
        page.fill("#c-bal", "30000")
        page.wait_for_timeout(200)
        check("추가 여력이 없습니다" in page.locator("#dsr-note").inner_text(), "dsr: 여력 없음 경고", page.locator("#dsr-note").inner_text()[:60])
        check(not errors, "dsr: 콘솔 에러 0건", errors)

        # ---- property tax
        errors.clear()
        page.goto(base + "tools/property-tax-fee.html", wait_until="load")
        check(abs(digits(page.locator("#r-total").inner_text()) - 6600000) < 2, "취득세: 6억 1주택 85㎡이하 660만", page.locator("#r-total").inner_text())
        check(abs(digits(page.locator("#r-br-each").inner_text()) - 2400000) < 2, "중개보수: 6억 매매 0.4% = 240만", page.locator("#r-br-each").inner_text())
        page.check("#big")
        page.wait_for_timeout(200)
        check(abs(digits(page.locator("#r-total").inner_text()) - 7800000) < 2, "취득세: 85㎡초과 농특세 0.2%", page.locator("#r-total").inner_text())
        page.check("#first")
        page.wait_for_timeout(200)
        check(abs(digits(page.locator("#r-total").inner_text()) - 5800000) < 2, "취득세: 생애최초 200만 감면", page.locator("#r-total").inner_text())
        page.fill("#price", "750000000")
        page.wait_for_timeout(200)
        rate_txt = page.locator("#r-rate").inner_text()
        check("2.00%" in rate_txt, "취득세: 7.5억 누진 2%", rate_txt)
        page.select_option("#trade", "wolse")
        page.fill("#deposit", "1000")
        page.fill("#monthly", "80")
        page.wait_for_timeout(250)
        check(abs(digits(page.locator("#r-deal").inner_text()) - 90000000) < 2, "중개보수: 월세 환산 보증금+월세×100", page.locator("#r-deal").inner_text())
        check(abs(digits(page.locator("#r-br-each").inner_text().split(" (")[0]) - 300000) < 2, "중개보수: 9천만 임대차 0.4%→한도 30만", page.locator("#r-br-each").inner_text())
        check(not errors, "취득세: 콘솔 에러 0건", errors)

        # ---- rent vs jeonse
        errors.clear()
        page.goto(base + "tools/rent-vs-jeonse.html", wait_until="load")
        j = digits(page.locator("#r-j-year").inner_text())
        w = digits(page.locator("#r-w-year").inner_text())
        check(abs(j - 13600000) < 5000, "전월세: 전세 연비용 1,360만", j)
        check(abs(w - 15900000) < 5000, "전월세: 월세 연비용 1,590만", w)
        check("전세" in page.locator("#r-main").inner_text(), "전월세: 판정(전세 유리)", page.locator("#r-main").inner_text())
        page.fill("#j-rate", "6")
        page.wait_for_timeout(200)
        check(digits(page.locator("#r-j-year").inner_text()) > w, "전월세: 금리 상승 시 전세 비용 증가", page.locator("#r-j-year").inner_text())
        check(not errors, "전월세: 콘솔 에러 0건", errors)

        # ---- savings
        errors.clear()
        page.goto(base + "tools/savings-calculator.html", wait_until="load")
        net = digits(page.locator("#r-main").inner_text())
        exp_int = 500000 * (0.035 / 12) * (12 * 13 / 2)
        exp_net = 6000000 + exp_int * (1 - 0.154)
        check(abs(net - exp_net) < 3, "적금: 12개월 단리 15.4% 실수령", (net, round(exp_net)))
        page.select_option("#kind", "deposit")
        page.fill("#lump", "10000000")
        page.wait_for_timeout(250)
        exp_dep = 10000000 + 350000 * (1 - 0.154)
        check(abs(digits(page.locator("#r-main").inner_text()) - exp_dep) < 3, "예금: 1천만 3.5% 12개월", (page.locator("#r-main").inner_text(), round(exp_dep)))
        page.select_option("#compound", "compound")
        page.wait_for_timeout(250)
        exp_comp = 10000000 + (10000000 * ((1 + 0.035 / 12) ** 12 - 1)) * (1 - 0.154)
        check(abs(digits(page.locator("#r-main").inner_text()) - exp_comp) < 5, "예금: 월복리", (page.locator("#r-main").inner_text(), round(exp_comp)))
        page.select_option("#tax", "0")
        page.wait_for_timeout(200)
        check(abs(digits(page.locator("#r-main").inner_text()) - (10000000 + 10000000 * ((1 + 0.035 / 12) ** 12 - 1))) < 5, "예금: 비과세", page.locator("#r-main").inner_text())
        check(page.locator("#tax-body tr").count() == 3, "적금: 과세 비교 3행", "")
        check(not errors, "적금: 콘솔 에러 0건", errors)

        # ---- salary
        errors.clear()
        page.goto(base + "tools/salary-calculator.html", wait_until="load")
        got = digits(page.locator("#r-main").inner_text())
        exp = exp_salary(50000000, 200000, 1, 0)
        check(abs(got - exp) < 2000, "연봉: 5천만 실수령", (got, round(exp)))
        page.fill("#salary", "3000")
        page.wait_for_timeout(200)
        got3 = digits(page.locator("#r-main").inner_text())
        exp3 = exp_salary(30000000, 200000, 1, 0)
        check(abs(got3 - exp3) < 2000, "연봉: 3천만 실수령", (got3, round(exp3)))
        page.fill("#salary", "12000")
        page.wait_for_timeout(200)
        got12 = digits(page.locator("#r-main").inner_text())
        exp12 = exp_salary(120000000, 200000, 1, 0)
        check(abs(got12 - exp12) < 3000, "연봉: 1.2억 실수령", (got12, round(exp12)))
        check(got12 > got3 * 3, "연봉: 구간별 증가 방향", (got3, got12))
        check(not errors, "연봉: 콘솔 에러 0건", errors)

        # ---- severance
        errors.clear()
        page.goto(base + "tools/severance-calculator.html", wait_until="load")
        sev = digits(page.locator("#r-main").inner_text())
        # 2021-03-02 ~ 2026-11-30
        import datetime
        wd = (datetime.date(2026, 11, 30) - datetime.date(2021, 3, 2)).days + 1
        m3 = (datetime.date(2026, 11, 30) - datetime.date(2026, 8, 30)).days
        exp_sev, daily = exp_severance(wd, 15000000, m3)
        check(abs(sev - exp_sev) < 500, "퇴직금: 5.75년 1,500만 기준", (sev, round(exp_sev)))
        check(abs(pnum(page.locator("#r-days").inner_text()) - wd) < 1, "퇴직금: 재직일수", page.locator("#r-days").inner_text())
        check(abs(digits(page.locator("#r-total-benefit").inner_text()) - 68100 * 210) < 2,
              "실업급여: 상한 68,100원·210일", page.locator("#r-total-benefit").inner_text())
        page.fill("#age", "55")
        page.wait_for_timeout(200)
        check(abs(pnum(page.locator("#r-bdays").inner_text()) - 240) < 1, "실업급여: 50세 이상 240일", page.locator("#r-bdays").inner_text())
        page.fill("#hire", "2026-06-01")
        page.wait_for_timeout(200)
        check(digits(page.locator("#r-main").inner_text()) == 0, "퇴직금: 1년 미만 0원", page.locator("#r-main").inner_text())
        check(not errors, "퇴직금: 콘솔 에러 0건", errors)

        # ---- subscription
        errors.clear()
        page.goto(base + "tools/subscription-score.html", wait_until="load")
        check("36점" in page.locator("#r-main").inner_text(), "청약: 5년+2명+7년 = 36점", page.locator("#r-main").inner_text())
        page.fill("#house-years", "15")
        page.select_option("#family", "6")
        page.fill("#account-years", "15")
        page.wait_for_timeout(250)
        check("84점" in page.locator("#r-main").inner_text(), "청약: 만점 84점", page.locator("#r-main").inner_text())
        page.fill("#house-years", "0")
        page.select_option("#family", "0")
        page.fill("#account-years", "0")
        page.wait_for_timeout(250)
        check("8점" in page.locator("#r-main").inner_text(), "청약: 최저 8점", page.locator("#r-main").inner_text())
        check(not errors, "청약: 콘솔 에러 0건", errors)

        # ---- capital gains tax
        errors.clear()
        page.goto(base + "tools/capital-gains-tax.html", wait_until="load")
        check(digits(page.locator("#r-main").inner_text()) == 0, "양도세: 1주택 12억 이하 비과세", page.locator("#r-main").inner_text())
        page.uncheck("#one-house")
        page.wait_for_timeout(200)
        gain = 7e8 - 4e8 - 12e6
        hold_years = 8 + 6 / 12  # 2018-05-10 → 2026-11-20
        lt = min(0.3, (8 + 6 / 12) * 0.02)
        base_tax = gain * (1 - lt) - 2500000
        br = [(14e6, .06, 0), (50e6, .15, 1.26e6), (88e6, .24, 5.76e6), (150e6, .35, 15.44e6),
              (300e6, .38, 19.94e6), (500e6, .40, 25.94e6), (1e9, .42, 35.94e6), (9e18, .45, 65.94e6)]
        tax = 0
        for lim_, r, d in br:
            if base_tax <= lim_:
                tax = base_tax * r - d
                break
        exp_total = tax * 1.1
        check(abs(digits(page.locator("#r-main").inner_text()) - exp_total) < 2000, "양도세: 일반 장특공제 30% 상한", (page.locator("#r-main").inner_text(), round(exp_total)))
        page.check("#one-house")
        page.fill("#sale", "1500000000")
        page.wait_for_timeout(250)
        check(digits(page.locator("#r-main").inner_text()) > 0, "양도세: 12억 초과 고가주택 과세", page.locator("#r-main").inner_text())
        page.fill("#sell-date", "2018-06-01")
        page.wait_for_timeout(250)
        check("70%" in page.locator("#r-rate-label").inner_text(), "양도세: 보유 1년 미만 70%", page.locator("#r-rate-label").inner_text())
        check(not errors, "양도세: 콘솔 에러 0건", errors)

        # ---- year-end tax refund
        errors.clear()
        page.goto(base + "tools/year-end-tax-calculator.html", wait_until="load")
        e = exp_yet(55000000)
        check(abs(digits(page.locator("#r-main").inner_text()) - e["refund"]) < 3,
              "연말정산: 기본값 환급액", (page.locator("#r-main").inner_text(), round(e["refund"])))
        check("환급" in page.locator("#r-main-label").inner_text(), "연말정산: 기본 라벨=환급", page.locator("#r-main-label").inner_text())
        check(abs(digits(page.locator("#r-base").inner_text()) - e["base"]) < 3,
              "연말정산: 과세표준", (page.locator("#r-base").inner_text(), e["base"]))
        check(abs(digits(page.locator("#r-final").inner_text()) - e["final"]) < 3,
              "연말정산: 결정세액", (page.locator("#r-final").inner_text(), round(e["final"])))
        check(abs(digits(page.locator("#r-card").inner_text()) - e["card"]) < 3,
              "연말정산: 카드 소득공제", (page.locator("#r-card").inner_text(), round(e["card"])))
        check("/ 350만" in page.locator("#r-card-use").inner_text(),
              "연말정산: 카드 한도 표시(자녀 가산 350만)", page.locator("#r-card-use").inner_text())
        check("자동 적용" in page.locator("#r-c-std").inner_text(), "연말정산: 표준세액공제 자동", page.locator("#r-c-std").inner_text())
        # 시나리오 카드와 표
        check(page.locator("#sim-body tr").count() == 5, "연말정산: 시뮬레이션 5행", page.locator("#sim-body tr").count())
        check("+" in page.locator("#sim-delta").inner_text() or "−" in page.locator("#sim-delta").inner_text(),
              "연말정산: 비교 카드 증감 표시", page.locator("#sim-delta").inner_text())
        rows = page.eval_on_selector_all("#sim-body tr", "els => els.map(e => e.innerText)")
        check(all("한도 소진" in r or "+" in r for r in rows), "연말정산: 시뮬레이션 금액 표기", rows)

        # 총급여 7,000만 → 카드 한도 300+50=350, 공제율 12%/15%
        page.fill("#gross", "7000")
        page.wait_for_timeout(250)
        e7 = exp_yet(70000000)
        check(abs(digits(page.locator("#r-main").inner_text()) - e7["refund"]) < 3,
              "연말정산: 총급여 7,000만 환급", (page.locator("#r-main").inner_text(), round(e7["refund"])))

        # 총급여 9,000만 + 월세 1,000 → 월세 세액공제 대상 아님
        page.fill("#gross", "9000")
        page.fill("#rent", "1000")
        page.wait_for_timeout(300)
        check("0원" in page.locator("#r-c-rent").inner_text(), "연말정산: 8천만 초과 월세공제 0", page.locator("#r-c-rent").inner_text())
        check("월세 세액공제 대상이 아닙니다" in page.locator("#yt-note").inner_text(), "연말정산: 월세 제외 안내", page.locator("#yt-note").inner_text()[:80])

        # 총급여 5,000만 + 월세 1,200 → 한도 1,000만 × 17% = 170만
        page.fill("#gross", "5000")
        page.wait_for_timeout(300)
        check("1,700,000" in page.locator("#r-c-rent").inner_text() and "1000만" in page.locator("#r-c-rent-base").inner_text(),
              "연말정산: 월세 1,200만 → 170만", page.locator("#r-c-rent").inner_text())

        # 연금저축 900만 → 135만 (15%)
        page.fill("#rent", "0")
        page.fill("#pension", "900")
        page.wait_for_timeout(300)
        check("1,350,000" in page.locator("#r-c-pen").inner_text(), "연말정산: 연금 900만 → 135만 공제", page.locator("#r-c-pen").inner_text())
        check("900 / 900만" in page.locator("#r-pen-use").inner_text(), "연말정산: 연금 한도 바", page.locator("#r-pen-use").inner_text())
        rows2 = page.eval_on_selector_all("#sim-body tr", "els => els.map(e => e.innerText)")
        check(all("한도 소진" in r for r in rows2 if "연금" in r), "연말정산: 연금 한도 소진 표시", rows2)

        # 카드 문턱 미달 → 공제 0
        page.fill("#pension", "0")
        page.fill("#cc", "500")
        page.fill("#chk", "200")
        page.wait_for_timeout(300)
        check(digits(page.locator("#r-card").inner_text()) == 0, "연말정산: 25% 문턱 미달 카드공제 0", page.locator("#r-card").inner_text())
        check("25%" in page.locator("#yt-note").inner_text(), "연말정산: 문턱 안내", page.locator("#yt-note").inner_text()[:90])

        # 결정세액 0 → 더 넣어도 환급 불변 안내
        page.fill("#gross", "2800")
        page.fill("#deps", "1")
        page.fill("#kids", "0")
        page.fill("#pension", "900")
        page.wait_for_timeout(300)
        check(digits(page.locator("#r-final").inner_text()) == 0, "연말정산: 저소득 결정세액 0", page.locator("#r-final").inner_text())
        check("결정세액이 0원" in page.locator("#yt-note").inner_text(), "연말정산: 결정세액 0 안내", page.locator("#yt-note").inner_text()[:90])

        # 자녀 0 → 자녀세액공제 0
        page.fill("#gross", "5500")
        page.fill("#deps", "2")
        page.fill("#pension", "200")
        page.fill("#cc", "1800")
        page.fill("#chk", "600")
        page.wait_for_timeout(300)
        check("250,000" in page.locator("#r-c-kid").inner_text(), "연말정산: 자녀 1명 25만", page.locator("#r-c-kid").inner_text())
        page.fill("#kids", "3")
        page.wait_for_timeout(300)
        check("950,000" in page.locator("#r-c-kid").inner_text(), "연말정산: 자녀 3명 95만", page.locator("#r-c-kid").inner_text())
        page.fill("#kids", "0")
        page.wait_for_timeout(300)
        check(digits(page.locator("#r-c-kid").inner_text()) == 0, "연말정산: 자녀 0명 0원", page.locator("#r-c-kid").inner_text())
        # 기납부세액 직접 입력 반영
        page.fill("#prepaid", "300")
        page.wait_for_timeout(300)
        check(digits(page.locator("#r-prepaid").inner_text()) == 3000000, "연말정산: 기납부세액 직접 입력", page.locator("#r-prepaid").inner_text())
        check(not errors, "연말정산: 콘솔 에러 0건", errors)

        # ---- mobile pass on one heavy tool page
        errors.clear()
        page.set_viewport_size({"width": 390, "height": 844})
        for path in ["tools/loan-interest.html", "tools/salary-calculator.html", "tools/capital-gains-tax.html",
                     "tools/year-end-tax-calculator.html"]:
            page.goto(base + path, wait_until="load")
            page.wait_for_timeout(300)
            ow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            check(ow <= 2, f"{path}: 가로 넘침 없음(mobile 390)", ow)
        page.goto(base + "tools/loan-interest.html", wait_until="load")
        page.wait_for_timeout(300)
        page.screenshot(path=os.path.join(SHOTS, "tool-mobile.png"), full_page=False)
        page.set_viewport_size({"width": 1440, "height": 1000})
        page.goto(base + "tools/salary-calculator.html", wait_until="load")
        page.wait_for_timeout(300)
        page.screenshot(path=os.path.join(SHOTS, "tool-desktop.png"), full_page=False)
        check(not errors, "mobile: 콘솔 에러 0건", errors)

        browser.close()

    print(f"\n== PASS {len(OK)} / FAIL {len(FAIL)} ==")
    for f in FAIL:
        print("FAIL:", f)
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
