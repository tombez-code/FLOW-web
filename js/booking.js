/**
 * Flow School – Custom Booking Widget
 * Replaces Calendly. Posts form to FormSubmit.co → email to info@skolaflow.cz
 * 
 * Usage: <div class="flow-booking" data-email="info@skolaflow.cz"></div>
 *        <script src="../js/booking.js"></script>
 */
(function() {
  'use strict';

  const VISIT_TYPES = [
    { id: 'prohlidka', label: 'Prohlídka školy + káva s ředitelem', days: [4], time: '8:30–10:00',
       calendlyUrl: 'https://calendly.com/skolaflowcz/kafe-s-ridou' },
    { id: 'dod',       label: 'Den otevřených dveří',               days: [1,2,3,4,5], time: 'dle termínu',
       calendlyUrl: 'https://calendly.com/skolaflowcz/zs-flow-den-otevrenych-dveri-2025-26' },
    { id: 'online',    label: 'Online schůzka se zakladatelem',     days: [1,2,3,4,5], time: 'dle dohody' },
    { id: 'zkusebni',  label: 'Zkušební dopoledne pro dítě',        days: [1,2,3,4,5], time: '8:00–12:00' },
  ];

  // Thursday = 4 in JS (0=Sun,1=Mon,...,4=Thu,5=Fri,6=Sat)
  const DAY_NAMES_CS = ['Ne', 'Po', 'Út', 'St', 'Čt', 'Pá', 'So'];
  const MONTH_NAMES_CS = ['Leden','Únor','Březen','Duben','Květen','Červen',
                           'Červenec','Srpen','Září','Říjen','Listopad','Prosinec'];

  function getAvailableDays(year, month, visitTypeDays) {
    const days = [];
    const today = new Date();
    today.setHours(0,0,0,0);
    const daysInMonth = new Date(year, month+1, 0).getDate();
    for (let d = 1; d <= daysInMonth; d++) {
      const date = new Date(year, month, d);
      if (date <= today) continue;
      const dow = date.getDay(); // 0=Sun
      if (visitTypeDays.includes(dow)) days.push(d);
    }
    return days;
  }

  function renderCalendar(container, state) {
    const { year, month, selectedDate, visitType } = state;
    const firstDay = new Date(year, month, 1).getDay();
    const startOffset = firstDay === 0 ? 6 : firstDay - 1; // Monday-based
    const daysInMonth = new Date(year, month+1, 0).getDate();
    const availDays = visitType ? getAvailableDays(year, month, visitType.days) : [];
    const today = new Date(); today.setHours(0,0,0,0);

    let html = `
      <div class="fbw-cal-header">
        <button class="fbw-nav fbw-prev" aria-label="Předchozí měsíc">‹</button>
        <span class="fbw-month-title">${MONTH_NAMES_CS[month]} ${year}</span>
        <button class="fbw-nav fbw-next" aria-label="Další měsíc">›</button>
      </div>
      <div class="fbw-cal-grid">`;

    DAY_NAMES_CS.forEach(d => { html += `<div class="fbw-day-name">${d}</div>`; });

    for (let i = 0; i < startOffset; i++) html += '<div class="fbw-day fbw-empty"></div>';

    for (let d = 1; d <= daysInMonth; d++) {
      const date = new Date(year, month, d);
      const isAvail = availDays.includes(d);
      const isToday = date.toDateString() === today.toDateString();
      const isSel = selectedDate && selectedDate.getDate()===d && selectedDate.getMonth()===month && selectedDate.getFullYear()===year;
      const isPast = date < today;
      
      let cls = 'fbw-day';
      if (isPast) cls += ' fbw-past';
      else if (isSel) cls += ' fbw-selected';
      else if (isAvail) cls += ' fbw-available';
      else cls += ' fbw-unavailable';
      if (isToday) cls += ' fbw-today';

      const clickable = isAvail && !isSel;
      html += `<div class="${cls}" ${clickable ? `data-day="${d}"` : ''}>${d}</div>`;
    }

    html += '</div>';
    container.innerHTML = html;

    container.querySelector('.fbw-prev').onclick = () => {
      if (month === 0) { state.year--; state.month = 11; }
      else state.month--;
      renderCalendar(container, state);
    };
    container.querySelector('.fbw-next').onclick = () => {
      if (month === 11) { state.year++; state.month = 0; }
      else state.month++;
      renderCalendar(container, state);
    };

    container.querySelectorAll('.fbw-available').forEach(el => {
      el.onclick = () => {
        const d = parseInt(el.dataset.day);
        state.selectedDate = new Date(year, month, d);
        renderCalendar(container, state);
        state.onDateSelected && state.onDateSelected(state.selectedDate);
      };
    });
  }

  function formatDate(date) {
    return `${date.getDate()}. ${date.getMonth()+1}. ${date.getFullYear()}`;
  }

  function initBookingWidget(el) {
    const submitEmail = el.dataset.email || 'info@skolaflow.cz';
    const lang = el.dataset.lang || 'cs';
    const now = new Date();

    const state = {
      year: now.getFullYear(),
      month: now.getMonth(),
      selectedDate: null,
      visitType: VISIT_TYPES[0],
    };

    el.innerHTML = `
      <div class="fbw-wrap">
        <div class="fbw-left">
          <div class="fbw-type-select">
            <label class="fbw-label">Typ návštěvy</label>
            <div class="fbw-type-btns">
              ${VISIT_TYPES.map(vt => `
                <button class="fbw-type-btn ${vt.id === state.visitType.id ? 'active' : ''}" data-type="${vt.id}">
                  ${vt.label}
                </button>`).join('')}
            </div>
          </div>
          <div class="fbw-calendar"></div>
          <div class="fbw-time-hint" style="display:none">
            <span class="fbw-time-icon">🕐</span>
            <span class="fbw-time-text"></span>
          </div>
        </div>
        <div class="fbw-right">
          <div class="fbw-form-wrap">
            <div class="fbw-no-date">
              <div class="fbw-no-date-icon">📅</div>
              <p>Vyberte nejdříve datum v kalendáři vlevo.</p>
            </div>
            <form class="fbw-form" style="display:none" action="https://formsubmit.co/${submitEmail}" method="POST">
              <input type="hidden" name="_subject" value="Nová rezervace – Flow škola">
              <input type="hidden" name="_captcha" value="false">
              <input type="hidden" name="_template" value="table">
              <input type="hidden" name="_next" value="">
              <input type="hidden" name="Typ_navstevy" value="">
              <input type="hidden" name="Datum" value="">

              <h3 class="fbw-form-title">Vaše údaje</h3>
              <div class="fbw-selected-info"></div>

              <div class="fbw-field">
                <label>Jméno a příjmení *</label>
                <input type="text" name="Jmeno" required placeholder="Jan Novák">
              </div>
              <div class="fbw-field">
                <label>E-mail *</label>
                <input type="email" name="Email" required placeholder="jan@example.com">
              </div>
              <div class="fbw-field">
                <label>Telefon</label>
                <input type="tel" name="Telefon" placeholder="+420 600 000 000">
              </div>
              <div class="fbw-field">
                <label>Počet dětí a ročník</label>
                <input type="text" name="Deti" placeholder="1 dítě, 6 let">
              </div>
              <div class="fbw-field">
                <label>Zpráva</label>
                <textarea name="Zprava" rows="3" placeholder="Máte otázky? Napište nám..."></textarea>
              </div>
              <button type="submit" class="fbw-submit">
                <span>Odeslat rezervaci</span>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
              </button>
              <p class="fbw-note">Po odeslání vám pošleme e-mailem potvrzení s podrobnostmi.</p>
            </form>
            <div class="fbw-success" style="display:none">
              <div class="fbw-success-icon">✓</div>
              <h3>Rezervace odeslána!</h3>
              <p>Brzy se vám ozveme na zadaný e-mail s potvrzením termínu.</p>
              <p class="fbw-success-sub">Máte otázky? Napište na <a href="mailto:info@skolaflow.cz">info@skolaflow.cz</a></p>
            </div>
          </div>
        </div>
      </div>`;

    const calContainer = el.querySelector('.fbw-calendar');
    const form = el.querySelector('.fbw-form');
    const noDate = el.querySelector('.fbw-no-date');
    const successDiv = el.querySelector('.fbw-success');
    const timeHint = el.querySelector('.fbw-time-hint');
    const timeText = el.querySelector('.fbw-time-text');
    const selectedInfo = el.querySelector('.fbw-selected-info');

    // Visit type buttons
    el.querySelectorAll('.fbw-type-btn').forEach(btn => {
      btn.onclick = () => {
        el.querySelectorAll('.fbw-type-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.visitType = VISIT_TYPES.find(vt => vt.id === btn.dataset.type);
        state.selectedDate = null;
        form.style.display = 'none';
        noDate.style.display = '';
        renderCalendar(calContainer, state);
      };
    });

    state.onDateSelected = (date) => {
      const vt = state.visitType;
      timeHint.style.display = 'flex';
      timeText.textContent = `${formatDate(date)} — ${vt.time}`;
      
      // Update hidden fields
      form.querySelector('[name="Typ_navstevy"]').value = vt.label;
      form.querySelector('[name="Datum"]').value = `${formatDate(date)}, ${vt.time}`;
      
      selectedInfo.innerHTML = `
        <div class="fbw-selected-badge">
          <strong>${vt.label}</strong><br>
          📅 ${formatDate(date)} &nbsp;🕐 ${vt.time}
        </div>`;
      
      noDate.style.display = 'none';
      form.style.display = '';
    };

    // Form submit with success state
    form.onsubmit = function(e) {
      // Let FormSubmit handle it, but show success after brief delay for UX
      const submitBtn = form.querySelector('.fbw-submit');
      submitBtn.innerHTML = '<span>Odesílám...</span>';
      submitBtn.disabled = true;
      
      // Show success after 1.5s (FormSubmit redirects, but we show inline success)
      // For better UX, we catch it with fetch if possible
      e.preventDefault();
      
      fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'Accept': 'application/json' }
      }).then(r => {
        form.style.display = 'none';
        successDiv.style.display = '';
        timeHint.style.display = 'none';
      }).catch(() => {
        // Fallback: submit normally
        form.submit();
      });
    };

    renderCalendar(calContainer, state);
  }

  // Auto-init all .flow-booking elements
  function init() {
    document.querySelectorAll('.flow-booking').forEach(initBookingWidget);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
