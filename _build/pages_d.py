# -*- coding: utf-8 -*-
"""Pages: 2026 연말정산 환급금·세액공제 모의계산기"""

YET_SCRIPT = r"""
var YT_BR = [[14000000,0.06,0],[50000000,0.15,1260000],[88000000,0.24,5760000],
             [150000000,0.35,15440000],[300000000,0.38,19940000],[500000000,0.40,25940000],
             [1000000000,0.42,35940000],[Infinity,0.45,65940000]];
var YT_CAP = [[33000000,740000],[70000000,660000],[120000000,500000],[Infinity,200000]];

function progTax(base){
  base = Math.floor(base);
  if(base <= 0) return 0;
  for(var k=0;k<YT_BR.length;k++){
    if(base <= YT_BR[k][0]) return Math.max(0, base*YT_BR[k][1] - YT_BR[k][2]);
  }
  return 0;
}
function earnedDed(g){
  if(g<=5000000) return g*0.70;
  if(g<=15000000) return 3500000 + (g-5000000)*0.40;
  if(g<=45000000) return 7500000 + (g-15000000)*0.15;
  if(g<=100000000) return 12000000 + (g-45000000)*0.05;
  return Math.min(20000000, 14750000 + (g-100000000)*0.02);
}
function premiums(g){          // 국민연금(근로자 4.75%), 건강보험 3.595% + 장기요양
  var m = g/12;
  var npBase = Math.min(Math.max(m, 400000), 6370000);
  var np = npBase*0.0475*12;
  var hi = m*0.03595*12;
  return {np:np, hicare:hi + hi*0.1314};
}
function cardLimit(g, kids){
  var add = Math.min(2, kids) * (g<=70000000 ? 500000 : 250000);
  return (g<=70000000 ? 3000000 : 2500000) + add;
}
function cardDed(g, cc, chk, mkt, tr, kids){
  var total = cc+chk+mkt+tr;
  var limit = cardLimit(g, kids);
  var out = {total:total, raw:0, basic:0, extra:0, ded:0, limit:limit, floor:g*0.25, cut:0};
  if(total<=0) return out;
  var grossDed = cc*0.15 + chk*0.30 + mkt*0.40 + tr*0.40;
  var cut;
  if(cc >= out.floor) cut = out.floor*0.15;
  else if(cc+chk >= out.floor) cut = cc*0.15 + (out.floor-cc)*0.30;
  else cut = cc*0.15 + chk*0.30 + Math.max(0, out.floor-cc-chk)*0.40;
  out.cut = cut;
  out.raw = Math.max(0, grossDed - cut);
  out.basic = Math.min(out.raw, limit);
  var over = Math.max(0, out.raw - limit);
  var special = mkt*0.40 + tr*0.40;
  out.extra = Math.min(over, special, g<=70000000 ? 3000000 : 2000000);
  out.ded = out.basic + out.extra;
  return out;
}
function workCredit(tax, g){
  if(tax<=0) return 0;
  var c = tax<=1300000 ? tax*0.55 : 715000 + (tax-1300000)*0.30;
  var cap = 200000;
  for(var k=0;k<YT_CAP.length;k++){ if(g<=YT_CAP[k][0]){ cap = YT_CAP[k][1]; break; } }
  return Math.min(c, cap);
}
function kidCredit(k){
  if(k<=0) return 0;
  if(k===1) return 250000;
  if(k===2) return 550000;
  return 550000 + (k-2)*400000;
}
function calcYT(i){
  var g = i.gross;
  var ed = earnedDed(g);
  var inc = Math.max(0, g - ed);
  var pr = premiums(g);
  var personal = 1500000 * i.deps;
  var cd = cardDed(g, i.cc, i.chk, i.mkt, i.tr, i.kids);
  var house = Math.min(i.jeonse, 4000000) * 0.40;      // 전세자금대출 원리금 40%, 400만 한도
  var incomeDed = personal + pr.np + pr.hicare + cd.ded + house;
  var base = Math.floor(Math.max(0, inc - incomeDed)/1000)*1000;
  var tax = progTax(base);

  var wc = workCredit(tax, g);
  var kc = kidCredit(i.kids);
  var penRate = g<=55000000 ? 0.15 : 0.12;
  var penBase = Math.min(i.pension, 6000000);
  var penAmt = penBase + Math.min(i.irp, Math.max(0, 9000000 - penBase));
  var pc = penAmt * penRate;
  var insCr = Math.min(i.insurance, 1000000) * 0.12;
  var medBase = Math.max(0, i.medical - g*0.03);
  var medCr = Math.min(medBase, 7000000 * Math.max(1, i.deps-1)) * 0.15;
  var donCr = Math.min(i.donation, 10000000)*0.15 + Math.max(0, i.donation-10000000)*0.30;
  var specialCr = insCr + medCr + donCr;
  var rentCr = 0, rentBase = 0;
  if(g <= 80000000 && i.rent > 0){
    rentBase = Math.min(i.rent, 10000000);
    rentCr = rentBase * (g<=55000000 ? 0.17 : 0.15);
  }
  var stdUsed = false;
  if(specialCr + rentCr < 130000){ specialCr = 130000; rentCr = 0; stdUsed = true; }
  var marriage = i.marriage ? 500000 : 0;
  var creditAll = wc + kc + pc + specialCr + rentCr + marriage;
  var credit = Math.min(creditAll, tax);
  var finalTax = Math.max(0, tax - credit);

  var estBase = Math.floor(Math.max(0, inc - 1500000*i.deps - pr.np - pr.hicare - 130000)/1000)*1000;
  var estTax = progTax(estBase);
  var estWithheld = Math.max(0, estTax - workCredit(estTax, g));
  var prepaid = i.prepaid > 0 ? i.prepaid : estWithheld;

  return {gross:g, earned:ed, income:inc, np:pr.np, hicare:pr.hicare, personal:personal,
          card:cd, house:house, incomeDed:incomeDed, base:base, tax:tax,
          workCredit:wc, kidCredit:kc, penRate:penRate, penAmt:penAmt, penCredit:pc,
          insCredit:insCr, medCredit:medCr, donCredit:donCr, specialCredit:specialCr,
          rentBase:rentBase, rentCredit:rentCr, std:stdUsed, marriage:marriage,
          credit:credit, final:finalTax, estWithheld:estWithheld, prepaid:prepaid,
          prepaidAuto:i.prepaid<=0, refund:prepaid - finalTax};
}
function cloneI(i){
  return {gross:i.gross, deps:i.deps, kids:i.kids, cc:i.cc, chk:i.chk, mkt:i.mkt, tr:i.tr,
          pension:i.pension, irp:i.irp, rent:i.rent, jeonse:i.jeonse, insurance:i.insurance,
          medical:i.medical, donation:i.donation, marriage:i.marriage, prepaid:i.prepaid};
}
function addPension(i, amt){          // 연금저축 600만 → IRP 순서로 채움
  var i2 = cloneI(i);
  var toJun = Math.min(amt, Math.max(0, 6000000 - i2.pension));
  i2.pension += toJun;
  var rest = amt - toJun;
  if(rest > 0){
    var used = Math.min(i2.pension, 6000000) + i2.irp;
    i2.irp += Math.min(rest, Math.max(0, 9000000 - used));
  }
  return i2;
}
function addCard(i, amt){
  var i2 = cloneI(i);
  i2.chk += amt;
  return i2;
}
function cardRoom(i){                 // 공제가 한도까지 차는 데 필요한 체크카드 추가 사용액(원)
  var baseDed = calcYT(i).card.ded;
  var maxDed = calcYT(addCard(i, 40000000)).card.ded;
  if(maxDed <= baseDed + 1) return 0;
  var lo = 0, hi = 40000000;
  for(var k=0;k<40;k++){
    var mid = (lo+hi)/2;
    if(calcYT(addCard(i, mid)).card.ded < maxDed - 1) lo = mid; else hi = mid;
  }
  return Math.ceil(hi/10000)*10000;
}
function deltaRefund(i, i2){
  return calcYT(i2).refund - calcYT(i).refund;
}
function readYT(){
  return {
    gross: n('gross')*10000,
    deps: Math.max(1, Math.round(n('deps'))),
    kids: Math.max(0, Math.round(n('kids'))),
    cc: n('cc')*10000, chk: n('chk')*10000, mkt: n('mkt')*10000, tr: n('tr')*10000,
    pension: n('pension')*10000, irp: n('irp')*10000,
    rent: n('rent')*10000, jeonse: n('jeonse')*10000,
    insurance: n('insurance')*10000, medical: n('medical')*10000, donation: n('donation')*10000,
    marriage: $('married').checked,
    prepaid: n('prepaid')*10000
  };
}
function wonsign(x){ return (x>0?'+':(x<0?'−':'')) + won(Math.abs(x)); }
function wonNeg(x){ return x>0 ? '−' + won(x) : '0원'; }

function calcYearEnd(){
  var i = readYT();
  var r = calcYT(i);
  var refund = r.refund;

  setText('r-main', won(Math.abs(refund)));
  setText('r-main-label', refund>=0 ? '예상 환급액 (소득세)' : '예상 추가 납부액 (소득세)');
  $('r-main').style.color = refund<0 ? '#e0483b' : '';
  setText('r-main-sub', '결정세액 ' + won(r.final) + ' · 기납부세액 ' + won(r.prepaid) +
          (r.prepaidAuto ? ' (자동 추정)' : ' (직접 입력)'));

  setText('r-gross', won(r.gross));
  setText('r-earned', wonNeg(r.earned));
  setText('r-income', won(r.income));
  setText('r-personal', wonNeg(r.personal));
  setText('r-np', wonNeg(r.np));
  setText('r-hicare', wonNeg(r.hicare));
  setText('r-card', wonNeg(r.card.ded));
  setText('r-house', wonNeg(r.house));
  setText('r-base', won(r.base));
  setText('r-tax', won(r.tax));
  setText('r-credit', wonNeg(r.credit));
  setText('r-final', won(r.final));
  setText('r-prepaid', won(r.prepaid));
  setText('r-with-local', wonsign(refund*1.1));

  setText('r-c-work', wonNeg(r.workCredit));
  setText('r-c-kid', wonNeg(r.kidCredit));
  setText('r-c-pen', wonNeg(r.penCredit));
  setText('r-c-pen-rate', r.penCredit>0 ? '(' + pct(r.penRate*100,1) + '% · ' + num(Math.round(r.penAmt/10000)) + '만원)' : '');
  setText('r-c-ins', wonNeg(r.insCredit));
  setText('r-c-med', wonNeg(r.medCredit));
  setText('r-c-don', wonNeg(r.donCredit));
  setText('r-c-rent', wonNeg(r.rentCredit));
  setText('r-c-rent-base', r.rentCredit>0 ? '(' + pct(r.rentBase/10000,0) + '만원)' : '');
  setText('r-c-marry', wonNeg(r.marriage));
  setText('r-c-std', r.std ? '−130,000원 (자동 적용)' : '해당 없음');

  var cardUse = r.card.limit>0 ? Math.min(100, r.card.basic/r.card.limit*100) : 0;
  $('bar-card').style.width = cardUse.toFixed(1) + '%';
  setText('r-card-use', pct(r.card.basic/10000,0) + ' / ' + pct(r.card.limit/10000,0) + '만');
  $('bar-pen').style.width = Math.min(100, r.penAmt/9000000*100).toFixed(1) + '%';
  setText('r-pen-use', pct(r.penAmt/10000,0) + ' / 900만');

  // 안내 문구
  var tips = [];
  if(r.final <= 0) tips.push('결정세액이 0원이라 지금은 더 넣어도 환급이 늘지 않습니다.');
  if(r.card.total < r.card.floor) tips.push('카드·현금영수증 사용액이 총급여 25%(' + eok(r.card.floor) + ')에 못 미쳐 카드 공제가 0원입니다.');
  else if(r.card.basic >= r.card.limit) tips.push('카드 공제 기본한도를 모두 채웠습니다. 더 써도 소득공제는 늘지 않습니다.');
  if(r.penAmt < 9000000 && r.final > 0) tips.push('연금계좌 한도까지 <strong>' + eok(9000000-r.penAmt) + '</strong>이 남아 있습니다 (12월 31일 입금 마감).');
  if(r.gross > 80000000 && i.rent > 0) tips.push('총급여 8,000만 원을 넘어 월세 세액공제 대상이 아닙니다.');
  if(r.std) tips.push('특별세액공제·월세 합계가 13만 원보다 적어 표준세액공제 13만 원이 자동 적용되었습니다.');
  $('yt-note').innerHTML = tips.length ? '<div class="note">' + tips.join(' ') + '</div>' : '<div class="note good">공제 항목을 고르게 챙기고 있습니다.</div>';

  // 11~12월 시뮬레이션
  var addCard100 = Math.min(1000000, cardRoom(i));
  var addCardMax = cardRoom(i);
  var penLeft = Math.max(0, 6000000 - i.pension);
  var penTotalLeft = Math.max(0, 9000000 - r.penAmt);
  var addPen100 = Math.min(1000000, penTotalLeft);

  var dCard100 = addCard100>0 ? deltaRefund(i, addCard(i, addCard100)) : 0;
  var dCardMax = addCardMax>0 ? deltaRefund(i, addCard(i, addCardMax)) : 0;
  var dPen100 = addPen100>0 ? deltaRefund(i, addPension(i, addPen100)) : 0;
  var dPenMax = penTotalLeft>0 ? deltaRefund(i, addPension(i, penTotalLeft)) : 0;

  var both = addPension(addCard(i, addCardMax), penTotalLeft);
  var dBoth = deltaRefund(i, both);
  var bothAmt = addCardMax + penTotalLeft;

  setText('sim-now', won(Math.abs(refund)));
  setText('sim-now-sub', refund>=0 ? '환급' : '추가 납부');
  var scen = addPension(addCard(i, addCard100), addPen100);
  var scenDelta = deltaRefund(i, scen);
  setText('sim-next', won(Math.abs(refund + scenDelta)));
  setText('sim-delta', (scenDelta>=0 ? '+' : '−') + won(Math.abs(scenDelta)) + ' 더 돌려받기');

  var rows = [];
  rows.push(['체크카드·현금영수증 100만원 더', addCard100>0 ? '+100만' : '한도 소진', dCard100]);
  rows.push(['체크카드 한도까지', addCardMax>0 ? '+' + pct(addCardMax/10000,0) + '만' : '한도 소진', dCardMax]);
  rows.push(['연금저축·IRP 100만원 더', addPen100>0 ? '+100만' : '한도 소진', dPen100]);
  rows.push(['연금계좌 900만원까지', penTotalLeft>0 ? '+' + pct(penTotalLeft/10000,0) + '만' : '한도 소진', dPenMax]);
  rows.push(['둘 다 한도까지', bothAmt>0 ? '+' + pct(bothAmt/10000,0) + '만' : '한도 소진', dBoth]);
  var html = '';
  for(var k=0;k<rows.length;k++){
    html += '<tr><td>' + rows[k][0] + '</td><td>' + rows[k][1] + '</td><td>' +
            (rows[k][2]>0 ? wonsign(rows[k][2]) : '0원') + '</td></tr>';
  }
  $('sim-body').innerHTML = html;

  setText('sim-note', '환급 증가액은 한계세율과 남은 한도에 따라 달라집니다. 카드는 소득공제(공제율 15~40%), 연금계좌는 세액공제(15% 또는 12%)라 같은 금액이면 연금계좌 쪽이 대체로 큽니다. 단, 결정세액이 0원이면 둘 다 효과가 없습니다.');
}
bindCalc(calcYearEnd);
"""

YET_FIELDS = r"""
<div class="field">
  <label for="gross">총급여 (연간)</label>
  <div class="input-line"><input id="gross" type="number" value="5500" step="100" min="0" inputmode="numeric"><span class="unit">만원</span></div>
  <span class="hint">연봉이 아니라 비과세(식대 등)를 뺀 과세 급여입니다. 원천징수영수증의 '총급여' 칸을 보세요.</span>
  <div class="chips">
    <button type="button" data-set="gross" data-val="3000">3,000만</button>
    <button type="button" data-set="gross" data-val="4500">4,500만</button>
    <button type="button" data-set="gross" data-val="5500">5,500만</button>
    <button type="button" data-set="gross" data-val="7000">7,000만</button>
    <button type="button" data-set="gross" data-val="10000">1억</button>
  </div>
</div>
<div class="row-2">
  <div class="field">
    <label for="deps">부양가족 수 (본인 포함)</label>
    <input id="deps" type="number" value="2" step="1" min="1" max="10" inputmode="numeric">
    <span class="hint">인적공제 1인당 150만 원</span>
  </div>
  <div class="field">
    <label for="kids">자녀 수 (8세 이상)</label>
    <input id="kids" type="number" value="1" step="1" min="0" max="6" inputmode="numeric">
    <span class="hint">자녀세액공제·카드 한도 가산</span>
  </div>
</div>

<h3 class="field-sub first">카드·현금영수증 (연간 사용액)</h3>
<div class="row-2">
  <div class="field">
    <label for="cc">신용카드</label>
    <div class="input-line"><input id="cc" type="number" value="1800" step="50" min="0" inputmode="numeric"><span class="unit">만원</span></div>
  </div>
  <div class="field">
    <label for="chk">체크카드·현금영수증</label>
    <div class="input-line"><input id="chk" type="number" value="600" step="50" min="0" inputmode="numeric"><span class="unit">만원</span></div>
  </div>
</div>
<div class="row-2">
  <div class="field">
    <label for="mkt">전통시장</label>
    <div class="input-line"><input id="mkt" type="number" value="0" step="10" min="0" inputmode="numeric"><span class="unit">만원</span></div>
  </div>
  <div class="field">
    <label for="tr">대중교통</label>
    <div class="input-line"><input id="tr" type="number" value="0" step="10" min="0" inputmode="numeric"><span class="unit">만원</span></div>
  </div>
</div>

<h3 class="field-sub">연금계좌 (연간 납입액)</h3>
<div class="row-2">
  <div class="field">
    <label for="pension">연금저축</label>
    <div class="input-line"><input id="pension" type="number" value="200" step="10" min="0" inputmode="numeric"><span class="unit">만원</span></div>
    <span class="hint">공제 한도 600만 원</span>
  </div>
  <div class="field">
    <label for="irp">IRP·DC 추가납입</label>
    <div class="input-line"><input id="irp" type="number" value="0" step="10" min="0" inputmode="numeric"><span class="unit">만원</span></div>
    <span class="hint">합산 900만 원 한도</span>
  </div>
</div>

<h3 class="field-sub">주택·보험·의료</h3>
<div class="row-2">
  <div class="field">
    <label for="rent">월세액 (연간)</label>
    <div class="input-line"><input id="rent" type="number" value="0" step="10" min="0" inputmode="numeric"><span class="unit">만원</span></div>
    <span class="hint">총급여 8,000만 원 이하 무주택</span>
  </div>
  <div class="field">
    <label for="jeonse">전세자금대출 원리금</label>
    <div class="input-line"><input id="jeonse" type="number" value="0" step="10" min="0" inputmode="numeric"><span class="unit">만원</span></div>
    <span class="hint">소득공제 40%, 400만 원 한도</span>
  </div>
</div>
<div class="row-2">
  <div class="field">
    <label for="insurance">보장성보험료</label>
    <div class="input-line"><input id="insurance" type="number" value="0" step="10" min="0" inputmode="numeric"><span class="unit">만원</span></div>
  </div>
  <div class="field">
    <label for="medical">의료비</label>
    <div class="input-line"><input id="medical" type="number" value="0" step="10" min="0" inputmode="numeric"><span class="unit">만원</span></div>
  </div>
</div>
<div class="field">
  <label for="donation">기부금</label>
  <div class="input-line"><input id="donation" type="number" value="0" step="10" min="0" inputmode="numeric"><span class="unit">만원</span></div>
  <span class="hint">1,000만 원까지 15%, 초과분 30%</span>
</div>

<label class="switch" style="margin:6px 0 12px"><input type="checkbox" id="married"> 2026년에 혼인신고 (결혼세액공제 50만 원)</label>

<div class="field">
  <label for="prepaid">기납부세액 (선택)</label>
  <div class="input-line"><input id="prepaid" type="number" value="" step="10" min="0" inputmode="numeric" placeholder="비우면 자동 추정"><span class="unit">만원</span></div>
  <span class="hint">원천징수영수증의 '기납부세액'. 비우면 간이세액표 기준으로 추정합니다.</span>
</div>
<p class="mini">입력한 값은 브라우저 안에서만 계산되며 서버로 전송되지 않습니다.</p>
"""

YET_RESULTS = r"""
<div class="big">
  <span class="lbl" id="r-main-label">예상 환급액</span>
  <div class="val" id="r-main">-</div>
  <div class="sub" id="r-main-sub">-</div>
</div>
<dl class="kv">
  <dt>총급여</dt><dd id="r-gross">-</dd>
  <dt>근로소득공제</dt><dd class="good" id="r-earned">-</dd>
  <dt>근로소득금액</dt><dd id="r-income">-</dd>
  <dt>인적공제</dt><dd id="r-personal">-</dd>
  <dt>연금보험료 (국민연금)</dt><dd id="r-np">-</dd>
  <dt>건강·장기요양보험료</dt><dd id="r-hicare">-</dd>
  <dt>신용카드 등 소득공제</dt><dd class="em" id="r-card">-</dd>
  <dt>주택자금 소득공제</dt><dd id="r-house">-</dd>
  <dt><strong>과세표준</strong></dt><dd><strong class="em" id="r-base">-</strong></dd>
  <dt>산출세액</dt><dd id="r-tax">-</dd>
  <dt><strong>세액공제 합계</strong></dt><dd><strong class="good" id="r-credit">-</strong></dd>
  <dt><strong>결정세액</strong></dt><dd><strong class="em" id="r-final">-</strong></dd>
  <dt>기납부세액 (원천징수)</dt><dd id="r-prepaid">-</dd>
  <dt>환급액 (지방소득세 포함)</dt><dd id="r-with-local">-</dd>
</dl>
<div class="bar-rows" style="margin-top:14px">
  <div class="bar-row"><span class="bar-k">카드한도</span><div class="bar-track"><span class="bar-fill fill-j" id="bar-card"></span></div><span class="bar-v" id="r-card-use">-</span></div>
  <div class="bar-row"><span class="bar-k">연금계좌</span><div class="bar-track"><span class="bar-fill fill-w" id="bar-pen"></span></div><span class="bar-v" id="r-pen-use">-</span></div>
</div>
<div id="yt-note"></div>

<div class="divider"></div>
<h3 style="font-size:14px;margin:0 0 10px;color:#0f2447">세액공제 내역</h3>
<dl class="kv">
  <dt>근로소득세액공제</dt><dd id="r-c-work">-</dd>
  <dt>자녀세액공제</dt><dd id="r-c-kid">-</dd>
  <dt>연금계좌 <span class="kv-note" id="r-c-pen-rate"></span></dt><dd id="r-c-pen">-</dd>
  <dt>보장성보험</dt><dd id="r-c-ins">-</dd>
  <dt>의료비</dt><dd id="r-c-med">-</dd>
  <dt>기부금</dt><dd id="r-c-don">-</dd>
  <dt>월세 <span class="kv-note" id="r-c-rent-base"></span></dt><dd id="r-c-rent">-</dd>
  <dt>결혼세액공제</dt><dd id="r-c-marry">-</dd>
  <dt>표준세액공제</dt><dd id="r-c-std">-</dd>
</dl>

<div class="divider"></div>
<h3 style="font-size:14px;margin:0 0 4px;color:#0f2447">11~12월에 더 채우면?</h3>
<p class="mini" style="margin:0 0 10px">남은 두 달에 카드와 연금계좌를 더 채웠을 때 환급금이 얼마나 달라지는지 비교합니다.</p>
<div class="sim">
  <div class="sim-card"><span>지금 그대로</span><strong id="sim-now">-</strong><em id="sim-now-sub">-</em></div>
  <div class="sim-card up"><span>체크카드 100만 + 연금 100만 더</span><strong id="sim-next">-</strong><em id="sim-delta">-</em></div>
</div>
<div class="tbl-wrap">
  <table class="tbl sim-tbl">
    <caption>남은 한도까지 채웠을 때 환급금 변화</caption>
    <thead><tr><th>이렇게 하면</th><th>추가 금액</th><th>환급금 증가</th></tr></thead>
    <tbody id="sim-body"></tbody>
  </table>
</div>
<p class="mini" id="sim-note"></p>
<p class="mini" style="margin-top:10px">기납부세액은 간이세액표 방식으로 추정하며, 부양가족 수는 연초부터 회사에 신고되어 매달 원천징수에 반영된 것으로 가정합니다. 회사가 실제로 뗀 세금과 다르면 기납부세액을 직접 입력하세요. 교육비·기부금 일부와 주택청약저축 같은 항목은 반영하지 않았습니다.</p>
"""

YET_CONTENT = r"""
<h2>연말정산 환급금은 어디서 나오나요</h2>
<p>연말정산은 세금을 더 내는 절차가 아니라, 1년 동안 매달 월급에서 미리 떼간 근로소득세(기납부세액)와 실제로 내야 할 세금(결정세액)을 비교해 차액을 돌려받거나 채우는 절차입니다. 미리 낸 세금이 실제 세금보다 많으면 환급, 적으면 추가 납부입니다.</p>
<div class="formula">
  환급액 = 기납부세액(매달 원천징수된 소득세) − 결정세액<br>
  결정세액 = 산출세액 − 세액공제<br>
  산출세액 = (총급여 − 근로소득공제 − 소득공제) × 6~45% − 누진공제
</div>
<p>그래서 환급액을 키우는 방법은 두 가지뿐입니다. 과세표준을 줄이는 <strong>소득공제</strong>(카드 사용액, 연금보험료, 인적공제)를 늘리거나, 계산된 세금에서 직접 빼 주는 <strong>세액공제</strong>(연금계좌, 월세, 의료비, 자녀)를 늘리는 것입니다. 이 계산기는 두 가지를 모두 반영해 결정세액과 환급액을 계산합니다.</p>

<h2>2026년 귀속, 달라진 것 세 가지</h2>
<ul>
  <li><strong>자녀가 있으면 카드 공제한도가 늘어납니다.</strong> 18세 미만 자녀 1명당 기본한도 50만 원(최대 100만 원)이 붙고, 총급여 7,000만 원 초과자는 25만 원(최대 50만 원)입니다.</li>
  <li><strong>예체능 학원비도 교육비 공제 대상</strong>입니다. 9세 미만이거나 초등 2학년 이하인 자녀의 태권도·피아노 학원비가 15% 세액공제됩니다.</li>
  <li><strong>결혼세액공제는 2026년이 마지막</strong>입니다. 2024년 1월 1일부터 2026년 12월 31일 사이 혼인신고분에 1인 50만 원(부부 합산 최대 100만 원), 생애 1회입니다.</li>
</ul>

<h2>실제 직장인 세 가지로 보는 환급액</h2>
<p>숫자만 보고는 감이 잘 안 오니, 실제로 많이 나오는 세 가지 경우를 계산기에 그대로 넣어 봤습니다. 표의 값을 그대로 입력하면 같은 결과가 나옵니다.</p>
<div class="cases">
  <div class="case">
    <span class="who">사회초년생 · 총급여 4,500만</span>
    <h3>카드만 챙겼더니 40만 원</h3>
    <p>부양가족은 본인 하나, 신용카드 1,200만 원·체크카드 600만 원을 썼습니다.</p>
    <dl>
      <dt>카드 소득공제</dt><dd>191만 원</dd>
      <dt>결정세액</dt><dd>179만 원</dd>
      <dt>기납부세액</dt><dd>219만 원</dd>
    </dl>
    <div class="res"><span>예상 환급</span><b>397,450원</b></div>
    <p class="mini" style="margin:9px 0 0">연금저축에 300만 원을 넣었다면 847,450원으로 늘어납니다.</p>
  </div>
  <div class="case">
    <span class="who">맞벌이 · 총급여 7,000만</span>
    <h3>신용카드로 몰아 쓴 800만 원</h3>
    <p>배우자도 벌어서 기본공제는 본인 1명만, 자녀는 1명. 신용카드 2,800만 원에 체크카드는 200만 원뿐입니다.</p>
    <dl>
      <dt>카드 소득공제</dt><dd>217만 원</dd>
      <dt>결정세액</dt><dd>473만 원</dd>
      <dt>기납부세액</dt><dd>542만 원</dd>
    </dl>
    <div class="res"><span>예상 환급</span><b>686,750원</b></div>
    <p class="mini" style="margin:9px 0 0">그중 800만 원을 체크카드로 옮기면 +18만 원, 연금저축 300만 원을 더하면 +36만 원입니다.</p>
  </div>
  <div class="case">
    <span class="who">외벌이 · 총급여 9,500만</span>
    <h3>연금계좌 900만 원이 만든 108만</h3>
    <p>부양가족 2명에 자녀 1명, 카드는 2,400만 원, 전세자금대출 원리금은 400만 원입니다.</p>
    <dl>
      <dt>카드 소득공제</dt><dd>3만 7,500원</dd>
      <dt>전세대출 소득공제</dt><dd>160만 원</dd>
      <dt>연금계좌 세액공제</dt><dd>108만 원</dd>
    </dl>
    <div class="res"><span>예상 환급</span><b>1,821,920원</b></div>
    <p class="mini" style="margin:9px 0 0">연금계좌를 비우면 741,920원으로 줄어듭니다. 총급여가 8,000만 원을 넘어 월세 세액공제는 해당되지 않습니다.</p>
  </div>
</div>
<p>세 사람의 차이는 연봉이 아니라 <strong>공제를 어디에 넣었는지</strong>에서 갈립니다. 총급여 4,500만 원인 사회초년생도 연금계좌를 채우면 맞벌이 직장인만큼 돌려받고, 총급여 9,500만 원인 고소득자도 연금계좌를 비우면 환급이 741,920원으로 절반 아래가 됩니다. 카드 사용액은 총급여의 25% 문턱을 넘기만 하면 거의 힘을 쓰지 못합니다.</p>
<p>세 번째 사례에서 눈여겨볼 점이 하나 더 있습니다. 카드를 2,400만 원이나 썼는데 소득공제는 3만 7,500원뿐입니다. 총급여 25%(2,375만 원)를 겨우 넘겨서, 넘긴 25만 원에만 15%가 붙었기 때문입니다. 카드 공제는 '얼마를 썼나'보다 <strong>문턱을 넘겼나</strong>가 먼저입니다.</p>

<h2>11~12월 막판에 환급액 늘리는 체크리스트</h2>
<p>연말정산은 12월 31일로 끝납니다. 1월에 아무리 서류를 챙겨도 그해에 쓰지 않은 돈은 소급되지 않으니, 남은 두 달에 할 수 있는 일만 순서대로 정리했습니다.</p>
<ol>
  <li><strong>카드 문턱을 넘겼는지 먼저 봅니다</strong> — 카드 공제는 총급여의 25%를 넘긴 금액부터 시작합니다. 총급여 5,500만 원이면 1,375만 원까지는 공제가 0원입니다. 계산기 결과 카드의 <strong>카드한도 막대</strong>와 '총급여 25%' 안내를 보고, 아직 문턱을 못 넘었다면 남은 두 달은 신용카드보다 체크카드·현금영수증으로 결제하세요. 공제율이 15%와 30%로 두 배 차이입니다.</li>
  <li><strong>카드 기본한도가 남았는지 확인합니다</strong> — 총급여 7,000만 원 이하면 300만 원, 넘으면 250만 원이 기본한도입니다. 자녀가 있으면 1명당 50만 원(7,000만 원 초과는 25만 원)씩 최대 100만 원이 더 붙습니다. 막대가 100%를 가리킨다면 더 써도 소득공제는 늘지 않으니, 그 돈은 연금계좌로 옮기는 게 납니다.</li>
  <li><strong>연금저축 600만 원을 먼저, 그다음 IRP 300만 원</strong> — 두 계좌를 합쳐 900만 원까지 세액공제됩니다. 연금저축만으로 600만 원을 채우고 남은 300만 원을 IRP에 넣는 순서가 무난합니다. IRP는 중도 인출이 어렵고 연금저축은 상대적으로 자유롭기 때문에, 먼저 채울 곳은 연금저축입니다. 100만 원당 15만 원(총급여 5,500만 원 초과는 12만 원)이 줄어들고, <strong>12월 31일까지 실제로 입금된 금액</strong>만 인정됩니다. 12월 말에는 이체 마감 시간과 처리 일자가 걸리니 20일 안에 넣는 게 안전해요.</li>
  <li><strong>월세는 12월 31일 기준으로 조건을 봅니다</strong> — 월세 세액공제는 <strong>12월 31일 현재 무주택 세대주</strong>이면서 총급여 8,000만 원 이하여야 합니다. 연말에 집을 사서 12월 31일에 1주택자가 되면 그해 월세 공제는 사라집니다. 임대차계약서 주소와 주민등록 주소가 같아야 하고, 계약 명의도 본인이나 기본공제 대상자여야 합니다.</li>
  <li><strong>결정세액이 0원인지 봅니다</strong> — 이미 낸 세금보다 공제가 커서 결정세액이 0원이면, 더 넣어도 돌려받을 세금이 없습니다. 이때 연금계좌를 넣는 건 절세가 아니라 그냥 노후 저축입니다.</li>
  <li><strong>놓쳤다면 5년 안에는 되찾을 수 있습니다</strong> — 회사에 서류를 못 낸 항목이 있어도 홈택스에서 경정청구를 하면 돌려받을 수 있습니다. 5월 종합소득세 신고 때 함께 처리하는 경우가 많고, 국세기본법상 5년이 지나면 청구할 수 없으니 오래된 영수증은 버리지 마세요.</li>
</ol>

<h2>신용카드 소득공제는 순서가 절반입니다</h2>
<p>카드 공제는 <strong>연간 사용액이 총급여의 25%를 넘은 부분</strong>부터 시작됩니다. 총급여 5,500만 원이라면 1,375만 원까지는 공제가 0원입니다. 이 문턱을 넘긴 금액에 결제수단별 공제율(신용카드 15%, 체크카드·현금영수증 30%, 전통시장·대중교통 40%)을 곱하고, 기본한도(총급여 7,000만 원 이하 300만 원)를 넘는 부분은 잘라냅니다. 전통시장·대중교통은 기본한도와 별도로 300만 원까지 더 공제됩니다.</p>
<p>문턱까지는 신용카드로, 문턱을 넘긴 뒤에는 체크카드로 쓰는 게 유리합니다. 같은 100만 원을 써도 신용카드는 15만 원, 체크카드는 30만 원이 공제되기 때문입니다. 반대로 한도를 다 채운 뒤에는 어떤 카드를 써도 공제가 늘지 않습니다.</p>

<h2>연금저축·IRP 900만 원, 12월 31일이 마감</h2>
<p>연금계좌는 소득공제가 아니라 <strong>세액공제</strong>입니다. 연금저축 600만 원, IRP·DC 추가납입을 합쳐 900만 원까지 납입액의 15%(총급여 5,500만 원 초과는 12%)를 세금에서 바로 빼 줍니다. 900만 원을 채우면 135만 원, 지방소득세를 포함하면 148만 5,000원이 줄어듭니다.</p>
<p>2026년 12월 31일까지 실제로 입금된 금액만 인정됩니다. 매달 나눠 넣든 12월에 한 번에 넣든 금액은 같으니, 남은 두 달에 여윳돈이 생겼다면 연금저축 600만 원을 먼저 채우고 나머지를 IRP로 넣는 순서가 무난합니다. 단, 결정세액이 0원이 되면 더 넣어도 돌려받을 세금이 없습니다.</p>

<h2>월세를 낸다면 반드시 챙기세요</h2>
<p>총급여 8,000만 원 이하 무주택 세대라면 연간 월세 1,000만 원까지 17%(총급여 5,500만 원 이하) 또는 15%를 세액공제받습니다. 최대 170만 원입니다. 임대차계약서 주소와 주민등록 주소가 같아야 하고, 계약서 사본과 지급 내역을 회사에 제출해야 합니다. 관리비와 별도로 월세만 계산합니다.</p>

<h2>공제율·한도 기준표 (2026년 귀속)</h2>
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>항목</th><th>공제율</th><th>한도</th></tr></thead>
    <tbody>
      <tr><td>신용카드</td><td>15%</td><td rowspan="2">기본 300만(7,000만 초과 250만) + 자녀 가산</td></tr>
      <tr><td>체크카드·현금영수증</td><td>30%</td></tr>
      <tr><td>전통시장·대중교통</td><td>40%</td><td>추가 300만(7,000만 초과 200만)</td></tr>
      <tr><td>연금저축·IRP</td><td>15% / 12%</td><td>900만 (연금저축 600만)</td></tr>
      <tr><td>월세</td><td>17% / 15%</td><td>1,000만</td></tr>
      <tr><td>보장성보험</td><td>12%</td><td>100만</td></tr>
      <tr><td>의료비</td><td>15%</td><td>총급여 3% 초과분</td></tr>
      <tr><td>기부금</td><td>15% / 30%</td><td>1,000만 초과분은 30%</td></tr>
    </tbody>
  </table>
</div>
<p>공제율 옆의 괄호는 총급여 5,500만 원을 기준으로 갈립니다. 연금계좌는 15%에서 12%로, 월세는 17%에서 15%로 낮아지니, 총급여가 그 경계에 걸쳐 있다면 비과세 식대를 확인해 보세요. 회사가 반영한 값과 이 계산기가 다르다면 대부분 이 두 기준선 때문입니다.</p>

<h2>같은 연봉인데 환급액이 다른 이유</h2>
<p>환급액은 총급여보다 <strong>공제를 얼마나 챙겼는지</strong>가 더 크게 좌우합니다. 총급여 5,500만 원, 배우자와 자녀 1명인 직장인이 카드·현금영수증을 2,500만 원가량 쓰고 연금저축에 200만 원을 넣었다면 환급액은 100만 원을 넘습니다. 여기에 연금계좌를 900만 원까지 채우고 월세 공제를 더하면 200만 원에 가까워집니다.</p>
<p>반대로 카드 사용액이 총급여의 25%에 못 미치면 카드 공제는 0원이고, 특별세액공제가 13만 원보다 적으면 표준세액공제 13만 원만 적용됩니다. 영수증을 챙기지 않으면 그만큼 덜 돌려받는다는 뜻입니다.</p>

<h2>이럴 때 써 보세요</h2>
<ul>
  <li><strong>12월 급여 전 마지막 점검</strong> — 지금까지의 카드·연금저축 납입으로 예상 환급액을 확인합니다.</li>
  <li><strong>연금저축 막차 판단</strong> — 100만 원을 더 넣으면 환급이 얼마 늘어나는지, 지금 넣을 여윳돈과 비교합니다.</li>
  <li><strong>이직·연봉 협상</strong> — 총급여가 5,500만 원·7,000만 원을 넘는지에 따라 공제율과 한도가 달라집니다.</li>
  <li><strong>원천징수영수증 검증</strong> — 회사가 정산한 결정세액과 비교해 공제가 빠짐없이 들어갔는지 확인합니다.</li>
</ul>
"""

YET_FAQS = [
    ("연말정산 환급금은 어떻게 계산되나요?",
     "기납부세액(매달 월급에서 원천징수된 소득세)에서 결정세액을 뺀 금액입니다. 결정세액은 총급여에서 근로소득공제와 소득공제(인적공제·연금보험료·건강보험료·카드 사용액 등)를 빼 과세표준을 구하고, 6~45% 세율을 적용한 산출세액에서 세액공제(근로·자녀·연금계좌·월세·의료비 등)를 빼서 구합니다. 미리 낸 세금이 더 많으면 환급, 적으면 추가 납부입니다."),
    ("11~12월에 카드를 더 쓰면 환급이 늘어나나요?",
     "카드 공제한도가 남아 있을 때만 늘어납니다. 체크카드로 100만 원을 더 쓰면 소득공제가 30만 원 늘고, 과세표준 15% 구간이라면 환급은 4만 5,000원 정도 늘어납니다. 안 쓸 돈을 억지로 쓰는 것은 남는 장사가 아니니, 이미 쓸 지출을 신용카드 대신 체크카드로 바꾸는 정도가 현실적입니다. 반면 연금계좌는 100만 원당 15만 원이 줄어 효과가 훨씬 큽니다."),
    ("연금저축은 왜 12월 31일까지 넣어야 하나요?",
     "연금계좌 세액공제는 1월 1일부터 12월 31일까지 실제로 입금된 금액을 기준으로 하기 때문입니다. 다음 해 1월에 넣으면 그다음 해 정산으로 넘어갑니다. 12월 말에는 금융사 이체 마감 시간이 있고 처리 일자가 넘어갈 수 있으니 며칠 여유를 두고 넣는 것이 안전합니다."),
    ("총급여 5,500만 원이 왜 기준이 되나요?",
     "연금계좌 세액공제율(15% 또는 12%)과 월세 세액공제율(17% 또는 15%)이 총급여 5,500만 원을 기준으로 갈리기 때문입니다. 여기서 총급여는 연봉이 아니라 비과세 소득(식대 월 20만 원 등)을 뺀 금액입니다. 연봉 5,700만 원이어도 식대 240만 원을 빼면 총급여 5,460만 원이 되어 높은 공제율을 받을 수 있습니다."),
    ("회사에서 받은 환급액과 왜 다른가요?",
     "이 계산기는 4대보험료를 총급여로 추정하고, 교육비·신용카드 제외 항목·부양가족별 의료비 한도 같은 세부 조건을 단순화했습니다. 기납부세액도 간이세액표 기준 추정치라 실제 원천징수액과 차이가 날 수 있습니다. 원천징수영수증의 기납부세액을 직접 입력하면 더 가까워지고, 최종 금액은 홈택스 연말정산 미리보기나 회사 정산 내역으로 확인하세요."),
    ("총급여 8,000만 원을 넘으면 월세 세액공제를 못 받나요?",
     "네, 월세 세액공제는 총급여 8,000만 원(종합소득금액 7,000만 원) 이하인 무주택 세대주만 받을 수 있습니다. 연봉이 8,000만 원을 조금 넘어도 비과세 식대를 빼면 총급여가 8,000만 원 이하로 내려오는 경우가 있으니 원천징수영수증의 총급여 칸을 먼저 확인해 보세요. 계산기에 월세를 넣었는데 0원으로 나온다면 이 기준에 걸린 것입니다. 대신 전세자금대출 원리금은 총급여와 상관없이 소득공제가 됩니다."),
    ("전세자금대출 이자도 돌려받을 수 있나요?",
     "전세자금대출 원리금 상환액의 40%를 연 400만 원까지 소득공제받습니다. 세액공제가 아니라 소득공제라서, 과세표준을 낮춰 세금을 줄이는 방식입니다. 총급여 제한은 없고, 12월 31일 기준 무주택 세대주이면서 임차한 집이 국민주택규모(전용 85㎡ 이하)여야 합니다. 대출이 임대인 계좌로 직접 입금된 경우에만 인정되고, 주택청약저축 공제와 합쳐 400만 원 한도라는 점도 기억해 두세요."),
    ("작년에 놓친 공제를 지금도 받을 수 있나요?",
     "받을 수 있습니다. 연말정산에서 빠뜨린 공제는 홈택스에서 경정청구를 하면 돌려받을 수 있고, 신고 기간과 상관없이 국세기본법상 5년 이내면 됩니다. 많은 사람이 5월 종합소득세 신고 때 함께 처리합니다. 병원비 영수증, 기부금 영수증, 연금계좌 납입증명서처럼 그해에 회사에 못 낸 서류가 있다면 홈택스에서 지금이라도 확인해 보세요. 금액이 크면 5년치를 한꺼번에 청구할 수도 있습니다."),
]

YET = {
    "slug": "tools/year-end-tax-calculator",
    "title": "2026 연말정산 환급금 계산기 | 세액공제·카드·연금저축 모의계산",
    "h1": "2026 연말정산 환급금·세액공제 모의계산기",
    "kicker": "2026년 귀속 · 2027년 초 정산",
    "lede": "총급여와 카드·연금저축·월세 납입액을 넣으면 예상 환급금이 바로 나옵니다. 11~12월에 체크카드와 연금계좌를 얼마 더 채우면 환급이 얼마나 늘어나는지도 한눈에 비교하세요.",
    "desc": "2026년 귀속 연말정산 환급금을 모의계산합니다. 근로소득공제, 신용카드·체크카드 소득공제 한도(자녀 가산), 연금저축·IRP 900만 원, 월세·의료비 세액공제를 반영하고, 총급여 4,500만·7,000만·9,500만 사례와 11~12월 절세 체크리스트를 함께 정리했습니다.",
    "keywords": "연말정산 환급금 계산기, 2026 연말정산, 2027 연말정산, 세액공제 계산, 연금저축 세액공제, IRP 900만, 신용카드 소득공제 한도, 월세 세액공제, 연말정산 미리보기, 연말정산 환급 사례, 12월 절세",
    "fields": YET_FIELDS,
    "results": YET_RESULTS,
    "script": YET_SCRIPT,
    "content": YET_CONTENT,
    "faqs": YET_FAQS,
    "disclaimer": "이 계산기는 2026년 귀속 소득세법·조세특례제한법의 공개된 요율과 공식을 적용한 참고용 추정치입니다. 실제 환급액은 회사가 반영한 부양가족·의료비·교육비·기부금 내역, 원천징수된 기납부세액, 보험료 실제 납부액에 따라 달라집니다. 정확한 금액은 국세청 홈택스 연말정산 미리보기와 원천징수영수증으로 확인하세요.",
}
