/**
 * Career Guidance System – Main Script
 * Handles quiz logic, career matching, browsing, and modal display.
 */

'use strict';

// ─── State ────────────────────────────────────────────────────────────────────
const state = {
  careers: [],
  questions: [],
  currentQuestion: 0,
  answers: [],        // array of selected category arrays per question
  activeFilter: 'all',
  searchQuery: '',
};

// ─── DOM helpers ──────────────────────────────────────────────────────────────
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

// ─── Navigation ───────────────────────────────────────────────────────────────
function showSection(id) {
  $$('section[data-section]').forEach(s => s.classList.remove('active'));
  $$('nav a').forEach(a => a.classList.remove('active'));

  const section = $(`[data-section="${id}"]`);
  if (section) section.classList.add('active');

  const navLink = $(`nav a[data-target="${id}"]`);
  if (navLink) navLink.classList.add('active');
}

// ─── Data Loading ─────────────────────────────────────────────────────────────
async function loadData() {
  try {
    const res = await fetch('data/careers.json');
    if (!res.ok) throw new Error('Failed to load career data');
    const data = await res.json();
    state.careers = data.careers;
    state.questions = data.questions;
    initApp();
  } catch (err) {
    console.error(err);
    document.body.innerHTML =
      '<p style="text-align:center;padding:3rem;color:#ef4444;">Failed to load career data. Please refresh the page.</p>';
  }
}

// ─── Initialisation ───────────────────────────────────────────────────────────
function initApp() {
  renderCareersGrid();
  bindNavigation();
  bindQuizStart();
  bindFilterButtons();
  bindSearch();
  bindModalClose();
  showSection('home');
}

// ─── Navigation bindings ──────────────────────────────────────────────────────
function bindNavigation() {
  $$('nav a[data-target]').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      showSection(link.dataset.target);
    });
  });

  // CTA buttons
  $$('[data-nav]').forEach(btn => {
    btn.addEventListener('click', () => showSection(btn.dataset.nav));
  });
}

// ─── Quiz ─────────────────────────────────────────────────────────────────────
function bindQuizStart() {
  const startBtn = $('#start-quiz-btn');
  if (startBtn) startBtn.addEventListener('click', startQuiz);
}

function startQuiz() {
  state.currentQuestion = 0;
  state.answers = [];
  showSection('quiz');
  renderQuestion();
}

function renderQuestion() {
  const { questions, currentQuestion } = state;
  const q = questions[currentQuestion];
  const total = questions.length;
  const quizContainer = $('#quiz-container');

  const progressPct = Math.round((currentQuestion / total) * 100);

  quizContainer.innerHTML = `
    <div class="quiz-wrapper">
      <p class="progress-label">Question ${currentQuestion + 1} of ${total}</p>
      <div class="progress-bar">
        <div class="progress-fill" style="width: ${progressPct}%"></div>
      </div>
      <div class="question-card">
        <h3>${escapeHtml(q.text)}</h3>
        <div class="options">
          ${q.options.map((opt, i) => `
            <button class="option-btn" data-index="${i}">
              ${escapeHtml(opt.label)}
            </button>
          `).join('')}
        </div>
        <div class="quiz-nav mt-2">
          <button class="btn btn-outline" id="prev-btn" ${currentQuestion === 0 ? 'disabled style="visibility:hidden"' : ''}>← Back</button>
          <button class="btn btn-primary" id="next-btn" disabled>Next →</button>
        </div>
      </div>
    </div>
  `;

  // Highlight previously selected answer if returning to this question
  if (state.answers[currentQuestion] !== undefined) {
    const savedIndex = state.answers[currentQuestion].index;
    const btns = $$('.option-btn', quizContainer);
    btns[savedIndex].classList.add('selected');
    $('#next-btn').disabled = false;
  }

  // Option selection
  $$('.option-btn', quizContainer).forEach(btn => {
    btn.addEventListener('click', () => {
      $$('.option-btn', quizContainer).forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      const idx = parseInt(btn.dataset.index, 10);
      state.answers[currentQuestion] = {
        index: idx,
        categories: q.options[idx].categories,
      };
      $('#next-btn').disabled = false;
    });
  });

  // Navigation
  const nextBtn = $('#next-btn');
  const prevBtn = $('#prev-btn');

  nextBtn.addEventListener('click', () => {
    if (state.currentQuestion < total - 1) {
      state.currentQuestion++;
      renderQuestion();
    } else {
      computeResults();
    }
  });

  if (prevBtn && !prevBtn.disabled) {
    prevBtn.addEventListener('click', () => {
      if (state.currentQuestion > 0) {
        state.currentQuestion--;
        renderQuestion();
      }
    });
  }
}

// ─── Results ──────────────────────────────────────────────────────────────────
function computeResults() {
  // Tally category scores
  const scores = {};
  state.answers.forEach(answer => {
    if (!answer) return;
    answer.categories.forEach(cat => {
      scores[cat] = (scores[cat] || 0) + 1;
    });
  });

  // Score each career
  const scored = state.careers.map(career => {
    let score = 0;
    career.categories.forEach(cat => {
      score += scores[cat] || 0;
    });
    return { career, score };
  });

  // Sort descending, take top 3
  scored.sort((a, b) => b.score - a.score);
  const maxScore = scored[0].score || 1;
  const top = scored.slice(0, 3);

  renderResults(top, maxScore);
}

function renderResults(top, maxScore) {
  showSection('results');
  const container = $('#results-container');

  container.innerHTML = `
    <div class="results-header">
      <h2>🎯 Your Career Matches</h2>
      <p>Based on your answers, here are the best-fit careers for you.</p>
    </div>
    <div class="career-results">
      ${top.map((item, i) => renderResultCard(item, i, maxScore)).join('')}
    </div>
    <div class="text-center mt-3">
      <button class="btn btn-outline" id="retake-quiz-btn">Retake Quiz</button>
      &nbsp;
      <button class="btn btn-primary" data-nav="careers">Browse All Careers →</button>
    </div>
  `;

  // Bind the buttons rendered inside the container
  $$('[data-nav]', container).forEach(btn => {
    btn.addEventListener('click', () => showSection(btn.dataset.nav));
  });

  const retakeBtn = $('#retake-quiz-btn', container);
  if (retakeBtn) retakeBtn.addEventListener('click', startQuiz);
}

function renderResultCard({ career, score }, index, maxScore) {
  const pct = Math.round((score / maxScore) * 100);
  const isTop = index === 0;

  return `
    <div class="career-result-card ${isTop ? 'top-match' : ''}">
      ${isTop ? '<span class="top-badge">⭐ Best Match</span>' : ''}
      <h3>${escapeHtml(career.title)}</h3>
      <div class="match-score">
        <div class="score-bar-bg">
          <div class="score-bar-fill" style="width:${pct}%"></div>
        </div>
        <span class="score-label">${pct}%</span>
      </div>
      <div class="career-meta">
        <span class="meta-tag">💰 ${escapeHtml(career.salaryRange)}</span>
        <span class="meta-tag">📈 ${escapeHtml(career.jobGrowth)}</span>
      </div>
      <p class="desc">${escapeHtml(career.description)}</p>
      <p class="meta-tag" style="margin-bottom:0.75rem">🎓 ${escapeHtml(career.education)}</p>
      <div class="skills-list">
        ${career.skills.map(s => `<span class="skill-tag">${escapeHtml(s)}</span>`).join('')}
      </div>
      <p style="font-size:0.8rem;color:var(--text-muted);margin:0.75rem 0 0.5rem;font-weight:600;">📚 Resources</p>
      <div class="resources-list">
        ${career.resources.map(r =>
          `<a class="resource-link" href="${escapeHtml(r.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(r.name)}</a>`
        ).join('')}
      </div>
    </div>
  `;
}

// ─── Careers Browse ───────────────────────────────────────────────────────────
function renderCareersGrid() {
  const grid = $('#careers-grid');
  if (!grid) return;

  const query = state.searchQuery.toLowerCase();
  const filter = state.activeFilter;

  const filtered = state.careers.filter(c => {
    const matchesFilter = filter === 'all' || c.categories.includes(filter);
    const matchesSearch = !query ||
      c.title.toLowerCase().includes(query) ||
      c.description.toLowerCase().includes(query) ||
      c.skills.some(s => s.toLowerCase().includes(query));
    return matchesFilter && matchesSearch;
  });

  if (filtered.length === 0) {
    grid.innerHTML = '<p style="color:var(--text-muted);text-align:center;grid-column:1/-1">No careers match your search.</p>';
    return;
  }

  grid.innerHTML = filtered.map(career => `
    <div class="career-card" data-career-id="${escapeHtml(career.id)}" tabindex="0" role="button" aria-label="View details for ${escapeHtml(career.title)}">
      <div class="category-badges">
        ${career.categories.map(cat =>
          `<span class="category-badge badge-${escapeHtml(cat)}">${escapeHtml(cat)}</span>`
        ).join('')}
      </div>
      <h3>${escapeHtml(career.title)}</h3>
      <p>${escapeHtml(career.description)}</p>
      <button class="btn btn-sm btn-outline">View Details →</button>
    </div>
  `).join('');

  $$('.career-card', grid).forEach(card => {
    const openModal = () => openCareerModal(card.dataset.careerId);
    card.addEventListener('click', openModal);
    card.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openModal();
      }
    });
  });
}

function bindFilterButtons() {
  $$('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      $$('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.activeFilter = btn.dataset.filter;
      renderCareersGrid();
    });
  });
}

function bindSearch() {
  const input = $('#career-search');
  if (!input) return;
  input.addEventListener('input', () => {
    state.searchQuery = input.value;
    renderCareersGrid();
  });
}

// ─── Modal ────────────────────────────────────────────────────────────────────
function openCareerModal(careerId) {
  const career = state.careers.find(c => c.id === careerId);
  if (!career) return;

  const overlay = $('#modal-overlay');
  const body = $('#modal-body');

  body.innerHTML = `
    <div class="category-badges" style="margin-bottom:1rem">
      ${career.categories.map(cat =>
        `<span class="category-badge badge-${escapeHtml(cat)}">${escapeHtml(cat)}</span>`
      ).join('')}
    </div>
    <h2 style="font-size:1.4rem;font-weight:700;margin-bottom:0.75rem">${escapeHtml(career.title)}</h2>
    <p style="color:var(--text-muted);margin-bottom:1.25rem">${escapeHtml(career.description)}</p>
    <div class="career-meta" style="margin-bottom:1.25rem">
      <span class="meta-tag">💰 ${escapeHtml(career.salaryRange)}</span>
      <span class="meta-tag">📈 ${escapeHtml(career.jobGrowth)}</span>
    </div>
    <p style="font-size:0.85rem;font-weight:600;margin-bottom:0.5rem">🎓 Education</p>
    <p style="font-size:0.9rem;color:var(--text-muted);margin-bottom:1.25rem">${escapeHtml(career.education)}</p>
    <p style="font-size:0.85rem;font-weight:600;margin-bottom:0.5rem">🛠 Key Skills</p>
    <div class="skills-list" style="margin-bottom:1.25rem">
      ${career.skills.map(s => `<span class="skill-tag">${escapeHtml(s)}</span>`).join('')}
    </div>
    <p style="font-size:0.85rem;font-weight:600;margin-bottom:0.5rem">📚 Learning Resources</p>
    <div class="resources-list">
      ${career.resources.map(r =>
        `<a class="resource-link" href="${escapeHtml(r.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(r.name)}</a>`
      ).join('')}
    </div>
  `;

  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function bindModalClose() {
  const overlay = $('#modal-overlay');
  const closeBtn = $('#modal-close-btn');

  if (closeBtn) {
    closeBtn.addEventListener('click', closeModal);
  }

  if (overlay) {
    overlay.addEventListener('click', e => {
      if (e.target === overlay) closeModal();
    });
  }

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
  });
}

function closeModal() {
  const overlay = $('#modal-overlay');
  overlay.classList.remove('open');
  document.body.style.overflow = '';
}

// ─── Security helper ──────────────────────────────────────────────────────────
function escapeHtml(str) {
  if (typeof str !== 'string') return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ─── Bootstrap ────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', loadData);
