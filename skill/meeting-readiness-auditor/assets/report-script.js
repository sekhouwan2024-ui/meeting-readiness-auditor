(() => {
  const params = new URLSearchParams(window.location.search);
  if (params.get('recording') === '1' || params.get('view') === 'portrait') {
    document.body.classList.add('recording-mode');
  }

  const tabButtons = [...document.querySelectorAll('.tabs button')];
  const tabPanels = [...document.querySelectorAll('.tab-panel')];

  function activateTab(tabId, scroll = false) {
    if (!tabId || !tabPanels.some((panel) => panel.id === tabId)) return;
    tabButtons.forEach((item) => item.classList.toggle('active', item.dataset.tab === tabId));
    tabPanels.forEach((panel) => panel.classList.toggle('active', panel.id === tabId));
    if (scroll) {
      const tabs = document.querySelector('.tabs');
      if (tabs) window.scrollTo({ top: tabs.offsetTop - 10, behavior: 'smooth' });
    }
  }

  tabButtons.forEach((button) => button.addEventListener('click', () => {
    activateTab(button.dataset.tab, true);
  }));

  if (params.get('tab')) activateTab(params.get('tab'), false);

  const statusLabels = {
    ready: '证据充分',
    partial: '部分准备',
    not_ready: '尚未准备',
    decision_needed: '需要决策',
  };

  function addEvidence(container, evidence) {
    container.innerHTML = '';
    if (!evidence || !evidence.length) {
      const empty = document.createElement('div');
      empty.className = 'empty compact';
      empty.textContent = '暂无可定位证据';
      container.appendChild(empty);
      return;
    }
    evidence.forEach((item) => {
      const row = document.createElement('div');
      row.className = 'evidence-row';
      const pin = document.createElement('div');
      pin.className = 'evidence-pin';
      const content = document.createElement('div');
      const title = document.createElement('b');
      title.textContent = [item.file, item.page_or_sheet, item.cell_or_object].filter(Boolean).join(' · ');
      const value = document.createElement('p');
      value.textContent = item.value_or_quote || '';
      content.append(title, value);
      row.append(pin, content);
      container.appendChild(row);
    });
  }

  function addUnknowns(container, unknowns) {
    container.innerHTML = '';
    const list = unknowns && unknowns.length ? unknowns : ['暂无明确缺口'];
    list.forEach((item) => {
      const li = document.createElement('li');
      li.textContent = item;
      container.appendChild(li);
    });
  }

  document.querySelectorAll('[data-simulation-root]').forEach((root) => {
    const dataNode = root.querySelector('[data-sim-data]');
    let rounds = [];
    try {
      rounds = JSON.parse(dataNode ? dataNode.textContent : '[]');
    } catch (error) {
      console.error('Unable to parse simulation rounds', error);
    }

    const els = {
      role: root.querySelector('[data-sim-role]'),
      index: root.querySelector('[data-sim-index]'),
      total: root.querySelector('[data-sim-total]'),
      progress: root.querySelector('[data-sim-progress]'),
      intent: root.querySelector('[data-sim-intent]'),
      question: root.querySelector('[data-sim-question]'),
      userAnswer: root.querySelector('[data-sim-user-answer]'),
      reveal: root.querySelector('[data-sim-reveal]'),
      next: root.querySelector('[data-sim-next]'),
      restart: root.querySelector('[data-sim-restart]'),
      feedback: root.querySelector('[data-sim-feedback]'),
      status: root.querySelector('[data-sim-status]'),
      answer: root.querySelector('[data-sim-answer]'),
      action: root.querySelector('[data-sim-action]'),
      evidence: root.querySelector('[data-sim-evidence]'),
      unknowns: root.querySelector('[data-sim-unknowns]'),
      avoid: root.querySelector('[data-sim-avoid]'),
      followup: root.querySelector('[data-sim-followup]'),
    };

    let current = 0;
    let finished = false;

    const requestedRound = params.get('round');
    if (rounds.length && requestedRound) {
      const normalized = requestedRound.toUpperCase();
      const byId = rounds.findIndex((item) => String(item.id || '').toUpperCase() === normalized);
      const numeric = Number.parseInt(requestedRound, 10);
      if (byId >= 0) current = byId;
      else if (Number.isFinite(numeric) && numeric >= 1 && numeric <= rounds.length) current = numeric - 1;
    }

    function renderRound() {
      finished = false;
      root.classList.remove('is-revealed', 'is-finished');
      if (!rounds.length) {
        root.dataset.currentRound = '';
        els.role.textContent = '暂无问题';
        els.question.textContent = '当前报告没有生成模拟过会轮次。';
        els.reveal.disabled = true;
        els.next.disabled = true;
        return;
      }
      const round = rounds[current];
      root.dataset.currentRound = round.id || String(current + 1);
      els.role.textContent = round.role || '提问角色';
      els.index.textContent = String(current + 1);
      els.total.textContent = String(rounds.length);
      els.progress.style.width = `${((current + 1) / rounds.length) * 100}%`;
      els.intent.textContent = round.intent ? `对方真正想确认：${round.intent}` : '';
      els.question.textContent = round.question || '';
      els.userAnswer.value = '';
      els.userAnswer.disabled = false;
      els.feedback.hidden = true;
      els.reveal.disabled = false;
      els.reveal.textContent = '对照建议回答';
      els.next.disabled = true;
      els.next.textContent = current === rounds.length - 1 ? '完成演练' : '下一问';
    }

    function revealAnswer() {
      if (!rounds.length || finished) return;
      const round = rounds[current];
      const status = round.answer_status || 'partial';
      els.status.textContent = statusLabels[status] || status;
      els.status.className = `status-pill ${status}`;
      els.answer.textContent = round.suggested_answer || '';
      els.action.textContent = round.prep_action || '';
      addEvidence(els.evidence, round.evidence || []);
      addUnknowns(els.unknowns, round.unknowns || []);
      els.avoid.textContent = round.avoid_answer || '';
      els.followup.textContent = round.follow_up_question || '';
      els.feedback.hidden = false;
      root.classList.add('is-revealed');
      els.reveal.disabled = true;
      els.userAnswer.disabled = true;
      els.next.disabled = false;
      if (params.get('recording') !== '1') {
        els.feedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }

    function finishSimulation() {
      finished = true;
      root.dataset.currentRound = 'complete';
      root.classList.remove('is-revealed');
      root.classList.add('is-finished');
      els.role.textContent = '演练完成';
      els.index.textContent = String(rounds.length);
      els.total.textContent = String(rounds.length);
      els.progress.style.width = '100%';
      els.intent.textContent = '把“尚未准备”和“需要决策”的问题带回会前补数与行动清单。';
      els.question.textContent = `你已经完成 ${rounds.length} 轮追问。现在最重要的不是背答案，而是补齐证据并明确取舍。`;
      els.userAnswer.value = '';
      els.userAnswer.disabled = true;
      els.feedback.hidden = true;
      els.reveal.disabled = true;
      els.reveal.textContent = '演练已完成';
      els.next.disabled = true;
    }

    els.reveal.addEventListener('click', revealAnswer);
    els.next.addEventListener('click', () => {
      if (current >= rounds.length - 1) {
        finishSimulation();
        return;
      }
      current += 1;
      renderRound();
      root.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    els.restart.addEventListener('click', () => {
      current = 0;
      renderRound();
      root.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    document.addEventListener('keydown', (event) => {
      if (!document.body.classList.contains('recording-mode')) return;
      if (event.key === ' ' && !els.reveal.disabled) {
        event.preventDefault();
        revealAnswer();
      } else if (event.key === 'ArrowRight' && !els.next.disabled) {
        event.preventDefault();
        els.next.click();
      } else if ((event.key === 'r' || event.key === 'R')) {
        event.preventDefault();
        els.restart.click();
      }
    });

    renderRound();
    if (params.get('reveal') === '1') revealAnswer();
  });

  const focusId = params.get('focus');
  if (focusId) {
    window.setTimeout(() => {
      const target = document.getElementById(focusId) || document.querySelector(`[data-finding-id="${focusId}"], [data-question-id="${focusId}"], [data-gap-id="${focusId}"]`);
      if (target) {
        target.classList.add('focus-target');
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 80);
  }
})();
