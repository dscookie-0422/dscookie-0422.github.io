# -*- coding: utf-8 -*-
"""Builder for the 10-tool finance portal at dscookie-0422.github.io."""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://dscookie-0422.github.io"
SITE = "생활 금융 계산기"
ADSENSE = ('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
           '?client=ca-pub-6285965398350241" crossorigin="anonymous"></script>')
NAVER = "0c094f9c82a10c5fcd5292b5a2744684c0ecfee2"
GOOGLE = "ROz-ZBABKqWs14o1I1dBc0h49IidcUGDRy0BjunFj2M"
LASTMOD = "2026-11-15"

# slug, short nav name, full title, one-line description, emoji
TOOLS = [
    ("web-ad", "대출 갈아타기", "대출 갈아타기 손익 계산기",
     "중도상환수수료·부대비용·LTV까지 넣고 갈아타면 본전 찾는 개월 수를 계산합니다.", "🔄"),
    ("tools/loan-interest", "주담대 이자", "주택담보·전세대출 월 이자 계산기",
     "원리금균등·원금균등·만기일시·체증식 상환방식을 비교하고 연도별 상환표를 봅니다.", "🏠"),
    ("tools/dsr-calculator", "DSR 한도", "DSR·대출 한도 계산기",
     "연소득과 기존 대출로 스트레스 DSR을 반영한 예상 대출 한도를 계산합니다.", "📊"),
    ("tools/property-tax-fee", "취득세·복비", "부동산 취득세·중개보수 계산기",
     "매매·전세·월세별 취득세와 중개보수 상한을 한 번에 계산합니다.", "🧾"),
    ("tools/rent-vs-jeonse", "월세vs전세", "월세 vs 전세 손익 비교 계산기",
     "전세대출 이자와 목돈 기회비용까지 넣어 월세와 전세 중 유리한 쪽을 가립니다.", "⚖️"),
    ("tools/savings-calculator", "예적금 이자", "적금·예금 만기 실수령액 계산기",
     "단리·복리, 일반과세·세금우대·비과세를 반영한 만기 실수령액을 계산합니다.", "💰"),
    ("tools/salary-calculator", "연봉 실수령", "연봉 실수령액·4대보험 계산기",
     "4대보험과 근로소득세를 반영한 월 실수령액과 공제 내역을 보여 줍니다.", "💵"),
    ("tools/severance-calculator", "퇴직금·실업급여", "퇴직금·실업급여 예상액 계산기",
     "평균임금으로 퇴직금을 계산하고 구직급여 예상 수급액까지 함께 봅니다.", "📦"),
    ("tools/subscription-score", "청약 가점", "청약 가점 계산기",
     "무주택기간·부양가족·통장 가입기간으로 84점 만점 청약 가점을 계산합니다.", "🎯"),
    ("tools/capital-gains-tax", "양도세", "양도소득세 간이 계산기",
     "취득가·양도가·보유기간으로 1세대1주택 장기보유특별공제를 반영해 추정합니다.", "🏷️"),
]
TOOL_BY_SLUG = {t[0]: t for t in TOOLS}


def href(slug, from_tools=False):
    if slug == "web-ad":
        return "https://dscookie-0422.github.io/web-ad/"
    if from_tools:
        return slug.split("/", 1)[1] + ".html"
    return slug + ".html"


# ---------------------------------------------------------------- CSS
CSS = r"""
*,*::before,*::after{box-sizing:border-box}
:root{
  --navy:#0f2447; --blue:#1b64da; --blue-d:#134fb0; --sky:#e8f1ff;
  --bg:#f4f6fa; --card:#ffffff; --line:#e3e7ee; --text:#191f28;
  --muted:#6b7684; --green:#0aa36f; --green-bg:#e6f7f1; --red:#e0483b; --amber:#b26a00;
  --shadow:0 8px 26px rgba(15,36,71,.07);
}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--bg); color:var(--text);
  font-family:"Pretendard","Apple SD Gothic Neo","Noto Sans KR",-apple-system,BlinkMacSystemFont,"Malgun Gothic",sans-serif;
  font-size:16px; line-height:1.65; -webkit-font-smoothing:antialiased;
}
a{color:var(--blue); text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1120px; margin:0 auto; padding:0 18px}
.narrow{max-width:860px; margin:0 auto}

/* header */
.site-header{position:sticky; top:0; z-index:50; background:rgba(255,255,255,.96); backdrop-filter:blur(8px); border-bottom:1px solid var(--line)}
.header-inner{display:flex; align-items:center; gap:18px; min-height:62px; min-width:0}
.brand{display:flex; align-items:center; gap:9px; font-weight:800; color:var(--navy); font-size:16px; white-space:nowrap; text-decoration:none}
.brand:hover{text-decoration:none}
.brand-mark{display:grid; place-items:center; width:30px; height:30px; border-radius:9px; background:var(--navy); color:#7ce0bb; flex:none}
.tool-nav{display:flex; gap:6px; overflow-x:auto; scrollbar-width:none; margin-left:auto; padding:8px 0; min-width:0; flex:1 1 auto}
.tool-nav::-webkit-scrollbar{display:none}
.tool-nav a{flex:none; font-size:13.5px; font-weight:600; color:#4e5968; padding:7px 11px; border-radius:999px; white-space:nowrap; border:1px solid transparent}
.tool-nav a:hover{background:var(--sky); text-decoration:none}
.tool-nav a.on{background:var(--navy); color:#fff}

/* page head */
.crumb{font-size:13px; color:var(--muted); padding:18px 0 0}
.crumb a{color:var(--muted)}
.page-head{padding:8px 0 22px}
h1{font-size:clamp(24px,3.4vw,34px); line-height:1.3; letter-spacing:-.02em; margin:10px 0 12px; font-weight:800}
.lede{font-size:16.5px; color:#4e5968; margin:0; max-width:760px}
.kicker{display:inline-flex; align-items:center; gap:7px; background:var(--sky); color:var(--blue-d); font-weight:700; font-size:13px; padding:5px 12px; border-radius:999px}

/* calculator */
.calc{display:grid; grid-template-columns:1fr; gap:18px; align-items:start; margin-bottom:34px}
.calc>*{min-width:0}
@media(min-width:960px){.calc{grid-template-columns:.95fr 1.05fr}}
.panel{background:var(--card); border:1px solid var(--line); border-radius:16px; padding:20px; box-shadow:var(--shadow); min-width:0}
.panel h2.panel-title{font-size:15px; margin:0 0 16px; color:var(--navy); letter-spacing:-.01em; display:flex; align-items:center; gap:8px}
.panel h2.panel-title::before{content:""; width:4px; height:15px; border-radius:2px; background:var(--blue)}
.field{margin-bottom:14px}
.field:last-child{margin-bottom:0}
.field label{display:block; font-size:13.5px; font-weight:600; color:#3c4653; margin-bottom:6px}
.field .hint{display:block; font-weight:400; font-size:12px; color:var(--muted); margin-top:3px; line-height:1.5}
.input-line{display:flex; align-items:center; gap:8px}
.input-line .unit{font-size:13px; color:var(--muted); flex:none; min-width:26px}
input[type=number],input[type=date],select,input[type=text]{
  width:100%; height:46px; padding:0 12px; font-size:16px; font-family:inherit; color:var(--text);
  background:#fbfcfe; border:1px solid #d8dee8; border-radius:10px; outline:none; -webkit-appearance:none; appearance:none;
}
select{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%236b7684' stroke-width='2' fill='none' stroke-linecap='round'/%3E%3C/svg%3E"); background-repeat:no-repeat; background-position:right 14px center; padding-right:34px}
input:focus,select:focus{border-color:var(--blue); background:#fff; box-shadow:0 0 0 3px rgba(27,100,218,.12)}
.range-row{display:flex; align-items:center; gap:10px}
input[type=range]{flex:1; accent-color:var(--blue); height:28px}
.range-val{font-variant-numeric:tabular-nums; font-weight:700; font-size:13.5px; color:var(--blue-d); min-width:60px; text-align:right}
.chips{display:flex; flex-wrap:wrap; gap:6px; margin-top:8px}
.chips button{font-family:inherit; font-size:12.5px; font-weight:600; color:#3c4653; background:#f1f4f9; border:1px solid var(--line); border-radius:999px; padding:5px 11px; cursor:pointer}
.chips button:hover{background:var(--sky); border-color:#c9dcff}
.switch{display:flex; align-items:center; gap:9px; font-size:14px; color:#3c4653; font-weight:600; cursor:pointer; padding:2px 0}
.switch input{width:18px; height:18px; accent-color:var(--blue); flex:none; margin:0}
.row-2{display:grid; grid-template-columns:1fr 1fr; gap:10px}

/* results */
.result-panel{background:linear-gradient(180deg,#fff 0%,#fbfdff 100%); border:1px solid var(--line); border-radius:16px; padding:20px; box-shadow:var(--shadow); min-width:0}
.big{padding:4px 0 16px; border-bottom:1px dashed var(--line); margin-bottom:14px}
.big .lbl{font-size:13px; font-weight:700; color:var(--muted); display:block; margin-bottom:4px}
.big .val{font-size:clamp(26px,4.2vw,34px); font-weight:800; letter-spacing:-.02em; color:var(--navy); font-variant-numeric:tabular-nums; line-height:1.2}
.big .sub{font-size:13px; color:var(--muted); margin-top:5px}
.kv{display:grid; grid-template-columns:1fr auto; gap:7px 12px; font-size:14px; margin:0}
.kv dt{color:#4e5968; min-width:0}
.kv dd{margin:0; text-align:right; font-weight:700; font-variant-numeric:tabular-nums; white-space:nowrap}
.kv .em{color:var(--blue-d)}
.kv .good{color:var(--green)}
.kv .bad{color:var(--red)}
.divider{height:1px; background:var(--line); margin:14px 0}
.mini{font-size:12.5px; color:var(--muted); line-height:1.6; margin:12px 0 0}
.note{padding:11px 13px; border-radius:10px; font-size:13px; line-height:1.6; margin-top:14px; background:#f6f8fb; color:#3c4653; border:1px solid var(--line)}
.note.warn{background:#fff8e8; border-color:#f3e2bb; color:#7a5200}
.note.good{background:var(--green-bg); border-color:#bfe9d9; color:#0a6b4b}

/* tables */
.tbl-wrap{overflow-x:auto; border:1px solid var(--line); border-radius:12px; background:#fff}
table.tbl{width:100%; border-collapse:collapse; font-size:13.5px; min-width:480px}
table.tbl caption{caption-side:top; text-align:left; font-size:13px; font-weight:700; color:var(--navy); padding:10px 12px; background:#fafbfd; border-bottom:1px solid var(--line)}
table.tbl th,table.tbl td{padding:9px 12px; border-bottom:1px solid #eef1f6; text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap}
table.tbl th:first-child,table.tbl td:first-child{text-align:left}
table.tbl thead th{background:#f7f9fc; color:#4e5968; font-weight:700; font-size:12.5px; position:sticky; top:0}
table.tbl tbody tr:nth-child(even){background:#fcfdff}
table.tbl tr:last-child td{border-bottom:0}
table.tbl td.hl{color:var(--blue-d); font-weight:700}

/* content */
.content{background:var(--card); border:1px solid var(--line); border-radius:16px; padding:26px 22px; box-shadow:var(--shadow); margin-bottom:26px}
@media(min-width:760px){.content{padding:34px 36px}}
.content h2{font-size:20px; letter-spacing:-.01em; margin:34px 0 12px; padding-left:12px; border-left:4px solid var(--blue); line-height:1.4}
.content h2:first-child{margin-top:0}
.content h3{font-size:16.5px; margin:22px 0 8px; color:var(--navy)}
.content p{margin:0 0 13px; color:#333c48}
.content ul,.content ol{margin:0 0 16px; padding-left:20px; color:#333c48}
.content li{margin-bottom:7px}
.content strong{color:var(--navy)}
.content .formula{background:#f6f8fc; border:1px solid var(--line); border-left:4px solid #b9cdf0; border-radius:10px; padding:13px 15px; font-size:14px; line-height:1.85; margin:0 0 16px; overflow-x:auto; font-variant-numeric:tabular-nums}
.content .formula code{font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace; font-size:13.5px; background:none; color:#123a75}
.content table.tbl{min-width:0}
.content .tbl-wrap{margin:0 0 18px}
.content .tip{background:#f2f8f4; border:1px solid #cbe8d9; border-radius:12px; padding:14px 16px; margin:0 0 16px}
.content .tip p:last-child{margin:0}

/* faq */
.faq{background:var(--card); border:1px solid var(--line); border-radius:16px; padding:8px 6px; box-shadow:var(--shadow); margin-bottom:26px}
@media(min-width:760px){.faq{padding:12px 12px}}
.faq h2{font-size:19px; margin:14px 16px 8px; letter-spacing:-.01em}
details.qa{border-bottom:1px solid #eef1f6; padding:0}
details.qa:last-child{border-bottom:0}
details.qa summary{cursor:pointer; list-style:none; padding:15px 16px; font-weight:700; font-size:15px; color:#232c39; display:flex; gap:9px; align-items:flex-start; line-height:1.5}
details.qa summary::-webkit-details-marker{display:none}
details.qa summary::before{content:"Q"; flex:none; font-weight:800; color:var(--blue); font-size:14px; line-height:1.6}
details.qa summary::after{content:"+"; margin-left:auto; color:var(--muted); font-weight:700; font-size:18px; line-height:1.2}
details.qa[open] summary::after{content:"−"}
details.qa .a{padding:0 16px 16px 40px; color:#3c4653; font-size:14.5px}
details.qa .a p{margin:0 0 9px}
details.qa .a p:last-child{margin:0}

.disclaimer{font-size:12.5px; color:var(--muted); line-height:1.75; background:#f0f3f8; border-radius:12px; padding:15px 17px; margin-bottom:30px}
.disclaimer strong{color:#4e5968}

/* related cards */
.related{margin-bottom:40px}
.related h2{font-size:18px; margin:0 0 12px}
.cards{display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:12px}
.card{display:block; background:#fff; border:1px solid var(--line); border-radius:14px; padding:16px; color:inherit; box-shadow:0 2px 10px rgba(15,36,71,.04); transition:transform .15s ease, box-shadow .15s ease}
.card:hover{text-decoration:none; transform:translateY(-2px); box-shadow:0 10px 22px rgba(15,36,71,.09); border-color:#cddcf5}
.card .num{font-size:12px; font-weight:800; color:var(--blue); letter-spacing:.06em}
.card h3{font-size:15.5px; margin:5px 0 5px; line-height:1.4; color:var(--navy)}
.card p{margin:0; font-size:13px; color:var(--muted); line-height:1.55}

/* footer */
.site-footer{background:var(--navy); color:#c9d3e3; margin-top:20px; padding:34px 0 26px; font-size:13.5px}
.footer-grid{display:grid; grid-template-columns:1fr; gap:24px}
@media(min-width:780px){.footer-grid{grid-template-columns:1.1fr 1.6fr .9fr}}
.site-footer h2{font-size:13px; color:#fff; margin:0 0 10px; letter-spacing:.02em}
.site-footer p{margin:0 0 9px; line-height:1.7; color:#a9b7cd}
.site-footer a{color:#c9d3e3}
.footer-links{display:grid; grid-template-columns:1fr 1fr; gap:6px 14px}
.footer-links a{font-size:13px; color:#b8c5da}
.site-footer .brand-foot{color:#fff; font-weight:800; font-size:15px; margin-bottom:8px; display:block}
.site-footer .copy{border-top:1px solid rgba(255,255,255,.12); margin-top:24px; padding-top:16px; font-size:12px; color:#8394ae}

/* portal */
.hero{background:linear-gradient(135deg,#0f2447 0%,#173a6b 55%,#1b64da 130%); color:#fff; border-radius:20px; padding:40px 28px; margin:22px 0 30px; box-shadow:0 16px 40px rgba(15,36,71,.22)}
@media(min-width:760px){.hero{padding:52px 46px}}
.hero .kicker{background:rgba(124,224,187,.16); color:#8ff0c8}
.hero h1{color:#fff; margin:14px 0 14px}
.hero p{color:#c7d6ee; margin:0; max-width:640px; font-size:16px}
.hero .stats{display:flex; flex-wrap:wrap; gap:10px; margin-top:24px}
.hero .stats span{background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.14); border-radius:999px; padding:7px 14px; font-size:13px; font-weight:600; color:#e4edfb}
.tool-cards{display:grid; grid-template-columns:1fr; gap:14px; margin-bottom:40px}
@media(min-width:640px){.tool-cards{grid-template-columns:1fr 1fr}}
@media(min-width:1000px){.tool-cards{grid-template-columns:repeat(3,1fr)}}
a.tool-card{display:flex; flex-direction:column; gap:8px; background:#fff; border:1px solid var(--line); border-radius:16px; padding:20px; color:inherit; box-shadow:var(--shadow); transition:transform .15s ease, box-shadow .15s ease, border-color .15s ease; min-height:150px}
a.tool-card:hover{text-decoration:none; transform:translateY(-3px); box-shadow:0 14px 30px rgba(15,36,71,.12); border-color:#c9dbf8}
a.tool-card .tc-top{display:flex; align-items:center; gap:9px}
a.tool-card .tc-ico{font-size:19px; line-height:1}
a.tool-card .tc-num{font-size:12px; font-weight:800; color:#9aa7ba; letter-spacing:.08em}
a.tool-card h2{font-size:17px; margin:0; color:var(--navy); letter-spacing:-.01em; line-height:1.4}
a.tool-card p{margin:0; font-size:13.5px; color:var(--muted); line-height:1.6; flex:1}
a.tool-card .tc-go{font-size:13px; font-weight:700; color:var(--blue); margin-top:2px}
.section-title{display:flex; align-items:baseline; justify-content:space-between; gap:12px; margin:0 0 14px}
.section-title h2{font-size:19px; margin:0; letter-spacing:-.01em}
.section-title span{font-size:13px; color:var(--muted)}
.doc{background:#fff; border:1px solid var(--line); border-radius:16px; padding:26px 22px; box-shadow:var(--shadow); margin:22px 0 40px}
@media(min-width:760px){.doc{padding:38px 42px}}
.doc h1{font-size:26px; margin-top:0}
.doc h2{font-size:18px; margin:30px 0 10px; padding-bottom:7px; border-bottom:1px solid #eef1f6}
.doc p,.doc li{color:#333c48; font-size:15px}
.doc ul{padding-left:20px}
.doc .meta{font-size:13px; color:var(--muted); margin:0 0 22px}
nav.doc-nav{display:flex; flex-wrap:wrap; gap:8px; margin:0 0 22px; padding-bottom:16px; border-bottom:1px solid #eef1f6; font-size:13px}
nav.doc-nav a{color:var(--muted)}
"""

JS_HELPERS = r"""
function $(id){return document.getElementById(id);}
function n(id){var el=$(id); if(!el) return 0; var v=String(el.value).replace(/[^0-9.\-]/g,''); var f=parseFloat(v); return isFinite(f)?f:0;}
function won(x){var v=Math.round(x); return (v<0?'-':'')+Math.abs(v).toLocaleString('ko-KR')+'원';}
function num(x){return Math.round(x).toLocaleString('ko-KR');}
function eok(x){ // 원 -> 억/만원 사람이 읽는 형태
  var v=Math.round(x);
  if(v===0) return '0원';
  var neg=v<0; v=Math.abs(v);
  var eok=Math.floor(v/100000000), man=Math.floor((v%100000000)/10000), wonR=v%10000;
  var s='';
  if(eok) s+=eok.toLocaleString('ko-KR')+'억 ';
  if(man) s+=man.toLocaleString('ko-KR')+'만';
  if(!eok&&!man) return (neg?'-':'')+v.toLocaleString('ko-KR')+'원';
  if(wonR) s+=' '+wonR.toLocaleString('ko-KR')+'원';
  else s+='원';
  return (neg?'-':'')+s.trim();
}
function pct(x,d){ if(!isFinite(x)) x=0; var q=Math.pow(10,d==null?1:d); return (Math.round(x*q)/q).toFixed(d==null?1:d); }
function setText(id,txt){var el=$(id); if(el){ if(el.tagName==='INPUT') el.value=txt; else el.textContent=txt; } }
function monthlyPayment(P, annualRate, months){ // 원리금균등 월 납입액
  var i=annualRate/100/12;
  if(months<=0) return 0;
  if(i===0) return P/months;
  return P*i/(1-Math.pow(1+i,-months));
}
function bindCalc(fn){
  document.querySelectorAll('input,select').forEach(function(el){
    el.addEventListener('input',fn); el.addEventListener('change',fn);
  });
  document.querySelectorAll('button[data-set]').forEach(function(b){
    b.addEventListener('click',function(ev){
      ev.preventDefault();
      var el=$(b.getAttribute('data-set'));
      if(el){ el.value=b.getAttribute('data-val'); fn(); }
    });
  });
  fn();
}
"""


def head(title, desc, keywords, url, faqs, app_name, app_desc, prefix):
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs],
    }
    app_ld = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": app_name,
        "url": url,
        "description": app_desc,
        "applicationCategory": "FinanceApplication",
        "operatingSystem": "Web",
        "inLanguage": "ko-KR",
        "isAccessibleForFree": True,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"},
        "publisher": {"@type": "Organization", "name": SITE, "url": BASE + "/"},
    }
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{keywords}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="{SITE}">
<meta name="theme-color" content="#0f2447">
<meta name="naver-site-verification" content="{NAVER}">
<meta name="google-site-verification" content="{GOOGLE}">
<link rel="canonical" href="{url}">

<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/web-ad/og-image.png">
<meta property="og:locale" content="ko_KR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{BASE}/web-ad/og-image.png">

<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230f2447'/%3E%3Cpath d='M18 40l10-10 6 6 12-14' stroke='%237ce0bb' stroke-width='5' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E">
<link rel="stylesheet" href="{prefix}assets/site.css">
{ADSENSE}
<script type="application/ld+json">
{json.dumps(app_ld, ensure_ascii=False, indent=2)}
</script>
<script type="application/ld+json">
{json.dumps(faq_ld, ensure_ascii=False, indent=2)}
</script>
</head>
"""


def header(prefix, current_slug, from_tools=False):
    items = []
    for i, (slug, short, _t, _d, _e) in enumerate(TOOLS, 1):
        cls = ' class="on"' if slug == current_slug else ""
        items.append(f'<a href="{href(slug, from_tools)}"{cls}>{short}</a>')
    nav = "\n      ".join(items)
    return f"""<body>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{prefix}index.html" aria-label="{SITE} 홈">
      <span class="brand-mark" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 15l4.5-4.5 3.5 3.5L20 6"/><path d="M20 11V6h-5"/></svg>
      </span>
      <span>{SITE}</span>
    </a>
    <nav class="tool-nav" aria-label="무료 계산기 10종">
      {nav}
    </nav>
  </div>
</header>
"""


def footer(prefix, from_tools=False):
    links = "\n        ".join(
        f'<a href="{href(s, from_tools)}">{t}</a>' for s, _sh, t, _d, _e in TOOLS)
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <span class="brand-foot">{SITE}</span>
        <p>회원가입도, 앱 설치도 없이 브라우저에서 바로 쓰는 무료 생활 금융 계산기 10종입니다. 입력한 값은 서버로 전송되지 않습니다.</p>
      </div>
      <div>
        <h2>계산기 10종</h2>
        <div class="footer-links">
        {links}
        </div>
      </div>
      <div>
        <h2>안내</h2>
        <p><a href="{prefix}privacy.html">개인정보처리방침</a></p>
        <p><a href="{prefix}index.html">전체 도구 보기</a></p>
        <p>계산 결과는 참고용이며, 실제 조건은 금융기관·관할 관청의 안내와 약정서로 확인해 주세요.</p>
      </div>
    </div>
    <p class="copy">© 2026 {SITE}. 계산 결과는 참고용 추정치이며 금융상품 중개나 세무 자문을 하지 않습니다.</p>
  </div>
</footer>
"""


def faq_html(faqs):
    rows = []
    for q, a in faqs:
        paras = "".join(f"<p>{p}</p>" for p in a.split("\n") if p.strip())
        rows.append(f"""<details class="qa">
  <summary>{q}</summary>
  <div class="a">{paras}</div>
</details>""")
    return "\n".join(rows)


def related(slug, prefix, exclude=()):
    picks = [t for t in TOOLS if t[0] != slug and t[0] not in exclude][:3]
    cards = []
    for s, _sh, t, d, e in picks:
        num_ = [x[0] for x in TOOLS].index(s) + 1
        cards.append(f"""<a class="card" href="{href(s, True)}">
  <span class="num">{num_:02d} · 무료</span>
  <h3>{e} {t}</h3>
  <p>{d}</p>
</a>""")
    return f"""<section class="related">
  <h2>함께 쓰면 좋은 계산기</h2>
  <div class="cards">
    {"".join(cards)}
  </div>
</section>"""


def tool_page(p):
    """p: dict with slug,title,h1,lede,desc,keywords,fields,results,script,content,faqs,disclaimer"""
    slug = p["slug"]
    url = f"{BASE}/" + (slug + ".html")
    title = p["title"]
    out = [head(title, p["desc"], p["keywords"], url, p["faqs"],
                p["h1"], p["desc"], "../")]
    out.append(header("../", slug, True))
    out.append(f"""<main>
  <div class="wrap">
    <p class="crumb"><a href="../index.html">{SITE}</a> &rsaquo; {p["h1"]}</p>
    <div class="page-head">
      <span class="kicker">{p["kicker"]}</span>
      <h1>{p["h1"]}</h1>
      <p class="lede">{p["lede"]}</p>
    </div>

    <section class="calc" aria-label="계산기">
      <form class="panel" id="calc-form" onsubmit="return false;">
        <h2 class="panel-title">조건 입력</h2>
        {p["fields"]}
      </form>
      <div class="result-panel" id="results" aria-live="polite">
        {p["results"]}
      </div>
    </section>

    <section class="content">
      {p["content"]}
    </section>

    <section class="faq">
      <h2>자주 묻는 질문</h2>
      {faq_html(p["faqs"])}
    </section>

    <p class="disclaimer"><strong>참고용 안내.</strong> {p["disclaimer"]}</p>

    {related(slug, "../")}
  </div>
</main>
{footer("../", True)}
<script>
{JS_HELPERS}
{p["script"]}
</script>
</body>
</html>
""")
    return "".join(out)


# ---------------------------------------------------------------- portal
def build_index():
    cards = []
    for i, (slug, _sh, title, desc, emoji) in enumerate(TOOLS, 1):
        cards.append(f"""<a class="tool-card" href="{href(slug, False)}">
  <div class="tc-top"><span class="tc-ico" aria-hidden="true">{emoji}</span><span class="tc-num">TOOL {i:02d}</span></div>
  <h2>{title}</h2>
  <p>{desc}</p>
  <span class="tc-go">계산기 열기 →</span>
</a>""")

    faqs = [
        ("이 계산기들은 무료인가요? 회원가입이 필요한가요?",
         "10종 모두 무료이고 회원가입이나 앱 설치가 필요 없습니다. 브라우저 주소만 열면 바로 계산할 수 있고, 계산 횟수 제한도 없습니다."),
        ("입력한 금액이 서버에 저장되나요?",
         "아니요. 모든 계산은 이용자의 브라우저 안에서 자바스크립트로만 처리됩니다. 대출 금액, 연봉, 매매가 같은 입력값은 서버로 전송되지 않고 어디에도 저장되지 않으며, 창을 닫으면 사라집니다."),
        ("계산 결과를 그대로 믿어도 되나요?",
         "계산 결과는 공개된 요율과 공식을 기준으로 한 참고용 추정치입니다. 실제 대출 금리·한도는 금융기관 심사에 따라, 세금은 관할 관청의 고지에 따라 달라질 수 있으니 계약 전에 해당 기관의 안내와 약정서를 확인해 주세요."),
        ("어떤 계산기부터 쓰면 좋을까요?",
         "집을 사거나 옮길 계획이면 대출 갈아타기 → 주담대 이자 → DSR 한도 → 취득세·복비 순서로 보면 전체 비용이 한 번에 정리됩니다. 전세와 월세를 저울질할 때는 월세 vs 전세 비교를, 소득·퇴직·청약이 궁금할 때는 연봉 실수령·퇴직금·청약 가점 계산기를 쓰면 됩니다."),
    ]
    desc = ("주담대 이자, DSR 한도, 취득세·복비, 월세 vs 전세, 예적금 실수령액, 연봉 실수령액, 퇴직금·실업급여, "
            "청약 가점, 양도소득세까지 — 회원가입 없이 바로 쓰는 무료 생활 금융 계산기 10종 모음입니다.")
    out = [head("생활 금융 계산기 10종 | 대출·세금·연봉·청약 무료 계산",
                desc,
                "금융 계산기, 대출 이자 계산기, DSR 계산기, 취득세 계산기, 중개보수 계산기, 월세 전세 비교, 적금 이자 계산기, 연봉 실수령액, 퇴직금 계산기, 실업급여 계산기, 청약 가점 계산기, 양도소득세 계산기",
                f"{BASE}/", faqs, "생활 금융 계산기 10종", desc, "")]
    out.append(header("", ""))
    out.append(f"""<main>
  <div class="wrap">
    <section class="hero">
      <span class="kicker">무료 · 회원가입 없음 · 입력값 서버 전송 없음</span>
      <h1>돈이 걸린 계산,<br>10가지 도구로 한 번에 정리하세요</h1>
      <p>대출을 갈아탈지, 집을 살지, 전세로 갈지, 연봉에서 얼마가 빠지는지 — 생활에서 실제로 돈이 오가는 계산만 모았습니다. 브라우저에서 바로 계산되고, 입력한 값은 어디에도 저장되지 않습니다.</p>
      <div class="stats"><span>계산기 10종</span><span>공식·요율 근거 공개</span><span>모바일 최적화</span><span>100% 무료</span></div>
    </section>

    <div class="section-title">
      <h2>계산기 10종</h2>
      <span>필요한 도구를 눌러 바로 시작하세요</span>
    </div>
    <section class="tool-cards">
      {"".join(cards)}
    </section>

    <section class="content">
      <h2>이 사이트를 만든 이유</h2>
      <p>부동산 거래와 대출, 세금, 연봉 이야기는 늘 숫자로 시작하지만 정작 그 숫자를 확인할 곳은 흩어져 있습니다. 은행 앱은 자기 상품만 계산해 주고, 세금은 관청마다 안내가 다르며, 커뮤니티에 올라온 계산은 어느 조건에서 나온 값인지 알 수 없습니다.</p>
      <p>그래서 <strong>계산식과 적용 요율을 페이지에 그대로 적어 두는 계산기</strong>를 만들었습니다. 결과만 보여 주고 끝내지 않고, 어떤 공식으로 어떤 값을 넣었는지 함께 적었기 때문에 숫자가 이상하면 어디가 다른지 직접 확인할 수 있습니다.</p>

      <h2>어떤 순서로 쓰면 좋을까요</h2>
      <ul>
        <li><strong>집을 살 때</strong> — 주택담보·전세대출 월 이자 계산기로 월 부담을 확인하고, DSR·대출 한도 계산기로 실제로 얼마까지 빌릴 수 있는지 본 뒤, 취득세·중개보수 계산기로 계약일에 나갈 현금을 정리합니다.</li>
        <li><strong>이사를 앞두고</strong> — 월세 vs 전세 비교 계산기로 2년 동안의 총비용을 비교하고, 대출 갈아타기 계산기로 기존 대출을 옮기는 게 나은지 봅니다.</li>
        <li><strong>월급과 노후</strong> — 연봉 실수령액 계산기로 통장에 들어오는 금액을 확인하고, 적금·예금 계산기로 만기 실수령액을, 퇴직금·실업급여 계산기로 회사를 나올 때의 현금 흐름을 가늠합니다.</li>
        <li><strong>내 집 마련 준비</strong> — 청약 가점 계산기로 현재 점수와 부족한 항목을 확인하고, 집을 팔 계획이 있다면 양도소득세 간이 계산기로 세금 규모를 미리 봅니다.</li>
      </ul>

      <h2>결과를 읽는 방법</h2>
      <p>모든 계산기는 ① 조건 입력 ② 결과 확인 ③ 계산 원리와 FAQ 순서로 구성했습니다. 결과 카드의 큰 숫자는 가장 궁금한 값(월 납입액, 실수령액, 예상 한도 등)이고, 그 아래 작은 표에 세부 내역이 이어집니다. 금액은 원 단위로 표시하며, 큰 금액은 억·만 단위로도 함께 읽을 수 있게 했습니다.</p>
      <p>요율은 2026년 11월 기준으로 확인한 값을 기본값으로 넣었습니다. 제도가 바뀌면 페이지의 기준일 표시와 함께 갱신하며, 직접 요율을 입력할 수 있는 항목은 입력칸으로 열어 두었습니다.</p>

      <h2>개인정보와 광고</h2>
      <p>계산에 쓰는 값은 브라우저 메모리에서만 처리되고 전송·저장되지 않습니다. 사이트 운영을 위해 Google AdSense 광고가 표시될 수 있으며, 광고 쿠키 사용 여부는 브라우저 설정에서 끌 수 있습니다. 자세한 내용은 <a href="privacy.html">개인정보처리방침</a>에 적어 두었습니다.</p>
    </section>

    <section class="faq">
      <h2>자주 묻는 질문</h2>
      {faq_html(faqs)}
    </section>

    <p class="disclaimer"><strong>참고용 안내.</strong> 이 사이트의 모든 계산 결과는 공개된 요율과 공식을 바탕으로 한 추정치입니다. 대출 금리·한도·세금은 개인의 신용 상태, 지역, 시점, 금융기관 정책에 따라 달라지므로 계약 전에 해당 금융기관과 관할 관청의 안내를 확인해 주세요. 이 사이트는 금융상품을 중개하거나 세무 자문을 제공하지 않습니다.</p>
  </div>
</main>
{footer("")}
</body>
</html>
""")
    return "".join(out)


# ---------------------------------------------------------------- privacy
def build_privacy():
    faqs = [("계산기에 입력한 값이 저장되나요?",
             "저장되지 않습니다. 모든 계산은 브라우저 안에서만 이루어지고 서버로 전송되는 값은 없습니다.")]
    desc = "생활 금융 계산기 10종의 개인정보처리방침입니다. 계산기 입력값은 브라우저에서만 처리되고 서버로 전송되지 않습니다."
    out = [head("개인정보처리방침 | 생활 금융 계산기", desc,
                "개인정보처리방침, 쿠키, 광고, 계산기 개인정보",
                f"{BASE}/privacy.html", faqs, "개인정보처리방침", desc, "")]
    out.append(header("", "__none__"))
    tool_links = "\n    ".join(f'<a href="{href(s, False)}">{t}</a>' for s, _x, t, _y, _z in TOOLS)
    out.append(f"""<main>
  <div class="wrap">
    <div class="doc narrow">
      <h1>개인정보처리방침</h1>
      <p class="meta">시행일: 2026년 11월 15일 · 최종 수정: 2026년 11월 15일</p>

      <nav class="doc-nav">
        {tool_links}
      </nav>

      <p>생활 금융 계산기(이하 &ldquo;사이트&rdquo;)는 이용자의 개인정보를 소중히 다루고, 「개인정보 보호법」 등 관련 법령을 지킵니다. 이 방침은 사이트가 어떤 정보를 다루고, 무엇을 하지 않는지 알려 드리기 위해 작성했습니다. 사이트에서 제공하는 10종의 계산기 모두에 동일하게 적용됩니다.</p>

      <h2>1. 계산기 입력값은 서버로 전송되지 않습니다</h2>
      <p>사이트의 계산기는 대출 원금, 금리, 연봉, 매매가, 보유 주택 수 같은 숫자를 이용자의 브라우저(기기) 안에서만 계산합니다. 이 값들은 <strong>서버로 전송되지 않고, 어디에도 저장되지 않으며, 회원가입이나 로그인이 필요하지 않습니다.</strong> 브라우저를 닫으면 입력값은 남지 않습니다.</p>

      <h2>2. 수집하지 않는 정보</h2>
      <p>사이트는 이름, 주민등록번호, 휴대전화번호, 주소, 계좌번호, 카드번호, 신용정보 등 개인을 식별할 수 있는 정보를 수집하지 않습니다. 대출 심사, 금융상품 가입, 세무 신고를 대신하지도 않습니다.</p>

      <h2>3. 자동으로 수집될 수 있는 정보</h2>
      <p>사이트를 제공하는 호스팅 사업자(GitHub Pages)는 서비스 운영과 보안을 위해 접속 IP 주소, 브라우저 종류와 버전, 접속 일시, 방문한 페이지 같은 접속 기록을 자동으로 남길 수 있습니다. 이 정보는 통계와 장애 대응 목적으로만 쓰이고, 개인을 식별하는 데 사용하지 않습니다.</p>

      <h2>4. 쿠키와 광고</h2>
      <p>사이트는 계산 기능을 위해 쿠키를 사용하지 않습니다. 다만 사이트에는 Google AdSense 광고가 게재되며, 이 경우 아래 내용이 적용됩니다.</p>
      <ul>
        <li>Google을 포함한 제3자 판매자는 쿠키를 사용해 이용자가 이전에 방문한 사이트를 기준으로 광고를 게재할 수 있습니다.</li>
        <li>Google이 광고 쿠키를 사용함으로써 Google과 파트너는 이용자의 사이트 방문 기록을 바탕으로 광고를 제공할 수 있습니다.</li>
        <li>이용자는 <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener">Google 광고 설정</a>에서 맞춤 광고를 해제할 수 있습니다.</li>
        <li>맞춤 광고를 원하지 않으면 <a href="https://www.aboutads.info/choices/" target="_blank" rel="noopener">aboutads.info</a>에서 제3자 판매자의 쿠키 사용을 거부할 수 있습니다.</li>
        <li>브라우저 설정에서 쿠키 저장을 막을 수 있으며, 이 경우에도 모든 계산기는 정상적으로 동작합니다.</li>
      </ul>

      <h2>5. 개인정보의 제3자 제공 및 처리 위탁</h2>
      <p>사이트는 이용자의 개인정보를 수집하지 않으므로 제3자에게 제공하거나 처리를 위탁하지 않습니다. 광고를 게재하는 경우 광고 사업자의 쿠키 사용은 위 4항에 따릅니다.</p>

      <h2>6. 보관 기간</h2>
      <p>사이트가 직접 보관하는 개인정보는 없습니다. 호스팅 사업자가 남기는 접속 기록의 보관 기간은 해당 사업자의 정책을 따릅니다.</p>

      <h2>7. 이용자의 권리</h2>
      <p>이용자는 언제든지 광고 쿠키 사용을 거부하거나 브라우저 설정을 변경할 수 있습니다. 사이트가 보관하는 개인정보가 없으므로 열람·정정·삭제를 요청할 대상 정보는 없습니다.</p>

      <h2>8. 아동의 개인정보</h2>
      <p>사이트는 만 14세 미만 아동을 대상으로 하지 않으며, 아동의 개인정보를 고의로 수집하지 않습니다.</p>

      <h2>9. 계산 결과의 성격</h2>
      <p>사이트가 제공하는 모든 계산 결과는 공개된 요율과 공식에 따른 참고용 추정치입니다. 대출 한도, 세금, 중개보수는 개별 계약과 심사 결과에 따라 달라지며, 사이트는 그 차이에 대해 책임지지 않습니다.</p>

      <h2>10. 방침의 변경</h2>
      <p>이 방침이 바뀌면 사이트에 변경 내용과 시행일을 함께 게시합니다. 중요한 변경이 있으면 시행 전에 미리 알려 드립니다.</p>

      <p style="margin-top:26px"><a href="index.html">&larr; 전체 계산기 보기</a></p>
    </div>
  </div>
</main>
{footer("")}
</body>
</html>
""")
    return "".join(out)


# ---------------------------------------------------------------- sitemap
def build_sitemap():
    rows = []
    for slug, _s, _t, _d, _e in TOOLS:
        loc = f"{BASE}/{slug}/" if slug == "web-ad" else f"{BASE}/{slug}.html"
        pri = "1.0" if slug == "web-ad" else "0.9"
        rows.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{LASTMOD}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>{pri}</priority>
  </url>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{BASE}/</loc>
    <lastmod>{LASTMOD}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
{chr(10).join(rows)}
  <url>
    <loc>{BASE}/privacy.html</loc>
    <lastmod>{LASTMOD}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
</urlset>
"""


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True) if os.path.dirname(full) else None
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path, len(content))
