# -*- coding: utf-8 -*-
"""Pages: 주담대 이자, DSR, 취득세·중개보수"""

LOAN_SCRIPT = r"""
function buildSchedule(P, rate, months, grace, method, growth){
  var i = rate/100/12, rows = [], bal = P;
  if(months < 1) return rows;
  if(grace >= months) grace = months - 1;
  var n = months - grace;
  var mPay = monthlyPayment(P, rate, n);
  var g = growth/100;
  var firstGrad = 0, pv = 0, k;
  if(method==='graduated'){
    for(k=1;k<=n;k++){ pv += Math.pow(1+g, Math.floor((k-1)/12))/Math.pow(1+i,k); }
    firstGrad = pv>0 ? P/pv : 0;
  }
  var eqP = P/n;
  for(var m=1;m<=months;m++){
    var interest = bal*i, principal = 0, pay = 0;
    if(m<=grace){
      pay = interest;
    } else if(method==='bullet'){
      if(m===months){ principal = bal; pay = interest + principal; } else { pay = interest; }
    } else if(method==='equal'){
      pay = mPay; principal = pay - interest;
      if(m===months){ principal = bal; pay = principal + interest; }
    } else if(method==='principal'){
      principal = (m===months) ? bal : Math.min(eqP, bal);
      pay = principal + interest;
    } else {
      var y = Math.floor((m-1-grace)/12);
      pay = firstGrad*Math.pow(1+g, y);
      principal = pay - interest;
      if(m===months || principal >= bal){ principal = bal; pay = principal + interest; }
    }
    if(principal < 0){ principal = 0; pay = interest; }
    bal -= principal; if(bal < 1) bal = 0;
    rows.push({m:m, pay:pay, interest:interest, principal:principal, bal:bal});
  }
  return rows;
}
function sumBy(rows, key){ var s=0; rows.forEach(function(r){ s+=r[key]; }); return s; }

function calcLoan(){
  var P = n('amount'), rate = n('rate'), years = n('term'), graceY = n('grace');
  var method = $('method').value, growth = n('growth');
  var months = Math.max(1, Math.round(years*12));
  var grace = Math.round(graceY*12);
  var rows = buildSchedule(P, rate, months, grace, method, growth);
  if(!rows.length){ return; }
  var totalInt = sumBy(rows,'interest'), totalPay = sumBy(rows,'pay');
  var first = rows[0], last = rows[rows.length-1];
  var avg = totalPay/months;

  setText('r-main', won(first.pay));
  var label = '월 납입액';
  if(method==='bullet') label = '월 이자(원금은 만기에 일시 상환)';
  if(method==='graduated') label = '첫해 월 납입액';
  if(grace>0 && method!=='bullet'){
    label = '거치기간 월 이자';
    setText('r-main-sub', '거치 ' + graceY + '년 후부터 월 ' + won(rows[Math.min(grace, rows.length-1)].pay) + ' · 총 ' + num(months) + '회');
    setText('r-main-label', label);
  } else {
    setText('r-main-label', label);
    setText('r-main-sub', method==='graduated'
        ? ('만기 무렵 월 ' + won(last.pay) + '까지 올라갑니다')
        : ('만기 ' + Math.round(months/12*10)/10 + '년 · 총 ' + num(months) + '회 납입'));
  }

  setText('r-last', won(last.pay));
  setText('r-total-int', won(totalInt));
  setText('r-total-pay', won(totalPay));
  setText('r-avg', won(avg));
  setText('r-ratio', P>0 ? pct(totalInt/P*100,1)+'%' : '0%');
  setText('r-principal', won(P));
  setText('amount-hint', eok(P) + ' · ' + num(months) + '개월');

  var body = '';
  for(var y=0;y<Math.ceil(months/12);y++){
    var pay=0,intr=0,prin=0,bal=0;
    for(var m=y*12;m<Math.min(months,(y+1)*12);m++){
      pay+=rows[m].pay; intr+=rows[m].interest; prin+=rows[m].principal; bal=rows[m].bal;
    }
    body += '<tr><td>'+(y+1)+'년차</td><td>'+num(pay)+'</td><td>'+num(prin)+'</td><td>'+num(intr)+'</td><td>'+num(bal)+'</td></tr>';
  }
  $('year-body').innerHTML = body;

  var methods = [['equal','원리금균등'],['principal','원금균등'],['bullet','만기일시'],['graduated','체증식']];
  var cmp = '';
  methods.forEach(function(mt){
    var r = buildSchedule(P, rate, months, grace, mt[0], growth);
    var ti = sumBy(r,'interest'), tp = sumBy(r,'pay');
    var fp = r.length ? r[0].pay : 0;
    cmp += '<tr'+(mt[0]===method?' class="onrow"':'')+'><td>'+mt[1]+'</td><td>'+num(fp)+'</td><td>'+num(ti)+'</td><td>'+num(tp)+'</td></tr>';
  });
  $('cmp-body').innerHTML = cmp;

  // 원금 vs 이자 비율 바
  var principalShare = totalPay>0 ? (P/totalPay*100) : 0;
  $('bar-principal').style.width = principalShare.toFixed(1)+'%';
  $('bar-interest').style.width = (100-principalShare).toFixed(1)+'%';
}
bindCalc(calcLoan);
"""

LOAN_FIELDS = r"""
<div class="field">
  <label for="amount">대출 금액</label>
  <div class="input-line"><input id="amount" type="number" value="300000000" step="1000000" min="0" inputmode="numeric"><span class="unit">원</span></div>
  <span class="hint" id="amount-hint">3억원</span>
  <div class="chips">
    <button type="button" data-set="amount" data-val="100000000">1억</button>
    <button type="button" data-set="amount" data-val="200000000">2억</button>
    <button type="button" data-set="amount" data-val="300000000">3억</button>
    <button type="button" data-set="amount" data-val="500000000">5억</button>
  </div>
</div>
<div class="row-2">
  <div class="field">
    <label for="rate">연 이자율</label>
    <div class="input-line"><input id="rate" type="number" value="4.0" step="0.01" min="0" max="30" inputmode="decimal"><span class="unit">%</span></div>
  </div>
  <div class="field">
    <label for="term">대출 기간</label>
    <div class="input-line"><input id="term" type="number" value="30" step="1" min="1" max="50" inputmode="numeric"><span class="unit">년</span></div>
  </div>
</div>
<div class="field">
  <label for="method">상환 방식</label>
  <select id="method">
    <option value="equal" selected>원리금균등분할 (매달 같은 금액)</option>
    <option value="principal">원금균등분할 (원금을 매달 똑같이)</option>
    <option value="bullet">만기일시 (이자만 내다가 만기에 원금)</option>
    <option value="graduated">체증식 (해마다 납입액이 증가)</option>
  </select>
  <span class="hint">전세자금대출은 대부분 만기일시 상환이에요.</span>
</div>
<div class="row-2">
  <div class="field">
    <label for="grace">거치기간</label>
    <div class="input-line"><input id="grace" type="number" value="0" step="0.5" min="0" max="30" inputmode="decimal"><span class="unit">년</span></div>
    <span class="hint">이자만 내는 기간</span>
  </div>
  <div class="field">
    <label for="growth">체증률 (체증식)</label>
    <div class="input-line"><input id="growth" type="number" value="3" step="0.1" min="0" max="10" inputmode="decimal"><span class="unit">%</span></div>
    <span class="hint">1년마다 오르는 비율</span>
  </div>
</div>
<p class="mini">입력한 값은 브라우저에서만 계산되고 전송되지 않습니다.</p>
"""

LOAN_RESULTS = r"""
<div class="big">
  <span class="lbl" id="r-main-label">월 납입액</span>
  <div class="val" id="r-main">-</div>
  <div class="sub" id="r-main-sub">-</div>
</div>
<dl class="kv">
  <dt>대출 원금</dt><dd id="r-principal">-</dd>
  <dt>마지막 달 납입액</dt><dd id="r-last">-</dd>
  <dt>월평균 납입액</dt><dd id="r-avg">-</dd>
  <dt>총 이자</dt><dd class="em" id="r-total-int">-</dd>
  <dt>총 상환액</dt><dd id="r-total-pay">-</dd>
  <dt>원금 대비 이자</dt><dd id="r-ratio">-</dd>
</dl>
<div class="divider"></div>
<div class="bar" aria-hidden="true"><span class="bar-p" id="bar-principal"></span><span class="bar-i" id="bar-interest"></span></div>
<p class="mini"><span class="dot dot-p"></span> 원금 &nbsp; <span class="dot dot-i"></span> 이자 — 총 상환액에서 차지하는 비중</p>
<div class="divider"></div>
<h3 style="font-size:14px;margin:0 0 10px;color:#0f2447">연도별 상환표 (원)</h3>
<div class="tbl-wrap" style="max-height:300px;overflow-y:auto">
  <table class="tbl">
    <thead><tr><th>구분</th><th>납입액</th><th>원금</th><th>이자</th><th>남은 원금</th></tr></thead>
    <tbody id="year-body"></tbody>
  </table>
</div>
<div class="divider"></div>
<h3 style="font-size:14px;margin:0 0 10px;color:#0f2447">상환방식별 총이자 비교 (원)</h3>
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>상환방식</th><th>첫 달 납입</th><th>총 이자</th><th>총 상환액</th></tr></thead>
    <tbody id="cmp-body"></tbody>
  </table>
</div>
<p class="mini">같은 금액·금리·기간에서 상환방식만 바꾼 비교예요. 체증식은 입력한 체증률을 적용했습니다.</p>
"""

LOAN_CONTENT = r"""
<h2>월 이자 계산, 어디서부터 봐야 할까요</h2>
<p>대출 상담을 받으면 제일 먼저 나오는 숫자가 &ldquo;월 얼마씩 갚으면 됩니다&rdquo;입니다. 그런데 같은 3억 원, 같은 연 4%라도 <strong>상환 방식</strong>에 따라 첫 달 납입액은 100만 원 넘게 차이 납니다. 이 계산기는 금액·금리·기간·상환방식을 넣으면 첫 달과 마지막 달 납입액, 총이자, 연도별로 원금이 얼마나 줄어드는지를 한 번에 보여 줍니다.</p>

<h2>상환 방식별 계산 공식</h2>
<p>아래에서 <code>P</code>는 대출 원금, <code>r</code>은 연 이자율(%), <code>i = r / 12 / 100</code>은 월 이자율, <code>n</code>은 총 상환 개월 수입니다.</p>
<div class="formula">
  <strong>원리금균등</strong> — 매달 같은 금액<br>
  <code>월 납입액 = P × i ÷ (1 − (1 + i)<sup>−n</sup>)</code><br>
  <strong>원금균등</strong> — 원금 <code>P ÷ n</code>씩 + 남은 원금에 대한 이자, 첫 달이 가장 많고 매달 줄어듦<br>
  <strong>만기일시</strong> — 매달 <code>P × i</code>만 내고 원금은 마지막 달에 한 번에<br>
  <strong>체증식</strong> — 첫해 납입액 A를 1년마다 (1+g)배로 올리며, 모든 납입액을 월 이자율로 할인한 합이 P가 되도록 A를 역산
</div>
<p>체증식은 한국주택금융공사 보금자리론·디딤돌대출 같은 정책 상품에서 볼 수 있는 방식입니다. 이 계산기는 &ldquo;1년 단위로 같은 비율씩 오르는&rdquo; 단순 모델로 계산하므로, 실제 상품이 매월 일정 금액씩 올리는 방식을 쓰면 금액이 조금 달라질 수 있습니다.</p>

<h2>상환 방식, 결국 무엇이 유리한가요</h2>
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>방식</th><th>첫 달 부담</th><th>총이자</th><th>어울리는 상황</th></tr></thead>
    <tbody>
      <tr><td>원리금균등</td><td>보통</td><td>중간</td><td>월 납입액을 고정해 가계 계획을 세우고 싶을 때</td></tr>
      <tr><td>원금균등</td><td>가장 높음</td><td>가장 적음</td><td>초반 소득이 충분하고 총이자를 줄이고 싶을 때</td></tr>
      <tr><td>만기일시</td><td>가장 낮음</td><td>가장 많음</td><td>전세대출처럼 만기에 목돈이 들어오는 구조</td></tr>
      <tr><td>체증식</td><td>낮게 시작</td><td>많음</td><td>사회초년생처럼 소득이 앞으로 늘어날 때</td></tr>
    </tbody>
  </table>
</div>
<p>총이자만 보면 원금균등이 언제나 유리합니다. 원금이 빨리 줄기 때문입니다. 하지만 첫 달 납입액이 원리금균등보다 30~40% 많아 현금 흐름이 버티지 못하면 오히려 연체로 이어집니다. <strong>총이자 100만 원을 아끼려고 매달 40만 원을 더 내는 선택</strong>이 합리적인지는 그 40만 원을 다른 곳에 썼을 때의 가치와 비교해 판단해야 합니다.</p>

<h2>거치기간을 넣으면 어떻게 되나요</h2>
<p>거치기간은 원금은 그대로 두고 이자만 내는 기간입니다. 예를 들어 3억 원·연 4%·30년 원리금균등에 거치 2년을 넣으면, 첫 2년은 매달 100만 원(3억 × 4% ÷ 12)만 내고, 남은 28년 동안 원리금을 나눠 갚습니다. 그만큼 월 납입액이 늘고 총이자도 함께 늘어납니다. 이 계산기는 거치기간을 &ldquo;년&rdquo; 단위로 받아 개월로 환산해 반영합니다.</p>

<h2>이럴 때 써 보세요</h2>
<ul>
  <li><strong>은행에서 받은 상환계획서가 맞는지 확인할 때</strong> — 금액·금리·기간을 넣고 첫 달 납입액과 총이자를 대조해 보세요.</li>
  <li><strong>전세대출 이자를 가늠할 때</strong> — 상환방식을 &lsquo;만기일시&rsquo;로 두면 매달 나가는 이자만 정확히 나옵니다.</li>
  <li><strong>체증식과 원리금균등을 비교할 때</strong> — 체증률을 2~4%로 바꿔 가며 첫해 부담이 얼마나 줄고 총이자가 얼마나 늘어나는지 확인하세요.</li>
  <li><strong>중도상환을 계획할 때</strong> — 연도별 표에서 남은 원금이 얼마인지 보면, 중도상환수수료(잔존일수 기준)와 절감 이자를 함께 계산할 수 있습니다.</li>
</ul>

<h2>계산할 때 알아 둘 점</h2>
<ul>
  <li>금리는 <strong>연 단위 고정금리</strong>를 가정했습니다. 변동금리라면 금리가 오를 때를 가정해 1~2%p 높여 다시 계산해 보세요.</li>
  <li>실제 은행은 원 단위 미만을 절사하거나 마지막 회차에서 조정하므로, 계산 결과와 수천 원 수준의 차이가 날 수 있습니다.</li>
  <li>취급 수수료, 인지세, 근저당 설정비 같은 부대비용은 포함되지 않았습니다.</li>
  <li>주택담보대출은 DSR·LTV 규제로 실제 한도가 계산보다 낮아질 수 있습니다. <a href="dsr-calculator.html">DSR·대출 한도 계산기</a>로 함께 확인해 보세요.</li>
</ul>
"""

LOAN_FAQS = [
    ("원리금균등과 원금균등, 총이자는 얼마나 차이 나나요?",
     "3억 원·연 4%·30년 기준으로 원리금균등의 총이자는 약 2억 1,561만 원, 원금균등은 약 1억 8,050만 원입니다. 차이는 3,500만 원 정도지만, 원금균등의 첫 달 납입액은 약 183만 원으로 원리금균등(약 143만 원)보다 40만 원 많습니다."),
    ("체증식은 어떤 사람에게 유리한가요?",
     "앞으로 소득이 늘어날 가능성이 큰 사회초년생이나, 지금 당장 매달 나가는 현금을 줄여야 하는 상황에 맞습니다. 첫해 납입액이 낮은 대신 원금이 늦게 줄어 총이자는 원리금균등보다 많아집니다. 체증률을 3%로 두면 첫해 부담은 30%가량 줄지만, 총이자는 20% 넘게 늘어날 수 있습니다."),
    ("전세대출 이자는 어떻게 계산하나요?",
     "전세자금대출은 대부분 만기일시 상환이라 매달 이자만 냅니다. 상환방식을 &lsquo;만기일시&rsquo;로 고르고 보증금 대출 금액과 금리를 넣으면 월 이자가 바로 나옵니다. 예를 들어 2억 원을 연 3.5%로 빌리면 월 이자는 약 58만 원입니다."),
    ("거치기간이 있으면 총이자가 얼마나 늘어나나요?",
     "거치기간에는 원금이 줄지 않기 때문에 그 기간만큼 이자가 그대로 쌓입니다. 3억 원·연 4%에서 거치 2년을 두면 그 2년 동안 원금이 3억 원에 머물러 약 2,400만 원의 이자가 추가로 발생하고, 남은 기간에 나눠 갚을 원금도 그대로라 월 납입액이 늘어납니다."),
    ("변동금리인데 어떤 금리를 넣어야 하나요?",
     "현재 적용 금리를 넣어 기본 부담을 확인한 뒤, 1~2%p 높인 값으로 한 번 더 계산해 보세요. 금리가 오르면 월 납입액과 총이자가 함께 늘기 때문에, 상승 시나리오에서도 감당 가능한지 보는 것이 안전합니다."),
]

LOAN = {
    "slug": "tools/loan-interest",
    "title": "주택담보·전세대출 월 이자 계산기 | 원리금균등·원금균등·체증식 비교",
    "h1": "주택담보·전세대출 월 이자 계산기",
    "kicker": "주택담보대출 · 전세자금대출",
    "lede": "금액과 금리만 넣으면 끝나는 계산기가 아닙니다. 원리금균등·원금균등·만기일시·체증식을 나란히 놓고 첫 달 부담과 총이자를 비교하고, 연도별로 원금이 얼마나 줄어드는지 확인하세요.",
    "desc": "주택담보대출·전세대출의 월 이자와 총이자를 계산합니다. 원리금균등·원금균등·만기일시·체증식 상환방식을 비교하고 거치기간까지 반영한 연도별 상환표를 무료로 확인하세요.",
    "keywords": "대출 이자 계산기, 주담대 이자 계산, 전세대출 이자, 원리금균등, 원금균등, 만기일시, 체증식 계산, 거치기간, 연도별 상환표",
    "fields": LOAN_FIELDS,
    "results": LOAN_RESULTS,
    "script": LOAN_SCRIPT,
    "content": LOAN_CONTENT,
    "faqs": LOAN_FAQS,
    "disclaimer": "이 계산기는 연 단위 고정금리와 원 단위 절사 없는 이상적인 상환을 가정한 참고용 도구입니다. 실제 월 납입액과 총이자는 금융기관의 계산 방식, 인지세·설정비 같은 부대비용, 금리 변동에 따라 달라질 수 있으니 대출 실행 전 금융기관의 상환계획서로 확인해 주세요.",
}

# ------------------------------------------------------------------ DSR
DSR_SCRIPT = r"""
function annualRepay(balance, rate, years){ // 원리금균등 연간 원리금
  if(balance<=0) return 0;
  var m = monthlyPayment(balance, rate, Math.max(1, Math.round(years*12)));
  return m*12;
}
function stressRate(){
  var region = $('region').value, kind = $('kind').value, type = $('ltype').value;
  var base = 1.5;
  if(kind==='mortgage'){
    base = (region==='metro') ? 3.0 : (region==='local' ? 0.75 : 1.5);
  }
  var share = 1.0;
  if(type==='mixed') share = 0.8;
  if(type==='cycle') share = 0.4;
  if(type==='fixed') share = 0;
  return {base: base, share: share, add: base*share};
}
function maxLoan(annualRoom, rate, years){
  if(annualRoom<=0) return 0;
  var i = rate/100/12, n = Math.max(1, Math.round(years*12));
  var m = annualRoom/12;
  if(i===0) return m*n;
  return m*(1-Math.pow(1+i,-n))/i;
}
function calcDsr(){
  var income = n('income')*10000;              // 만원 -> 원
  var mBal = n('m-bal')*10000, mRate = n('m-rate'), mYears = n('m-years');
  var cBal = n('c-bal')*10000, cRate = n('c-rate');
  var otherMonth = n('other')*10000;
  var newRate = n('new-rate'), newYears = n('new-years');
  var limitRate = n('limit').value==='50' ? 0.5 : 0.4;

  var existMortgage = annualRepay(mBal, mRate, mYears);
  var existCredit = annualRepay(cBal, cRate, 5);  // 신용대출 DSR 산정 만기 5년
  var existOther = otherMonth*12;
  var existTotal = existMortgage + existCredit + existOther;

  var sr = stressRate();
  var judgedRate = newRate + sr.add;
  var cap = income*limitRate;
  var room = cap - existTotal;
  var limitStress = maxLoan(room, judgedRate, newYears);
  var limitPlain = maxLoan(room, newRate, newYears);
  var limitDsr0 = cap>0 ? (room/cap*100) : 0;

  // 스트레스 반영 시 실제 DSR (한도만큼 빌렸을 때)
  var dsrNow = income>0 ? ((existTotal + annualRepay(limitStress, judgedRate, newYears))/income*100) : 0;

  setText('r-main', eok(Math.max(0,limitStress)));
  setText('r-main-sub', income>0 ? ('연소득 ' + eok(income) + ' · DSR ' + $('limit').value + '% 기준') : '연소득을 입력해 주세요');
  setText('r-judged', pct(judgedRate,2)+'%');
  setText('r-stress', '+'+pct(sr.add,2)+'%p');
  setText('r-stress-detail', pct(sr.base,2)+'%p × 반영 ' + pct(sr.share*100,0)+'%');
  setText('r-room', eok(Math.max(0,room)));
  setText('r-exist', eok(existTotal));
  setText('r-cap', eok(cap));
  setText('r-limit-plain', eok(Math.max(0,limitPlain)));
  setText('r-diff', eok(Math.max(0,limitPlain-limitStress)));
  setText('r-dsr-now', pct(dsrNow,1)+'%');
  setText('r-ratio', income>0 ? pct(existTotal/income*100,1)+'%' : '-');

  var warn = '';
  if(room<=0){
    warn = '<div class="note warn"><strong>추가 여력이 없습니다.</strong> 기존 대출의 연간 원리금(' + eok(existTotal) + ')이 DSR 한도(' + eok(cap) + ')를 이미 넘었습니다. 기존 대출을 먼저 줄이거나, 만기를 늘려 원리금을 낮추거나, 소득 인정 방식을 조정해야 합니다.</div>';
  } else if(limitStress < limitPlain*0.85){
    warn = '<div class="note warn">스트레스 DSR 때문에 한도가 <strong>' + eok(limitPlain-limitStress) + '</strong> 줄었습니다. 금리 유형을 고정형·주기형으로 바꾸면 가산폭이 줄어 한도가 올라갑니다.</div>';
  } else {
    warn = '<div class="note good">DSR 여력이 남아 있습니다. 다만 실제 한도는 LTV·주택가격별 한도·신용심사에서 한 번 더 잘립니다.</div>';
  }
  $('dsr-note').innerHTML = warn;
}
bindCalc(calcDsr);
"""

DSR_FIELDS = r"""
<div class="field">
  <label for="income">연소득 (세전)</label>
  <div class="input-line"><input id="income" type="number" value="6000" step="100" min="0" inputmode="numeric"><span class="unit">만원</span></div>
  <span class="hint">근로소득은 원천징수영수증 총급여, 사업소득은 종합소득금액 기준</span>
</div>
<div class="field">
  <label for="limit">DSR 규제 한도</label>
  <select id="limit">
    <option value="40" selected>은행 40%</option>
    <option value="50">2금융권(저축은행·카드·보험) 50%</option>
  </select>
</div>
<div class="divider" style="margin:18px 0"></div>
<h3 style="font-size:14px;margin:0 0 12px;color:#0f2447">신규로 받을 대출</h3>
<div class="row-2">
  <div class="field">
    <label for="kind">대출 종류</label>
    <select id="kind">
      <option value="mortgage" selected>주택담보대출</option>
      <option value="other">신용대출·기타대출</option>
    </select>
  </div>
  <div class="field">
    <label for="region">담보 지역</label>
    <select id="region">
      <option value="metro" selected>수도권·규제지역</option>
      <option value="local">지방</option>
      <option value="none">해당 없음</option>
    </select>
  </div>
</div>
<div class="row-2">
  <div class="field">
    <label for="ltype">금리 유형</label>
    <select id="ltype">
      <option value="var" selected>변동형 (가산 100%)</option>
      <option value="mixed">혼합형 5년 고정 (80%)</option>
      <option value="cycle">주기형 5년 (40%)</option>
      <option value="fixed">만기 고정형 (0%)</option>
    </select>
  </div>
  <div class="field">
    <label for="new-years">대출 기간</label>
    <div class="input-line"><input id="new-years" type="number" value="30" step="1" min="1" max="50" inputmode="numeric"><span class="unit">년</span></div>
  </div>
</div>
<div class="field">
  <label for="new-rate">신규 대출 연 금리</label>
  <div class="input-line"><input id="new-rate" type="number" value="4.0" step="0.01" min="0" max="30" inputmode="decimal"><span class="unit">%</span></div>
  <span class="hint">스트레스 금리는 여기에 자동으로 더해집니다</span>
</div>
<div class="divider" style="margin:18px 0"></div>
<h3 style="font-size:14px;margin:0 0 12px;color:#0f2447">기존 대출</h3>
<div class="row-2">
  <div class="field">
    <label for="m-bal">주담대 잔액</label>
    <div class="input-line"><input id="m-bal" type="number" value="0" step="100" min="0" inputmode="numeric"><span class="unit">만원</span></div>
  </div>
  <div class="field">
    <label for="m-rate">주담대 금리</label>
    <div class="input-line"><input id="m-rate" type="number" value="4.0" step="0.01" min="0" inputmode="decimal"><span class="unit">%</span></div>
  </div>
</div>
<div class="row-2">
  <div class="field">
    <label for="m-years">남은 기간</label>
    <div class="input-line"><input id="m-years" type="number" value="25" step="1" min="1" inputmode="numeric"><span class="unit">년</span></div>
  </div>
  <div class="field">
    <label for="c-bal">신용대출 잔액</label>
    <div class="input-line"><input id="c-bal" type="number" value="0" step="100" min="0" inputmode="numeric"><span class="unit">만원</span></div>
  </div>
</div>
<div class="row-2">
  <div class="field">
    <label for="c-rate">신용대출 금리</label>
    <div class="input-line"><input id="c-rate" type="number" value="6.0" step="0.01" min="0" inputmode="decimal"><span class="unit">%</span></div>
    <span class="hint">DSR은 만기 5년 가정</span>
  </div>
  <div class="field">
    <label for="other">기타 월 상환액</label>
    <div class="input-line"><input id="other" type="number" value="0" step="10" min="0" inputmode="numeric"><span class="unit">만원</span></div>
    <span class="hint">자동차·마이너스통장 등</span>
  </div>
</div>
"""

DSR_RESULTS = r"""
<div class="big">
  <span class="lbl">예상 최대 대출 금액 (스트레스 DSR 반영)</span>
  <div class="val" id="r-main">-</div>
  <div class="sub" id="r-main-sub">-</div>
</div>
<dl class="kv">
  <dt>심사용 금리</dt><dd class="em" id="r-judged">-</dd>
  <dt>스트레스 가산</dt><dd id="r-stress">-</dd>
  <dt>&nbsp;└ 계산 근거</dt><dd style="font-weight:400;color:#6b7684;font-size:12.5px" id="r-stress-detail">-</dd>
  <dt>스트레스 미반영 한도</dt><dd id="r-limit-plain">-</dd>
  <dt>한도 감소액</dt><dd class="bad" id="r-diff">-</dd>
  <dt>스트레스 반영 DSR</dt><dd id="r-dsr-now">-</dd>
</dl>
<div class="divider"></div>
<dl class="kv">
  <dt>DSR 한도 금액 (연소득 × 한도)</dt><dd id="r-cap">-</dd>
  <dt>기존 대출 연간 원리금</dt><dd id="r-exist">-</dd>
  <dt>&nbsp;└ 소득 대비 비중</dt><dd id="r-ratio">-</dd>
  <dt>신규 대출에 쓸 수 있는 여력</dt><dd class="good" id="r-room">-</dd>
</dl>
<div id="dsr-note"></div>
<p class="mini">DSR(총부채원리금상환비율) = (기존 연간 원리금 + 신규 연간 원리금) ÷ 연소득. 신규 대출은 원리금균등·입력한 만기로 계산했습니다.</p>
"""

DSR_CONTENT = r"""
<h2>DSR은 &ldquo;내가 갚을 수 있는가&rdquo;를 보는 비율입니다</h2>
<p>DSR(총부채원리금상환비율, Debt Service Ratio)은 <strong>1년 동안 갚아야 하는 모든 대출의 원금과 이자를 연소득으로 나눈 비율</strong>입니다. 주택담보대출뿐 아니라 신용대출, 자동차 할부, 마이너스통장까지 모두 합산합니다. 은행은 40%, 2금융권(저축은행·카드·보험)은 50%를 넘으면 새로운 대출을 내주지 않습니다.</p>
<div class="formula">
  <code>DSR = (기존 대출의 연간 원리금 + 신규 대출의 연간 원리금) ÷ 연소득 × 100</code><br>
  신규 대출 한도 = (연소득 × DSR 한도 − 기존 연간 원리금)을 원리금균등으로 역산한 원금
</div>
<p>역산은 간단합니다. 연간 상환 여력이 <code>A</code>라면 월 상환 여력은 <code>A ÷ 12</code>이고, 이 금액을 월 이자율 <code>i</code>, 만기 <code>n</code>개월의 원리금균등 공식에 넣어 원금을 구합니다.</p>

<h2>스트레스 DSR은 왜 붙나요</h2>
<p>스트레스 DSR은 지금 금리가 아니라 <strong>금리가 더 올라도 갚을 수 있는지</strong> 심사하는 장치입니다. 실제 약정금리에 &lsquo;스트레스 금리&rsquo;를 더한 심사용 금리로 원리금을 계산해 한도를 낮춥니다. 실제로 내는 이자는 약정금리 그대로이고, 줄어드는 것은 한도뿐입니다.</p>
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>대출·지역</th><th>스트레스 금리</th><th>비고</th></tr></thead>
    <tbody>
      <tr><td>주담대 · 수도권·규제지역</td><td>3.0%p</td><td>2025.10.16부터 상향</td></tr>
      <tr><td>주담대 · 지방</td><td>0.75%p</td><td>2단계 수준 유지(2026.12.31까지)</td></tr>
      <tr><td>신용대출 등 기타 가계대출</td><td>1.5%p</td><td>신용대출은 잔액 1억 원 초과 시 적용</td></tr>
    </tbody>
  </table>
</div>
<p>금리 유형에 따라 반영 비율도 다릅니다. 변동형은 100%, 5년 고정 후 변동되는 혼합형은 80%, 5년마다 금리를 새로 정하는 주기형은 40%, 만기까지 고정이면 0%입니다. 이 계산기의 &lsquo;금리 유형&rsquo; 선택이 바로 이 비율을 적용합니다.</p>

<h2>한도를 계산하는 순서</h2>
<ol>
  <li><strong>연소득을 확정합니다</strong> — 근로자는 회사가 신고한 총급여, 사업자는 종합소득금액 기준입니다. 금융기관은 건강보험료 납부액으로 소득을 추정하기도 합니다.</li>
  <li><strong>기존 대출의 연간 원리금을 넣습니다</strong> — 주담대는 실제 금리·남은 기간, 신용대출은 DSR 산정 시 만기 5년을 가정하는 것이 일반적입니다.</li>
  <li><strong>DSR 한도 금액을 구합니다</strong> — 연소득 × 40%(또는 50%).</li>
  <li><strong>여력으로 신규 한도를 역산합니다</strong> — 위 계산기가 하는 일입니다.</li>
  <li><strong>LTV·주택가격별 한도와 비교합니다</strong> — 실제 한도는 두 값 중 작은 쪽입니다. 수도권·규제지역 주택구입 목적 주담대는 15억 원 이하 6억 원, 15억~25억 원 4억 원, 25억 원 초과 2억 원 한도가 별도로 붙습니다.</li>
</ol>

<h2>한도가 부족할 때 손볼 수 있는 것</h2>
<ul>
  <li><strong>만기를 늘립니다</strong> — 30년 만기는 40년보다 연간 원리금이 적어 한도가 올라갑니다. 다만 총이자는 늘어납니다.</li>
  <li><strong>금리 유형을 바꿉니다</strong> — 변동형보다 주기형·혼합형이 스트레스 가산이 적어 한도가 유리합니다.</li>
  <li><strong>신용대출을 정리합니다</strong> — 신용대출 잔액은 DSR을 가장 빨리 잡아먹습니다. 3,000만 원을 갚으면 연간 원리금이 700만 원가량 줄어 주담대 한도가 1억 원 이상 늘어나기도 합니다.</li>
  <li><strong>소득 증빙을 보강합니다</strong> — 부업·임대소득이 있다면 소득으로 인정받을 수 있는지 상담해 보세요.</li>
</ul>

<h2>계산 결과를 볼 때 주의할 점</h2>
<p>이 계산기는 DSR 산식만 반영합니다. 실제 심사에서는 ①금융기관이 인정하는 소득, ②기존 대출의 실제 스트레스 금리(실행 당시 기준), ③전세대출 이자 상환분, ④신용점수·재직기간 같은 종합 심사가 함께 작용합니다. 계산 결과는 &ldquo;최대 이 정도까지 가능하다&rdquo;는 상한으로 보고, 실제 신청 금액은 10~20% 낮춰 잡는 편이 안전합니다.</p>
"""

DSR_FAQS = [
    ("DSR 40%면 연봉 6,000만 원일 때 얼마까지 빌릴 수 있나요?",
     "기존 대출이 없고 은행 DSR 40%, 금리 4%, 30년 원리금균등이라면 연간 원리금 한도는 2,400만 원이고 이론상 한도는 약 4억 1,890만 원입니다. 다만 수도권·규제지역 주담대는 스트레스 금리 3%p가 붙어 심사 금리가 7%가 되고, 한도는 약 3억 원으로 줄어듭니다. 여기에 LTV와 주택가격별 한도(6억·4억·2억 원)가 다시 적용됩니다."),
    ("스트레스 DSR이 실제로 내는 이자를 올리나요?",
     "아니요. 스트레스 금리는 심사에만 쓰입니다. 약정금리 4%면 실제 이자는 4%로 계산되고, 7%는 &ldquo;금리가 7%까지 올라도 갚을 수 있는가&rdquo;를 보는 데만 쓰입니다. 달라지는 것은 받을 수 있는 한도입니다."),
    ("신용대출도 DSR에 들어가나요?",
     "네. 신용대출·자동차 할부·마이너스통장의 원리금이 모두 합산됩니다. 신용대출은 보통 만기 5년을 가정해 원리금을 계산하므로, 3,000만 원 잔액이면 연간 원리금이 약 700만 원으로 잡혀 연소득 6,000만 원 차주의 DSR을 11%p 이상 차지합니다."),
    ("전세대출은 DSR에 포함되나요?",
     "전세대출 원금은 원칙적으로 DSR에서 제외되고 이자 상환분만 반영됩니다. 다만 2025년 10월 29일부터 1주택자가 수도권·규제지역에서 받는 전세대출은 이자상환분이 DSR에 들어갑니다. 버팀목 전세대출 같은 정책 상품은 별도 기준이 적용됩니다."),
    ("DSR 계산 결과와 은행에서 알려 준 한도가 다른 이유는 무엇인가요?",
     "은행은 자체 인정소득, 기존 대출의 실제 스트레스 금리, 신용등급, 연체 이력, 주택 담보가치(LTV), 주택가격별 총액 한도를 모두 반영합니다. 이 계산기는 공개된 DSR 산식만 적용한 상한값이므로, 실제 한도는 더 낮게 나오는 것이 보통입니다."),
]

DSR = {
    "slug": "tools/dsr-calculator",
    "title": "DSR·대출 한도 계산기 | 스트레스 DSR 반영 예상 한도",
    "h1": "DSR·대출 한도 계산기",
    "kicker": "총부채원리금상환비율 · 스트레스 DSR",
    "lede": "연소득과 기존 대출만 넣으면 DSR 40% 기준으로 얼마까지 빌릴 수 있는지, 스트레스 금리가 한도를 얼마나 깎는지 바로 확인할 수 있습니다.",
    "desc": "연소득과 기존 대출을 입력하면 DSR(총부채원리금상환비율) 40%·50% 기준 예상 대출 한도를 계산합니다. 수도권·규제지역 스트레스 DSR 3.0%p와 금리 유형별 반영률까지 적용한 무료 계산기입니다.",
    "keywords": "DSR 계산기, 대출 한도 계산기, 스트레스 DSR, 총부채원리금상환비율, 주담대 한도, 신용대출 한도, DSR 40%",
    "fields": DSR_FIELDS,
    "results": DSR_RESULTS,
    "script": DSR_SCRIPT,
    "content": DSR_CONTENT,
    "faqs": DSR_FAQS,
    "disclaimer": "이 계산기는 공개된 DSR 산식과 2026년 11월 기준 스트레스 금리를 적용한 참고용 추정치입니다. 실제 한도는 금융기관의 인정소득, 신용 심사, LTV, 주택가격별 총액 한도에 따라 달라지며, 스트레스 금리는 금융위원회 행정지도 변경에 따라 수시로 바뀝니다.",
}

# ------------------------------------------------------------------ 취득세·중개보수
PROP_SCRIPT = r"""
function acqRate(price){
  var eok = price/100000000;
  if(eok <= 6) return 1.0;
  if(eok <= 9) return (eok*2/3 - 3);
  return 3.0;
}
function brokerage(amount, trade){
  // trade: 'sale' | 'lease'  -> [상한요율(%), 한도액(원 or 0)]
  var a = amount;
  if(trade==='sale'){
    if(a < 50000000) return [0.6, 250000];
    if(a < 200000000) return [0.5, 800000];
    if(a < 900000000) return [0.4, 0];
    if(a < 1200000000) return [0.5, 0];
    if(a < 1500000000) return [0.6, 0];
    return [0.7, 0];
  }
  if(a < 50000000) return [0.5, 200000];
  if(a < 100000000) return [0.4, 300000];
  if(a < 600000000) return [0.3, 0];
  if(a < 1200000000) return [0.4, 0];
  if(a < 1500000000) return [0.5, 0];
  return [0.6, 0];
}
function calcProp(){
  var trade = $('trade').value;       // sale | jeonse | wolse
  var price = n('price');
  var deposit = n('deposit')*10000, monthly = n('monthly')*10000;
  var houses = $('houses').value;
  var big = $('big').checked;
  var first = $('first').checked;

  var dealAmount = price;
  if(trade!=='sale'){
    dealAmount = deposit + monthly*100;
    if(dealAmount < 50000000) dealAmount = deposit + monthly*70;
  }

  // 취득세 (매매만)
  var rate = 0, taxBase = 0, edu = 0, farm = 0, total = 0, reduced = 0, note = '';
  if(trade==='sale'){
    taxBase = price;
    if(houses==='one'){ rate = acqRate(price); }
    else if(houses==='two'){ rate = 8; }
    else { rate = 12; }
    var base = taxBase*rate/100;
    edu = base*0.1;
    farm = big ? taxBase*0.002 : 0;
    total = base + edu + farm;
    if(first && houses==='one' && price <= 1200000000){
      reduced = Math.min(2000000, total);
      total -= reduced;
    }
    if(houses!=='one') note = '<div class="note warn">다주택 중과세율(2주택 8%, 3주택 이상 12%)을 적용했습니다. 중과 유예 적용 여부와 조정대상지역 지정은 취득 시점에 관할 관청에서 확인해야 합니다.</div>';
  } else {
    note = '<div class="note">전세·월세는 취득세가 발생하지 않습니다(임차인 기준). 아래 중개보수만 확인하세요.</div>';
  }

  var br = brokerage(dealAmount, trade==='sale' ? 'sale' : 'lease');
  var brFee = dealAmount*br[0]/100;
  if(br[1] > 0 && brFee > br[1]) brFee = br[1];
  var brEach = brFee;  // 매도·매수 각각 부담 (임대차는 임대인·임차인 각각)

  setText('price-hint', trade==='sale' ? eok(price) : (eok(dealAmount) + ' 환산'));
  setText('r-main', won(total));
  setText('r-main-label', trade==='sale' ? '총 취득세 (본세+지방교육세+농특세)' : '취득세 없음 (임차인)');
  setText('r-main-sub', trade==='sale' ? ('과세표준 ' + won(taxBase) + ' · 적용세율 ' + pct(rate,2) + '%') : '전세·월세 계약은 취득세 대신 중개보수만 발생합니다');

  setText('r-rate', trade==='sale' ? pct(rate,2)+'%' : '-');
  setText('r-base', trade==='sale' ? won(taxBase*rate/100) : '-');
  setText('r-edu', trade==='sale' ? won(edu) : '-');
  setText('r-farm', trade==='sale' ? won(farm) : '-');
  setText('r-reduced', trade==='sale' ? (reduced>0 ? '-'+won(reduced) : '해당 없음') : '-');
  setText('r-total', won(total));

  setText('r-deal', won(dealAmount));
  setText('r-br-rate', pct(br[0],2)+'%');
  setText('r-br-each', won(brFee) + (br[1]>0 ? ' (한도 ' + num(br[1]) + '원)' : ''));
  setText('r-br-total', won(brFee*2));
  setText('r-all', won(total + brFee*2));
  $('prop-note').innerHTML = note;
}
bindCalc(calcProp);
"""

PROP_FIELDS = r"""
<div class="field">
  <label for="trade">거래 유형</label>
  <select id="trade">
    <option value="sale" selected>매매 (취득세 + 중개보수)</option>
    <option value="jeonse">전세 (중개보수만)</option>
    <option value="wolse">월세 (중개보수만)</option>
  </select>
</div>
<div class="field" id="f-price">
  <label for="price">매매 가격</label>
  <div class="input-line"><input id="price" type="number" value="600000000" step="1000000" min="0" inputmode="numeric"><span class="unit">원</span></div>
  <span class="hint" id="price-hint">6억원</span>
  <div class="chips">
    <button type="button" data-set="price" data-val="400000000">4억</button>
    <button type="button" data-set="price" data-val="600000000">6억</button>
    <button type="button" data-set="price" data-val="900000000">9억</button>
    <button type="button" data-set="price" data-val="1200000000">12억</button>
  </div>
</div>
<div class="row-2" id="f-lease">
  <div class="field">
    <label for="deposit">보증금</label>
    <div class="input-line"><input id="deposit" type="number" value="30000" step="100" min="0" inputmode="numeric"><span class="unit">만원</span></div>
  </div>
  <div class="field">
    <label for="monthly">월세</label>
    <div class="input-line"><input id="monthly" type="number" value="0" step="10" min="0" inputmode="numeric"><span class="unit">만원</span></div>
  </div>
</div>
<div class="row-2">
  <div class="field">
    <label for="houses">주택 수 (매매)</label>
    <select id="houses">
      <option value="one" selected>1주택 (또는 무주택 취득)</option>
      <option value="two">2주택 (조정대상지역)</option>
      <option value="three">3주택 이상 · 법인</option>
    </select>
  </div>
  <div class="field">
    <label>면적·감면</label>
    <label class="switch"><input type="checkbox" id="big"> 전용 85㎡ 초과 (농특세 0.2%)</label>
    <label class="switch"><input type="checkbox" id="first"> 생애최초 취득세 감면</label>
  </div>
</div>
<p class="mini">생애최초 감면은 취득가 12억 원 이하 1주택 취득 시 최대 200만 원까지 적용됩니다. 월세는 &lsquo;보증금 + 월세×100&rsquo;으로 거래금액을 환산하고, 5천만 원 미만이면 월세×70을 적용합니다.</p>
"""

PROP_RESULTS = r"""
<div class="big">
  <span class="lbl" id="r-main-label">총 취득세 (본세+지방교육세+농특세)</span>
  <div class="val" id="r-main">-</div>
  <div class="sub" id="r-main-sub">-</div>
</div>
<dl class="kv">
  <dt>적용 취득세율</dt><dd class="em" id="r-rate">-</dd>
  <dt>취득세 본세</dt><dd id="r-base">-</dd>
  <dt>지방교육세 (본세의 10%)</dt><dd id="r-edu">-</dd>
  <dt>농어촌특별세 (0.2%)</dt><dd id="r-farm">-</dd>
  <dt>생애최초 감면</dt><dd class="good" id="r-reduced">-</dd>
  <dt><strong>취득세 합계</strong></dt><dd><strong id="r-total">-</strong></dd>
</dl>
<div class="divider"></div>
<dl class="kv">
  <dt>중개보수 거래금액</dt><dd id="r-deal">-</dd>
  <dt>적용 상한요율</dt><dd id="r-br-rate">-</dd>
  <dt>한쪽(매도자·매수자) 부담</dt><dd id="r-br-each">-</dd>
  <dt>양쪽 합계 (보통 매수자만 부담)</dt><dd id="r-br-total">-</dd>
  <dt><strong>취득세 + 중개보수 합계</strong></dt><dd><strong class="em" id="r-all">-</strong></dd>
</dl>
<div id="prop-note"></div>
<p class="mini">중개보수는 법정 상한요율과 한도액이며, 실제 금액은 중개의뢰인과 개업공인중개사가 협의해 정합니다. 매매·교환은 거래금액의 0.9%, 임대차는 0.8% 이내에서 협의가 가능합니다.</p>
"""

PROP_CONTENT = r"""
<h2>집을 사면 세금과 복비가 얼마나 나갈까요</h2>
<p>계약금을 치르고 나면 가장 먼저 나가는 돈이 <strong>취득세</strong>와 <strong>중개보수(복비)</strong>입니다. 6억 원짜리 집을 사면 취득세가 660만 원(85㎡ 이하)~780만 원(85㎡ 초과), 중개보수가 240만 원 안팎이라 계약 직후 1,000만 원 가까운 현금이 필요합니다. 이 계산기는 두 금액을 한 화면에서 계산해 계약일까지 준비할 현금을 가늠하게 해 줍니다.</p>

<h2>취득세 계산 공식</h2>
<div class="formula">
  취득세 본세 = 과세표준 × 세율<br>
  6억 원 이하: <code>1%</code> · 6억 초과 9억 이하: <code>(취득가액 억 단위 × 2/3 − 3)%</code> · 9억 원 초과: <code>3%</code><br>
  지방교육세 = 취득세 본세 × 10%<br>
  농어촌특별세 = 과세표준 × 0.2% (전용 85㎡ 초과 주택만)
</div>
<p>6억~9억 구간이 헷갈리는 이유는 세율이 고정값이 아니라 <strong>가격에 따라 1%에서 3%로 올라가는 누진 구조</strong>이기 때문입니다. 예를 들어 7억 5,000만 원이면 (7.5 × 2/3 − 3) = 2%가 적용됩니다. 9억 원에서 정확히 3%가 되고, 그 위로는 다시 3% 고정입니다. 그래서 9억 원과 9억 100만 원의 세금 차이가 크지 않지만, 6억 원과 6억 100만 원은 세율이 1%에서 1.01%로 바뀌며 총액이 눈에 띄게 달라집니다.</p>

<h3>다주택자는 세율이 다릅니다</h3>
<p>조정대상지역에서 2주택을 취득하면 8%, 3주택 이상이거나 법인이면 12%가 적용됩니다. 10억 원 주택을 2주택자로 사면 취득세만 8,000만 원을 넘습니다. 다만 정부가 여러 차례 중과 유예를 연장해 왔기 때문에, 실제 적용 세율은 계약 시점의 유예 여부를 관할 구청에 확인해야 합니다.</p>

<h2>중개보수(복비) 계산 공식</h2>
<p>중개보수는 <strong>거래금액 × 상한요율</strong>로 계산하고, 구간별 한도액이 있으면 그 금액을 넘을 수 없습니다. 매매와 임대차의 요율표가 다릅니다.</p>
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>매매·교환</th><th>상한요율</th><th>한도액</th></tr></thead>
    <tbody>
      <tr><td>5천만 원 미만</td><td>0.6%</td><td>25만 원</td></tr>
      <tr><td>5천만 ~ 2억 원</td><td>0.5%</td><td>80만 원</td></tr>
      <tr><td>2억 ~ 9억 원</td><td>0.4%</td><td>없음</td></tr>
      <tr><td>9억 ~ 12억 원</td><td>0.5%</td><td>없음</td></tr>
      <tr><td>12억 ~ 15억 원</td><td>0.6%</td><td>없음</td></tr>
      <tr><td>15억 원 이상</td><td>0.7%</td><td>없음</td></tr>
    </tbody>
  </table>
</div>
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>임대차(전세·월세)</th><th>상한요율</th><th>한도액</th></tr></thead>
    <tbody>
      <tr><td>5천만 원 미만</td><td>0.5%</td><td>20만 원</td></tr>
      <tr><td>5천만 ~ 1억 원</td><td>0.4%</td><td>30만 원</td></tr>
      <tr><td>1억 ~ 6억 원</td><td>0.3%</td><td>없음</td></tr>
      <tr><td>6억 ~ 12억 원</td><td>0.4%</td><td>없음</td></tr>
      <tr><td>12억 ~ 15억 원</td><td>0.5%</td><td>없음</td></tr>
      <tr><td>15억 원 이상</td><td>0.6%</td><td>없음</td></tr>
    </tbody>
  </table>
</div>
<p>월세는 거래금액을 <strong>보증금 + (월세 × 100)</strong>으로 환산합니다. 예를 들어 보증금 1,000만 원, 월세 80만 원이면 거래금액은 9,000만 원이 되어 임대차 0.4% 구간에 들어갑니다. 환산액이 5천만 원 미만이면 월세 × 70을 적용하는 예외가 있습니다.</p>

<h2>취득세, 언제 내나요</h2>
<p>취득세는 잔금을 치르고 등기를 하기 전에 내야 합니다. 등기를 먼저 하려면 취득세를 납부한 영수증이 필요하기 때문입니다. 신고·납부 기한은 취득일(잔금일)부터 60일 이내이고, 기한을 넘기면 무신고 가산세 20%와 납부지연 가산세가 붙습니다. 상속은 6개월, 증여는 3개월로 기한이 다릅니다.</p>

<h2>이럴 때 써 보세요</h2>
<ul>
  <li><strong>가계약 전 현금 계획</strong> — 매매가를 넣고 취득세와 복비 합계를 확인해 잔금일 준비 금액을 잡습니다.</li>
  <li><strong>6억·9억 경계선 비교</strong> — 5억 9,000만 원과 6억 1,000만 원, 8억 9,000만 원과 9억 1,000만 원을 각각 넣어 세금 차이를 확인하세요.</li>
  <li><strong>전세·월세 복비 확인</strong> — 중개사가 부른 금액이 상한을 넘는지 확인합니다. 상한을 넘겨 받는 것은 불법입니다.</li>
  <li><strong>생애최초 감면 대상 확인</strong> — 무주택 세대가 12억 원 이하 주택을 처음 사는 경우 최대 200만 원 감면됩니다.</li>
</ul>
"""

PROP_FAQS = [
    ("6억 원과 6억 1,000만 원, 취득세가 얼마나 차이 나나요?",
     "6억 원은 1%로 본세 600만 원, 지방교육세 60만 원(85㎡ 초과면 농특세 120만 원 추가)입니다. 6억 1,000만 원은 세율이 약 1.07%로 올라 본세가 650만 원을 넘습니다. 1,000만 원 차이로 세금이 50만 원 이상 달라지므로, 6억 원 근처라면 계약가를 조정할 여지가 있는지 따져 볼 만합니다."),
    ("85㎡ 초과하면 세금이 얼마나 더 나오나요?",
     "농어촌특별세 0.2%가 추가됩니다. 6억 원 주택이면 120만 원, 9억 원 주택이면 180만 원이 더 붙습니다. 85㎡ 이하는 취득세 1% + 지방교육세 0.1%로 총 1.1%, 초과하면 1.3%가 됩니다."),
    ("중개보수 상한을 넘겨 달라고 하면 어떻게 해야 하나요?",
     "법정 상한요율과 한도액을 넘는 중개보수는 받을 수 없습니다. 초과 요구는 공인중개사법 위반으로, 관할 지자체에 신고할 수 있습니다. 계약 전에 중개보수 금액과 요율을 서면으로 확인받고, 지급 시기(보통 잔금일)도 정확히 적어 두세요."),
    ("생애최초 취득세 감면은 누가 받을 수 있나요?",
     "본인과 배우자가 주택을 소유한 적이 없는 세대가 취득가액 12억 원 이하 주택을 처음 취득할 때 최대 200만 원까지 감면됩니다. 취득 후 3개월 이내에 주민등록을 옮기고 3년 이상 거주해야 하며, 기한 내 전입하지 않으면 감면이 취소됩니다. 정확한 요건은 관할 구청 세무과에 확인하세요."),
    ("다주택 중과세, 지금도 적용되나요?",
     "법령상 2주택 8%, 3주택 이상·법인 12%의 중과세율이 있습니다. 다만 정부가 중과 유예를 반복 연장해 왔기 때문에 실제 적용 여부는 취득 시점의 유예 조치와 조정대상지역 지정 여부에 따라 달라집니다. 이 계산기의 &lsquo;주택 수&rsquo; 선택은 중과세율이 적용된다고 가정한 값입니다."),
]

PROP = {
    "slug": "tools/property-tax-fee",
    "title": "부동산 취득세·중개보수(복비) 계산기 | 매매·전세·월세",
    "h1": "부동산 취득세·중개보수 계산기",
    "kicker": "취득세 · 중개보수",
    "lede": "매매가를 넣으면 취득세 본세·지방교육세·농특세와 중개보수 상한이 한 번에 나옵니다. 전세·월세는 중개보수만 계산하고, 6억·9억 구간의 누진 세율도 그대로 반영합니다.",
    "desc": "부동산 매매 취득세(1~3% 누진, 지방교육세, 농어촌특별세)와 중개보수 상한을 계산합니다. 매매·전세·월세, 다주택 중과, 생애최초 감면, 85㎡ 초과 여부를 반영한 무료 계산기입니다.",
    "keywords": "취득세 계산기, 취득세율, 중개보수 계산기, 복비 계산, 부동산 세금, 지방교육세, 농어촌특별세, 생애최초 취득세 감면, 다주택 취득세",
    "fields": PROP_FIELDS,
    "results": PROP_RESULTS,
    "script": PROP_SCRIPT,
    "content": PROP_CONTENT,
    "faqs": PROP_FAQS,
    "disclaimer": "취득세율과 중개보수 요율은 2026년 11월 기준 법령·조례를 따랐으나, 지방자치단체 조례, 조정대상지역 지정, 중과 유예, 개별 물건의 지분·면적에 따라 달라질 수 있습니다. 취득세는 반드시 관할 구청 세무과의 모의계산과 고지서로 확인하세요.",
}
