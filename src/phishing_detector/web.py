"""The browser interface for the phishing detector.

The page is intentionally dependency-free so the API remains easy to deploy as
a single FastAPI service. Its JavaScript only consumes the public ``/predict``
endpoint and never opens the URL submitted by the user.
"""

LANDING_PAGE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#071427">
  <title>LinkSentry — Phishing URL Detector</title>
  <style>
    :root {
      color-scheme: dark;
      --ink: #eef5ff;
      --muted: #a4b4ce;
      --line: rgba(186, 208, 240, .17);
      --surface: rgba(14, 31, 56, .75);
      --surface-strong: #102441;
      --accent: #71e4c5;
      --accent-deep: #2aa888;
      --danger: #ff8e9d;
      --danger-deep: #d94d68;
      --shadow: 0 30px 80px rgba(0, 0, 0, .28);
    }

    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      min-width: 320px;
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 8% 0%, rgba(43, 168, 136, .21), transparent 28rem),
        radial-gradient(circle at 92% 18%, rgba(57, 116, 214, .20), transparent 30rem),
        #071427;
      min-height: 100vh;
    }
    a { color: inherit; }
    button, input { font: inherit; }
    button { cursor: pointer; }
    .shell { width: min(1120px, calc(100% - 40px)); margin: 0 auto; }
    .nav {
      display: flex; align-items: center; justify-content: space-between;
      padding: 28px 0 22px;
    }
    .brand { display: inline-flex; align-items: center; gap: 11px; font-weight: 750; letter-spacing: -.02em; text-decoration: none; }
    .brand-mark {
      width: 34px; height: 34px; display: grid; place-items: center; border-radius: 11px;
      color: #062319; background: var(--accent); box-shadow: 0 8px 24px rgba(113, 228, 197, .24);
    }
    .brand-mark svg { width: 20px; height: 20px; }
    .docs-link {
      color: #c8d6ec; font-size: .9rem; font-weight: 650; text-decoration: none;
      padding: 9px 13px; border: 1px solid var(--line); border-radius: 9px;
    }
    .docs-link:hover, .docs-link:focus-visible { color: white; background: rgba(255,255,255,.07); outline: none; }
    main { padding: 52px 0 50px; }
    .eyebrow {
      display: inline-flex; align-items: center; gap: 8px; padding: 7px 10px 7px 8px;
      border: 1px solid rgba(113, 228, 197, .27); border-radius: 99px; color: #b9f4e2;
      background: rgba(48, 174, 142, .10); font-size: .78rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase;
    }
    .pulse { width: 7px; height: 7px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 0 4px rgba(113, 228, 197, .12); }
    h1 { max-width: 760px; margin: 19px 0 15px; font-size: clamp(2.55rem, 6vw, 4.8rem); line-height: .99; letter-spacing: -.065em; }
    .lede { max-width: 630px; margin: 0; color: var(--muted); font-size: clamp(1rem, 2vw, 1.13rem); line-height: 1.65; }
    .scanner {
      position: relative; display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(260px, .8fr);
      gap: 30px; margin-top: 46px; padding: clamp(22px, 4vw, 38px);
      overflow: hidden; border: 1px solid var(--line); border-radius: 24px; background: var(--surface); box-shadow: var(--shadow); backdrop-filter: blur(18px);
    }
    .scanner::before { content: ""; position: absolute; width: 340px; height: 340px; top: -230px; right: -160px; border: 1px solid rgba(113, 228, 197, .14); border-radius: 50%; box-shadow: 0 0 0 38px rgba(113, 228, 197, .035), 0 0 0 76px rgba(113, 228, 197, .02); pointer-events: none; }
    .panel { position: relative; z-index: 1; }
    .panel-heading { margin: 0 0 7px; font-size: 1.14rem; letter-spacing: -.025em; }
    .panel-copy { color: var(--muted); font-size: .9rem; line-height: 1.5; margin: 0 0 20px; }
    .url-field { position: relative; display: flex; align-items: center; gap: 11px; min-height: 62px; padding: 7px 8px 7px 17px; border: 1px solid rgba(186,208,240,.25); border-radius: 14px; background: rgba(2, 12, 27, .55); transition: border-color .18s, box-shadow .18s; }
    .url-field:focus-within { border-color: var(--accent); box-shadow: 0 0 0 4px rgba(113, 228, 197, .11); }
    .url-icon { flex: none; color: #78cbb5; }
    .url-icon svg { display: block; width: 20px; height: 20px; }
    input[type="url"] { min-width: 0; width: 100%; color: var(--ink); border: 0; outline: 0; background: transparent; font-size: .98rem; }
    input[type="url"]::placeholder { color: #7185a4; opacity: 1; }
    .scan-button { flex: none; min-height: 46px; padding: 0 18px; color: #062319; border: 0; border-radius: 10px; background: var(--accent); font-weight: 800; transition: transform .18s, background .18s, opacity .18s; }
    .scan-button:hover { background: #94efd7; transform: translateY(-1px); }
    .scan-button:focus-visible { outline: 3px solid white; outline-offset: 2px; }
    .scan-button:disabled { cursor: wait; opacity: .66; transform: none; }
    .field-options { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-top: 14px; }
    .live-toggle { display: inline-flex; align-items: flex-start; gap: 9px; color: #c0cde0; font-size: .83rem; line-height: 1.35; cursor: pointer; }
    .live-toggle input { width: 16px; height: 16px; margin: 1px 0 0; accent-color: var(--accent); }
    .example-row { display: flex; align-items: center; gap: 7px; color: #8295b4; font-size: .78rem; white-space: nowrap; }
    .example { padding: 0; color: #b8c8de; border: 0; border-bottom: 1px solid rgba(184, 200, 222, .38); background: transparent; font-size: inherit; }
    .example:hover { color: var(--accent); border-color: var(--accent); }
    .scan-note { display: flex; align-items: flex-start; gap: 8px; margin-top: 20px; color: #8092af; font-size: .75rem; line-height: 1.45; }
    .scan-note svg { flex: none; width: 16px; height: 16px; color: #78cbb5; }
    .info-card { align-self: stretch; padding: 23px; border: 1px solid rgba(186,208,240,.12); border-radius: 17px; background: rgba(4, 17, 37, .5); }
    .info-card h2 { margin: 0 0 20px; color: #d5e0f0; font-size: .87rem; letter-spacing: .04em; text-transform: uppercase; }
    .method { display: grid; grid-template-columns: 28px 1fr; gap: 12px; margin: 0 0 18px; }
    .method:last-child { margin-bottom: 0; }
    .method-number { display: grid; place-items: center; width: 28px; height: 28px; color: var(--accent); border: 1px solid rgba(113,228,197,.28); border-radius: 8px; font-size: .76rem; font-weight: 800; }
    .method strong { display: block; margin: 2px 0 3px; font-size: .87rem; }
    .method p { margin: 0; color: #93a6c2; font-size: .78rem; line-height: 1.45; }
    .result { display: none; margin-top: 22px; padding: 21px; border: 1px solid var(--line); border-radius: 16px; background: rgba(4, 17, 37, .62); animation: rise .32s ease-out; }
    .result.is-visible { display: block; }
    .result[data-verdict="legitimate"] { border-color: rgba(113,228,197,.35); }
    .result[data-verdict="phishing"] { border-color: rgba(255,142,157,.4); }
    .result-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 18px; }
    .result-kicker { margin: 0 0 5px; color: #91a5c2; font-size: .73rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
    .verdict { margin: 0; font-size: 1.36rem; letter-spacing: -.035em; }
    .risk { flex: none; color: var(--accent); font-size: 1.8rem; font-weight: 800; letter-spacing: -.06em; }
    .result[data-verdict="phishing"] .risk { color: var(--danger); }
    .meter { height: 8px; margin: 18px 0 16px; overflow: hidden; border-radius: 99px; background: #1a2e4c; }
    .meter > span { display: block; width: 0; height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--accent-deep), var(--accent)); transition: width .55s cubic-bezier(.2,.8,.2,1); }
    .result[data-verdict="phishing"] .meter > span { background: linear-gradient(90deg, #e45a73, #ff9b9e); }
    .checked-url { overflow: hidden; color: #c4d2e5; font-size: .82rem; line-height: 1.4; text-overflow: ellipsis; white-space: nowrap; }
    .stats { display: grid; grid-template-columns: repeat(3, 1fr); margin-top: 18px; border-top: 1px solid var(--line); }
    .stat { min-width: 0; padding: 14px 15px 0 0; }
    .stat + .stat { padding-left: 15px; border-left: 1px solid var(--line); }
    .stat-label { display: block; margin-bottom: 4px; color: #8295b4; font-size: .7rem; font-weight: 700; letter-spacing: .045em; text-transform: uppercase; }
    .stat-value { display: block; overflow: hidden; color: #dce7f5; font-size: .82rem; font-weight: 700; text-overflow: ellipsis; white-space: nowrap; }
    .signals { margin-top: 17px; padding-top: 16px; border-top: 1px solid var(--line); }
    .signals-title { margin: 0 0 10px; color: #9badc7; font-size: .73rem; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; }
    .signal-list { display: flex; flex-wrap: wrap; gap: 7px; }
    .signal { padding: 6px 8px; color: #bdd0e8; border: 1px solid rgba(186,208,240,.14); border-radius: 7px; background: rgba(148,171,204,.07); font-size: .74rem; }
    .error { display: none; margin-top: 16px; padding: 13px 14px; color: #ffd2d8; border: 1px solid rgba(255,142,157,.33); border-radius: 11px; background: rgba(217,77,104,.13); font-size: .85rem; line-height: 1.45; }
    .error.is-visible { display: block; }
    .principles { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 27px; }
    .principle { padding: 18px; border: 1px solid rgba(186,208,240,.11); border-radius: 14px; background: rgba(13,29,53,.37); }
    .principle-icon { display: grid; place-items: center; width: 31px; height: 31px; margin-bottom: 13px; color: var(--accent); border-radius: 9px; background: rgba(113,228,197,.1); }
    .principle-icon svg { width: 17px; height: 17px; }
    .principle h2 { margin: 0 0 5px; font-size: .91rem; letter-spacing: -.015em; }
    .principle p { margin: 0; color: #91a5c2; font-size: .8rem; line-height: 1.48; }
    footer { display: flex; justify-content: space-between; gap: 22px; padding: 19px 0 29px; color: #7084a2; border-top: 1px solid rgba(186,208,240,.12); font-size: .75rem; line-height: 1.45; }
    .footer-status { display: inline-flex; align-items: center; gap: 7px; white-space: nowrap; }
    .footer-status .pulse { width: 6px; height: 6px; }
    .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }
    @keyframes rise { from { opacity: 0; transform: translateY(7px); } to { opacity: 1; transform: translateY(0); } }
    @media (max-width: 760px) {
      main { padding-top: 30px; }
      .scanner { grid-template-columns: 1fr; gap: 23px; }
      .info-card { padding: 20px; }
      .principles { grid-template-columns: 1fr; }
      .field-options { align-items: flex-start; flex-direction: column; }
    }
    @media (max-width: 540px) {
      .shell { width: min(100% - 26px, 1120px); }
      .nav { padding-top: 17px; }
      .docs-link { padding: 8px 10px; }
      .scanner { margin-top: 31px; padding: 17px; border-radius: 18px; }
      .url-field { align-items: stretch; flex-wrap: wrap; padding: 12px; }
      .url-icon { padding-top: 2px; }
      input[type="url"] { width: calc(100% - 32px); height: 24px; }
      .scan-button { width: 100%; }
      .stats { grid-template-columns: 1fr; gap: 0; }
      .stat { padding: 11px 0 0; }
      .stat + .stat { margin-top: 10px; padding-left: 0; border-left: 0; border-top: 1px solid var(--line); }
      footer { flex-direction: column; gap: 7px; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <nav class="nav" aria-label="Primary navigation">
      <a class="brand" href="/" aria-label="LinkSentry home">
        <span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 5 6v5c0 5 3 8.6 7 10 4-1.4 7-5 7-10V6l-7-3Z"/><path d="m9.5 12 1.6 1.6 3.6-4"/></svg></span>
        <span>LinkSentry</span>
      </a>
      <a class="docs-link" href="/docs">API docs <span aria-hidden="true">↗</span></a>
    </nav>

    <main>
      <div class="eyebrow"><span class="pulse" aria-hidden="true"></span> URL risk assessment</div>
      <h1>Know where a link is taking you.</h1>
      <p class="lede">Run a fast, private lexical check before you click. LinkSentry inspects the URL itself and gives you a clear, explainable risk signal.</p>

      <section class="scanner" aria-labelledby="scanner-title">
        <div class="panel">
          <h2 class="panel-heading" id="scanner-title">Check a suspicious link</h2>
          <p class="panel-copy">Paste a complete HTTP(S) address. We analyze the address—you never visit it.</p>
          <form id="scanner-form" novalidate>
            <label class="sr-only" for="url">Website address to scan</label>
            <div class="url-field">
              <span class="url-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.07.07l2-2a5 5 0 0 0-7.07-7.07l-1.15 1.15"/><path d="M14 11a5 5 0 0 0-7.07-.07l-2 2A5 5 0 0 0 12 20l1.15-1.15"/></svg></span>
              <input id="url" name="url" type="url" inputmode="url" autocomplete="url" placeholder="https://example.com/sign-in" aria-describedby="scan-note error-message" required>
              <button class="scan-button" id="scan-button" type="submit"><span class="button-text">Analyze link</span></button>
            </div>
            <div class="field-options">
              <label class="live-toggle"><input id="live-features" type="checkbox"> <span>Also run live checks <span aria-hidden="true">·</span> DNS, TLS, WHOIS &amp; page signals</span></label>
              <div class="example-row">Try <button class="example" type="button" data-url="https://example.com/login">an example URL</button></div>
            </div>
          </form>
          <p class="scan-note" id="scan-note"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="10" width="16" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg><span>Standard scans use local URL characteristics only. Live checks are optional and may contact the submitted public website.</span></p>
          <div class="error" id="error-message" role="alert"></div>

          <section class="result" id="result" aria-live="polite" aria-label="Analysis result">
            <div class="result-top">
              <div><p class="result-kicker">Assessment</p><h3 class="verdict" id="verdict">Analyzing…</h3></div>
              <div class="risk" id="risk-score">—</div>
            </div>
            <div class="meter" aria-hidden="true"><span id="meter-fill"></span></div>
            <div class="checked-url" id="checked-url"></div>
            <div class="stats">
              <div class="stat"><span class="stat-label">Model</span><span class="stat-value" id="model-name">—</span></div>
              <div class="stat"><span class="stat-label">Version</span><span class="stat-value" id="model-version">—</span></div>
              <div class="stat"><span class="stat-label">Scan time</span><span class="stat-value" id="latency">—</span></div>
            </div>
            <div class="signals" id="signals-section" hidden>
              <p class="signals-title">URL signals analyzed</p>
              <div class="signal-list" id="signal-list"></div>
            </div>
          </section>
        </div>

        <aside class="info-card" aria-label="How the analysis works">
          <h2>Designed for a safer first look</h2>
          <div class="method"><span class="method-number">01</span><div><strong>Inspect structure</strong><p>Looks at the URL’s syntax and lexical patterns without opening it.</p></div></div>
          <div class="method"><span class="method-number">02</span><div><strong>Score risk</strong><p>A trained classifier estimates the likelihood of phishing behavior.</p></div></div>
          <div class="method"><span class="method-number">03</span><div><strong>Keep context</strong><p>Use the result as a safety signal, not a substitute for your judgment.</p></div></div>
        </aside>
      </section>

      <section class="principles" aria-label="Product principles">
        <article class="principle"><span class="principle-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z"/><path d="M12 8v4l2.5 2.5"/></svg></span><h2>Fast by default</h2><p>Local scoring means standard checks return without a network lookup.</p></article>
        <article class="principle"><span class="principle-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m12 3 7 3v5c0 5-3 8.6-7 10-4-1.4-7-5-7-10V6l7-3Z"/><path d="M9 12l2 2 4-4"/></svg></span><h2>Safer enrichment</h2><p>Optional live checks reject private and loopback destinations.</p></article>
        <article class="principle"><span class="principle-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5V4.5h16v15Z"/><path d="M8 8h8M8 12h5"/></svg></span><h2>Transparent output</h2><p>Every result includes its model details, risk score, and scan timing.</p></article>
      </section>
    </main>

    <footer>
      <span>LinkSentry is decision support, not a guarantee. Avoid opening links you don’t trust.</span>
      <span class="footer-status"><span class="pulse" aria-hidden="true"></span> Detector ready</span>
    </footer>
  </div>
  <script>
    (() => {
      const form = document.querySelector('#scanner-form');
      const urlInput = document.querySelector('#url');
      const liveFeatures = document.querySelector('#live-features');
      const submitButton = document.querySelector('#scan-button');
      const buttonText = document.querySelector('.button-text');
      const result = document.querySelector('#result');
      const error = document.querySelector('#error-message');
      const signalList = document.querySelector('#signal-list');
      const signalsSection = document.querySelector('#signals-section');
      const readableName = (name) => name.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());

      document.querySelectorAll('.example').forEach(button => button.addEventListener('click', () => {
        urlInput.value = button.dataset.url;
        urlInput.focus();
      }));

      form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const url = urlInput.value.trim();
        error.classList.remove('is-visible');
        result.classList.remove('is-visible');
        if (!url) {
          showError('Enter a complete HTTP(S) address to start the analysis.');
          urlInput.focus();
          return;
        }
        submitButton.disabled = true;
        buttonText.textContent = 'Analyzing…';
        try {
          const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, include_live_features: liveFeatures.checked })
          });
          const data = await response.json().catch(() => ({}));
          if (!response.ok) throw new Error(data.detail || 'The analysis could not be completed.');
          renderResult(data);
        } catch (err) {
          showError(err.message || 'The analysis could not be completed. Please try again.');
        } finally {
          submitButton.disabled = false;
          buttonText.textContent = 'Analyze link';
        }
      });

      function showError(message) {
        error.textContent = message;
        error.classList.add('is-visible');
      }

      function renderResult(data) {
        const probability = Math.round(Number(data.phishing_probability || 0) * 100);
        const isPhishing = data.label === 'phishing';
        result.dataset.verdict = isPhishing ? 'phishing' : 'legitimate';
        document.querySelector('#verdict').textContent = isPhishing ? 'Potential phishing detected' : 'Likely legitimate';
        document.querySelector('#risk-score').textContent = `${probability}%`;
        document.querySelector('#meter-fill').style.width = `${probability}%`;
        document.querySelector('#checked-url').textContent = data.url;
        document.querySelector('#model-name').textContent = data.model_name || '—';
        document.querySelector('#model-version').textContent = data.model_version || '—';
        document.querySelector('#latency').textContent = `${Number(data.latency_ms || 0).toFixed(1)} ms`;
        const features = Object.entries(data.lexical_features || {}).slice(0, 7);
        signalList.replaceChildren();
        features.forEach(([name, value]) => {
          const item = document.createElement('span');
          item.className = 'signal';
          item.textContent = `${readableName(name)}: ${Number(value).toFixed(0)}`;
          signalList.appendChild(item);
        });
        signalsSection.hidden = features.length === 0;
        result.classList.add('is-visible');
        result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    })();
  </script>
</body>
</html>"""
