(() => {
  const form = document.querySelector('#tester'), progress = document.querySelector('#progress');
  const submit = document.querySelector('#submit'), resume = document.querySelector('#resume');
  const fresh = document.querySelector('#new'), link = document.querySelector('#detail');
  let payload, statusUrl, stopped = false, controller, active = false, generation = 0, wake;
  const say = text => { progress.textContent = text; };
  async function run() {
    if (active || stopped || !payload) return;
    active = true;
    const current = generation;
    resume.hidden = true;
    controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    try {
      if (!statusUrl) {
        const response = await fetch('/api/v1/requests/', {method:'POST', credentials:'same-origin', signal:controller.signal,
          headers:{'Content-Type':'application/json','X-CSRFToken':form.querySelector('[name=csrfmiddlewaretoken]').value}, body:JSON.stringify(payload)});
        if (!response.ok) { say(`Submission returned HTTP ${response.status}. Resume retries the same submission key.`); resume.hidden = false; return; }
        const data = await response.json(); statusUrl = data.status_url;
        link.href = `/requests/${encodeURIComponent(data.id)}/`; link.hidden = false;
      }
      if (current !== generation) return;
      clearTimeout(timeout);
      for (let i = 0; i < 60 && !stopped; i++) {
        if (document.hidden) { say('Polling paused. Resume when ready.'); resume.hidden = false; return; }
        controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), 10000);
        let response;
        try { response = await fetch(statusUrl, {credentials:'same-origin', signal:controller.signal}); } finally { clearTimeout(timer); }
        if (!response.ok) throw new Error('status unavailable');
        const data = await response.json();
        if (current !== generation) return;
        say(`State: ${data.status}. Attempts: ${data.attempt_count}.${data.dispatch_error ? ' Dispatch interrupted; operator intervention may be required.' : ''}${data.error ? ' Error: ' + data.error : ''}`);
        if (['completed','failed'].includes(data.status)) return;
        await new Promise(resolve => { const timer = setTimeout(resolve, 1000); wake = () => { clearTimeout(timer); resolve(); }; });
        if (current !== generation) return;
      }
      say('Polling window ended. Resume to check this request.'); resume.hidden = false;
    } catch { if (!stopped) { say('Network interrupted. Outcome unknown. Resume safely checks or retries the same submission.'); resume.hidden = false; } }
    finally { clearTimeout(timeout); active = false; }
  }
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (payload) return;
    payload = {source:document.querySelector('#source').value, message:document.querySelector('#message').value, idempotency_key:crypto.randomUUID()};
    submit.disabled = true; fresh.hidden = false;
    document.querySelector('#source').disabled = true; document.querySelector('#message').readOnly = true;
    say('Sending request…'); run();
  });
  resume.addEventListener('click', run);
  fresh.addEventListener('click', () => location.reload());
  window.addEventListener('pagehide', () => { stopped = true; generation++; controller?.abort(); wake?.(); });
  window.addEventListener('pageshow', () => {
    stopped = false;
    if (payload) { say('Navigation restored. Resume to check or retry this request safely.'); resume.hidden = false; }
  });
})();
