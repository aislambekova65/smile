'use strict';

// ===== THEME (CSS-driven: data-theme on <html>) =====
const THEME_KEY = 'smile_theme';

function getTheme() {
  return localStorage.getItem(THEME_KEY) ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);
}

function toggleTheme() {
  applyTheme(getTheme() === 'dark' ? 'light' : 'dark');
}

// ===== SCROLL TO TOP =====
function initScrollTop() {
  const btn = document.getElementById('scrollTop');
  if (!btn) return;
  window.addEventListener('scroll', () => btn.classList.toggle('visible', window.scrollY > 350), { passive: true });
  btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

// ===== FADE-UP ANIMATIONS =====
function initFadeUp() {
  const els = document.querySelectorAll('.fade-up');
  if (!els.length) return;
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); } });
  }, { threshold: 0.1 });
  els.forEach(el => obs.observe(el));
}

// ===== NAVBAR ACTIVE LINK =====
function initActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && (path === href || (href !== '/' && path.startsWith(href)))) {
      link.classList.add('active');
    }
  });
}

// ===== AUTO-DISMISS ALERTS =====
function initAlerts() {
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });
}

// ===== COUNTER ANIMATION =====
function animateCounter(el) {
  const target = parseInt(el.dataset.target, 10);
  const suffix = el.dataset.suffix || '';
  let current = 0;
  const step = target / (1500 / 16);
  const timer = setInterval(() => {
    current += step;
    if (current >= target) { el.textContent = target + suffix; clearInterval(timer); }
    else el.textContent = Math.floor(current) + suffix;
  }, 16);
}

function initCounters() {
  const els = document.querySelectorAll('[data-target]');
  if (!els.length) return;
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { animateCounter(e.target); obs.unobserve(e.target); } });
  }, { threshold: 0.5 });
  els.forEach(el => obs.observe(el));
}

// ===== ADMIN FAB MENU =====
function initAdminFab() {
  const btn  = document.getElementById('adminFabBtn');
  const menu = document.getElementById('adminFabMenu');
  if (!btn || !menu) return;

  btn.addEventListener('click', e => {
    e.stopPropagation();
    menu.classList.toggle('open');
  });

  document.addEventListener('click', () => menu.classList.remove('open'));
  menu.addEventListener('click', e => e.stopPropagation());
}

// ===== ADMIN LOGIN MODAL =====
function initAdminLoginModal() {
  const form = document.getElementById('adminLoginForm');
  if (!form) return;

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const btn     = form.querySelector('[type=submit]');
    const errBox  = document.getElementById('adminLoginError');
    const origTxt = btn.innerHTML;

    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Вход…';
    btn.disabled = true;
    if (errBox) errBox.style.display = 'none';

    const data = new FormData(form);
    // Django CSRF token must be in the form
    try {
      const resp = await fetch('/api/login/', { method: 'POST', body: data });
      const json = await resp.json();
      if (json.success) {
        // Close modal and go to admin
        const modal = bootstrap.Modal.getInstance(document.getElementById('adminLoginModal'));
        if (modal) modal.hide();
        window.location.href = '/admin/';
      } else {
        if (errBox) { errBox.textContent = json.error || 'Ошибка входа'; errBox.style.display = 'block'; }
      }
    } catch {
      if (errBox) { errBox.textContent = 'Ошибка сети. Попробуйте снова.'; errBox.style.display = 'block'; }
    }

    btn.innerHTML = origTxt;
    btn.disabled = false;
  });
}

// ===== TIME AVAILABILITY CHECK =====
const BOOKED_MARKER = ' — занято';

function initTimeAvailability() {
  const specialistEl = document.getElementById('id_specialist');
  const dateEl       = document.getElementById('id_preferred_date');
  const timeEl       = document.getElementById('id_preferred_time');
  if (!timeEl) return;

  // Store original options
  const originalOptions = Array.from(timeEl.options).map(o => ({
    value: o.value, text: o.text,
  }));

  async function updateSlots() {
    const specId  = specialistEl ? specialistEl.value : '';
    const dateVal = dateEl ? dateEl.value : '';

    if (!dateVal) return;

    // Show loading
    const info = document.getElementById('time-slot-info');
    if (info) { info.className = 'time-slot-info loading'; info.innerHTML = '<i class="bi bi-arrow-repeat"></i> Проверяем свободное время…'; }

    const params = new URLSearchParams({ date: dateVal });
    if (specId) params.append('specialist_id', specId);

    let booked = [], slots = [], dayOff = false;
    try {
      const resp = await fetch('/api/availability/?' + params.toString());
      const json = await resp.json();
      booked = json.booked || [];
      slots  = json.slots  || [];
      dayOff = json.day_off || false;
    } catch {
      if (info) { info.className = 'time-slot-info'; info.textContent = ''; }
      return;
    }

    // Rebuild options
    const savedVal = timeEl.value;
    timeEl.innerHTML = '';

    // Blank option
    const blank = document.createElement('option');
    blank.value = ''; blank.textContent = '— выберите время —';
    timeEl.appendChild(blank);

    if (dayOff) {
      const offOpt = document.createElement('option');
      offOpt.value = ''; offOpt.textContent = '⛔ Специалист не работает в этот день';
      offOpt.disabled = true;
      timeEl.appendChild(offOpt);
      if (info) { info.className = 'time-slot-info booked'; info.innerHTML = '<i class="bi bi-x-circle"></i> Специалист не работает в этот день'; }
      return;
    }

    if (slots.length === 0) {
      const noOpt = document.createElement('option');
      noOpt.value = ''; noOpt.textContent = 'Нет доступных слотов';
      noOpt.disabled = true;
      timeEl.appendChild(noOpt);
    }

    let freeCount = 0;
    slots.forEach(slot => {
      const opt = document.createElement('option');
      opt.value = slot;
      if (booked.includes(slot)) {
        opt.textContent = slot + BOOKED_MARKER;
        opt.disabled = true;
        opt.className = 'time-booked';
      } else {
        opt.textContent = slot;
        freeCount++;
      }
      timeEl.appendChild(opt);
    });

    // Restore previous value if still free
    if (savedVal && !booked.includes(savedVal)) {
      timeEl.value = savedVal;
    }

    if (info) {
      if (freeCount > 0) {
        info.className = 'time-slot-info free';
        info.innerHTML = `<i class="bi bi-check-circle"></i> Свободно слотов: <strong>${freeCount}</strong>`;
      } else {
        info.className = 'time-slot-info booked';
        info.innerHTML = '<i class="bi bi-x-circle"></i> Все слоты заняты на эту дату';
      }
    }
  }

  if (specialistEl) specialistEl.addEventListener('change', updateSlots);
  if (dateEl) dateEl.addEventListener('change', updateSlots);
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
  // Apply saved theme immediately (also done inline to avoid flash)
  applyTheme(getTheme());

  // Wire theme toggle click + keyboard
  const toggle = document.getElementById('themeToggle');
  if (toggle) {
    toggle.addEventListener('click', toggleTheme);
    toggle.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleTheme(); }
    });
  }

  initScrollTop();
  initFadeUp();
  initActiveNav();
  initAlerts();
  initCounters();
  initAdminFab();
  initAdminLoginModal();
  initTimeAvailability();
});
