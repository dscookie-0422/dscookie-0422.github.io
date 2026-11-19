# -*- coding: utf-8 -*-
"""Pages: 월세 vs 전세, 예적금, 연봉 실수령액"""

RENT_SCRIPT = r"""
function calcRent(){
  var jeonse = n('j-price'), jRate = n('j-rate'), jRatio = n('j-ratio');
  var wDep = n('w-deposit'), wRent = n('w-rent');
  var years = Math.max(1, n('years'));
  var yieldPct = n('yield');

  var loan = jeonse*jRatio/100;
  var myCashJ = Math.max(0, jeonse - loan);
  var jInterest = loan*jRate/100;
  var jOpp = myCashJ*yieldPct/100;
  var jAnnual = jInterest + jOpp;

  var wOpp = wDep*yieldPct/100;
  var wAnnual = wRent*12 + wOpp;

  var diff = jAnnual - wAnnual;   // 양수면 전세가 더 비쌈 = 월세 유리
  var jMonthly = jAnnual/12, wMonthly = wAnnual/12;

  var better = diff > 0 ? '월세' : (diff < 0 ? '전세' : '비슷함');
  var saveAbs = Math.abs(diff);

  setText('r-main', better==='비슷함' ? '비슷합니다' : (better + '가 유리합니다'));
  setText('r-main-label', '연간 비용 비교 결과');
  setText('r-main-sub', better==='비슷함'
      ? '연간 비용 차이가 거의 없습니다'
      : ('연 ' + won(saveAbs) + ' · ' + years + '년이면 ' + eok(saveAbs*years) + ' 차이'));

  setText('r-j-month', won(jMonthly));
  setText('r-w-month', won(wMonthly));
  setText('r-j-year', won(jAnnual));
  setText('r-w-year', won(wAnnual));
  setText('r-j-total', won(jAnnual*years));
  setText('r-w-total', won(wAnnual*years));
  setText('r-diff', (diff>=0?'+':'') + won(diff) + ' / 년');
  setText('r-diff-total', (diff>=0?'+':'') + won(diff*years));
  setText('j-hint', eok(jeonse));
  setText('wd-hint', eok(wDep));
  setText('wr-hint', eok(wRent));
  setText('r-loan', eok(loan));
  setText('r-cash', eok(myCashJ));
  setText('r-j-int', won(jInterest) + ' / 년');
  setText('r-j-opp', won(jOpp) + ' / 년');

  // 손익분기 월세: 전세 비용과 같아지는 월세 (보증금은 현재 월세 보증금 가정)
  var be = (jAnnual - wOpp)/12;
  setText('r-breakeven', won(Math.max(0,be)));

  var max = Math.max(jAnnual, wAnnual, 1);
  $('bar-j').style.width = (jAnnual/max*100).toFixed(1)+'%';
  $('bar-w').style.width = (wAnnual/max*100).toFixed(1)+'%';
  $('bar-j-val').textContent = won(jAnnual);
  $('bar-w-val').textContent = won(wAnnual);

  var note = '';
  if(jRatio>0 && myCashJ<0) note = '<div class="note warn">전세대출이 보증금보다 많습니다. 대출 비율을 다시 확인해 주세요.</div>';
  else if(jAnnual>0 && Math.abs(diff)/Math.max(jAnnual,wAnnual) < 0.05) note = '<div class="note">차이가 5% 안쪽이라 어느 쪽을 골라도 비슷합니다. 이사 부담·집 상태·재계약 조건을 함께 보세요.</div>';
  else note = '<div class="note ' + (diff>0?'good':'') + '">' + (diff>0
      ? '같은 기간 동안 <strong>월세</strong>가 ' + eok(Math.abs(diff)*years) + ' 저렴합니다. 다만 보증금을 돌려받는 시점과 집값 변동은 따로 봐야 합니다.'
      : '같은 기간 동안 <strong>전세</strong>가 ' + eok(Math.abs(diff)*years) + ' 저렴합니다. 대출 금리가 오르면 차이가 줄어들 수 있습니다.') + '</div>';
  $('rent-note').innerHTML = note;
}
bindCalc(calcRent);
"""

RENT_FIELDS = r"""
<div class="field">
  <label for="j-price">전세 보증금</label>
  <div class="input-line"><input id="j-price" type="number" value="400000000" step="1000000" min="0" inputmode="numeric"><span class="unit">원</span></div>
  <span class="hint" id="j-hint">4억원</span>
  <div class="chips">
    <button type="button" data-set="j-price" data-val="200000000">2억</button>
    <button type="button" data-set="j-price" data-val="300000000">3억</button>
    <button type="button" data-set="j-price" data-val="400000000">4억</button>
    <button type="button" data-set="j-price" data-val="600000000">6억</button>
  </div>
</div>
<div class="row-2">
  <div class="field">
    <label for="j-rate">전세대출 금리</label>
    <div class="input-line"><input id="j-rate" type="number" value="3.5" step="0.01" min="0" max="20" inputmode="decimal"><span class="unit">%</span></div>
  </div>
  <div class="field">
    <label for="j-ratio">전세대출 비율</label>
    <div class="input-line"><input id="j-ratio" type="number" value="80" step="5" min="0" max="100" inputmode="numeric"><span class="unit">%</span></div>
  </div>
</div>
<div class="divider" style="margin:18px 0"></div>
<div class="row-2">
  <div class="field">
    <label for="w-deposit">월세 보증금</label>
    <div class="input-line"><input id="w-deposit" type="number" value="50000000" step="1000000" min="0" inputmode="numeric"><span class="unit">원</span></div>
    <span class="hint" id="wd-hint">5,000만원</span>
  </div>
  <div class="field">
    <label for="w-rent">월세</label>
    <div class="input-line"><input id="w-rent" type="number" value="1200000" step="10000" min="0" inputmode="numeric"><span class="unit">원</span></div>
    <span class="hint" id="wr-hint">120만원</span>
  </div>
</div>
<div class="row-2">
  <div class="field">
    <label for="years">비교 기간</label>
    <div class="input-line"><input id="years" type="number" value="2" step="1" min="1" max="10" inputmode="numeric"><span class="unit">년</span></div>
  </div>
  <div class="field">
    <label for="yield">목돈 운용 수익률</label>
    <div class="input-line"><input id="yield" type="number" value="3.0" step="0.1" min="0" max="20" inputmode="decimal"><span class="unit">%</span></div>
    <span class="hint">보증금을 넣지 않았을 때 기대 수익</span>
  </div>
</div>
<p class="mini">전세대출은 만기일시(이자만 납부) 가정입니다. 전세대출 비율을 0으로 두면 자기 자금만으로 전세를 구하는 경우를 계산합니다.</p>
"""

RENT_RESULTS = r"""
<div class="big">
  <span class="lbl" id="r-main-label">연간 비용 비교 결과</span>
  <div class="val" id="r-main">-</div>
  <div class="sub" id="r-main-sub">-</div>
</div>
<div class="bar-rows">
  <div class="bar-row"><span class="bar-k">전세</span><div class="bar-track"><span class="bar-fill fill-j" id="bar-j"></span></div><span class="bar-v" id="bar-j-val">-</span></div>
  <div class="bar-row"><span class="bar-k">월세</span><div class="bar-track"><span class="bar-fill fill-w" id="bar-w"></span></div><span class="bar-v" id="bar-w-val">-</span></div>
</div>
<p class="mini">막대는 연간 비용(이자·월세·기회비용 합계)입니다.</p>
<div class="divider"></div>
<dl class="kv">
  <dt>전세 — 월 환산 비용</dt><dd id="r-j-month">-</dd>
  <dt>월세 — 월 환산 비용</dt><dd id="r-w-month">-</dd>
  <dt>전세 연간 비용</dt><dd class="em" id="r-j-year">-</dd>
  <dt>월세 연간 비용</dt><dd class="em" id="r-w-year">-</dd>
  <dt>전세 총비용 (기간)</dt><dd id="r-j-total">-</dd>
  <dt>월세 총비용 (기간)</dt><dd id="r-w-total">-</dd>
  <dt>연간 차액 (전세−월세)</dt><dd id="r-diff">-</dd>
  <dt>기간 총 차액</dt><dd><strong id="r-diff-total">-</strong></dd>
  <dt>전세대출 금액 · 자기자금</dt><dd><span id="r-loan">-</span> · <span id="r-cash">-</span></dd>
  <dt>전세대출 이자</dt><dd id="r-j-int">-</dd>
  <dt>자기자금 기회비용</dt><dd id="r-j-opp">-</dd>
  <dt>전세와 같아지는 월세</dt><dd class="good" id="r-breakeven">-</dd>
</dl>
<div id="rent-note"></div>
"""

RENT_CONTENT = r"""
<h2>월세와 전세, 숫자로 비교하는 법</h2>
<p>&ldquo;전세대출 이자가 아깝다&rdquo;는 말과 &ldquo;월세는 나가는 돈이다&rdquo;는 말이 동시에 도는 이유는, 두 방식의 비용 구조가 다르기 때문입니다. 전세는 <strong>목돈을 묶어 두는 비용</strong>이 들고, 월세는 <strong>매달 현금이 나가는 비용</strong>이 듭니다. 이 계산기는 두 비용을 같은 단위(연간 원)로 바꿔 놓고 비교합니다.</p>

<h2>계산 공식</h2>
<div class="formula">
  <strong>전세 비용</strong> = 전세대출 이자 + (전세금 − 대출금) × 운용수익률<br>
  &nbsp;&nbsp;전세대출 이자 = 전세금 × 대출비율 × 금리<br>
  <strong>월세 비용</strong> = 월세 × 12 + 월세보증금 × 운용수익률<br>
  <strong>차액</strong> = 전세 비용 − 월세 비용 &nbsp;(양수면 월세가 유리)
</div>
<p>핵심은 <strong>기회비용</strong>입니다. 전세로 4억 원을 맡기면 그 돈으로 얻을 수 있었던 이자·수익을 포기하게 됩니다. 월세 보증금 5,000만 원도 마찬가지입니다. 운용수익률을 0%로 두면 &ldquo;실제로 나가는 현금&rdquo;만 비교하는 셈이고, 3~4%로 두면 &ldquo;목돈을 굴렸다면 얻었을 수익까지 포함&rdquo;한 비교가 됩니다.</p>

<h2>전세대출 이자는 왜 이자가 아니라 비용인가요</h2>
<p>전세대출로 낸 이자는 집주인에게 가는 돈이 아니라 금융기관에 내는 비용입니다. 월세와 똑같이 매달 사라지는 돈이므로, 두 방식을 비교할 때는 반드시 전세 쪽 비용에 포함해야 합니다. 전세대출 비율을 80%로 두면 4억 원 전세에서 대출 3억 2,000만 원, 자기자금 8,000만 원으로 계산합니다.</p>

<h2>실제 예시로 보기</h2>
<p>전세 4억 원, 전세대출 80%·연 3.5%, 월세 보증금 5,000만 원·월세 120만 원, 운용수익률 3%라면 이렇게 됩니다.</p>
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>항목</th><th>전세</th><th>월세</th></tr></thead>
    <tbody>
      <tr><td>연간 이자·월세</td><td>1,120만 원</td><td>1,440만 원</td></tr>
      <tr><td>목돈 기회비용</td><td>240만 원(자기자금 8,000만 원)</td><td>150만 원(보증금 5,000만 원)</td></tr>
      <tr><td>연간 총비용</td><td>1,360만 원</td><td>1,590만 원</td></tr>
      <tr><td>월 환산</td><td>113만 원</td><td>132만 원</td></tr>
    </tbody>
  </table>
</div>
<p>이 조건에서는 전세가 연 230만 원 저렴합니다. 하지만 전세대출 금리가 4.5%로 오르면 전세 비용이 1,680만 원이 되어 월세보다 비싸집니다. <strong>금리 1%p가 판단을 뒤집는 지점</strong>이 생기므로, 금리를 0.5%p씩 올려 가며 다시 계산해 보는 것이 좋습니다.</p>

<h2>숫자 밖에서 봐야 하는 것</h2>
<ul>
  <li><strong>보증금 회수 위험</strong> — 전세는 계약이 끝날 때 목돈을 돌려받아야 합니다. 전세가율이 높거나 다주택 임대인이라면 전세보증금 반환보증(HUG·HF) 가입 여부를 확인하세요.</li>
  <li><strong>재계약·이사 비용</strong> — 2년마다 이사하면 중개보수와 이사비가 반복됩니다. 전세를 길게 유지할 수 있는지도 비용입니다.</li>
  <li><strong>금리 변동</strong> — 전세대출은 대부분 변동금리이거나 6개월·1년 단위로 조정됩니다. 금리 상승 시나리오에서도 감당 가능한지 보세요.</li>
  <li><strong>월세의 협상 여지</strong> — 보증금을 올리면 월세를 낮출 수 있습니다. 보증금 1,000만 원을 더 넣고 월세 5만 원을 깎는 조건이 유리한지도 이 계산기로 확인할 수 있습니다.</li>
  <li><strong>주거 안정성</strong> — 월세는 갱신 계약에서 보증금·월세 인상 요구를 받을 수 있습니다. 5% 인상 상한이 있지만 2년마다 반복됩니다.</li>
</ul>

<h2>이럴 때 써 보세요</h2>
<ul>
  <li>전세와 월세 매물을 두고 고민할 때 — 두 조건을 그대로 넣으면 연간·기간 총비용 차이가 나옵니다.</li>
  <li>전세대출 금리가 오를 때 — 금리를 0.5%p씩 올려 어느 지점에서 판단이 뒤집히는지 확인합니다.</li>
  <li>반전세(보증금 + 월세)를 비교할 때 — 보증금과 월세를 넣고 보증금을 올린 조건을 다시 계산합니다.</li>
  <li>전세를 월세로 돌릴지 고민될 때 — &lsquo;전세와 같아지는 월세&rsquo; 값보다 실제 월세가 낮으면 월세가 유리합니다.</li>
</ul>
"""

RENT_FAQS = [
    ("전세대출 이자는 비용에 넣어야 하나요?",
     "넣어야 합니다. 전세대출 이자는 매달 금융기관에 나가는 현금이라 월세와 성격이 같습니다. 이자를 빼고 비교하면 전세가 실제보다 싸게 보입니다. 이 계산기는 전세대출 이자와 자기자금 기회비용을 모두 전세 비용에 포함합니다."),
    ("기회비용 수익률은 몇 %로 넣어야 하나요?",
     "목돈을 실제로 어디에 둘지에 맞춰 넣으세요. 예금·적금이면 연 3% 안팎, 채권·배당주면 4~5%, 그냥 통장에 두면 0%입니다. 수익률을 높게 잡을수록 전세 비용이 커져 월세가 유리하게 나옵니다. 0%와 4% 두 가지로 각각 계산해 보면 판단이 흔들리지 않습니다."),
    ("보증금이 있는 월세는 어떻게 비교하나요?",
     "월세 보증금도 목돈이 묶이는 것이므로 기회비용에 포함합니다. 보증금 5,000만 원, 월세 120만 원, 수익률 3%라면 연간 비용은 1,440만 원 + 150만 원 = 1,590만 원입니다. 보증금을 올려 월세를 낮춘 조건도 같은 방식으로 넣어 비교하세요."),
    ("전세가 유리하다고 나오면 무조건 전세가 좋은가요?",
     "숫자는 비용만 봅니다. 전세는 계약 종료 시 보증금을 돌려받아야 하고, 집주인의 반환 능력에 따라 위험이 생깁니다. 전세가율이 80%를 넘거나 임대인이 다주택자라면 전세보증금 반환보증 가입을 확인하세요. 월세는 매달 현금이 나가지만 보증금 위험이 작고 이사가 자유롭다는 장점이 있습니다."),
]

RENT = {
    "slug": "tools/rent-vs-jeonse",
    "title": "월세 vs 전세 손익 비교 계산기 | 전세대출 이자·기회비용",
    "h1": "월세 vs 전세 손익 비교 계산기",
    "kicker": "전세대출 이자 · 목돈 기회비용",
    "lede": "전세 4억과 월세 120만 원, 어느 쪽이 실제로 더 나갈까요. 전세대출 이자와 목돈 기회비용까지 같은 단위로 바꿔 연간·기간 총비용을 비교합니다.",
    "desc": "월세와 전세의 실제 비용을 비교합니다. 전세대출 이자와 보증금 기회비용을 반영해 연간 비용, 기간 총비용, 판단이 뒤집히는 월세 수준까지 계산하는 무료 계산기입니다.",
    "keywords": "월세 전세 비교, 전세 월세 계산기, 전세대출 이자, 기회비용, 반전세 비교, 주거비 계산",
    "fields": RENT_FIELDS,
    "results": RENT_RESULTS,
    "script": RENT_SCRIPT,
    "content": RENT_CONTENT,
    "faqs": RENT_FAQS,
    "disclaimer": "이 계산기는 전세대출을 만기일시 상환으로 가정하고, 보증금 반환 위험·이사비·중개보수·세금(임대소득세 등)은 포함하지 않습니다. 실제 주거 비용은 계약 조건과 금리 변동에 따라 달라지므로 참고용으로만 활용하세요.",
}

# ------------------------------------------------------------------ 예적금
SAVE_SCRIPT = r"""
function calcSave(){
  var kind = $('kind').value;          // save(적금) | deposit(예금)
  var monthly = n('monthly'), lump = n('lump');
  var rate = n('rate'), months = Math.max(1, Math.round(n('months')));
  var compound = $('compound').value==='compound';
  var taxRate = parseFloat($('tax').value);

  var principal = (kind==='save') ? monthly*months : lump;
  var interest = 0, i = rate/100/12;

  if(kind==='save'){
    if(compound){
      interest = i===0 ? 0 : monthly*((Math.pow(1+i,months)-1)/i) - monthly*months;
    } else {
      interest = monthly*(rate/100/12)*(months*(months+1)/2);
    }
  } else {
    if(compound){
      interest = lump*(Math.pow(1+i,months)-1);
    } else {
      interest = lump*(rate/100)*months/12;
    }
  }
  var tax = interest*taxRate;
  var net = principal + interest - tax;

  setText('r-main', won(net));
  setText('r-main-label', '만기 실수령액');
  setText('r-main-sub', (kind==='save'?'월 ' + won(monthly) + ' × ' + months + '개월':'예치금 ' + won(lump)) + ' · ' + pct(rate,2) + '% ' + (compound?'월복리':'단리'));

  setText('r-principal', won(principal));
  setText('r-interest', won(interest));
  setText('r-tax', '-' + won(tax));
  setText('r-net', won(net));
  setText('r-net-profit', won(interest - tax));
  var effAnnual = (principal>0 && months>0) ? ((interest-tax)/principal)*(12/months)*100 : 0;
  setText('r-eff', pct(effAnnual,2) + '%');
  setText('r-monthly-avg', won((interest-tax)/months) + ' / 월');

  var rows = '';
  [['일반과세 (15.4%)',0.154],['세금우대 (9.5%)',0.095],['비과세 (0%)',0]].forEach(function(t){
    var tx = interest*t[1];
    var nv = principal + interest - tx;
    rows += '<tr'+(parseFloat(t[1])===taxRate?' class="onrow"':'')+'><td>'+t[0]+'</td><td>'+num(tx)+'</td><td>'+num(interest-tx)+'</td><td class="hl">'+num(nv)+'</td></tr>';
  });
  $('tax-body').innerHTML = rows;

  // 단리 vs 복리 비교
  var simple, comp;
  if(kind==='save'){
    simple = monthly*(rate/100/12)*(months*(months+1)/2);
    comp = i===0 ? 0 : monthly*((Math.pow(1+i,months)-1)/i) - monthly*months;
  } else {
    simple = lump*(rate/100)*months/12;
    comp = lump*(Math.pow(1+i,months)-1);
  }
  $('cmp-body').innerHTML =
    '<tr'+(compound?'':' class="onrow"')+'><td>단리</td><td>'+num(simple)+'</td><td>'+num(simple*(1-taxRate))+'</td></tr>' +
    '<tr'+(compound?' class="onrow"':'')+'><td>월복리</td><td>'+num(comp)+'</td><td>'+num(comp*(1-taxRate))+'</td></tr>';

  $('kind-note').innerHTML = kind==='save'
    ? '<div class="note">적금은 매달 넣은 돈이 각각 다른 기간만큼 이자가 붙습니다. 그래서 같은 금리·기간이면 예금보다 이자가 적습니다(단리 기준 약 절반).</div>'
    : '<div class="note">예금은 목돈을 한 번에 맡기고 만기에 원금과 이자를 받습니다. 이자에 이자가 붙는 복리 상품은 기간이 길수록 유리합니다.</div>';
}
bindCalc(calcSave);
"""

SAVE_FIELDS = r"""
<div class="field">
  <label for="kind">상품 유형</label>
  <select id="kind">
    <option value="save" selected>적금 (매달 납입)</option>
    <option value="deposit">예금 (한 번에 예치)</option>
  </select>
</div>
<div class="field">
  <label for="monthly">월 납입액 (적금)</label>
  <div class="input-line"><input id="monthly" type="number" value="500000" step="10000" min="0" inputmode="numeric"><span class="unit">원</span></div>
  <div class="chips">
    <button type="button" data-set="monthly" data-val="300000">30만</button>
    <button type="button" data-set="monthly" data-val="500000">50만</button>
    <button type="button" data-set="monthly" data-val="1000000">100만</button>
  </div>
</div>
<div class="field">
  <label for="lump">예치금 (예금)</label>
  <div class="input-line"><input id="lump" type="number" value="10000000" step="100000" min="0" inputmode="numeric"><span class="unit">원</span></div>
</div>
<div class="row-2">
  <div class="field">
    <label for="rate">연 이자율</label>
    <div class="input-line"><input id="rate" type="number" value="3.5" step="0.01" min="0" max="20" inputmode="decimal"><span class="unit">%</span></div>
    <span class="hint">우대금리 포함 최종 금리</span>
  </div>
  <div class="field">
    <label for="months">기간</label>
    <div class="input-line"><input id="months" type="number" value="12" step="1" min="1" max="120" inputmode="numeric"><span class="unit">개월</span></div>
  </div>
</div>
<div class="row-2">
  <div class="field">
    <label for="compound">이자 방식</label>
    <select id="compound">
      <option value="simple" selected>단리</option>
      <option value="compound">월복리</option>
    </select>
  </div>
  <div class="field">
    <label for="tax">과세 방식</label>
    <select id="tax">
      <option value="0.154" selected>일반과세 15.4%</option>
      <option value="0.095">세금우대 9.5%</option>
      <option value="0">비과세 0%</option>
    </select>
  </div>
</div>
<p class="mini">이자 과세율에는 지방소득세(소득세의 10%)가 포함되어 있습니다. 비과세는 ISA·비과세종합저축 등 요건을 갖춘 상품에만 적용됩니다.</p>
"""

SAVE_RESULTS = r"""
<div class="big">
  <span class="lbl" id="r-main-label">만기 실수령액</span>
  <div class="val" id="r-main">-</div>
  <div class="sub" id="r-main-sub">-</div>
</div>
<dl class="kv">
  <dt>납입 원금 합계</dt><dd id="r-principal">-</dd>
  <dt>세전 이자</dt><dd id="r-interest">-</dd>
  <dt>이자 과세</dt><dd class="bad" id="r-tax">-</dd>
  <dt>세후 이자</dt><dd class="good" id="r-net-profit">-</dd>
  <dt><strong>만기 수령액</strong></dt><dd><strong class="em" id="r-net">-</strong></dd>
  <dt>연 환산 수익률 (세후)</dt><dd id="r-eff">-</dd>
  <dt>월 평균 이자 (세후)</dt><dd id="r-monthly-avg">-</dd>
</dl>
<div id="kind-note"></div>
<div class="divider"></div>
<h3 style="font-size:14px;margin:0 0 10px;color:#0f2447">과세 방식별 비교 (원)</h3>
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>과세</th><th>세금</th><th>세후 이자</th><th>만기 수령액</th></tr></thead>
    <tbody id="tax-body"></tbody>
  </table>
</div>
<div class="divider"></div>
<h3 style="font-size:14px;margin:0 0 10px;color:#0f2447">단리 vs 월복리 (원)</h3>
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>방식</th><th>세전 이자</th><th>세후 이자</th></tr></thead>
    <tbody id="cmp-body"></tbody>
  </table>
</div>
"""

SAVE_CONTENT = r"""
<h2>적금과 예금, 이자 계산이 왜 다를까요</h2>
<p>같은 연 3.5%, 같은 12개월이라도 <strong>적금</strong>은 매달 넣은 돈이 각각 다른 기간만큼 이자가 붙고, <strong>예금</strong>은 목돈 전체에 12개월 이자가 붙습니다. 그래서 50만 원씩 12개월 적금(600만 원)의 이자는 10만 원이 조금 넘지만, 600만 원을 1년 예금하면 두 배 가까운 이자가 나옵니다. 이 계산기는 두 상품을 같은 화면에서 바꿔 볼 수 있게 했습니다.</p>

<h2>적금 이자 공식</h2>
<div class="formula">
  <strong>적금 · 단리</strong> = 월 납입액 × (연이자율 ÷ 12) × <code>n(n+1)/2</code><br>
  <strong>적금 · 월복리</strong> = 월 납입액 × <code>[(1+i)<sup>n</sup> − 1] ÷ i</code> − 월 납입액 × n<br>
  <code>i = 연이자율 ÷ 12</code>, <code>n</code> = 납입 개월 수
</div>
<p>단리 공식의 <code>n(n+1)/2</code>가 낯설 수 있는데, 이는 &ldquo;첫 달에 넣은 돈은 n개월, 마지막 달에 넣은 돈은 1개월&rdquo; 동안 이자가 붙는 것을 더한 값입니다. 12개월이면 78개월분의 이자가 붙습니다. 그래서 적금의 실효 수익률은 표시 금리의 절반 수준으로 느껴집니다.</p>

<h2>예금 이자 공식</h2>
<div class="formula">
  <strong>예금 · 단리</strong> = 예치금 × 연이자율 × (개월 수 ÷ 12)<br>
  <strong>예금 · 월복리</strong> = 예치금 × <code>[(1+i)<sup>n</sup> − 1]</code>
</div>
<p>단리 상품은 만기에 이자를 한꺼번에 주고, 복리 상품은 이자에 다시 이자가 붙습니다. 3년 이상 장기라면 복리 효과가 눈에 띄기 시작합니다. 다만 국내 은행 정기예금은 대부분 단리이므로, 상품 설명의 &lsquo;이자 지급 방식&rsquo;을 확인하세요.</p>

<h2>세금이 실수령액을 바꿉니다</h2>
<p>이자소득에는 <strong>15.4%</strong>(소득세 14% + 지방소득세 1.4%)가 원천징수됩니다. 100만 원 이자면 15만 4,000원을 떼고 84만 6,000원을 받습니다. 세금우대(9.5%)는 2008년 이후 가입 상품이 거의 없어 현재는 일부 조합·특판 상품에만 남아 있고, 비과세는 <strong>비과세종합저축</strong>(만 65세 이상·장애인 등, 5,000만 원 한도)이나 <strong>ISA</strong>(200만 원 비과세, 초과분 9.9% 분리과세)로 받을 수 있습니다.</p>
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>과세</th><th>세율</th><th>1,000만 원 · 연 3.5% 예금의 세후 이자</th></tr></thead>
    <tbody>
      <tr><td>일반과세</td><td>15.4%</td><td>약 296,100원</td></tr>
      <tr><td>세금우대</td><td>9.5%</td><td>약 316,750원</td></tr>
      <tr><td>비과세</td><td>0%</td><td>350,000원</td></tr>
    </tbody>
  </table>
</div>

<h2>이럴 때 써 보세요</h2>
<ul>
  <li><strong>특판 적금 비교</strong> — 금리 0.3%p 차이가 12개월 50만 원 적금에서 얼마인지 확인하고 상품을 고르세요.</li>
  <li><strong>목표 금액 역산</strong> — 월 납입액을 바꿔 가며 1년 뒤 목표 금액이 되는지 확인합니다.</li>
  <li><strong>ISA·비과세 상품 판단</strong> — 과세 방식을 바꿔 세후 차이를 확인하면 갈아탈 가치가 있는지 보입니다.</li>
  <li><strong>예금 만기 재투자</strong> — 12개월과 24개월을 각각 넣어 기간을 늘릴 가치가 있는지 봅니다.</li>
</ul>

<h2>숫자를 볼 때 주의할 점</h2>
<ul>
  <li>금리는 <strong>세전 연이자율</strong>입니다. 우대금리는 조건(자동이체·카드 사용)을 채워야 하므로, 조건 미충족 시 금리로도 한 번 계산해 보세요.</li>
  <li>적금은 납입일 기준으로 이자가 계산됩니다. 월초에 넣는 것이 월말에 넣는 것보다 하루라도 이자가 더 붙습니다.</li>
  <li>중도해지하면 약정 금리의 절반 수준(보통 0.1~1%)만 적용됩니다.</li>
  <li>이자소득은 금융소득 종합과세 대상(연 2,000만 원 초과)이 될 수 있습니다.</li>
</ul>
"""

SAVE_FAQS = [
    ("적금 이자가 예금보다 적은 이유가 뭔가요?",
     "적금은 매달 넣은 돈이 각각 다른 기간만큼만 이자가 붙기 때문입니다. 12개월 적금에서 첫 달 납입금은 12개월, 마지막 달 납입금은 1개월분 이자만 받습니다. 50만 원씩 12개월(600만 원) 적금의 세전 이자는 연 3.5% 기준 약 113,750원으로, 같은 600만 원 1년 예금(약 210,000원)의 절반 수준입니다."),
    ("단리와 복리, 얼마나 차이 나나요?",
     "1,000만 원을 연 3.5%로 1년 맡기면 단리 이자는 350,000원, 월복리는 약 355,700원으로 차이가 6,000원 안쪽입니다. 3년이면 차이가 3만 원대로 벌어지고, 10년이면 20만 원을 넘습니다. 기간이 짧으면 단리·복리 차이는 크지 않으니 금리를 먼저 비교하세요."),
    ("이자에서 세금은 얼마나 떼나요?",
     "일반과세는 이자의 15.4%(소득세 14% + 지방소득세 1.4%)를 원천징수합니다. 이자 100만 원이면 15만 4,000원을 떼고 84만 6,000원을 받습니다. 비과세종합저축이나 ISA 같은 비과세·분리과세 상품은 세율이 0% 또는 9.9%로 낮아 실수령액이 늘어납니다."),
    ("우대금리는 어떻게 반영하나요?",
     "기본금리에 우대금리를 더한 최종 금리를 넣으면 됩니다. 예를 들어 기본 3.0%에 우대 0.5%면 3.5%를 입력하세요. 다만 우대 조건(자동이체, 카드 실적, 첫 거래)을 채우지 못할 가능성도 있으니 기본금리로도 한 번 계산해 두면 실제 수령액을 보수적으로 가늠할 수 있습니다."),
    ("적금 12개월과 24개월, 어느 쪽이 유리한가요?",
     "금리가 같다면 이자 총액은 24개월이 더 많지만, 연 환산 수익률은 비슷합니다. 문제는 금리 변동입니다. 24개월 동안 금리가 오르면 더 높은 금리 상품으로 갈아타지 못합니다. 금리 상승기에는 짧게, 하락기에는 길게 가입하는 것이 일반적입니다."),
]

SAVE = {
    "slug": "tools/savings-calculator",
    "title": "적금·예금 이자 계산기 | 만기 실수령액 (단리·복리·세금)",
    "h1": "적금·예금 만기 실수령액 계산기",
    "kicker": "단리 · 복리 · 이자 과세",
    "lede": "금리만 보고 가입하면 만기에 실망합니다. 단리·복리와 일반과세·세금우대·비과세를 각각 반영해 실제로 손에 쥐는 금액을 계산합니다.",
    "desc": "적금·예금 만기 실수령액을 계산합니다. 단리·월복리, 일반과세 15.4%·세금우대 9.5%·비과세를 반영한 세후 이자와 연 환산 수익률까지 무료로 확인하세요.",
    "keywords": "적금 이자 계산기, 예금 이자 계산기, 만기 실수령액, 단리 복리, 이자 과세 15.4%, 세금우대, 비과세, 적금 금리",
    "fields": SAVE_FIELDS,
    "results": SAVE_RESULTS,
    "script": SAVE_SCRIPT,
    "content": SAVE_CONTENT,
    "faqs": SAVE_FAQS,
    "disclaimer": "이 계산기는 우대금리 조건 충족을 가정한 세전 금리를 기준으로 하며, 금융기관의 일할 계산·원 단위 절사·중도해지 약정금리를 반영하지 않습니다. 실제 수령액은 가입 상품의 약정서와 만기 정산 내역으로 확인하세요.",
}

# ------------------------------------------------------------------ 연봉 실수령액
SALARY_SCRIPT = r"""
var NP_RATE = 0.0475, NP_CAP = 6370000, NP_FLOOR = 400000;
var HI_RATE = 0.03595, LTC_RATE = 0.1314, EI_RATE = 0.009;

function laborIncomeDeduction(gross){
  if(gross <= 5000000) return gross*0.7;
  if(gross <= 15000000) return 3500000 + (gross-5000000)*0.4;
  if(gross <= 45000000) return 7500000 + (gross-15000000)*0.15;
  if(gross <= 100000000) return 12000000 + (gross-45000000)*0.05;
  return 14750000 + (gross-100000000)*0.02;
}
function bracketTax(base){
  var b = [[14000000,0.06,0],[50000000,0.15,1260000],[88000000,0.24,5760000],
           [150000000,0.35,15440000],[300000000,0.38,19940000],[500000000,0.40,25940000],
           [1000000000,0.42,35940000],[Infinity,0.45,65940000]];
  for(var k=0;k<b.length;k++){
    if(base <= b[k][0]) return Math.max(0, base*b[k][1] - b[k][2]);
  }
  return 0;
}
function kidTaxCredit(k){           // 자녀세액공제 (2024년 이후: 1명 25만·2명 55만·3명부터 40만 추가)
  if(k<=0) return 0;
  if(k===1) return 250000;
  if(k===2) return 550000;
  return 550000 + (k-2)*400000;
}
function wageTaxCredit(tax, gross){
  var c = tax<=1300000 ? tax*0.55 : 715000 + (tax-1300000)*0.3;
  var cap = gross<=33000000?740000 : gross<=70000000?660000 : gross<=120000000?500000 : 200000;
  return Math.min(c, cap);
}
function calcSalary(){
  var annual = n('salary')*10000;        // 만원 -> 원
  var nonTaxMonth = n('nontax')*10000;
  var family = Math.max(0, Math.round(n('family')));
  var kids = Math.max(0, Math.round(n('kids')));

  var nonTaxYear = nonTaxMonth*12;
  var taxableYear = Math.max(0, annual - nonTaxYear);
  var monthPay = annual/12;
  var monthInsBase = taxableYear/12;

  // 4대보험 (근로자 부담)
  var npBase = Math.min(Math.max(monthInsBase, NP_FLOOR), NP_CAP);
  var np = npBase*NP_RATE;
  var hi = monthInsBase*HI_RATE;
  var ltc = hi*LTC_RATE;
  var ei = monthInsBase*EI_RATE;
  var insMonth = np+hi+ltc+ei;

  // 소득세 (연말정산 기준 추정)
  var wageIncome = Math.max(0, taxableYear - laborIncomeDeduction(taxableYear));
  var basicDed = 1500000*(1+family);
  var pensionDed = np*12;
  var healthDed = (hi+ltc)*12;
  var standardDed = 130000;
  var taxBase = Math.max(0, wageIncome - basicDed - pensionDed - healthDed - standardDed);
  var calcTax = bracketTax(taxBase);
  var credit = wageTaxCredit(calcTax, taxableYear) + kidTaxCredit(kids);
  var decided = Math.max(0, calcTax - credit);
  var localTaxYear = decided*0.1;
  var incomeTaxMonth = decided/12;
  var localTaxMonth = localTaxYear/12;

  var deduct = insMonth + incomeTaxMonth + localTaxMonth;
  var net = monthPay - deduct;

  setText('salary-hint', eok(annual) + ' · 월 ' + eok(monthPay));
  setText('r-main', won(net));
  setText('r-main2', won(net));
  setText('r-main-label', '월 실수령액');
  setText('r-main-sub', '연 ' + eok(annual) + ' 기준 · 공제 ' + pct(deduct/monthPay*100,1) + '%');
  setText('r-annual-net', eok(net*12));
  setText('r-month-pay', won(monthPay));
  setText('r-np', '-' + won(np));
  setText('r-hi', '-' + won(hi));
  setText('r-ltc', '-' + won(ltc));
  setText('r-ei', '-' + won(ei));
  setText('r-ins', '-' + won(insMonth));
  setText('r-income-tax', '-' + won(incomeTaxMonth));
  setText('r-local', '-' + won(localTaxMonth));
  setText('r-deduct', '-' + won(deduct));
  setText('r-taxbase', eok(taxBase));
  setText('r-calc-tax', eok(decided));
  setText('r-rate-ins', pct(insMonth/monthPay*100,1)+'%');
  setText('r-rate-tax', pct((incomeTaxMonth+localTaxMonth)/monthPay*100,1)+'%');
  $('salary-note').innerHTML = '<div class="note">2026년 요율 기준 국민연금 4.75%, 건강보험 3.595%, 장기요양(건강보험료의 13.14%), 고용보험 0.9%를 적용했습니다. 국민연금은 기준소득월액 상한 ' + num(NP_CAP) + '원까지만 부과됩니다. 실제 공제액은 회사의 급여 계산과 연말정산 결과에 따라 달라집니다.</div>';
}
bindCalc(calcSalary);
"""

SALARY_FIELDS = r"""
<div class="field">
  <label for="salary">연봉 (세전)</label>
  <div class="input-line"><input id="salary" type="number" value="5000" step="100" min="0" inputmode="numeric"><span class="unit">만원</span></div>
  <span class="hint" id="salary-hint">5,000만원 · 월 416.7만원</span>
  <div class="chips">
    <button type="button" data-set="salary" data-val="3000">3,000</button>
    <button type="button" data-set="salary" data-val="4000">4,000</button>
    <button type="button" data-set="salary" data-val="5000">5,000</button>
    <button type="button" data-set="salary" data-val="7000">7,000</button>
  </div>
</div>
<div class="field">
  <label for="nontax">월 비과세액</label>
  <div class="input-line"><input id="nontax" type="number" value="20" step="10" min="0" inputmode="numeric"><span class="unit">만원</span></div>
  <span class="hint">식대 20만 원 등. 4대보험·소득세 부과 대상에서 빠집니다</span>
</div>
<div class="row-2">
  <div class="field">
    <label for="family">부양가족 수</label>
    <div class="input-line"><input id="family" type="number" value="1" step="1" min="0" max="10" inputmode="numeric"><span class="unit">명</span></div>
    <span class="hint">본인 제외, 배우자·부모 등</span>
  </div>
  <div class="field">
    <label for="kids">자녀 수 (만 8세~20세)</label>
    <div class="input-line"><input id="kids" type="number" value="0" step="1" min="0" max="10" inputmode="numeric"><span class="unit">명</span></div>
    <span class="hint">자녀세액공제 1명 25만·2명 55만 원 (만 8세 이상)</span>
  </div>
</div>
<p class="mini">상여금·성과급이 포함된 연봉이라면 총액을 넣으세요. 매달 똑같이 나눠 받는다고 가정합니다.</p>
"""

SALARY_RESULTS = r"""
<div class="big">
  <span class="lbl" id="r-main-label">월 실수령액</span>
  <div class="val" id="r-main">-</div>
  <div class="sub" id="r-main-sub">-</div>
</div>
<dl class="kv">
  <dt>세전 월급</dt><dd id="r-month-pay">-</dd>
  <dt>국민연금 (4.75%)</dt><dd id="r-np">-</dd>
  <dt>건강보험 (3.595%)</dt><dd id="r-hi">-</dd>
  <dt>장기요양 (건강보험료의 13.14%)</dt><dd id="r-ltc">-</dd>
  <dt>고용보험 (0.9%)</dt><dd id="r-ei">-</dd>
  <dt><strong>4대보험 합계</strong></dt><dd><strong id="r-ins">-</strong></dd>
  <dt>근로소득세</dt><dd id="r-income-tax">-</dd>
  <dt>지방소득세</dt><dd id="r-local">-</dd>
  <dt><strong>공제 합계</strong></dt><dd><strong class="bad" id="r-deduct">-</strong></dd>
  <dt><strong>실수령액</strong></dt><dd><strong class="em" id="r-main2">-</strong></dd></dl>
<div class="divider"></div>
<dl class="kv">
  <dt>연간 실수령액 (12개월)</dt><dd class="em" id="r-annual-net">-</dd>
  <dt>보험료 비중</dt><dd id="r-rate-ins">-</dd>
  <dt>세금 비중</dt><dd id="r-rate-tax">-</dd>
  <dt>과세표준 (연)</dt><dd id="r-taxbase">-</dd>
  <dt>결정세액 (연)</dt><dd id="r-calc-tax">-</dd>
</dl>
<div id="salary-note"></div>
"""

SALARY_CONTENT = r"""
<h2>연봉 5,000만 원, 통장에 얼마가 들어올까요</h2>
<p>연봉 계약서에 적힌 금액과 통장에 찍히는 금액은 다릅니다. 4대보험료와 근로소득세, 지방소득세가 빠지기 때문입니다. 연봉 5,000만 원이면 매달 세전 416만 원가량이지만, 실제로는 357만 원 안팎이 들어옵니다. 이 계산기는 <strong>2026년 요율</strong>로 항목별 공제액을 하나씩 보여 줍니다.</p>

<h2>연봉 3,000만·5,000만·1억, 실제로 얼마가 들어오나</h2>
<p>아래 표는 이 계산기에 <strong>비과세 식대 월 20만 원, 부양가족 1명(본인 제외), 자녀 없음</strong>을 넣고 연봉만 바꿔 가며 계산한 값입니다. 조건을 같게 두어야 차이가 보이니, 내 상황을 넣어 볼 때도 비과세와 부양가족 칸을 먼저 맞춰 보세요.</p>
<div class="tbl-wrap">
  <table class="tbl">
    <caption>2026년 요율 · 비과세 월 20만 원 · 부양가족 1명 기준 (단위: 원)</caption>
    <thead><tr><th>연봉</th><th>세전 월급</th><th>4대보험</th><th>소득세+지방세</th><th>월 실수령</th><th>연 실수령</th><th>뗀 비율</th></tr></thead>
    <tbody>
      <tr><td>3,000만</td><td>2,500,000</td><td>223,500</td><td>31,300</td><td class="hl">2,245,200</td><td>2,694만</td><td>10.2%</td></tr>
      <tr><td>4,000만</td><td>3,333,333</td><td>304,478</td><td>102,639</td><td class="hl">2,926,216</td><td>3,511만</td><td>12.2%</td></tr>
      <tr><td>5,000만</td><td>4,166,667</td><td>385,456</td><td>210,965</td><td class="hl">3,570,245</td><td>4,284만</td><td>14.3%</td></tr>
      <tr><td>6,000만</td><td>5,000,000</td><td>466,434</td><td>329,466</td><td class="hl">4,204,099</td><td>5,045만</td><td>15.9%</td></tr>
      <tr><td>8,000만</td><td>6,666,667</td><td>623,799</td><td>615,329</td><td class="hl">5,427,539</td><td>6,513만</td><td>18.6%</td></tr>
      <tr><td>1억</td><td>8,333,333</td><td>706,589</td><td>1,015,432</td><td class="hl">6,611,312</td><td>7,934만</td><td>20.7%</td></tr>
    </tbody>
  </table>
</div>
<p class="hint-mobile">표가 화면보다 넓으면 좌우로 밀어서 보세요.</p>
<p>표에서 먼저 눈에 들어오는 건 <strong>연봉이 두 배가 되어도 실수령액은 두 배가 되지 않는다</strong>는 점입니다. 연봉 3,000만 원과 6,000만 원은 세전 월급이 250만 원에서 500만 원으로 두 배가 되지만, 실수령액은 224만 5,200원에서 420만 4,099원으로 1.87배가 됩니다. 떼는 돈은 25만 4,800원에서 79만 5,900원으로 세 배 넘게 늘어납니다.</p>
<p>오르는 폭도 구간마다 다릅니다. 연봉 5,000만 원에서 6,000만 원으로 가면 세전 월급은 83만 3,333원 느는데 실수령액은 63만 3,854원만 늘어납니다. 반대로 연봉 8,000만 원에서 1억 원으로 가면 세전은 166만 6,667원 느는데 실수령은 118만 3,773원 늘어납니다. 이 구간에서 4대보험료는 8만 2,790원밖에 안 늘어나는데, 국민연금이 기준소득월액 상한(637만 원)에 걸려 더 오르지 않기 때문입니다. 대신 소득세가 40만 원 늘어납니다.</p>

<h2>같은 연봉인데 실수령액이 달라지는 3가지 이유</h2>
<p>같은 회사, 같은 연봉인데 옆자리 동료와 통장 금액이 다르다면 대개 다음 세 가지 중 하나입니다.</p>

<h3>① 비과세 수당을 얼마나 받는가</h3>
<p>식대·자가운전보조금처럼 비과세로 인정되는 수당은 4대보험료와 소득세를 <strong>둘 다</strong> 줄여 줍니다. 연봉 5,000만 원 기준으로 비과세가 하나도 없으면 월 352만 2,370원, 식대 20만 원이 붙으면 357만 245원, 30만 원이면 359만 4,183원입니다. 같은 연봉인데 월 7만 원 가까이 차이가 납니다.</p>
<div class="tbl-wrap">
  <table class="tbl">
    <caption>연봉 5,000만 원 · 월 비과세액별 월 실수령액</caption>
    <thead><tr><th>월 비과세액</th><th>4대보험</th><th>소득세+지방세</th><th>월 실수령액</th></tr></thead>
    <tbody>
      <tr><td>없음</td><td>404,891</td><td>239,405</td><td>3,522,370</td></tr>
      <tr><td>20만 원 (식대)</td><td>385,456</td><td>210,965</td><td class="hl">3,570,245</td></tr>
      <tr><td>30만 원</td><td>375,739</td><td>196,745</td><td>3,594,183</td></tr>
    </tbody>
  </table>
</div>
<p class="hint-mobile">표가 화면보다 넓으면 좌우로 밀어서 보세요.</p>
<p>비과세는 회사가 급여 항목으로 신고해야 적용됩니다. 명세서에 식대가 '과세'로 잡혀 있다면 그만큼 매달 손해를 보고 있는 셈이니, 인사팀에 한 번 확인해 볼 만합니다.</p>

<h3>② 부양가족과 자녀를 몇 명 올렸는가</h3>
<p>부양가족 1명당 기본공제 150만 원이 붙어 월 2만 원 안팎, 만 8세 이상 20세 이하 자녀 1명당 자녀세액공제 25만 원(2명이면 55만 원)이 붙어 월 2만 3,000원 정도 실수령액이 늘어납니다. 연봉 5,000만 원에서 부양가족이 본인뿐이면 354만 9,620원, 1명이면 357만 245원, 2명이면 359만 870원입니다. 부모님이나 배우자를 올릴 수 있는데도 그냥 둔 경우가 의외로 많습니다. 다만 부양가족으로 올리려면 나이와 소득 요건(연 100만 원 이하)을 함께 봐야 합니다.</p>

<h3>③ 성과급과 중도 입사가 섞였는가</h3>
<p>성과급은 과세 소득이라 받은 달에 4대보험료와 소득세가 함께 올라갑니다. 연간으로 보면 총급여가 같으니 연말정산에서 다시 정산되지만, 그 달 통장만 보면 크게 줄어 보입니다. 또 연봉 협상에서 '성과급 포함 총액'인지 '기본급'인지에 따라 매달 들어오는 금액이 크게 달라집니다. 중도 입사한 해도 비슷합니다. 6월에 입사해 반년만 일했다면 연간 총급여가 적어 실제 세금은 낮은데, 회사는 간이세액표로 매달 일정하게 떼기 때문에 다음 해 2월 연말정산에서 돌려받는 금액이 커집니다. 그래서 이 계산기가 보여 주는 중도 입사 연도의 월 실수령액은 실제보다 조금 적게 나올 수 있습니다.</p>

<h2>4대보험료 계산 (2026년 근로자 부담)</h2>
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>항목</th><th>근로자 부담</th><th>계산 기준</th></tr></thead>
    <tbody>
      <tr><td>국민연금</td><td>4.75%</td><td>기준소득월액 (상한 637만 원)</td></tr>
      <tr><td>건강보험</td><td>3.595%</td><td>보수월액</td></tr>
      <tr><td>장기요양보험</td><td>건강보험료의 13.14%</td><td>건강보험료에 부가</td></tr>
      <tr><td>고용보험</td><td>0.9%</td><td>보수월액 (실업급여분)</td></tr>
      <tr><td>산재보험</td><td>0%</td><td>사업주 전액 부담</td></tr>
    </tbody>
  </table>
</div>
<p>보수월액은 <strong>비과세를 제외한 월 급여</strong>입니다. 식대 20만 원이 비과세라면 4대보험과 소득세는 그만큼 줄어든 금액에 부과됩니다. 2026년부터 국민연금 요율이 9.5%(근로자 4.75%)로 올라 2025년보다 매달 1만 원 남짓이 더 빠져나갑니다.</p>

<h2>근로소득세 계산 구조</h2>
<div class="formula">
  총급여 − 비과세 = 과세 급여<br>
  과세 급여 − 근로소득공제 = 근로소득금액<br>
  근로소득금액 − 기본공제(1인 150만 원) − 연금보험료공제 − 건강보험료공제 − 표준세액공제(13만 원) = 과세표준<br>
  과세표준 × 세율 − 누진공제 = 산출세액 → 근로소득세액공제 → 결정세액 + 지방소득세 10%
</div>
<p>근로소득공제는 총급여 구간에 따라 달라집니다. 500만 원 이하는 70%, 500만~1,500만 원은 350만 원 + 초과분의 40%, 1,500만~4,500만 원은 750만 원 + 초과분의 15%, 4,500만~1억 원은 1,200만 원 + 초과분의 5%입니다. 소득이 늘수록 공제율이 낮아지는 구조입니다.</p>

<h3>회사가 떼는 세금과 연말정산이 다른 이유</h3>
<p>회사는 <strong>근로소득 간이세액표</strong>에 따라 매달 세금을 떼고, 이듬해 2월 연말정산에서 실제 세금과 차액을 정산합니다. 이 계산기는 연간 기준으로 계산한 세액을 12로 나눈 값이라, 매달 원천징수액과 수만 원 차이가 날 수 있습니다. 연말정산에서 의료비·교육비·연금저축 공제를 받으면 실제 부담은 더 줄어듭니다.</p>

<h2>급여명세서에서 확인할 것 (원천징수 팁)</h2>
<ul>
  <li><strong>국민연금은 상한에서 멈춥니다</strong> — 기준소득월액 상한이 637만 원이라 월 보수가 그보다 많아도 4.75%는 30만 2,575원까지만 뗍니다. 연봉 8,000만 원과 1억 원의 4대보험료 차이가 월 8만 2,790원뿐인 이유입니다.</li>
  <li><strong>4월 급여는 평소와 다를 수 있습니다</strong> — 건강보험료는 전년도 보수총액으로 이듬해 4월에 정산합니다. 상여를 많이 받은 해라면 4월에 추가로 빠져나가고, 반대로 줄었으면 돌려받습니다.</li>
  <li><strong>상여금 받은 달의 세금에 놀라지 마세요</strong> — 그 달만 보면 많이 떼인 것 같지만 연간 기준으로 다시 계산되니 연말정산에서 조정됩니다. 한 달 금액만 보고 '세금이 늘었다'고 판단하지 않는 게 좋습니다.</li>
  <li><strong>지방소득세는 소득세의 10%</strong> — 명세서에 두 줄로 나뉘어 보이지만 실제로는 소득세에 10%를 더한 금액이 함께 빠져나갑니다.</li>
  <li><strong>산재보험은 근로자 부담이 0원</strong> — 명세서에 산재보험이 보여도 회사가 전액 냅니다. 4대보험이라고 해서 네 가지를 다 반씩 나누는 건 아닙니다.</li>
</ul>

<h2>회사에 요청해서 늘릴 수 있는 것</h2>
<ul>
  <li><strong>비과세 항목을 급여에 넣어 달라고 하세요</strong> — 식대(월 20만 원), 자가운전보조금(월 20만 원), 육아수당(월 20만 원) 같은 법정 비과세는 4대보험료와 소득세를 모두 줄여 줍니다. 연봉 5,000만 원 기준 식대 20만 원만 있어도 월 4만 8,000원가량 차이가 납니다.</li>
  <li><strong>부양가족을 빠짐없이 올리세요</strong> — 1인당 150만 원 소득공제가 늘어 월 2만 원 안팎이 달라집니다. 나이와 소득 요건(연 100만 원 이하)을 확인한 뒤 회사에 제출하면 됩니다.</li>
  <li><strong>연금저축·IRP는 연말정산에서 돌려받습니다</strong> — 900만 원까지 15%(지방소득세 포함 16.5%)를 세액공제받습니다. 900만 원을 다 채우면 135만 원, 지방소득세까지 148만 5,000원입니다. 매달 실수령액이 아니라 다음 해 2월에 한 번에 돌아오는 돈이라는 점만 기억하세요. <a href="year-end-tax-calculator.html">연말정산 환급금 계산기</a>로 얼마가 돌아오는지 미리 볼 수 있습니다.</li>
  <li><strong>월세·주택자금 공제도 챙기세요</strong> — 무주택 세대주는 월세액의 15~17%를 세액공제받습니다. 계약서 주소와 주민등록 주소가 같아야 합니다.</li>
</ul>

<h2>이럴 때 써 보세요</h2>
<ul>
  <li><strong>연봉 협상</strong> — 500만 원 오르면 실수령액이 얼마나 늘어나는지 확인합니다. 세율 구간이 바뀌면 늘어나는 금액이 줄어듭니다.</li>
  <li><strong>이직 제안 비교</strong> — 연봉은 높지만 상여 비중이 큰 회사와 매달 고정인 회사를 실수령 기준으로 비교합니다.</li>
  <li><strong>생활비 계획</strong> — 실제 입금액을 기준으로 고정지출 비율을 잡습니다.</li>
  <li><strong>부양가족·자녀 등록 효과</strong> — 부양가족 수를 바꿔 가며 월 세금이 얼마나 줄어드는지 봅니다.</li>
</ul>
"""

SALARY_FAQS = [
    ("연봉 5,000만 원이면 월 실수령액이 얼마인가요?",
     "비과세 월 20만 원, 부양가족 1명을 가정하면 월 실수령액은 약 357만 원입니다. 4대보험이 월 38만 5,000원 안팎, 근로소득세와 지방소득세가 월 21만 원 안팎 빠집니다. 부양가족이 본인뿐이면 354만 9,620원, 비과세 항목이 전혀 없으면 352만 2,370원으로 줄어듭니다."),
    ("4대보험료는 어떻게 계산하나요?",
     "비과세를 뺀 보수월액에 요율을 곱합니다. 2026년 근로자 부담은 국민연금 4.75%, 건강보험 3.595%, 장기요양은 건강보험료의 13.14%, 고용보험 0.9%입니다. 합하면 보수월액의 9.4% 안팎이고, 여기에 사업주가 같은 금액을 별도로 부담합니다."),
    ("국민연금은 연봉이 아무리 높아도 같은 금액인가요?",
     "네, 상한이 있습니다. 기준소득월액 상한이 637만 원이라 월급이 그보다 높아도 국민연금은 637만 원의 4.75%인 302,575원까지만 부과됩니다. 반대로 월급이 40만 원보다 적으면 하한(40만 원)을 기준으로 계산합니다."),
    ("회사에서 떼는 세금과 이 계산기가 다른 이유는 무엇인가요?",
     "회사는 근로소득 간이세액표로 매달 원천징수하고, 이 계산기는 연간 소득세를 12로 나눈 값을 보여 줍니다. 부양가족·비과세·연말정산 공제 항목이 회사에 신고된 내용과 다르면 차이가 납니다. 정확한 금액은 급여명세서와 연말정산 결과로 확인하세요."),
    ("연봉이 오르면 실수령액은 얼마나 늘어나나요?",
     "연봉 5,000만 원에서 5,500만 원으로 오르면 세전 월급은 41만 7,000원 늘지만 실수령액은 31만 7,000원(약 32만 원)만 늘어납니다. 소득세율 구간(15%→24%)이 바뀌는 8,800만 원 부근에서는 인상분의 체감이 더 둔해집니다. 계산기에 두 연봉을 각각 넣어 비교해 보세요."),
    ("성과급·상여금이 많으면 실수령액이 어떻게 달라지나요?",
     "성과급은 비과세 항목이 아니라서 받은 달에 4대보험료와 소득세가 함께 붙습니다. 500만 원을 한 번에 받으면 그 달 공제액이 크게 늘어 통장 금액이 눈에 띄게 줄어 보입니다. 다만 연말정산은 1년 총급여로 다시 계산하므로, 연간으로는 결국 같은 세금을 나눠 내는 것과 비슷해집니다. 연봉 협상 때는 총액에 성과급이 포함됐는지, 기본급 기준인지를 꼭 확인하세요."),
    ("중도 입사·퇴사한 해에는 왜 세금을 더 떼나요?",
     "회사는 근로소득 간이세액표에 따라 매달 일정하게 세금을 뗍니다. 반년만 일한 해에는 연간 총급여가 적어 실제 세금이 훨씬 낮은데도 매달 비슷한 비율로 떼이기 때문에, 다음 해 2월 연말정산에서 차액을 돌려받게 됩니다. 이 계산기는 연간 기준으로 세금을 12로 나눠 보여 주니, 중도 입사한 해의 월 실수령액은 실제보다 조금 적게 나올 수 있습니다."),
    ("건강보험료는 왜 4월에 다시 정산하나요?",
     "건강보험료는 전년도 보수총액이 확정된 뒤 이듬해 4월에 실제 보험료와 낸 보험료의 차이를 정산하기 때문입니다. 상여·성과급이 많았던 해에는 4월 급여에서 추가로 빠져나가고, 예상보다 적었으면 돌려받습니다. 연봉이 크게 오른 해에는 그다음 해 4월까지 예전 기준으로 보험료를 내다가 정산에서 한꺼번에 더 내는 구조입니다."),
]

SALARY = {
    "slug": "tools/salary-calculator",
    "title": "연봉 실수령액 계산기 | 4대보험·근로소득세 반영 월 실수령액",
    "h1": "연봉 실수령액·4대보험 계산기",
    "kicker": "4대보험 · 근로소득세",
    "lede": "연봉 5,000만 원이 매달 얼마로 바뀌는지, 4대보험과 소득세가 각각 얼마인지 항목별로 확인하세요. 비과세액과 부양가족 수를 넣으면 실제에 더 가까운 금액이 나옵니다.",
    "desc": "연봉으로 월 실수령액을 계산합니다. 2026년 4대보험 요율(국민연금 4.75%, 건강보험 3.595%, 장기요양, 고용보험)과 근로소득세·지방소득세 공제 내역을 보여 주고, 연봉 3,000만~1억 원 구간별 실수령액 비교표와 비과세·부양가족이 금액을 바꾸는 이유도 정리했습니다.",
    "keywords": "연봉 실수령액, 실수령액 계산기, 4대보험 계산, 근로소득세, 월급 실수령, 연봉 5000 실수령액, 비과세, 연봉별 실수령액 비교, 2026 4대보험 요율",
    "fields": SALARY_FIELDS,
    "results": SALARY_RESULTS,
    "script": SALARY_SCRIPT,
    "content": SALARY_CONTENT,
    "faqs": SALARY_FAQS,
    "disclaimer": "이 계산기는 2026년 요율과 연말정산 기준의 소득세 구조를 단순화한 추정치입니다. 실제 원천징수액은 근로소득 간이세액표, 회사 신고 내역, 연말정산 공제 항목에 따라 달라지며, 상여·수당·퇴직소득은 반영하지 않았습니다.",
}
