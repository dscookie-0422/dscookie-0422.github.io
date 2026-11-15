# -*- coding: utf-8 -*-
"""Pages: 퇴직금·실업급여, 청약 가점, 양도소득세"""

SEVER_SCRIPT = r"""
var LIMIT_HI = 68100, LIMIT_LO = 66048;   // 2026년 이직자 기준 1일 상·하한

function daysBetween(a, b){ return Math.round((b-a)/86400000); }
function parseDate(id){
  var v = $(id).value;
  if(!v) return null;
  var p = v.split('-');
  return new Date(Date.UTC(+p[0], +p[1]-1, +p[2]));
}
function daysIn3Months(end){
  var start = new Date(Date.UTC(end.getUTCFullYear(), end.getUTCMonth()-3, end.getUTCDate()));
  return daysBetween(start, end);
}
function benefitDays(years, old){
  if(years < 1) return 120;
  if(years < 3) return old?180:150;
  if(years < 5) return old?210:180;
  if(years < 10) return old?240:210;
  return old?270:240;
}
function calcSever(){
  var hire = parseDate('hire'), leave = parseDate('leave');
  var pay3 = n('pay3')*10000, bonus = n('bonus')*10000, annual = n('annual')*10000;
  var age = n('age');

  if(!hire || !leave || leave <= hire){
    setText('r-main','-'); setText('r-main-sub','입사일과 퇴사일을 확인해 주세요');
    return;
  }
  var workDays = daysBetween(hire, leave) + 1;
  var workYears = workDays/365;
  var m3days = daysIn3Months(leave);
  var bonus3 = bonus*3/12, annual3 = annual*3/12;
  var wage3 = pay3 + bonus3 + annual3;
  var daily = wage3/m3days;
  var severance = daily*30*(workDays/365);
  if(workYears < 1) severance = 0;

  var baseDaily = daily;
  var benefit = Math.min(Math.max(baseDaily*0.6, LIMIT_LO), LIMIT_HI);
  var old = age >= 50;
  var bDays = benefitDays(workYears, old);
  var totalBenefit = benefit*bDays;

  setText('r-main', won(severance));
  setText('r-main-label', '예상 퇴직금');
  setText('r-main-sub', '근속 ' + pct(workYears,2) + '년(' + num(workDays) + '일) · 1일 평균임금 ' + won(daily));
  setText('r-days', num(workDays) + '일');
  setText('r-years', pct(workYears,2) + '년');
  setText('r-m3', num(m3days) + '일');
  setText('r-wage3', won(wage3));
  setText('r-daily', won(daily));
  setText('r-sever', won(severance));
  setText('r-sever-month', won(severance/12) + ' / 월 환산');

  setText('r-base-daily', won(baseDaily));
  setText('r-60', won(baseDaily*0.6));
  setText('r-benefit', won(benefit));
  setText('r-bdays', num(bDays) + '일');
  setText('r-total-benefit', eok(totalBenefit));

  var notes = '';
  if(workYears < 1) notes += '<div class="note warn">근속 1년 미만은 퇴직금이 발생하지 않습니다(계속근로기간 1년 이상 요건).</div>';
  if(baseDaily*0.6 < LIMIT_LO) notes += '<div class="note">평균임금의 60%가 하한액보다 낮아 <strong>' + num(LIMIT_LO) + '원</strong>(2026년 하한)이 적용됩니다.</div>';
  else if(baseDaily*0.6 > LIMIT_HI) notes += '<div class="note">평균임금의 60%가 상한액을 넘어 <strong>' + num(LIMIT_HI) + '원</strong>(2026년 상한)이 적용됩니다.</div>';
  if(workDays < 180) notes += '<div class="note warn">구직급여는 이직 전 18개월 중 피보험 단위기간 180일 이상이어야 받을 수 있습니다. 단순 근속일수와 다를 수 있으니 고용센터에 확인하세요.</div>';
  $('sever-note').innerHTML = notes;
}
bindCalc(calcSever);
"""

SEVER_FIELDS = r"""
<div class="row-2">
  <div class="field">
    <label for="hire">입사일</label>
    <input id="hire" type="date" value="2021-03-02">
  </div>
  <div class="field">
    <label for="leave">퇴사일</label>
    <input id="leave" type="date" value="2026-11-30">
  </div>
</div>
<div class="field">
  <label for="pay3">최근 3개월 급여 총액</label>
  <div class="input-line"><input id="pay3" type="number" value="1500" step="10" min="0" inputmode="numeric"><span class="unit">만원</span></div>
  <span class="hint">세전 기준, 3개월치 합계 (월 500만 원이면 1,500)</span>
</div>
<div class="row-2">
  <div class="field">
    <label for="bonus">연간 상여금 총액</label>
    <div class="input-line"><input id="bonus" type="number" value="0" step="10" min="0" inputmode="numeric"><span class="unit">만원</span></div>
    <span class="hint">3개월분으로 안분해 반영</span>
  </div>
  <div class="field">
    <label for="annual">연차수당 총액</label>
    <div class="input-line"><input id="annual" type="number" value="0" step="10" min="0" inputmode="numeric"><span class="unit">만원</span></div>
    <span class="hint">퇴직 전 1년분</span>
  </div>
</div>
<div class="field">
  <label for="age">퇴사일 기준 나이</label>
  <div class="input-line"><input id="age" type="number" value="35" step="1" min="15" max="80" inputmode="numeric"><span class="unit">세</span></div>
  <span class="hint">만 50세 이상이면 소정급여일수가 늘어납니다</span>
</div>
<p class="mini">3개월 급여에 상여·연차수당을 안분한 금액을 더해 1일 평균임금을 구합니다. 실제 퇴직금은 통상임금 기준과 비교해 높은 쪽으로 정산합니다.</p>
"""

SEVER_RESULTS = r"""
<div class="big">
  <span class="lbl" id="r-main-label">예상 퇴직금</span>
  <div class="val" id="r-main">-</div>
  <div class="sub" id="r-main-sub">-</div>
</div>
<dl class="kv">
  <dt>재직일수</dt><dd id="r-days">-</dd>
  <dt>근속연수</dt><dd id="r-years">-</dd>
  <dt>3개월 역일수</dt><dd id="r-m3">-</dd>
  <dt>3개월 임금총액 (상여·연차 안분)</dt><dd id="r-wage3">-</dd>
  <dt>1일 평균임금</dt><dd class="em" id="r-daily">-</dd>
  <dt><strong>퇴직금</strong></dt><dd><strong class="em" id="r-sever">-</strong></dd>
  <dt>&nbsp;└ 월 환산</dt><dd style="font-weight:400;color:#6b7684;font-size:13px" id="r-sever-month">-</dd>
</dl>
<div class="divider"></div>
<h3 style="font-size:14px;margin:0 0 10px;color:#0f2447">실업급여(구직급여) 예상</h3>
<dl class="kv">
  <dt>급여기초임금일액</dt><dd id="r-base-daily">-</dd>
  <dt>60% 금액</dt><dd id="r-60">-</dd>
  <dt>1일 구직급여</dt><dd class="em" id="r-benefit">-</dd>
  <dt>소정급여일수</dt><dd id="r-bdays">-</dd>
  <dt><strong>총 예상 수급액</strong></dt><dd><strong class="em" id="r-total-benefit">-</strong></dd>
</dl>
<div id="sever-note"></div>
<p class="mini">2026년 1월 1일 이후 이직자 기준 1일 상한 68,100원, 하한 66,048원(하루 8시간)을 적용했습니다.</p>
"""

SEVER_CONTENT = r"""
<h2>퇴직금과 실업급여, 얼마나 나올까요</h2>
<p>회사를 그만두면 두 가지 돈이 생깁니다. 회사가 주는 <strong>퇴직금</strong>과 고용보험에서 나오는 <strong>실업급여(구직급여)</strong>입니다. 두 금액은 계산 방식이 완전히 다르지만, 둘 다 &ldquo;최근 3개월 평균임금&rdquo;에서 출발합니다. 이 계산기는 평균임금을 한 번 구해 두 금액을 함께 보여 줍니다.</p>

<h2>퇴직금 계산 공식</h2>
<div class="formula">
  1일 평균임금 = (최근 3개월 임금총액 + 상여금 × 3/12 + 연차수당 × 3/12) ÷ 3개월 역일수<br>
  퇴직금 = 1일 평균임금 × 30일 × (재직일수 ÷ 365)
</div>
<p>재직일수는 입사일부터 퇴사일까지의 역일수입니다. 근속 1년이면 약 한 달치 임금이, 10년이면 약 10개월치 임금이 퇴직금으로 쌓입니다. 상여금과 연차수당은 <strong>3개월분으로 안분</strong>해 임금총액에 넣습니다. 연간 상여 1,200만 원이면 3개월분 300만 원이 3개월 임금총액에 더해집니다.</p>
<p>실제 퇴직금은 두 가지 방식으로 계산해 <strong>근로자에게 유리한 금액</strong>으로 정산합니다. 하나는 위의 평균임금 기준, 다른 하나는 통상임금(기본급+고정수당) 기준입니다. 평균임금이 통상임금보다 낮으면 통상임금으로 계산합니다. 상여금이 많거나 초과근로가 잦았다면 평균임금이 더 높아 유리합니다.</p>

<h2>퇴직금이 발생하지 않는 경우</h2>
<ul>
  <li>계속근로기간이 <strong>1년 미만</strong>인 경우 (수습기간도 근로기간에 포함됩니다)</li>
  <li>4주간 평균 근로시간이 15시간 미만인 초단시간 근로자</li>
  <li>정년 퇴직 등으로 이미 퇴직금을 받은 경우</li>
</ul>
<p>1년 이상 근무했다면 퇴직금은 법정 권리입니다. 퇴사 후 14일 이내에 지급되어야 하며, 늦어지면 지연이자가 붙습니다. 지급되지 않으면 노동청에 진정을 넣을 수 있습니다.</p>

<h2>실업급여(구직급여) 계산 공식</h2>
<div class="formula">
  1일 구직급여 = 급여기초임금일액 × 60% → 상·하한 적용<br>
  2026년 이직자: 상한 <strong>68,100원</strong> · 하한 <strong>66,048원</strong>(하루 8시간 기준)<br>
  총 수급액 = 1일 구직급여 × 소정급여일수
</div>
<p>2026년에는 최저임금이 오르면서 하한액(66,048원)이 기존 상한액(66,000원)을 넘어서는 역전이 생겼습니다. 그래서 정부가 기초일액 상한을 11만 3,500원으로 올려 상한액을 <strong>68,100원</strong>으로 조정했습니다. 2026년 1월 1일 이후 이직자에게 적용되고, 2025년 12월 31일 이전 이직자는 종전 기준(66,000원)이 적용됩니다.</p>

<h3>소정급여일수 표</h3>
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>고용보험 가입기간</th><th>50세 미만</th><th>50세 이상·장애인</th></tr></thead>
    <tbody>
      <tr><td>1년 미만</td><td>120일</td><td>120일</td></tr>
      <tr><td>1년 이상 3년 미만</td><td>150일</td><td>180일</td></tr>
      <tr><td>3년 이상 5년 미만</td><td>180일</td><td>210일</td></tr>
      <tr><td>5년 이상 10년 미만</td><td>210일</td><td>240일</td></tr>
      <tr><td>10년 이상</td><td>240일</td><td>270일</td></tr>
    </tbody>
  </table>
</div>
<p>가입기간은 이전 직장까지 합산할 수 있습니다. 다만 자격 상실 후 3년이 넘게 지났거나 그 기간으로 이미 구직급여를 받았다면 합산되지 않습니다.</p>

<h2>실업급여를 받으려면</h2>
<ul>
  <li>이직일 이전 18개월 중 피보험 단위기간이 합산 <strong>180일 이상</strong></li>
  <li>근로 의사와 능력이 있는데도 취업하지 못한 상태</li>
  <li>이직 사유가 수급자격 제한 사유가 아닐 것 — 권고사직·계약만료·정리해고는 인정되고, 정당한 사유 없는 자발적 퇴사는 원칙적으로 제외됩니다</li>
</ul>
<p>수급자격을 인정받으면 7일 대기 후 구직활동을 하며 실업인정을 받아 급여가 지급됩니다. 퇴직 후 12개월이 지나면 남은 급여는 소멸합니다.</p>

<h2>이럴 때 써 보세요</h2>
<ul>
  <li><strong>퇴사 전 자금 계획</strong> — 퇴직금과 실업급여를 합쳐 몇 달을 버틸 수 있는지 계산합니다.</li>
  <li><strong>이직 협상</strong> — 권고사직과 자발적 퇴사 중 어느 쪽이 유리한지 비교합니다.</li>
  <li><strong>퇴직금 정산 검증</strong> — 회사가 제시한 금액이 맞는지 직접 계산해 봅니다.</li>
  <li><strong>50세 전후 퇴사</strong> — 나이에 따라 소정급여일수가 30일 늘어나는 것을 확인합니다.</li>
</ul>

<h2>퇴직금 세금</h2>
<p>퇴직금은 <strong>퇴직소득세</strong>로 분리 과세됩니다. 근속연수에 따른 공제가 커서 10년 이상 근무하면 세금이 크게 줄어듭니다. 퇴직금을 IRP(개인형 퇴직연금)로 받으면 당장 세금을 내지 않고, 연금으로 수령할 때까지 과세가 이연됩니다.</p>
"""

SEVER_FAQS = [
    ("퇴직금은 어떻게 계산되나요?",
     "1일 평균임금 × 30일 × (재직일수 ÷ 365)입니다. 1일 평균임금은 최근 3개월 임금총액(상여·연차수당을 3개월분으로 안분해 포함)을 3개월 역일수로 나눈 값입니다. 월급 500만 원으로 5년 9개월(2,100일) 근무했다면 퇴직금은 약 2,814만 원입니다."),
    ("실업급여는 얼마나 받나요?",
     "퇴직 전 3개월 평균임금의 60%를 1일 기준으로 지급하되, 2026년 이직자는 하루 66,048원에서 68,100원 사이로 조정됩니다. 여기에 나이와 고용보험 가입기간에 따라 120~270일을 곱한 금액을 받습니다. 월급 500만 원, 5년 근무, 40세라면 1일 68,100원 × 210일 = 약 1,430만 원입니다."),
    ("자발적으로 퇴사하면 실업급여를 못 받나요?",
     "원칙적으로 받을 수 없지만 예외가 있습니다. 임금 체불, 직장 내 괴롭힘, 통근이 불가능한 이사, 건강 악화, 육아·간병 등 정당한 사유가 있으면 인정됩니다. 계약기간 만료, 권고사직, 정리해고는 자발적 퇴사가 아니므로 바로 대상입니다."),
    ("퇴직금을 IRP로 받으면 유리한가요?",
     "세금을 바로 내지 않고 미룰 수 있어 유리한 경우가 많습니다. 다만 IRP는 55세 이후 연금으로 받아야 세제 혜택이 유지되고, 중도 인출은 제한됩니다. 당장 목돈이 필요하다면 세금을 내고 현금으로 받는 편이 나을 수 있습니다."),
    ("3개월 급여에 상여금이 포함되나요?",
     "네. 평균임금 산정 시 3개월 임금총액에 상여금의 3/12, 연차수당의 3/12을 더합니다. 연간 상여 1,200만 원이면 300만 원이 더해져 1일 평균임금이 약 3만 3,000원 올라가고, 퇴직금은 5년 근무 기준 약 490만 원 늘어납니다."),
]

SEVER = {
    "slug": "tools/severance-calculator",
    "title": "퇴직금·실업급여 계산기 | 평균임금으로 예상 수급액 계산",
    "h1": "퇴직금·실업급여 예상액 계산기",
    "kicker": "평균임금 · 구직급여",
    "lede": "입사일과 퇴사일, 최근 3개월 급여만 넣으면 퇴직금과 실업급여 예상액이 함께 나옵니다. 상여금·연차수당 안분과 2026년 상·하한액까지 반영합니다.",
    "desc": "퇴직금과 실업급여(구직급여) 예상액을 계산합니다. 최근 3개월 평균임금, 상여금·연차수당 안분, 근속기간과 나이에 따른 소정급여일수, 2026년 상·하한액을 반영한 무료 계산기입니다.",
    "keywords": "퇴직금 계산기, 실업급여 계산기, 구직급여, 평균임금, 소정급여일수, 퇴직금 계산방법, 2026 실업급여",
    "fields": SEVER_FIELDS,
    "results": SEVER_RESULTS,
    "script": SEVER_SCRIPT,
    "content": SEVER_CONTENT,
    "faqs": SEVER_FAQS,
    "disclaimer": "이 계산기는 퇴직금과 구직급여의 공개된 산식을 적용한 추정치입니다. 실제 퇴직금은 통상임금과 평균임금 중 유리한 기준으로 정산되고, 실업급여는 고용센터의 수급자격 심사와 실업인정 결과에 따라 달라집니다. 정확한 금액은 고용24와 회사 정산 내역으로 확인하세요.",
}

# ------------------------------------------------------------------ 청약 가점
SUB_SCRIPT = r"""
function housingScore(years){
  if(years < 1) return 2;
  return Math.min(32, 2 + 2*Math.floor(years));
}
function familyScore(n){
  return Math.min(35, 5 + n*5);
}
function accountScore(years){
  var m = years*12;
  if(m < 6) return 1;
  if(m < 12) return 2;
  return Math.min(17, 2 + Math.floor(m/12));
}
function calcSub(){
  var hy = n('house-years'), fam = Math.round(n('family')), ay = n('account-years');
  var s1 = housingScore(hy), s2 = familyScore(fam), s3 = accountScore(ay);
  var total = s1+s2+s3;

  setText('r-main', total + '점');
  setText('r-main-label', '청약 가점 합계 (84점 만점)');
  setText('r-main-sub', '무주택 ' + s1 + '점 + 부양가족 ' + s2 + '점 + 통장 ' + s3 + '점');
  setText('r-s1', s1 + '점');
  setText('r-s2', s2 + '점');
  setText('r-s3', s3 + '점');
  setText('r-total', total + ' / 84점');
  setText('r-gap', Math.max(0, 84-total) + '점');
  setText('r-rate', pct(total/84*100,1) + '%');

  $('bar-s1').style.width = (s1/84*100).toFixed(1)+'%';
  $('bar-s2').style.width = (s2/84*100).toFixed(1)+'%';
  $('bar-s3').style.width = (s3/84*100).toFixed(1)+'%';

  // 최대치 대비 남은 점수 안내
  var tips = [];
  if(s1 < 32) tips.push('무주택기간이 1년 늘 때마다 <strong>2점</strong>씩 오릅니다(최대 32점).');
  if(s2 < 35) tips.push('부양가족 1명당 <strong>5점</strong>씩 오릅니다(최대 35점, 6명 이상 만점).');
  if(s3 < 17) tips.push('통장 가입기간이 1년 늘 때마다 <strong>1점</strong>씩 오릅니다(최대 17점).');
  $('sub-tips').innerHTML = tips.length ? '<div class="note">' + tips.join(' ') + '</div>' : '<div class="note good">세 항목 모두 만점입니다. 가점제에서 최상위권입니다.</div>';

  setText('r-need-years', total>=84 ? '만점 달성' : '무주택 15년 · 부양가족 6명 · 통장 15년');
}
bindCalc(calcSub);
"""

SUB_FIELDS = r"""
<div class="field">
  <label for="house-years">무주택기간</label>
  <div class="input-line"><input id="house-years" type="number" value="5" step="1" min="0" max="30" inputmode="numeric"><span class="unit">년</span></div>
  <span class="hint">만 30세부터(30세 미만은 혼인신고일부터) 계산합니다. 1년 미만은 2점</span>
  <div class="chips">
    <button type="button" data-set="house-years" data-val="0">1년 미만</button>
    <button type="button" data-set="house-years" data-val="5">5년</button>
    <button type="button" data-set="house-years" data-val="10">10년</button>
    <button type="button" data-set="house-years" data-val="15">15년</button>
  </div>
</div>
<div class="field">
  <label for="family">부양가족 수</label>
  <select id="family">
    <option value="0">0명 (5점)</option>
    <option value="1">1명 (10점)</option>
    <option value="2" selected>2명 (15점)</option>
    <option value="3">3명 (20점)</option>
    <option value="4">4명 (25점)</option>
    <option value="5">5명 (30점)</option>
    <option value="6">6명 이상 (35점)</option>
  </select>
  <span class="hint">본인과 배우자 제외, 3년 이상 같은 주민등록에 있어야 인정</span>
</div>
<div class="field">
  <label for="account-years">청약통장 가입기간</label>
  <div class="input-line"><input id="account-years" type="number" value="7" step="1" min="0" max="30" inputmode="numeric"><span class="unit">년</span></div>
  <span class="hint">6개월 미만 1점, 6개월~1년 미만 2점, 이후 1년마다 1점</span>
</div>
<p class="mini">가점제는 국민주택(공공분양·공공임대 일부)에 적용되며, 84점 만점에 최저 가점 커트라인이 있습니다. 지역·단지별 커트라인은 청약홈 공고에서 확인하세요.</p>
"""

SUB_RESULTS = r"""
<div class="big">
  <span class="lbl" id="r-main-label">청약 가점 합계 (84점 만점)</span>
  <div class="val" id="r-main">-</div>
  <div class="sub" id="r-main-sub">-</div>
</div>
<div class="bar-rows">
  <div class="bar-row"><span class="bar-k">무주택</span><div class="bar-track"><span class="bar-fill fill-s1" id="bar-s1"></span></div><span class="bar-v" id="r-s1">-</span></div>
  <div class="bar-row"><span class="bar-k">부양가족</span><div class="bar-track"><span class="bar-fill fill-s2" id="bar-s2"></span></div><span class="bar-v" id="r-s2">-</span></div>
  <div class="bar-row"><span class="bar-k">통장기간</span><div class="bar-track"><span class="bar-fill fill-s3" id="bar-s3"></span></div><span class="bar-v" id="r-s3">-</span></div>
</div>
<div class="divider"></div>
<dl class="kv">
  <dt>합계</dt><dd class="em" id="r-total">-</dd>
  <dt>만점까지 남은 점수</dt><dd id="r-gap">-</dd>
  <dt>만점 대비 비율</dt><dd id="r-rate">-</dd>
  <dt>만점 조건</dt><dd id="r-need-years">-</dd>
</dl>
<div id="sub-tips"></div>
<p class="mini">무주택기간은 만 30세가 되는 날부터(그 전에 혼인하면 혼인신고일부터) 청약할 때까지로 계산합니다. 부양가족은 3년 이상 같은 주민등록지에 있어야 인정됩니다.</p>
"""

SUB_CONTENT = r"""
<h2>청약 가점은 세 항목으로 84점</h2>
<p>청약 가점제는 <strong>무주택기간(32점) + 부양가족 수(35점) + 청약통장 가입기간(17점)</strong>으로 계산합니다. 세 항목이 만점이면 84점입니다. 서울 인기 단지의 당첨 커트라인이 60~70점대이므로, 내가 몇 점인지 정확히 아는 것이 전략의 출발점입니다.</p>

<h2>무주택기간 점수 (최대 32점)</h2>
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>무주택기간</th><th>점수</th><th>무주택기간</th><th>점수</th></tr></thead>
    <tbody>
      <tr><td>1년 미만</td><td>2점</td><td>8년</td><td>18점</td></tr>
      <tr><td>1년</td><td>4점</td><td>9년</td><td>20점</td></tr>
      <tr><td>2년</td><td>6점</td><td>10년</td><td>22점</td></tr>
      <tr><td>3년</td><td>8점</td><td>11년</td><td>24점</td></tr>
      <tr><td>4년</td><td>10점</td><td>12년</td><td>26점</td></tr>
      <tr><td>5년</td><td>12점</td><td>13년</td><td>28점</td></tr>
      <tr><td>6년</td><td>14점</td><td>14년</td><td>30점</td></tr>
      <tr><td>7년</td><td>16점</td><td>15년 이상</td><td>32점</td></tr>
    </tbody>
  </table>
</div>
<p>무주택기간은 <strong>만 30세가 되는 날</strong>부터 계산합니다. 30세 이전에 혼인했다면 혼인신고일부터입니다. 그래서 20대에 결혼한 경우가 30세 미혼보다 무주택기간이 길어질 수 있습니다. 주택을 소유한 적이 있으면 그 기간은 제외되고, 분양권·입주권도 주택으로 봅니다.</p>

<h2>부양가족 점수 (최대 35점)</h2>
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>부양가족 수</th><th>0명</th><th>1명</th><th>2명</th><th>3명</th><th>4명</th><th>5명</th><th>6명 이상</th></tr></thead>
    <tbody><tr><td>점수</td><td>5점</td><td>10점</td><td>15점</td><td>20점</td><td>25점</td><td>30점</td><td>35점</td></tr></tbody>
  </table>
</div>
<p>부양가족은 본인과 배우자를 제외한 가구원으로, <strong>3년 이상 같은 주민등록지에 등재</strong>되어 있어야 인정됩니다. 만 30세 이상 자녀, 직계존속(부모·조부모)이 대상이고, 자녀는 30세 미만이면 미혼·소득 요건을 따집니다. 태어난 자녀도 가구원 수에 포함됩니다.</p>

<h2>청약통장 가입기간 점수 (최대 17점)</h2>
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>가입기간</th><th>6개월 미만</th><th>6개월~1년</th><th>1년</th><th>2년</th><th>5년</th><th>10년</th><th>15년 이상</th></tr></thead>
    <tbody><tr><td>점수</td><td>1점</td><td>2점</td><td>3점</td><td>4점</td><td>7점</td><td>12점</td><td>17점</td></tr></tbody>
  </table>
</div>
<p>가입기간은 통장을 만든 날부터 청약 신청일까지입니다. 중간에 해지하고 다시 가입하면 기간이 초기화되므로, 당장 청약할 계획이 없어도 통장은 유지하는 것이 좋습니다. 가입 후 2년이 지나야 1순위 자격이 생기고, 매달 2만 원 이상 납입해야 합니다.</p>

<h2>가점제와 특별공급, 무엇이 유리할까</h2>
<p>가점 60점 이하라면 가점제로는 인기 단지 당첨이 어렵습니다. 이때는 <strong>특별공급</strong>을 노리는 편이 현실적입니다.</p>
<ul>
  <li><strong>신혼부부 특공</strong> — 혼인 7년 이내(또는 3년 이내 자녀), 소득·자산 요건 충족 시. 물량이 가장 많습니다.</li>
  <li><strong>생애최초 특공</strong> — 본인·배우자가 주택을 소유한 적 없는 무주택 세대. 소득 요건(도시근로자 월평균소득 130~160%)을 봅니다.</li>
  <li><strong>다자녀 특공</strong> — 미성년 자녀 3명 이상. 소득 요건이 상대적으로 넉넉합니다.</li>
  <li><strong>노부모부양 특공</strong> — 만 65세 이상 직계존속을 3년 이상 부양. 가점 84점 중 부양가족 항목이 유리합니다.</li>
</ul>
<p>특별공급은 청약통장 가입기간과 무관하게 소득·자산·자녀 수로 당첨자를 정하는 경우가 많아, 가점이 낮아도 기회가 있습니다. 다만 특공에 당첨되면 5년간 재당첨이 제한되므로 신중해야 합니다.</p>

<h2>가점을 올리는 현실적인 방법</h2>
<ul>
  <li><strong>무주택기간은 시간이 답</strong> — 1년에 2점씩 오릅니다. 집을 사면 무주택기간이 리셋되므로, 청약을 노린다면 매수 시점을 신중히 정하세요.</li>
  <li><strong>부양가족 등재</strong> — 부모님을 3년 이상 함께 등재하면 5점이 오릅니다. 실제 거주가 전제입니다.</li>
  <li><strong>통장은 해지하지 마세요</strong> — 1년에 1점, 15년이면 17점입니다. 납입금은 월 2만 원 이상이면 됩니다.</li>
  <li><strong>지역·단지 조정</strong> — 같은 점수라도 경쟁률이 낮은 지역·단지를 노리면 당첨 확률이 올라갑니다.</li>
</ul>
"""

SUB_FAQS = [
    ("청약 가점 84점은 어떻게 구성되나요?",
     "무주택기간 32점, 부양가족 수 35점, 청약통장 가입기간 17점으로 총 84점입니다. 무주택기간은 1년마다 2점(1년 미만 2점), 부양가족은 1명마다 5점(0명 5점), 통장은 1년마다 1점(6개월 미만 1점)입니다."),
    ("무주택기간은 언제부터 계산하나요?",
     "만 30세가 되는 날부터입니다. 30세 이전에 혼인했다면 혼인신고일부터 계산합니다. 주택을 소유한 기간은 제외되며, 분양권·입주권도 주택 소유로 봅니다. 30세 이전 미혼이라면 30세 생일 전까지는 무주택기간이 0입니다."),
    ("부양가족은 누구까지 인정되나요?",
     "본인과 배우자를 제외한 가구원으로, 3년 이상 같은 주민등록지에 등재되어 있어야 합니다. 부모·조부모 같은 직계존속과 30세 이상 자녀가 대상입니다. 30세 미만 자녀는 미혼이고 소득이 없어야 하며, 태어난 자녀도 포함됩니다."),
    ("가점이 낮으면 청약은 포기해야 하나요?",
     "가점제에서는 불리하지만 특별공급을 노릴 수 있습니다. 신혼부부·생애최초·다자녀·노부모부양 특공은 가점 대신 소득·자산·자녀 수로 당첨자를 정합니다. 청약통장 가입기간 2년과 납입 횟수 요건만 갖추면 신청할 수 있으니, 가점이 낮다면 특공 물량이 많은 단지를 노리는 편이 현실적입니다."),
    ("청약통장을 해지하면 어떻게 되나요?",
     "가입기간이 초기화됩니다. 다시 가입하면 1순위 자격을 위해 2년을 기다려야 하고, 그동안 쌓은 가점 17점도 사라집니다. 당장 청약 계획이 없어도 통장은 유지하고 월 2만 원 이상 납입을 이어가는 것이 좋습니다. 다만 1순위 요건은 지역별로 납입 횟수(24회 등)와 금액 조건이 있으니 청약홈에서 확인하세요."),
]

SUB = {
    "slug": "tools/subscription-score",
    "title": "청약 가점 계산기 | 무주택기간·부양가족·통장 84점 만점",
    "h1": "청약 가점 계산기",
    "kicker": "무주택기간 · 부양가족 · 통장기간",
    "lede": "내 청약 가점이 몇 점인지, 만점까지 무엇이 부족한지 10초 만에 확인하세요. 무주택기간 32점, 부양가족 35점, 통장 가입기간 17점을 항목별로 계산합니다.",
    "desc": "청약 가점을 계산합니다. 무주택기간(32점)·부양가족 수(35점)·청약통장 가입기간(17점) 84점 만점 기준으로 내 점수와 부족한 항목을 확인하고 특별공급 자격까지 안내합니다.",
    "keywords": "청약 가점 계산기, 청약 가점, 무주택기간 점수, 부양가족 점수, 청약통장 가입기간, 84점 만점, 특별공급 자격",
    "fields": SUB_FIELDS,
    "results": SUB_RESULTS,
    "script": SUB_SCRIPT,
    "content": SUB_CONTENT,
    "faqs": SUB_FAQS,
    "disclaimer": "가점 계산은 국민주택 가점제 기준이며, 민간분양 가점제(무주택기간 32점·부양가족 35점·통장 17점 동일)와 일부 항목이 다를 수 있습니다. 청약 자격과 특별공급 요건은 청약홈 공고문과 해당 지역의 기준을 확인하세요.",
}

# ------------------------------------------------------------------ 양도소득세
CGT_SCRIPT = r"""
function parseD(id){ var v=$(id).value; if(!v) return null; var p=v.split('-'); return new Date(Date.UTC(+p[0], +p[1]-1, +p[2])); }
function monthsBetween(a,b){
  var m = (b.getUTCFullYear()-a.getUTCFullYear())*12 + (b.getUTCMonth()-a.getUTCMonth());
  if(b.getUTCDate() < a.getUTCDate()) m -= 1;
  return Math.max(0, m);
}
function bracketTax2(base){
  var b = [[14000000,0.06,0],[50000000,0.15,1260000],[88000000,0.24,5760000],
           [150000000,0.35,15440000],[300000000,0.38,19940000],[500000000,0.40,25940000],
           [1000000000,0.42,35940000],[Infinity,0.45,65940000]];
  for(var k=0;k<b.length;k++){ if(base <= b[k][0]) return Math.max(0, base*b[k][1]-b[k][2]); }
  return 0;
}
function calcCgt(){
  var buy = n('buy'), sale = n('sale'), cost = n('cost');
  var bd = parseD('buy-date'), sd = parseD('sell-date');
  var one = $('one-house').checked, resYears = n('res-years');
  var multi = $('multi').value;

  if(!bd || !sd || sd <= bd){ setText('r-main','-'); setText('r-main-sub','취득일과 양도일을 확인해 주세요'); return; }

  var months = monthsBetween(bd, sd);
  var holdYears = months/12;
  var gain = sale - buy - cost;
  if(gain < 0) gain = 0;

  var highPrice = one && sale > 1200000000;
  var taxableGain = gain;
  if(highPrice) taxableGain = gain*((sale-1200000000)/sale);

  // 장기보유특별공제
  var ltRate = 0;
  if(holdYears >= 3){
    if(one && resYears >= 2){
      ltRate = Math.min(0.8, Math.min(10, holdYears)*0.04 + Math.min(10, resYears)*0.04);
    } else if(!one) {
      ltRate = Math.min(0.3, holdYears*0.02);
    }
  }
  var ltDed = taxableGain*ltRate;
  var basic = 2500000;
  var taxBase = Math.max(0, taxableGain - ltDed - basic);

  // 비과세: 1세대1주택, 12억 이하, 2년 이상 보유
  var exempt = one && sale <= 1200000000 && holdYears >= 2;
  var tax = 0, rateLabel = '', surcharge = 0;
  if(exempt){
    tax = 0; rateLabel = '비과세 (1세대1주택 · 12억 원 이하 · 2년 이상 보유)';
  } else {
    var rate;
    if(holdYears < 1){ rate = 0.7; rateLabel = '70% (보유 1년 미만)'; }
    else if(holdYears < 2){ rate = 0.6; rateLabel = '60% (보유 1~2년)'; }
    else { rate = 0; rateLabel = '기본세율 6~45% 누진'; }
    if(multi==='two') surcharge = 0.10;
    if(multi==='three') surcharge = 0.20;
    if(rate > 0){ tax = Math.max(0, taxBase*(rate+surcharge)); }
    else { tax = Math.max(0, taxableGain>0 ? (bracketTax2(taxBase) + taxBase*surcharge) : 0); }
    if(surcharge>0) rateLabel += ' + 중과 ' + pct(surcharge*100,0) + '%p';
  }
  var local = tax*0.1;
  var total = tax + local;

  setText('r-main', won(total));
  setText('r-main-label', '예상 양도소득세 (지방소득세 포함)');
  setText('r-main-sub', exempt ? '1세대1주택 비과세 요건을 충족합니다' : ('보유 ' + pct(holdYears,2) + '년 · 과세표준 ' + eok(taxBase)));
  setText('r-hold', pct(holdYears,2) + '년 (' + num(months) + '개월)');
  setText('r-gain', won(gain));
  setText('r-taxable-gain', won(taxableGain) + (highPrice ? ' (고가주택 안분)' : ''));
  setText('r-lt-rate', pct(ltRate*100,1)+'%');
  setText('r-lt', '-' + won(ltDed));
  setText('r-base', won(taxBase));
  setText('r-rate-label', rateLabel);
  setText('r-tax', won(tax));
  setText('r-local', won(local));
  setText('r-total', won(total));
  setText('r-eff', pct(total/sale*100,2) + '%');

  var notes = '';
  if(exempt) notes = '<div class="note good"><strong>비과세로 계산되었습니다.</strong> 1세대1주택자가 12억 원 이하 주택을 2년 이상 보유하고 양도하면 양도소득세가 없습니다. 다만 취득 후 2년 이상 거주 요건이 적용되는 조정대상지역 취득분은 거주기간도 확인해야 합니다.</div>';
  else if(holdYears < 2) notes = '<div class="note warn">보유 2년 미만 주택은 60~70%의 단일세율이 적용되어 세 부담이 매우 큽니다. 매도 시점을 조정할 여지가 있는지 검토하세요.</div>';
  else if(highPrice) notes = '<div class="note">양도가액이 12억 원을 넘는 고가주택이라 전체 차익 중 12억 원 초과분에 해당하는 부분만 과세했습니다. 장기보유특별공제는 보유·거주 기간에 따라 최대 80%까지 적용됩니다.</div>';
  else notes = '<div class="note">장기보유특별공제를 반영했습니다. 1세대1주택은 보유 연 4%(최대 40%) + 거주 연 4%(최대 40%)로 최대 80%까지 공제됩니다.</div>';
  $('cgt-note').innerHTML = notes;
}
bindCalc(calcCgt);
"""

CGT_FIELDS = r"""
<div class="row-2">
  <div class="field">
    <label for="buy">취득가액</label>
    <div class="input-line"><input id="buy" type="number" value="400000000" step="1000000" min="0" inputmode="numeric"><span class="unit">원</span></div>
  </div>
  <div class="field">
    <label for="sale">양도가액</label>
    <div class="input-line"><input id="sale" type="number" value="700000000" step="1000000" min="0" inputmode="numeric"><span class="unit">원</span></div>
  </div>
</div>
<div class="row-2">
  <div class="field">
    <label for="buy-date">취득일</label>
    <input id="buy-date" type="date" value="2018-05-10">
  </div>
  <div class="field">
    <label for="sell-date">양도일</label>
    <input id="sell-date" type="date" value="2026-11-20">
  </div>
</div>
<div class="field">
  <label for="cost">필요경비</label>
  <div class="input-line"><input id="cost" type="number" value="12000000" step="100000" min="0" inputmode="numeric"><span class="unit">원</span></div>
  <span class="hint">취득세·중개보수·법무사비·수리비 등 (취득가의 3~5% 수준)</span>
</div>
<div class="divider" style="margin:18px 0"></div>
<label class="switch"><input type="checkbox" id="one-house" checked> 1세대 1주택 (보유 2년 이상, 12억 원 이하 비과세)</label>
<div class="row-2" style="margin-top:12px">
  <div class="field">
    <label for="res-years">거주기간</label>
    <div class="input-line"><input id="res-years" type="number" value="4" step="1" min="0" max="50" inputmode="numeric"><span class="unit">년</span></div>
    <span class="hint">1세대1주택 장특공제에 반영</span>
  </div>
  <div class="field">
    <label for="multi">다주택 중과</label>
    <select id="multi">
      <option value="none" selected>해당 없음</option>
      <option value="two">조정대상지역 2주택 (+10%p)</option>
      <option value="three">조정대상지역 3주택 이상 (+20%p)</option>
    </select>
  </div>
</div>
<p class="mini">입력한 값은 브라우저에서만 계산되며 서버로 전송되지 않습니다. 실제 신고는 세무 대리인과 상담하세요.</p>
"""

CGT_RESULTS = r"""
<div class="big">
  <span class="lbl" id="r-main-label">예상 양도소득세 (지방소득세 포함)</span>
  <div class="val" id="r-main">-</div>
  <div class="sub" id="r-main-sub">-</div>
</div>
<dl class="kv">
  <dt>보유기간</dt><dd id="r-hold">-</dd>
  <dt>양도차익</dt><dd id="r-gain">-</dd>
  <dt>과세대상 차익</dt><dd id="r-taxable-gain">-</dd>
  <dt>장기보유특별공제율</dt><dd id="r-lt-rate">-</dd>
  <dt>장기보유특별공제</dt><dd class="good" id="r-lt">-</dd>
  <dt>과세표준 (기본공제 250만 원)</dt><dd id="r-base">-</dd>
  <dt>적용 세율</dt><dd id="r-rate-label" style="font-size:13px">-</dd>
  <dt>산출세액</dt><dd id="r-tax">-</dd>
  <dt>지방소득세 (10%)</dt><dd id="r-local">-</dd>
  <dt><strong>총 납부세액</strong></dt><dd><strong class="em" id="r-total">-</strong></dd>
  <dt>양도가 대비 실효세율</dt><dd id="r-eff">-</dd>
</dl>
<div id="cgt-note"></div>
<p class="mini">기본공제 250만 원, 장기보유특별공제, 고가주택(12억 원 초과) 안분, 지방소득세 10%를 반영했습니다. 개인별 감면·다주택 중과 유예·주택 수 판정은 반영하지 않았습니다.</p>
"""

CGT_CONTENT = r"""
<h2>집을 팔면 세금이 얼마나 나갈까요</h2>
<p>양도소득세는 <strong>판 가격에서 산 가격과 필요경비를 뺀 차익</strong>에 붙는 세금입니다. 1세대1주택자가 12억 원 이하 주택을 2년 이상 보유하고 팔면 비과세이지만, 그 밖의 경우에는 차익의 6~45%가 과세됩니다. 보유 2년 미만이면 60~70%의 단일세율이 적용되어 세 부담이 확 커집니다.</p>

<h2>계산 순서와 공식</h2>
<div class="formula">
  양도차익 = 양도가액 − 취득가액 − 필요경비<br>
  과세표준 = (양도차익 − 장기보유특별공제) − 기본공제 250만 원<br>
  산출세액 = 과세표준 × 세율 − 누진공제 (+ 다주택 중과)<br>
  총 납부세액 = 산출세액 + 지방소득세(산출세액의 10%)
</div>
<p>필요경비에는 취득세, 중개보수, 법무사 비용, 등기 비용, 그리고 양도가액을 높이기 위한 수리비(자본적 지출)가 들어갑니다. 취득가의 3~5% 정도를 잡으면 대략 맞습니다. 영수증이 있어야 인정되므로 계약서·영수증을 보관하세요.</p>

<h3>장기보유특별공제</h3>
<p>오래 보유한 사람에게 차익의 일부를 빼 주는 제도입니다.</p>
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>구분</th><th>공제율</th><th>요건</th></tr></thead>
    <tbody>
      <tr><td>1세대 1주택</td><td>보유 연 4% (최대 40%) + 거주 연 4% (최대 40%) = <strong>최대 80%</strong></td><td>3년 이상 보유, 2년 이상 거주(조정대상지역)</td></tr>
      <tr><td>일반 주택</td><td>3년 이상 보유 시 연 2%, 최대 30%</td><td>보유기간만 반영</td></tr>
    </tbody>
  </table>
</div>
<p>1세대1주택이라도 <strong>거주하지 않으면</strong> 거주분 40%를 받지 못해 공제율이 최대 40%로 떨어집니다. 8년 보유·8년 거주면 64%, 10년 보유·10년 거주면 80%가 됩니다.</p>

<h3>고가주택(12억 원 초과)은 어떻게 과세되나요</h3>
<p>1세대1주택이라도 양도가액이 12억 원을 넘으면 고가주택으로 보아 <strong>12억 원 초과분에 해당하는 차익만</strong> 과세합니다. 계산식은 <code>양도차익 × (양도가액 − 12억) ÷ 양도가액</code>입니다. 15억 원에 팔아 차익이 6억 원이라면 과세대상은 6억 × 3억/15억 = 1억 2,000만 원입니다.</p>

<h2>세율</h2>
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>과세표준</th><th>세율</th><th>누진공제</th></tr></thead>
    <tbody>
      <tr><td>1,400만 원 이하</td><td>6%</td><td>0</td></tr>
      <tr><td>1,400만 ~ 5,000만 원</td><td>15%</td><td>126만 원</td></tr>
      <tr><td>5,000만 ~ 8,800만 원</td><td>24%</td><td>576만 원</td></tr>
      <tr><td>8,800만 ~ 1억 5,000만 원</td><td>35%</td><td>1,544만 원</td></tr>
      <tr><td>1억 5,000만 ~ 3억 원</td><td>38%</td><td>1,994만 원</td></tr>
      <tr><td>3억 ~ 5억 원</td><td>40%</td><td>2,594만 원</td></tr>
      <tr><td>5억 ~ 10억 원</td><td>42%</td><td>3,594만 원</td></tr>
      <tr><td>10억 원 초과</td><td>45%</td><td>6,594만 원</td></tr>
    </tbody>
  </table>
</div>
<p>보유 1년 미만은 70%, 1년 이상 2년 미만은 60%의 단일세율이 적용됩니다. 조정대상지역 다주택자는 기본세율에 2주택 +10%p, 3주택 이상 +20%p가 더해집니다. 다만 중과 유예 조치가 반복 연장되어 왔으므로 양도 시점의 시행 여부를 확인해야 합니다.</p>

<h2>이럴 때 써 보세요</h2>
<ul>
  <li><strong>매도 전 세금 가늠</strong> — 양도가액을 바꿔 가며 세금이 얼마나 달라지는지 확인합니다.</li>
  <li><strong>보유기간 2년 경계</strong> — 1년 11개월과 2년 1개월을 각각 넣어 세금 차이를 봅니다. 60%와 기본세율의 차이가 큽니다.</li>
  <li><strong>1세대1주택 비과세 판단</strong> — 12억 원 이하인지, 보유 2년을 넘겼는지 확인합니다.</li>
  <li><strong>거주기간의 가치</strong> — 거주기간을 0년과 5년으로 바꿔 장특공제 차이를 확인합니다.</li>
</ul>

<h2>신고와 납부</h2>
<p>양도소득세는 양도일이 속하는 달의 말일부터 <strong>2개월 이내</strong>에 신고·납부해야 합니다. 기한을 넘기면 무신고 가산세 20%와 납부지연 가산세가 붙습니다. 1세대1주택 비과세라도 요건을 확인하기 위해 신고하는 것이 안전하며, 예정신고 후에는 분양권·주식 등 다른 양도 건과 합산해 다음 해 5월에 확정신고합니다.</p>
"""

CGT_FAQS = [
    ("1세대1주택이면 양도소득세가 무조건 없나요?",
     "아니요. 12억 원 이하, 2년 이상 보유 요건을 모두 충족해야 비과세입니다. 12억 원을 넘으면 초과분에 비례해 과세되고, 조정대상지역에서 취득했다면 2년 이상 거주 요건도 필요합니다. 1주택이라도 보유 2년을 채우지 못하면 60~70%의 단일세율이 적용됩니다."),
    ("장기보유특별공제는 얼마나 받을 수 있나요?",
     "1세대1주택은 보유 연 4%(최대 40%)와 거주 연 4%(최대 40%)를 합쳐 최대 80%까지 공제됩니다. 10년 보유·10년 거주가 만점 조건입니다. 일반 주택은 3년 이상 보유 시 연 2%, 최대 30%입니다. 거주하지 않은 1주택은 40%까지만 받을 수 있습니다."),
    ("필요경비에는 무엇이 들어가나요?",
     "취득세, 중개보수, 법무사·등기 비용, 그리고 양도가액을 높이는 수리비(자본적 지출)가 포함됩니다. 취득가액의 3~5% 수준이면 대략 맞습니다. 다만 단순 수선·도배 같은 유지비는 인정되지 않고, 영수증·계약서 같은 증빙이 있어야 합니다."),
    ("다주택 중과세는 지금도 적용되나요?",
     "법령상 조정대상지역 2주택은 기본세율 +10%p, 3주택 이상은 +20%p가 적용됩니다. 다만 정부가 중과 유예를 반복 연장해 왔기 때문에 실제 적용 여부는 양도 시점의 조치에 따라 달라집니다. 이 계산기의 중과 선택은 적용된다고 가정한 값이니, 정확한 판단은 세무사와 상담하세요."),
    ("양도소득세는 언제 신고하나요?",
     "양도일이 속하는 달의 말일부터 2개월 이내에 신고·납부합니다. 예를 들어 11월 20일에 잔금을 치렀다면 다음 해 1월 31일까지입니다. 기한을 넘기면 무신고 가산세 20%와 납부지연 가산세가 붙으므로, 매도 전에 세금을 미리 계산해 두는 것이 안전합니다."),
]

CGT = {
    "slug": "tools/capital-gains-tax",
    "title": "양도소득세 간이 계산기 | 1세대1주택·장기보유특별공제 반영",
    "h1": "양도소득세 간이 계산기",
    "kicker": "참고용 간이 추정",
    "lede": "취득가·양도가·보유기간만 넣으면 양도소득세 규모를 미리 가늠할 수 있습니다. 1세대1주택 비과세, 12억 원 초과 고가주택 안분, 장기보유특별공제를 반영합니다.",
    "desc": "양도소득세를 간이 추정합니다. 취득가·양도가·보유기간·필요경비로 양도차익을 계산하고 1세대1주택 비과세, 고가주택 안분, 장기보유특별공제(최대 80%), 지방소득세까지 반영합니다.",
    "keywords": "양도소득세 계산기, 양도세 계산, 1세대1주택 비과세, 장기보유특별공제, 고가주택 12억, 다주택 중과, 양도세율",
    "fields": CGT_FIELDS,
    "results": CGT_RESULTS,
    "script": CGT_SCRIPT,
    "content": CGT_CONTENT,
    "faqs": CGT_FAQS,
    "disclaimer": "이 계산기는 참고용 간이 추정입니다. 실제 양도소득세는 취득·양도 시점의 법령, 주택 수 판정, 조정대상지역 여부, 중과 유예, 감면, 필요경비 증빙, 보유·거주기간 산정 방식에 따라 크게 달라집니다. 신고 전 반드시 세무 대리인과 상담하세요.",
}
