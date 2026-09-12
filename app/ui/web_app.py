import os
import re
import subprocess
import tempfile
import threading
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template_string, request

from app.core.chatbot import RAGChatbot
from app.core.settings import load_settings, update_settings
from app.services.diagnostics import get_diagnostics, scan_project
from app.services.knowledge_store import get_store_summary, search_topics, store_user_data
from app.services.simulator_catalog import SIMULATOR_CATALOG, flatten_simulators
from app.services.web_search import search_web, summarize_results
from app.services.google_drive import authorization_url, integration_status, upload_text
from app.tools.formula_sheet import FORMULA_SHEET
from app.tools.coding_engine import analyze_code, explain_code, language_template, run_code
from app.tools.calculator import evaluate_expression
from app.utils.image_ai import generate_image, inspect_image

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

README_PATH = Path(__file__).resolve().parents[2] / "README.md"
VERSION_MATCH = re.search(r"^## Version\s*\n\s*([^\s]+)", README_PATH.read_text(encoding="utf-8"), re.MULTILINE) if README_PATH.exists() else None
APP_VERSION = VERSION_MATCH.group(1) if VERSION_MATCH else "development"


HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Edulab Lab</title>
  <style>
    :root {
      --bg: #f4f7fb;
      --panel: #ffffff;
      --primary: #2d7dd2;
      --accent: #1f4e79;
      --text: #1d2a3a;
      --muted: #57657e;
      --line: #dfeaf7;
      --success: #1a5e30;
      --warning: #8a4b15;
      --soft: #f7fbff;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; font-family: "Segoe UI", system-ui, sans-serif; background: var(--bg);
      color: var(--text);
    }
    .topbar {
      background: var(--accent); color: white; padding: 14px 22px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    .brand { font-size: 28px; font-weight: 700; }
    .topbar-right { display: flex; gap: 12px; align-items: center; }
    .pill { border-radius: 999px; background: rgba(255,255,255,0.12); padding: 6px 12px; font-size: 12px; }
    .layout {
      display: grid; grid-template-columns: 220px minmax(0, 1fr); min-height: calc(100vh - 72px);
    }
    .sidebar {
      background: var(--panel); border-right: 1px solid var(--line); padding: 18px;
    }
    .section-title { font-size: 13px; color: var(--muted); letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 10px; }
    .sidebar button, .chip {
      background: var(--panel); color: var(--text); border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; margin-bottom: 8px; width: 100%; text-align: left; cursor: pointer; font-size: 14px;
    }
    .content { padding: 20px; }
    .hero {
      background: var(--accent); color: white; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 8px 20px rgba(31,78,121,0.14);
    }
    .hero h2 { margin: 0 0 8px; font-size: 30px; }
    .cards {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px;
    }
    .card {
      background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 16px; box-shadow: 0 8px 20px rgba(0,0,0,0.04);
    }
    .card h3 { margin-top: 0; }
    .search {
      width: 100%; padding: 12px 14px; border-radius: 12px; border: 1px solid var(--line); margin-bottom: 14px; font-size: 14px;
    }
    .tabs { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 16px; }
    .tab { padding: 8px 12px; border-radius: 999px; border: 1px solid var(--line); background: var(--panel); color: var(--text); cursor: pointer; }
    .tab.active { background: var(--primary); color: white; border-color: var(--primary); }
    .sim-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
    .sim-item { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 12px; }
    .sim-item small { color: var(--muted); display: block; margin-bottom: 8px; }
    .sim-item button { background: var(--primary); color: white; border: none; border-radius: 8px; padding: 8px 12px; cursor: pointer; }
    .formula-box { background: var(--soft); border: 1px solid var(--line); padding: 12px; border-radius: 12px; margin-top: 12px; }
    .mb { margin-bottom: 10px; }
    .chatbox { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 12px; }
    textarea, input, select { width: 100%; background: var(--panel); color: var(--text); border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; font-size: 14px; }
    button.primary { background: var(--primary); color: white; border: none; border-radius: 10px; padding: 10px 16px; cursor: pointer; }
    .status { margin-top: 12px; color: var(--success); font-weight: 600; }
    .footer { color: var(--muted); font-size: 12px; text-align: center; padding: 26px 0 8px; }
    .toolbar { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
    .toolbar button { width: auto; margin: 0; text-align: center; }
    .drawer { position: fixed; inset: 0 0 0 auto; width: min(520px, 94vw); background: var(--panel); border-left: 1px solid var(--line); box-shadow: -12px 0 30px rgba(0,0,0,.16); padding: 22px; overflow: auto; z-index: 5; }
    .drawer[hidden] { display: none; }
    .file-row { display: flex; justify-content: space-between; gap: 12px; border-bottom: 1px solid var(--line); padding: 9px 0; font-size: 13px; }
    .error { color: #a12626; }
    .dark { --bg: #101820; --panel: #172330; --soft: #203242; --text: #e8f0f7; --muted: #a7b7c8; --line: #304454; --primary: #49a3a2; --accent: #0d2e3b; --success: #8ee1b2; }
    .modal { position: fixed; inset: 0; display: grid; place-items: center; background: rgba(8, 18, 28, .56); z-index: 10; padding: 18px; }
    .modal[hidden] { display: none; }
    .modal-card { width: min(580px, 100%); background: var(--panel); color: var(--text); border: 1px solid var(--line); border-radius: 18px; padding: 24px; box-shadow: 0 24px 70px rgba(0,0,0,.28); }
    .setting-row { display: grid; grid-template-columns: 1fr auto; gap: 14px; align-items: center; padding: 14px 0; border-bottom: 1px solid var(--line); }
    .setting-row small { display: block; color: var(--muted); margin-top: 4px; }
    .subject-grid { display: grid; grid-template-columns: repeat(5, minmax(130px, 1fr)); gap: 10px; margin-bottom: 18px; }
    .subject-card { min-height: 128px; padding: 15px; border-radius: 12px; border: 1px solid var(--line); background: var(--soft); }
    .subject-card strong { display: block; margin: 10px 0 6px; }
    .subject-card span { color: var(--muted); font-size: 12px; }
    .search-summary { display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap; margin: -4px 0 12px; color: var(--muted); font-size: 12px; }
    .tiny-note { display: inline-flex; align-items: center; gap: 6px; border-radius: 999px; background: var(--soft); border: 1px solid var(--line); padding: 5px 10px; }
    .empty-state { background: var(--soft); border: 1px dashed var(--line); border-radius: 12px; padding: 16px; color: var(--muted); }
    .tool-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
    .tool-grid button { min-height: 52px; text-align: center; }
    .calculator-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; max-width: 420px; }
    .calculator-grid button { min-height: 44px; font-size: 16px; }
    .rail-title { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
    .pagination { display: flex; align-items: center; justify-content: center; gap: 12px; margin-top: 18px; }
    .pagination button { width: auto; margin: 0; text-align: center; }
    .loading-screen { position: fixed; inset: 0; display: grid; place-items: center; background: #08131d; color: #fff; z-index: 20; }
    .loading-screen[hidden] { display: none; }
    .loading-card { width: min(520px, 90vw); text-align: center; padding: 34px; }
    .loading-mark { width: 58px; height: 58px; margin: 0 auto 18px; border: 4px solid #28495e; border-top-color: #48b8b5; border-radius: 50%; animation: spin 1s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .sim-canvas { width: 100%; height: 320px; background: #0b1722; border-radius: 12px; border: 1px solid var(--line); display: block; }
    .sim-controls { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 14px 0; }
    .sim-controls label { color: var(--muted); font-size: 12px; }
    .sim-controls input, .sim-controls select { margin-top: 5px; }
    .circuit-list { display: flex; flex-wrap: wrap; gap: 8px; min-height: 44px; padding: 10px; background: var(--soft); border: 1px dashed var(--line); border-radius: 10px; }
    .circuit-chip { padding: 8px 10px; background: var(--primary); color: #fff; border-radius: 8px; cursor: pointer; }
    .dark body, body.dark { background: #101820; color: var(--text); }
    @media (max-width: 780px) {
      .layout { display: block; }
      .sidebar { border-right: 0; border-bottom: 1px solid var(--line); }
      .sidebar button { width: calc(50% - 6px); margin-right: 6px; }
      .content { padding: 14px; }
      .topbar { padding: 12px 14px; }
      .topbar-right .pill:not(#clock), .topbar-right #settingsBtn { display: none; }
      .subject-grid { grid-template-columns: repeat(2, 1fr); }
      .tool-grid { grid-template-columns: repeat(2, 1fr); }
      .sim-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
  </style>
</head>
<body>
<div class="topbar">
  <div class="brand">Edulab</div>
  <div class="topbar-right">
    <div class="pill" id="clock">--:--</div>
    <div class="pill">Network: Online</div>
    <button class="pill" id="settingsBtn">Settings</button>
  </div>
</div>
<div class="layout">
  <aside class="sidebar">
    <div class="section-title">Subjects</div>
    <button class="subject-btn active" data-subject="all">All</button>
    <button class="subject-btn" data-subject="Physics">Physics</button>
    <button class="subject-btn" data-subject="Chemistry">Chemistry</button>
    <button class="subject-btn" data-subject="Mathematics">Mathematics</button>
    <button class="subject-btn" data-subject="Computer Science">Computer Science</button>
    <br><br>
    <div class="section-title">Quick Tools</div>
    <button id="formulaBtn">▦ Formula sheet</button>
    <button id="chatBtn">◌ AI tutor</button>
    <button id="codeBtn">▣ Code compiler</button>
    <button id="calculatorBtn">⌗ Scientific calculator</button>
    <button id="webSearchBtn">⌕ Web search</button>
    <button id="simulatorsBtn">◫ Simulators</button>
    <button id="debugBtn" hidden>Diagnostics</button>
  </aside>
  <main class="content">
    <div class="hero">
      <h2>Learning Lab</h2>
      <div>EduEngine 1 connects EduCore AI, EduSim simulations, and EduCalc tools in one learning workspace.</div>
    </div>
    <div class="subject-grid">
      <button class="subject-card" data-subject="Physics"><strong>⚛ Physics</strong><span>Simulations and concepts</span></button>
      <button class="subject-card" data-subject="Chemistry"><strong>⚗ Chemistry</strong><span>Reactions and molecules</span></button>
      <button class="subject-card" data-subject="Mathematics"><strong>π Mathematics</strong><span>Graphs and problem solving</span></button>
      <button class="subject-card" id="codingHome"><strong>⌘ Coding</strong><span>Write, run, and learn</span></button>
      <button class="subject-card" id="aiHome"><strong>◉ EduCore AI</strong><span>Your learning assistant</span></button>
      <button class="subject-card" id="calculatorHome"><strong>⌗ Calculator</strong><span>Scientific calculations</span></button>
    </div>
    <div class="card" style="margin-bottom: 16px;">
      <div class="rail-title"><h3>Quick search</h3><span class="pill">Ctrl + K</span></div>
      <input class="search" id="searchInput" placeholder="Find simulators, formulas, or ask EduCore..." />
      <div class="search-summary">
        <span id="searchSummary">Showing all subjects</span>
        <span class="tiny-note">Press Ctrl + K to focus</span>
      </div>
      <div class="tabs" id="tabs"></div>
    </div>
    <div class="toolbar">
      <button class="primary" id="knowledgeSearchBtn">Search knowledge base</button>
      <span class="pill">Ctrl+Alt+Space+R reloads</span>
    </div>
    <div id="appView"></div>
    <footer class="footer">Edulab version {{ app_version }} · Local-first learning workspace</footer>
  </main>
</div>
<aside class="drawer" id="drawer" hidden></aside>
<div class="loading-screen" id="simLoading" hidden><div class="loading-card"><div class="loading-mark"></div><h2>EduSim</h2><p>Edulab's unified scientific simulation engine for Physics, Chemistry, and Mathematics.</p><p id="loadingName"></p></div></div>

<script>
const catalog = {{ catalog | tojson }};
const formulaSheet = {{ formula_sheet | tojson }};
const initialSettings = {{ settings | tojson }};
const knowledgeSummary = {{ knowledge_summary | tojson }};
const initialPage = {{ initial_page | tojson }};
const featuredSimulators = [
  { name: 'Projectile Motion', subject: 'Physics', group: 'Mechanics' },
  { name: "Newton's Laws", subject: 'Physics', group: 'Mechanics' },
  { name: 'Collision Lab', subject: 'Physics', group: 'Mechanics' },
  { name: 'Inclined Plane', subject: 'Physics', group: 'Mechanics' },
  { name: 'Circular Motion', subject: 'Physics', group: 'Mechanics' },
  { name: 'Spring-Mass', subject: 'Physics', group: 'Mechanics' },
  { name: 'Pendulum', subject: 'Physics', group: 'Mechanics' },
  { name: 'Wave Motion', subject: 'Physics', group: 'Waves' },
  { name: 'Ray Optics', subject: 'Physics', group: 'Optics' },
  { name: "Ohm's Law", subject: 'Physics', group: 'Electricity' },
  { name: 'Molecule Builder', subject: 'Chemistry', group: 'Organic Chemistry' },
  { name: 'Titration Simulator', subject: 'Chemistry', group: 'Acids and Bases' },
  { name: '3D Geometry Lab', subject: 'Mathematics', group: '3D Geometry' },
  { name: 'Function Grapher', subject: 'Mathematics', group: 'Functions' },
  { name: 'Vector Visualizer', subject: 'Mathematics', group: 'Vectors' },
  { name: 'Probability Simulator', subject: 'Mathematics', group: 'Probability' },
  { name: 'Calculus Visualizer', subject: 'Mathematics', group: 'Calculus' }
];

const state = { subject: 'all', group: 'all', page: 1, pageSize: 24 };
const allSimulators = Object.entries(catalog).flatMap(([subject, groups]) => Object.entries(groups).flatMap(([group, names]) => names.map(name => ({ name, subject, group })))).sort((a, b) => a.name.localeCompare(b.name));

function renderTabs() {
  const tabs = ['all'];
  Object.keys(catalog).forEach((subject) => tabs.push(subject));
  const container = document.getElementById('tabs');
  container.innerHTML = tabs.map((tab) => `
    <button class="tab ${state.subject === tab ? 'active' : ''}" data-subject="${tab}">${tab === 'all' ? 'All subjects' : tab}</button>
  `).join('');

  document.querySelectorAll('.tab').forEach((btn) => {
    btn.onclick = () => {
      state.subject = btn.dataset.subject;
      state.page = 1;
      renderTabs();
      renderHome();
    };
  });
}

function renderHome() {
  const searchTerm = document.getElementById('searchInput').value.trim().toLowerCase();
  const featured = featuredSimulators.filter(item => {
    const subjectOk = state.subject === 'all' || item.subject === state.subject;
    const searchOk = !searchTerm || item.name.toLowerCase().includes(searchTerm) || item.subject.toLowerCase().includes(searchTerm);
    return subjectOk && searchOk;
  });

  const view = document.getElementById('appView');
  view.innerHTML = `
    <div class="card" style="margin-bottom:20px;">
      <h3>Most important simulators</h3>
      <div class="sim-grid">
        ${featured.map(item => `
          <div class="sim-item">
            <small>${item.subject} / ${item.group}</small>
            <h4>${item.name}</h4>
            <button class="sim-launch" data-simulator="${item.name}">Launch</button>
          </div>
        `).join('') || '<div class="sim-item"><h4>No featured simulators</h4></div>'}
      </div>
    </div>
    <div class="card">
      <h3>Full simulator catalog</h3>
      ${renderCatalogCards(searchTerm)}
    </div>
  `;
  document.querySelectorAll('.sim-launch').forEach((button) => {
    button.onclick = () => runSimulator(button.dataset.simulator);
  });
  attachPagination();
}

function renderSimulators() {
  renderHome();
}

function renderCatalogCards(searchTerm) {
  const items = getFilteredSimulators(searchTerm).filter(item => !featuredSimulators.some(f => f.name === item.name));

  const pageCount = Math.max(1, Math.ceil(items.length / state.pageSize));
  state.page = Math.min(state.page, pageCount);
  const visible = items.slice((state.page - 1) * state.pageSize, state.page * state.pageSize);
  return visible.length ? `<div class="sim-grid">${visible.map(item => `
    <div class="sim-item">
      <small>${item.subject} / ${item.group}</small>
      <h4>${item.name}</h4>
      <button class="sim-launch" data-simulator="${item.name}">Open</button>
    </div>
  `).join('')}</div><div class="pagination"><button class="chip" id="previousPage" ${state.page === 1 ? 'disabled' : ''}>Previous</button><span>Page ${state.page} of ${pageCount}</span><button class="chip" id="nextPage" ${state.page === pageCount ? 'disabled' : ''}>Next</button></div>` : '<div class="empty-state">No simulator matches the current search or subject filter.</div>';
}

function attachPagination() {
  const previous = document.getElementById('previousPage');
  const next = document.getElementById('nextPage');
  if (previous) previous.onclick = () => { state.page -= 1; renderHome(); };
  if (next) next.onclick = () => { state.page += 1; renderHome(); };
}

function openSimulatorLibrary() {
  const loading = document.getElementById('simLoading');
  document.getElementById('loadingName').innerText = 'Simulator library';
  loading.hidden = false;
  window.setTimeout(() => { loading.hidden = true; state.page = 1; renderHome(); document.getElementById('appView').scrollIntoView({behavior:'smooth'}); }, 450);
}

function runSimulator(name) {
  const simulatorMap = {
    'Projectile Motion': projectileVisualSimulator,
    "Ohm's Law": ohmsLawSimulator,
    'Quadratic Equation': quadraticEquationSimulator,
    'Molarity': molaritySimulator,
    'Circuit Helper': circuitBuilderSimulator,
    'DC Circuit': circuitBuilderSimulator,
    'Magnetic Field': magneticFieldSimulator,
    'Bar Magnet': magneticFieldSimulator,
    'Matrix Tool': matrixToolSimulator,
    'Wave on a String': genericVisualSimulator,
    'Chemical Equation Balancer': genericVisualSimulator,
    'Function Grapher': functionGrapherSimulator
  };

  const renderer = simulatorMap[name] || genericVisualSimulator;
  const loading = document.getElementById('simLoading');
  document.getElementById('loadingName').innerText = name;
  loading.hidden = false;
  window.setTimeout(() => { loading.hidden = true; renderer(name); }, 450);
}

function canvasFrame(title, controls, canvasId, outputId) {
  document.getElementById('appView').innerHTML = `<div class="card"><div class="rail-title"><h3>${title}</h3><span class="pill">EduSim / HTML5</span></div><div class="sim-controls">${controls}</div><canvas id="${canvasId}" class="sim-canvas" width="900" height="320"></canvas><div id="${outputId}" class="status" style="color:var(--text);">Adjust the controls to run the simulation.</div></div>`;
  return document.getElementById(canvasId).getContext('2d');
}

function projectileVisualSimulator() {
  const ctx = canvasFrame('Projectile Motion', '<label>Velocity<input id="vInput" type="range" min="1" max="60" value="24"></label><label>Angle<input id="aInput" type="range" min="5" max="85" value="45"></label><label>Gravity<input id="gInput" type="range" min="1" max="20" step="0.1" value="9.8"></label>', 'projectileCanvas', 'projectileOutput');
  const draw = () => { const v = Number(vInput.value), angle = Number(aInput.value) * Math.PI / 180, g = Number(gInput.value); const time = 2 * v * Math.sin(angle) / g; const range = v * v * Math.sin(2 * angle) / g; ctx.clearRect(0, 0, 900, 320); ctx.strokeStyle = '#78a9c2'; ctx.beginPath(); ctx.moveTo(40, 270); ctx.lineTo(860, 270); ctx.stroke(); ctx.strokeStyle = '#49a3a2'; ctx.lineWidth = 3; ctx.beginPath(); for (let i=0;i<=60;i++) { const t = time*i/60; const x = 50 + (v*Math.cos(angle)*t/range)*760; const y = 270 - Math.max(0, (v*Math.sin(angle)*t - .5*g*t*t)/(v*v*Math.sin(angle)**2/(2*g)))*220; i ? ctx.lineTo(x,y) : ctx.moveTo(x,y); } ctx.stroke(); ctx.fillStyle = '#e8f0f7'; ctx.fillText(`Range ${range.toFixed(2)} m · Flight ${time.toFixed(2)} s`, 40, 30); projectileOutput.innerText = `Range: ${range.toFixed(2)} m | Time: ${time.toFixed(2)} s | Max height: ${(v*v*Math.sin(angle)**2/(2*g)).toFixed(2)} m`; }; [vInput,aInput,gInput].forEach(input => input.oninput = draw); draw();
}

function circuitBuilderSimulator() {
  document.getElementById('appView').innerHTML = `<div class="card"><div class="rail-title"><h3>Circuit Construction Kit</h3><span class="pill">EduSim / HTML5</span></div><div class="sim-controls"><label>Battery voltage<input id="batteryInput" type="number" value="12" min="0"></label><label>Add component<select id="componentSelect"><option value="resistor">Resistor</option><option value="bulb">Light bulb</option><option value="switch">Switch</option></select></label><button class="primary" id="addComponent">Add to circuit</button></div><div class="circuit-list" id="circuitList"></div><canvas id="circuitCanvas" class="sim-canvas" width="900" height="320"></canvas><div id="circuitOutput" class="status" style="color:var(--text);">Add components to build a series circuit.</div></div>`;
  const components = []; const canvas = document.getElementById('circuitCanvas'); const ctx = canvas.getContext('2d');
  const draw = () => { ctx.clearRect(0,0,900,320); ctx.strokeStyle='#c9d6df'; ctx.lineWidth=4; ctx.beginPath(); ctx.moveTo(110,80); ctx.lineTo(790,80); ctx.lineTo(790,240); ctx.lineTo(110,240); ctx.closePath(); ctx.stroke(); ctx.fillStyle='#f6c453'; ctx.fillRect(55,135,70,50); ctx.fillStyle='#172330'; ctx.fillText(`${batteryInput.value} V`, 70,165); components.forEach((component,index) => { const x=170+index*110; ctx.fillStyle=component.type==='switch' ? (component.closed?'#53c878':'#d06d6d') : '#49a3a2'; ctx.fillRect(x,125,72,70); ctx.fillStyle='#fff'; ctx.fillText(component.type, x+10,163); }); const resistance=components.filter(c=>c.type==='resistor').length*10+components.filter(c=>c.type==='bulb').length*5; const current=resistance ? Number(batteryInput.value)/resistance : 0; circuitOutput.innerText=`${components.length} component(s) · Series resistance ${resistance} Ω · Current ${current.toFixed(2)} A`; circuitList.innerHTML=components.map((component,index)=>`<span class="circuit-chip" data-index="${index}">${component.type}${component.type==='switch' ? (component.closed?' ON':' OFF') : ''}</span>`).join('') || 'No components yet'; document.querySelectorAll('.circuit-chip').forEach(chip=>chip.onclick=()=>{ const item=components[Number(chip.dataset.index)]; if(item.type==='switch') item.closed=!item.closed; draw(); }); }; addComponent.onclick=()=>{ components.push({type:componentSelect.value,closed:false}); draw(); }; batteryInput.oninput=draw; draw();
}

function magneticFieldSimulator() {
  const ctx = canvasFrame('Magnetic Field', '<label>Strength<input id="magStrength" type="range" min="10" max="100" value="65"></label><label>Polarity<select id="magPolarity"><option value="1">North right</option><option value="-1">North left</option></select></label><label>Show field<input id="magShow" type="checkbox" checked></label>', 'magneticCanvas', 'magneticOutput');
  const draw = () => { const strength=Number(magStrength.value), polarity=Number(magPolarity.value); ctx.clearRect(0,0,900,320); ctx.fillStyle=polarity===1?'#d94141':'#4169b1'; ctx.fillRect(330,125,240,70); ctx.fillStyle='#fff'; ctx.font='28px Segoe UI'; ctx.fillText(polarity===1?'S':'N',350,170); ctx.fillStyle='#fff'; ctx.fillText(polarity===1?'N':'S',530,170); if(magShow.checked){ ctx.strokeStyle=`rgba(73,163,162,${strength/140})`; for(let i=0;i<7;i++){ctx.beginPath();ctx.ellipse(450,160,120+i*35,40+i*18,0,0,Math.PI*2);ctx.stroke();} } magneticOutput.innerText=`Field strength: ${strength}% · Polarity: ${polarity===1?'N → right':'N → left'}`; }; [magStrength,magPolarity,magShow].forEach(input=>input.oninput=draw); draw();
}

function functionGrapherSimulator() {
  const ctx = canvasFrame('Function Grapher', '<label>Function<select id="graphFunction"><option value="quadratic">y = x²</option><option value="sine">y = sin(x)</option><option value="line">y = 2x + 1</option></select></label><label>Scale<input id="graphScale" type="range" min="20" max="60" value="40"></label>', 'graphCanvas', 'graphOutput');
  const draw=()=>{const scale=Number(graphScale.value);ctx.clearRect(0,0,900,320);ctx.strokeStyle='#91aabd';ctx.beginPath();ctx.moveTo(450,10);ctx.lineTo(450,310);ctx.moveTo(10,160);ctx.lineTo(890,160);ctx.stroke();ctx.strokeStyle='#49a3a2';ctx.lineWidth=3;ctx.beginPath();for(let px=0;px<900;px++){const x=(px-450)/scale;const y=graphFunction.value==='sine'?Math.sin(x):graphFunction.value==='line'?2*x+1:x*x;const py=160-y*scale/4;px?ctx.lineTo(px,py):ctx.moveTo(px,py);}ctx.stroke();graphOutput.innerText=`Showing ${graphFunction.value} across the current viewport.`;};[graphFunction,graphScale].forEach(input=>input.oninput=draw);draw();
}

function genericVisualSimulator(name) {
  const ctx = canvasFrame(name, '<label>Parameter<input id="genericParam" type="range" min="0" max="100" value="50"></label><label>View<select id="genericView"><option>Simulation</option><option>Model</option></select></label><label>Play<input id="genericPlay" type="checkbox" checked></label>', 'genericCanvas', 'genericOutput');
  const draw=()=>{const value=Number(genericParam.value);const lower=name.toLowerCase();ctx.clearRect(0,0,900,320);ctx.fillStyle='#49a3a2';ctx.strokeStyle='#9dc6d7';ctx.lineWidth=2;if(lower.includes('wave')||lower.includes('oscill')){ctx.beginPath();for(let x=0;x<900;x++){const y=160+Math.sin(x/35+value/18)*70;x?ctx.lineTo(x,y):ctx.moveTo(x,y);}ctx.stroke();}else if(lower.includes('molecule')||lower.includes('bond')||lower.includes('atom')){const points=[[390,145],[510,145],[450,220]];ctx.strokeStyle='#d5e8f2';points.forEach((point,index)=>{if(index){ctx.beginPath();ctx.moveTo(points[0][0],points[0][1]);ctx.lineTo(point[0],point[1]);ctx.stroke();}ctx.fillStyle=index===0?'#49a3a2':'#e8a45b';ctx.beginPath();ctx.arc(point[0],point[1],28+value/12,0,Math.PI*2);ctx.fill();});}else if(lower.includes('graph')||lower.includes('function')||lower.includes('equation')||lower.includes('geometry')){ctx.strokeStyle='#9dc6d7';ctx.beginPath();ctx.moveTo(450,20);ctx.lineTo(450,300);ctx.moveTo(30,160);ctx.lineTo(870,160);ctx.stroke();ctx.strokeStyle='#49a3a2';ctx.beginPath();for(let x=0;x<900;x++){const scaled=(x-450)/45;const y=160-Math.sin(scaled*(1+value/100))*65;x?ctx.lineTo(x,y):ctx.moveTo(x,y);}ctx.stroke();}else{for(let i=0;i<8;i++){ctx.beginPath();ctx.arc(90+i*105,160+Math.sin(i+value/20)*45,16+value/10,0,Math.PI*2);ctx.fill();}}genericOutput.innerText=`${name} interactive model · Parameter ${value}% · ${genericPlay.checked?'running':'paused'}`;};[genericParam,genericView,genericPlay].forEach(input=>input.oninput=draw);draw();
}

function projectileMotionSimulator() {
  document.getElementById('appView').innerHTML = `
    <div class="card">
      <h3>Projectile Motion Simulator</h3>
      <label>Initial velocity (m/s)</label>
      <input id="projVel" value="20" class="mb" /><br>
      <label>Launch angle (deg)</label>
      <input id="projAngle" value="45" class="mb" /><br>
      <button class="primary" id="projBtn">Calculate</button>
      <div id="projOut" class="status" style="color: var(--text);">Results will appear here.</div>
    </div>
  `;

  document.getElementById('projBtn').onclick = () => {
    const u = Number(document.getElementById('projVel').value || 0);
    const a = Number(document.getElementById('projAngle').value || 0);
    const rad = a * Math.PI / 180;
    const g = 9.81;
    const time = (2 * u * Math.sin(rad)) / g;
    const range = (u * u * Math.sin(2 * rad)) / g;
    const maxHeight = (u * u * Math.sin(rad) ** 2) / (2 * g);
    document.getElementById('projOut').innerHTML = `Time: ${time.toFixed(2)} s<br>Range: ${range.toFixed(2)} m<br>Max height: ${maxHeight.toFixed(2)} m`;
  };
}

function ohmsLawSimulator() {
  document.getElementById('appView').innerHTML = `
    <div class="card">
      <h3>Ohm's Law Simulator</h3>
      <label>Voltage (V)</label>
      <input id="volt" value="12" class="mb" /><br>
      <label>Resistance (Ω)</label>
      <input id="res" value="4" class="mb" /><br>
      <button class="primary" id="ohmBtn">Calculate current</button>
      <div id="ohmOut" class="status" style="color: var(--text);">Current will appear here.</div>
    </div>
  `;

  document.getElementById('ohmBtn').onclick = () => {
    const v = Number(document.getElementById('volt').value || 0);
    const r = Number(document.getElementById('res').value || 0);
    const i = r === 0 ? 0 : v / r;
    document.getElementById('ohmOut').innerHTML = `Current I = ${i.toFixed(3)} A`;
  };
}

function quadraticEquationSimulator() {
  document.getElementById('appView').innerHTML = `
    <div class="card">
      <h3>Quadratic Equation Simulator</h3>
      <label>a</label>
      <input id="qa" value="1" class="mb" /><br>
      <label>b</label>
      <input id="qb" value="-3" class="mb" /><br>
      <label>c</label>
      <input id="qc" value="2" class="mb" /><br>
      <button class="primary" id="quadBtn">Solve</button>
      <div id="quadOut" class="status" style="color: var(--text);">Roots will appear here.</div>
    </div>
  `;

  document.getElementById('quadBtn').onclick = () => {
    const a = Number(document.getElementById('qa').value || 0);
    const b = Number(document.getElementById('qb').value || 0);
    const c = Number(document.getElementById('qc').value || 0);
    const d = b * b - 4 * a * c;
    if (d < 0) {
      document.getElementById('quadOut').innerHTML = 'No real roots.';
      return;
    }
    const r1 = (-b + Math.sqrt(d)) / (2 * a);
    const r2 = (-b - Math.sqrt(d)) / (2 * a);
    document.getElementById('quadOut').innerHTML = `x₁ = ${r1.toFixed(3)}<br>x₂ = ${r2.toFixed(3)}`;
  };
}

function molaritySimulator() {
  document.getElementById('appView').innerHTML = `
    <div class="card">
      <h3>Molarity Simulator</h3>
      <label>Moles</label>
      <input id="moles" value="2" class="mb" /><br>
      <label>Volume (L)</label>
      <input id="vol" value="1" class="mb" /><br>
      <button class="primary" id="molarBtn">Calculate molarity</button>
      <div id="molarOut" class="status" style="color: var(--text);">Molarity will appear here.</div>
    </div>
  `;

  document.getElementById('molarBtn').onclick = () => {
    const n = Number(document.getElementById('moles').value || 0);
    const v = Number(document.getElementById('vol').value || 0);
    const molarity = v === 0 ? 0 : n / v;
    document.getElementById('molarOut').innerHTML = `Molarity = ${molarity.toFixed(3)} mol/L`;
  };
}

function circuitHelperSimulator() {
  document.getElementById('appView').innerHTML = `
    <div class="card">
      <h3>Circuit Helper</h3>
      <label>Resistors (comma separated)</label>
      <input id="rlist" value="10,20,30" class="mb" /><br>
      <button class="primary" id="circuitBtn">Calculate</button>
      <div id="circuitOut" class="status" style="color: var(--text);">Series and parallel results here.</div>
    </div>
  `;

  document.getElementById('circuitBtn').onclick = () => {
    const vals = (document.getElementById('rlist').value || '').split(',').map(v => Number(v.trim())).filter(v => !Number.isNaN(v));
    const series = vals.reduce((a, b) => a + b, 0);
    const parallel = vals.length ? 1 / vals.reduce((a, b) => a + (1 / b), 0) : 0;
    document.getElementById('circuitOut').innerHTML = `Series = ${series.toFixed(2)} Ω<br>Parallel = ${parallel.toFixed(2)} Ω`;
  };
}

function matrixToolSimulator() {
  document.getElementById('appView').innerHTML = `
    <div class="card">
      <h3>Matrix Tool</h3>
      <label>2x2 matrix as a,b;c,d</label>
      <input id="matrixInput" value="1,2;3,4" class="mb" /><br>
      <button class="primary" id="matrixBtn">Find determinant</button>
      <div id="matrixOut" class="status" style="color: var(--text);">Determinant will appear here.</div>
    </div>
  `;

  document.getElementById('matrixBtn').onclick = () => {
    const text = document.getElementById('matrixInput').value || '1,2;3,4';
    const rows = text.split(';').map(row => row.split(',').map(v => Number(v.trim())));
    if (rows.length !== 2 || rows[0].length !== 2 || rows[1].length !== 2) {
      document.getElementById('matrixOut').innerHTML = 'Use 2x2 matrix format: a,b;c,d';
      return;
    }
    const det = rows[0][0] * rows[1][1] - rows[0][1] * rows[1][0];
    document.getElementById('matrixOut').innerHTML = `Determinant = ${det}`;
  };
}

function showDrawer(title, body) {
  const drawer = document.getElementById('drawer');
  drawer.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center;"><h2>${title}</h2><button class="primary" id="closeDrawer">Close</button></div>${body}`;
  drawer.hidden = false;
  document.getElementById('closeDrawer').onclick = () => { drawer.hidden = true; };
}

async function showKnowledge() {
  const response = await fetch('/api/knowledge/search?q=' + encodeURIComponent(document.getElementById('searchInput').value));
  const data = await response.json();
  showDrawer('Knowledge package', `<p>${knowledgeSummary.topics} topics, ${knowledgeSummary.formulas} formulas, ${knowledgeSummary.facts} facts.</p>${data.results.map(item => `<article class="formula-box"><strong>${item.subject}: ${item.title}</strong><p>${item.summary}</p><div>${item.formulas.join(' | ')}</div></article>`).join('')}`);
}

async function showWebSearch() {
  const query = prompt('Search the internet for:');
  if (!query) return;
  const response = await fetch('/api/web-search?q=' + encodeURIComponent(query));
  const data = await response.json();
  showDrawer('Internet research', data.results.length ? `<article class="formula-box"><strong>AI-ready summary</strong><p>${data.summary.replaceAll('\n', '<br>')}</p></article>` + data.results.map(item => `<article class="formula-box"><a href="${item.url}" target="_blank" rel="noreferrer">${item.title}</a><p>${item.snippet}</p></article>`).join('') : '<p>No results or network unavailable.</p>');
}

async function showFiles() {
  const response = await fetch('/api/files');
  const data = await response.json();
  showDrawer('Project files', data.files.map(item => `<div class="file-row ${item.status === 'error' ? 'error' : ''}"><span>${item.path}</span><span>${item.status}</span></div>`).join(''));
}

async function showDiagnostics() {
  const response = await fetch('/api/diagnostics');
  const data = await response.json();
  showDrawer('Edulab diagnostics', `<p>Scanned ${data.file_count} files. Errors: <strong class="${data.errors ? 'error' : ''}">${data.errors}</strong></p><p>${data.note}</p>${data.files.map(item => `<div class="file-row ${item.status === 'error' ? 'error' : ''}"><span>${item.path}</span><span>${item.detail || item.status}</span></div>`).join('')}`);
}

async function showSettings() {
  const drive = await fetch('/api/google-drive').then(response => response.json());
  showDrawer('Workspace settings', `<div class="setting-row"><span><strong>Appearance</strong><small>Choose the reading contrast for the whole workspace.</small></span><select id="themeSetting"><option value="light">Light</option><option value="dark">Dark</option></select></div><div class="setting-row"><span><strong>Accent colour</strong><small>Used for buttons and active controls.</small></span><input id="accentSetting" type="color" value="${initialSettings.accent}"></div><div class="setting-row"><span><strong>Internet tutor context</strong><small>Allow the tutor to add live web results.</small></span><input id="webSetting" type="checkbox" ${initialSettings.web_search ? 'checked' : ''}></div><div class="formula-box"><strong>File explorer</strong><p>Inspect project files and Python syntax status.</p><button class="primary" id="filesSetting">Open file explorer</button></div><div class="formula-box"><strong>Google Drive</strong><p>${drive.connected ? 'Connected and ready to save study files.' : drive.configured ? 'OAuth client found. Connect to authorize this device.' : 'Optional. Add data/google_client_secret.json to enable Drive sync.'}</p><button class="primary" id="driveBtn">${drive.connected ? 'Drive connected' : 'Connect Google Drive'}</button></div><div class="toolbar"><button class="primary" id="saveSettings">Save settings</button><button class="chip" id="closeSettings">Cancel</button></div>`);
  document.getElementById('themeSetting').value = initialSettings.theme;
  document.getElementById('driveBtn').onclick = async () => { const result = await fetch('/api/google-drive/connect', {method: 'POST'}); const data = await result.json(); document.getElementById('driveBtn').innerText = data.connected ? 'Drive connected' : (data.error || 'Connect failed'); };
  document.getElementById('filesSetting').onclick = showFiles;
  document.getElementById('closeSettings').onclick = () => { document.getElementById('drawer').hidden = true; };
  document.getElementById('saveSettings').onclick = async () => {
    const settings = { theme: document.getElementById('themeSetting').value, accent: document.getElementById('accentSetting').value, web_search: document.getElementById('webSetting').checked };
    await fetch('/api/settings', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(settings) });
    applySettings(settings);
    document.getElementById('drawer').hidden = true;
  };
}

function applySettings(settings) {
  document.documentElement.style.setProperty('--primary', settings.accent || '#2d7dd2');
  document.body.classList.toggle('dark', settings.theme === 'dark');
}

async function reloadApplication() {
  document.getElementById('appView').innerHTML = '<div class="card"><h3>Reloading data...</h3></div>';
  await fetch('/api/reload', { method: 'POST' });
  window.location.reload();
}

function renderFormulaSheet() {
  const sections = Object.entries(formulaSheet).map(([section, formulas]) => `
    <div class="card mb">
      <h3>${section}</h3>
      ${Object.entries(formulas).map(([k, v]) => `<div class="formula-box"><strong>${k}:</strong> ${v}</div>`).join('')}
    </div>
  `).join('');
  document.getElementById('appView').innerHTML = sections;
}

function renderChat() {
  document.getElementById('appView').innerHTML = `
    <div class="chatbox">
      <h3>EduCore AI Tutor</h3>
      <p class="muted">Context-aware tutoring with knowledge retrieval, simulator state, and optional web research.</p>
      <div class="tabs"><button class="tab active tutor-mode" data-mode="explain">Explain</button><button class="tab tutor-mode" data-mode="summarize">Summarize</button><button class="tab tutor-mode" data-mode="solve">Solve</button></div>
      <textarea id="chatInput" rows="4" placeholder="Ask about a simulator, formula, code, or image..."></textarea>
      <input id="chatImage" type="file" accept="image/*" class="mb">
      <div style="margin-top: 12px; display: flex; gap: 10px;">
        <button class="primary" id="sendChat">Ask EduCore</button>
        <button class="chip" id="generateImage">Generate image</button>
      </div>
      <div id="chatOutput" class="status" style="color: var(--text);">Tutor ready.</div>
    </div>
  `;
  let tutorMode = 'explain';
  document.querySelectorAll('.tutor-mode').forEach((button) => { button.onclick = () => { tutorMode = button.dataset.mode; document.querySelectorAll('.tutor-mode').forEach(item => item.classList.toggle('active', item === button)); }; });
  document.getElementById('sendChat').onclick = async () => {
    const q = document.getElementById('chatInput').value.trim();
    if (!q) return;
    document.getElementById('chatOutput').innerText = 'Thinking...';
    const res = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: q, mode: tutorMode, context: { currentPage: 'Home', currentSubject: state.subject } }) });
    const data = await res.json();
    document.getElementById('chatOutput').innerText = data.reply || 'No response.';
  };
  document.getElementById('chatImage').onchange = async () => {
    const file = document.getElementById('chatImage').files[0];
    if (!file) return;
    const body = new FormData(); body.append('image', file); body.append('prompt', document.getElementById('chatInput').value || 'Read this educational image.');
    document.getElementById('chatOutput').innerText = 'Reading image...';
    const response = await fetch('/api/image/inspect', {method:'POST', body});
    const data = await response.json();
    document.getElementById('chatOutput').innerText = data.description || data.error || 'Image service unavailable.';
  };
  document.getElementById('generateImage').onclick = async () => {
    const prompt = document.getElementById('chatInput').value.trim();
    if (!prompt) return;
    const response = await fetch('/api/image/generate', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({prompt})});
    const data = await response.json();
    document.getElementById('chatOutput').innerText = data.error || JSON.stringify(data.result || data);
  };
}

function renderCodeCompiler() {
  document.getElementById('appView').innerHTML = `
    <div class="card">
      <div class="rail-title"><h3>EduCode runner</h3><span class="pill">EduEngine</span></div>
      <select id="langSelect" class="mb">
        <option value="python">Python</option>
        <option value="html">HTML</option>
        <option value="javascript">JavaScript</option>
        <option value="c">C</option>
        <option value="cpp">C++</option>
        <option value="java">Java</option>
      </select>
      <textarea id="codeInput" rows="14" spellcheck="false"></textarea>
      <div style="margin-top: 12px; display: flex; gap: 10px; flex-wrap: wrap;">
        <button class="primary" id="runCode">Run</button>
        <button class="primary" id="explainCode">Explain code</button>
        <button class="chip" id="analyzeCode">Find exact mistake</button>
      </div>
      <pre id="codeOutput" style="margin-top: 12px; background:#111827; color:#e5f2ff; border-radius:12px; padding: 14px; white-space: pre-wrap; overflow-wrap: anywhere; min-height: 80px;">Output will appear here.</pre>
    </div>
  `;
  const loadTemplate = async () => {
    const response = await fetch('/api/code/template?language=' + encodeURIComponent(document.getElementById('langSelect').value));
    document.getElementById('codeInput').value = (await response.json()).template || '';
  };
  document.getElementById('langSelect').onchange = loadTemplate;
  loadTemplate();
  document.getElementById('runCode').onclick = async () => {
    const code = document.getElementById('codeInput').value;
    const lang = document.getElementById('langSelect').value;
    const res = await fetch('/api/compile', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ code, lang }) });
    const data = await res.json();
    document.getElementById('codeOutput').innerText = data.output || 'No output.';
  };
  document.getElementById('explainCode').onclick = async () => {
    const code = document.getElementById('codeInput').value;
    const language = document.getElementById('langSelect').value;
    const res = await fetch('/api/code/explain', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({code, language}) });
    document.getElementById('codeOutput').innerText = (await res.json()).explanation;
  };
  document.getElementById('analyzeCode').onclick = async () => {
    const code = document.getElementById('codeInput').value;
    const language = document.getElementById('langSelect').value;
    const res = await fetch('/api/code/analyze', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({code, language}) });
    const data = await res.json();
    const location = data.line ? `Line ${data.line}${data.column ? `, column ${data.column}` : ''}` : 'No exact line reported';
    document.getElementById('codeOutput').innerText = data.error ? `${location}: ${data.error}\n\n${(data.hints || []).join('\n')}\n\nBuilt-ins: ${(data.library?.builtins || []).join(', ')}\nLibraries: ${(data.library?.libraries || []).join(', ')}` : `No syntax mistake found.\n\nBuilt-ins: ${(data.library?.builtins || []).join(', ')}\nLibraries: ${(data.library?.libraries || []).join(', ')}`;
  };
}

function renderScientificCalculator() {
  document.getElementById('appView').innerHTML = `<div class="card"><h3>Scientific calculator</h3><p class="muted">Use sin, cos, tan, log, ln, sqrt, pi, and standard arithmetic.</p><input id="calcExpression" placeholder="sin(pi / 2) + sqrt(16)" class="mb"><div class="calculator-grid">${['7','8','9','/','4','5','6','*','1','2','3','-','0','.','(',')','sin(','cos(','sqrt(','+'].map(value => `<button class="chip calc-key" data-value="${value}">${value}</button>`).join('')}</div><div class="toolbar"><button class="primary" id="calculateExpression">Calculate</button><button class="chip" id="clearExpression">Clear</button></div><pre id="calculatorOutput" class="formula-box">Enter an expression.</pre></div>`;
  const expression = document.getElementById('calcExpression');
  document.querySelectorAll('.calc-key').forEach(button => button.onclick = () => { expression.value += button.dataset.value; expression.focus(); });
  document.getElementById('clearExpression').onclick = () => { expression.value = ''; document.getElementById('calculatorOutput').innerText = 'Enter an expression.'; };
  document.getElementById('calculateExpression').onclick = async () => { const response = await fetch('/api/calculator', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({expression: expression.value})}); const data = await response.json(); document.getElementById('calculatorOutput').innerText = data.error || `Result: ${data.result}`; };
}

function attachEvents() {
  const searchInput = document.getElementById('searchInput');
  searchInput.addEventListener('input', () => { state.page = 1; renderHome(); });
  searchInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      showKnowledge();
    }
  });
  document.querySelectorAll('.subject-btn').forEach((btn) => {
    btn.onclick = () => {
      document.querySelectorAll('.subject-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.subject = btn.dataset.subject;
      state.page = 1;
      renderTabs();
      renderHome();
    };
  });
  document.querySelectorAll('.subject-card[data-subject]').forEach((btn) => {
    btn.onclick = () => {
      state.subject = btn.dataset.subject;
      state.page = 1;
      document.querySelectorAll('.subject-btn').forEach(b => b.classList.toggle('active', b.dataset.subject === state.subject || (state.subject === 'all' && b.dataset.subject === 'all')));
      renderTabs();
      renderHome();
    };
  });

  document.getElementById('formulaBtn').onclick = renderFormulaSheet;
  document.getElementById('chatBtn').onclick = () => { window.location.href = '/ai'; };
  document.getElementById('codeBtn').onclick = () => { window.location.href = '/coding'; };
  document.getElementById('knowledgeSearchBtn').onclick = showKnowledge;
  document.getElementById('webSearchBtn').onclick = showWebSearch;
  document.getElementById('calculatorBtn').onclick = renderScientificCalculator;
  document.getElementById('simulatorsBtn').onclick = () => { window.location.href = '/simulators'; };
  const debugButton = document.getElementById('debugBtn');
  if (debugButton) debugButton.onclick = showDiagnostics;
  document.getElementById('settingsBtn').onclick = () => { window.location.href = '/settings'; };
  document.getElementById('openTutor')?.addEventListener('click', renderChat);
  document.getElementById('aiHome').onclick = renderChat;
  document.getElementById('codingHome').onclick = renderCodeCompiler;
  document.getElementById('calculatorHome').onclick = renderScientificCalculator;
  document.addEventListener('keydown', (event) => {
    if (event.ctrlKey && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      const field = document.getElementById('searchInput');
      if (field) {
        field.focus();
        field.select();
      }
    }
    if (event.ctrlKey && event.altKey && event.code === 'Space') {
      event.preventDefault();
      window.__edulabReloadArmed = true;
    }
    if (event.ctrlKey && event.altKey && event.key.toLowerCase() === 'r' && window.__edulabReloadArmed) {
      event.preventDefault();
      window.__edulabReloadArmed = false;
      reloadApplication();
    }
    if (event.ctrlKey && event.altKey && event.key === 'Insert') {
      event.preventDefault();
      showDiagnostics();
    }
  });
}

function updateClock() {
  const now = new Date();
  document.getElementById('clock').innerText = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

updateClock();
setInterval(updateClock, 30000);
applySettings(initialSettings);
renderTabs();
renderSimulators();
attachEvents();
if (initialPage === 'coding') renderCodeCompiler();
if (initialPage === 'ai') renderChat();
if (initialPage === 'simulators') openSimulatorLibrary();
if (initialPage === 'settings') showSettings();
</script>
</body>
</html>
"""


def render_page(page="home"):
  return render_template_string(
    HTML_TEMPLATE,
    catalog=SIMULATOR_CATALOG,
    formula_sheet=FORMULA_SHEET,
    settings=load_settings(),
    knowledge_summary=get_store_summary(),
    app_version=APP_VERSION,
    initial_page=page,
  )


@app.route("/")
def home():
  return render_page("home")


@app.route("/coding")
def coding_page():
  return render_page("coding")


@app.route("/simulators")
def simulators_page():
  return render_page("simulators")


@app.route("/ai")
def ai_page():
  return render_page("ai")


@app.route("/settings")
def settings_page():
  return render_page("settings")


@app.get("/api/knowledge/search")
def api_knowledge_search():
  return jsonify({"results": search_topics(request.args.get("q", ""), request.args.get("subject", "all"))})


@app.get("/api/web-search")
def api_web_search():
  query = request.args.get("q", "")
  results = search_web(query)
  return jsonify({"query": query, "results": results, "summary": summarize_results(query, results)})


@app.get("/api/settings")
def api_get_settings():
  return jsonify(load_settings())


@app.get("/api/code/template")
def api_code_template():
  return jsonify({"language": request.args.get("language", "python"), "template": language_template(request.args.get("language", "python"))})


@app.post("/api/settings")
def api_save_settings():
  changes = request.get_json(silent=True) or {}
  allowed = {key: value for key, value in changes.items() if key in load_settings()}
  return jsonify(update_settings(allowed))


@app.get("/api/google-drive")
def api_google_drive():
  return jsonify(integration_status())


@app.post("/api/google-drive/connect")
def api_google_drive_connect():
  try:
    return jsonify(authorization_url())
  except (RuntimeError, OSError, ValueError) as exc:
    return jsonify({"connected": False, "error": str(exc)}), 400


@app.post("/api/google-drive/upload")
def api_google_drive_upload():
  try:
    data = request.get_json(silent=True) or {}
    return jsonify(upload_text(data.get("filename", "edulab-note.txt"), data.get("content", ""), data.get("folder_id")))
  except (RuntimeError, OSError, ValueError) as exc:
    return jsonify({"error": str(exc)}), 400


@app.get("/api/files")
def api_files():
  return jsonify({"files": scan_project()})


@app.get("/api/diagnostics")
def api_diagnostics():
  return jsonify(get_diagnostics())


@app.post("/api/reload")
def api_reload():
  # Reload means rebuilding the persisted data view and returning fresh diagnostics.
  return jsonify({"ok": True, "diagnostics": get_diagnostics()})


@app.post("/api/user-data")
def api_user_data():
  changes = request.get_json(silent=True) or {}
  return jsonify(store_user_data({key: changes[key] for key in ("notes", "saved_files") if key in changes}))


@app.post("/api/code/explain")
def api_code_explain():
  data = request.get_json(silent=True) or {}
  return jsonify({"explanation": explain_code(data.get("code", ""), data.get("language", "python"))})


@app.post("/api/code/analyze")
def api_code_analyze():
  data = request.get_json(silent=True) or {}
  return jsonify(analyze_code(data.get("code", ""), data.get("language", "python")))


@app.post("/api/calculator")
def api_calculator():
  try:
    data = request.get_json(silent=True) or {}
    return jsonify({"result": evaluate_expression(data.get("expression", ""))})
  except (TypeError, ValueError, ZeroDivisionError) as exc:
    return jsonify({"error": str(exc)}), 400


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"reply": "Ask me anything about your study topics."})
    chatbot = RAGChatbot(flatten_simulators())
    return jsonify({"reply": chatbot.generate_response(message, include_web_search=load_settings().get("web_search", True), app_context=data.get("context", {}), mode=data.get("mode", "explain"))})


@app.post("/api/image/inspect")
def api_image_inspect():
    image = request.files.get("image")
    if image is None:
        return jsonify({"error": "Upload an image first."}), 400
    suffix = Path(image.filename or ".png").suffix or ".png"
    path = Path(tempfile.gettempdir()) / f"edulab-image-{uuid.uuid4().hex}{suffix}"
    try:
        image.save(path)
        return jsonify(inspect_image(path, request.form.get("prompt", "Read this educational image.")))
    except Exception as exc:
        return jsonify({"error": f"Image reading unavailable: {exc}"}), 400
    finally:
        path.unlink(missing_ok=True)


@app.post("/api/image/generate")
def api_image_generate():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify({"result": generate_image(data.get("prompt", ""), data.get("size", "1024x1024"))})
    except (RuntimeError, OSError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/compile", methods=["POST"])
def api_compile():
    try:
        data = request.get_json(silent=True) or {}
        code = data.get("code", "")
        lang = data.get("lang", "python")
        return jsonify(run_code(code, lang))
    except (SyntaxError, ValueError, OSError, TimeoutError, subprocess.TimeoutExpired) as exc:
        return jsonify({"output": f"Execution error: {exc}", "status": "error"}), 400


def start_web_app(host="0.0.0.0", port=5000):
    import webbrowser
    threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    start_web_app()
