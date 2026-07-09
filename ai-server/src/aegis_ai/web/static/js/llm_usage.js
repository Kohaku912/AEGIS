(() => {
  const $ = id => document.getElementById(id);
  const esc = v => String(v || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const fmt = n => n >= 1e6 ? (n / 1e6).toFixed(1) + 'M' : n >= 1e3 ? (n / 1e3).toFixed(1) + 'K' : String(n);
  const fmtCost = n => n >= 0.01 ? '$' + n.toFixed(2) : n >= 0.0001 ? '$' + n.toFixed(4) : '$' + n.toFixed(6);
  const fmtMs = n => n >= 1000 ? (n / 1000).toFixed(1) + 's' : n + 'ms';
  const fmtPct = n => (n * 100).toFixed(1) + '%';

  function luParams() {
    const p = new URLSearchParams();
    p.set('period', $('lu-period').value);
    const c = $('lu-caller').value; if (c) p.set('caller', c);
    const m = $('lu-model').value; if (m) p.set('model', m);
    const pr = $('lu-profile').value; if (pr) p.set('profile', pr);
    if ($('lu-errors').checked) p.set('errors_only', '1');
    const mt = parseInt($('lu-min-tokens').value); if (mt > 0) p.set('min_tokens', mt);
    return p.toString();
  }

  async function luFetch(path) {
    try {
      const r = await fetch('/api/llm-usage/' + path + '?' + luParams());
      if (!r.ok) return null;
      return await r.json();
    } catch (e) { return null; }
  }

  function luRenderKPIs(s) {
    if (!s) { $('lu-kpis').innerHTML = '<div class="lu-empty">No data</div>'; return; }
    const items = [
      ['Total Calls', fmt(s.total_calls)],
      ['Total Tokens', fmt(s.total_tokens)],
      ['Est. Cost', fmtCost(s.estimated_cost)],
      ['Avg Tokens', fmt(Math.round(s.avg_tokens))],
      ['P95 Tokens', fmt(s.p95_tokens)],
      ['Avg Latency', fmtMs(Math.round(s.avg_latency_ms))],
      ['P95 Latency', fmtMs(s.p95_latency_ms)],
      ['Failed', s.failed_calls],
      ['Failure Rate', fmtPct(s.failure_rate)],
      ['Tool Call Rate', fmtPct(s.tool_call_rate)]
    ];
    $('lu-kpis').innerHTML = items.map(([k, v]) =>
      `<div class="lu-kpi"><div class="k">${esc(k)}</div><div class="v">${esc(String(v))}</div></div>`
    ).join('');
  }

  function luRenderTimeseries(ts) {
    const area = $('lu-chart-timeseries');
    if (!ts || !ts.length) { area.innerHTML = '<div class="lu-empty">No time series data</div>'; return; }
    const maxTok = Math.max(...ts.map(b => b.tokens), 1);
    const w = 600, h = 180, pad = 40;
    const barW = Math.max(4, (w - pad * 2) / ts.length - 2);
    let svg = `<svg class="lu-svg-chart" viewBox="0 0 ${w} ${h + 20}" preserveAspectRatio="xMidYMid meet">`;
    ts.forEach((b, i) => {
      const x = pad + i * (barW + 2);
      const bh = (b.tokens / maxTok) * h * 0.8;
      const y = h - bh;
      svg += `<rect x="${x}" y="${y}" width="${barW}" height="${bh}" fill="var(--accent)" opacity="0.7" rx="2"><title>${fmt(b.tokens)} tokens, ${fmtCost(b.cost)}</title></rect>`;
      if (b.failures > 0) {
        const fh = (b.failures / Math.max(...ts.map(t => t.failures), 1)) * h * 0.3;
        svg += `<rect x="${x}" y="${h - fh}" width="${barW}" height="${fh}" fill="var(--red)" opacity="0.8" rx="2"></rect>`;
      }
    });
    svg += `<line x1="${pad}" y1="${h}" x2="${w - pad}" y2="${h}" stroke="var(--border)" stroke-width="1"/>`;
    svg += `</svg>`;
    area.innerHTML = svg;
  }

  function luRenderFailureRate(ts) {
    const el = $('lu-chart-failure-rate');
    if (!ts || !ts.length) { el.innerHTML = '<div class="lu-empty">No data</div>'; return; }
    const maxRate = Math.max(...ts.map(b => b.calls > 0 ? b.failures / b.calls : 0), 0.01);
    const w = 600, h = 120, pad = 40;
    const barW = Math.max(4, (w - pad * 2) / ts.length - 2);
    let svg = `<svg class="lu-svg-chart" viewBox="0 0 ${w} ${h + 20}" preserveAspectRatio="xMidYMid meet">`;
    ts.forEach((b, i) => {
      const x = pad + i * (barW + 2);
      const rate = b.calls > 0 ? b.failures / b.calls : 0;
      const bh = (rate / maxRate) * h * 0.8;
      const y = h - bh;
      svg += `<rect x="${x}" y="${y}" width="${barW}" height="${bh}" fill="${rate > 0.1 ? 'var(--red)' : 'var(--yellow)'}" opacity="0.7" rx="2"><title>${fmtPct(rate)}</title></rect>`;
    });
    svg += `<line x1="${pad}" y1="${h}" x2="${w - pad}" y2="${h}" stroke="var(--border)" stroke-width="1"/>`;
    svg += `</svg>`;
    el.innerHTML = svg;
  }

  function luRenderBreakdown(el, rows) {
    if (!rows || !rows.length) { el.innerHTML = '<div class="lu-empty">No data</div>'; return; }
    const maxVal = Math.max(...rows.map(r => r.tokens), 1);
    el.innerHTML = `<table class="lu-table"><thead><tr><th>Key</th><th>Calls</th><th>Tokens</th><th>Avg</th><th>P95</th><th>Fail%</th></tr></thead><tbody>` +
      rows.slice(0, 15).map(r => `<tr><td style="font-weight:500">${esc(r.key)}</td><td>${r.calls}</td><td>${fmt(r.tokens)}<span class="lu-bar" style="width:${(r.tokens / maxVal) * 60}px"></span></td><td>${fmt(Math.round(r.avg_tokens))}</td><td>${fmt(r.p95_tokens)}</td><td>${fmtPct(r.failure_rate)}</td></tr>`).join('') +
      '</tbody></table>';
  }

  function luRenderWasteTypeCounts(cands) {
    const el = $('lu-chart-waste-types');
    if (!cands || !cands.length) { el.innerHTML = '<div class="lu-empty">No candidates</div>'; return; }
    const counts = {};
    cands.forEach(c => { counts[c.candidate_type] = (counts[c.candidate_type] || 0) + 1; });
    const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
    const maxCount = Math.max(...entries.map(e => e[1]), 1);
    el.innerHTML = entries.map(([type, count]) => {
      const pct = (count / maxCount) * 100;
      return `<div style="margin-bottom:6px"><span style="font-size:12px;color:var(--text-dim)">${esc(type)}</span><div style="background:var(--surface2);border-radius:4px;height:18px;margin-top:2px"><div style="background:var(--accent);height:100%;width:${pct}%;border-radius:4px;display:flex;align-items:center;padding-left:6px;font-size:11px;color:var(--text)">${count}</div></div></div>`;
    }).join('');
  }

  function luRenderTraces(traces) {
    const el = $('lu-trace-table');
    if (!traces || !traces.length) { el.innerHTML = '<div class="lu-empty">No traces</div>'; return; }
    el.innerHTML = `<table class="lu-table"><thead><tr><th>Time</th><th>Caller</th><th>Model</th><th>Profile</th><th>Tokens</th><th>Duration</th><th>Status</th><th>Action</th></tr></thead><tbody>` +
      traces.map((t, i) => {
        const dt = new Date(t.timestamp_ms).toLocaleTimeString();
        const badge = t.success ? '<span class="lu-badge lu-badge-green">OK</span>' : '<span class="lu-badge lu-badge-red">FAIL</span>';
        const ctx = Object.entries(t.context_tokens || {}).map(([k, v]) => `${k}: ${fmt(v)}`).join(', ');
        return `<tr onclick="window.luToggleDetail(${i})" style="cursor:pointer"><td>${dt}</td><td>${esc(t.caller)}</td><td>${esc(t.model)}</td><td>${esc(t.profile_id)}</td><td>${fmt(t.tokens_used)}</td><td>${fmtMs(t.duration_ms)}</td><td>${badge}</td><td>${esc(t.action)}</td></tr><tr><td colspan="8"><div class="lu-detail" id="lu-det-${i}">prompt: ${esc(t.detail_preview)}\nresponse: ${esc(t.response_preview)}\nerror: ${esc(t.error)}\nrequest_id: ${esc(t.request_id)}\ntools: ${esc(t.tool_names.join(', '))}\ninput/output: ${fmt(t.input_tokens || 0)} / ${fmt(t.output_tokens || 0)}\ncache hit/miss: ${fmt(t.input_cache_hit_tokens || 0)} / ${fmt(t.input_cache_miss_tokens || 0)}\ncontext: ${esc(ctx)}\nprovider cost: ${fmtCost(t.provider_reported_cost || 0)}</div></td></tr>`;
      }).join('') + '</tbody></table>';
  }

  function luRenderHighTokenTraces(traces) {
    const el = $('lu-high-token-table');
    if (!traces || !traces.length) { el.innerHTML = '<div class="lu-empty">No high token traces</div>'; return; }
    const sorted = [...traces].sort((a, b) => b.tokens_used - a.tokens_used).slice(0, 20);
    el.innerHTML = `<table class="lu-table"><thead><tr><th>Time</th><th>Model</th><th>Tokens</th><th>Duration</th><th>Caller</th></tr></thead><tbody>` +
      sorted.map(t => {
        const dt = new Date(t.timestamp_ms).toLocaleTimeString();
        return `<tr><td>${dt}</td><td>${esc(t.model)}</td><td>${fmt(t.tokens_used)}</td><td>${fmtMs(t.duration_ms)}</td><td>${esc(t.caller)}</td></tr>`;
      }).join('') + '</tbody></table>';
  }

  function luRenderFailedTraces(traces) {
    const el = $('lu-failed-table');
    if (!traces || !traces.length) { el.innerHTML = '<div class="lu-empty">No failed traces</div>'; return; }
    const failed = traces.filter(t => !t.success).slice(0, 20);
    el.innerHTML = `<table class="lu-table"><thead><tr><th>Time</th><th>Model</th><th>Error</th><th>Tokens</th><th>Caller</th></tr></thead><tbody>` +
      failed.map(t => {
        const dt = new Date(t.timestamp_ms).toLocaleTimeString();
        return `<tr><td>${dt}</td><td>${esc(t.model)}</td><td style="max-width:200px;overflow:hidden;text-overflow:ellipsis">${esc(t.error)}</td><td>${fmt(t.tokens_used)}</td><td>${esc(t.caller)}</td></tr>`;
      }).join('') + '</tbody></table>';
  }

  function luRenderPrompts(prompts) {
    const el = $('lu-prompt-table');
    if (!prompts || !prompts.length) { el.innerHTML = '<div class="lu-empty">No prompts</div>'; return; }
    el.innerHTML = `<table class="lu-table"><thead><tr><th>Prompt ID</th><th>Calls</th><th>Total Tokens</th><th>Avg</th><th>P95</th><th>Last Seen</th></tr></thead><tbody>` +
      prompts.map(r => `<tr><td style="font-weight:500">${esc(r.prompt_id)}</td><td>${r.calls}</td><td>${fmt(r.tokens)}</td><td>${fmt(Math.round(r.avg_tokens))}</td><td>${fmt(r.p95_tokens)}</td><td>${new Date(r.last_seen_ms).toLocaleString()}</td></tr>`).join('') +
      '</tbody></table>';
  }

  function luRenderWaste(cands) {
    const el = $('lu-waste-table');
    if (!cands || !cands.length) { el.innerHTML = '<div class="lu-empty">削減候補は見つかりませんでした</div>'; return; }
    el.innerHTML = `<table class="lu-table"><thead><tr><th>種別</th><th>説明</th><th>信頼度</th><th>根拠</th><th>推奨実験</th></tr></thead><tbody>` +
      cands.map(c => {
        const conf = c.confidence >= 0.7 ? '<span class="lu-badge lu-badge-yellow">高</span>' : c.confidence >= 0.4 ? '<span class="lu-badge lu-badge-blue">中</span>' : '<span class="lu-badge lu-badge-gray">低</span>';
        return `<tr><td style="white-space:nowrap">${esc(c.candidate_type)}</td><td>${esc(c.description)}</td><td>${conf}</td><td style="font-size:11px;max-width:200px">${esc(c.evidence)}</td><td style="font-size:11px;max-width:200px">${esc(c.recommended_experiment)}</td></tr>`;
      }).join('') + '</tbody></table>';
  }

  function luPopulateFilters(callers, models, profiles) {
    const fill = (el, items) => { const v = el.value; el.innerHTML = '<option value="">All</option>' + items.map(i => `<option value="${esc(i)}">${esc(i)}</option>`).join(''); el.value = v; };
    if (callers) fill($('lu-caller'), callers.map(r => r.key));
    if (models) fill($('lu-model'), models.map(r => r.key));
    if (profiles) fill($('lu-profile'), profiles.map(r => r.key));
  }

  window.luToggleDetail = function (i) {
    const d = $('lu-det-' + i); if (d) d.style.display = d.style.display === 'block' ? 'none' : 'block';
  };

  window.luRefresh = async function () {
    const [sum, ts, callers, profiles, prompts, traces, waste, models, context] = await Promise.all([
      luFetch('summary'), luFetch('timeseries'),
      luFetch('breakdown/callers'), luFetch('breakdown/profiles'),
      luFetch('breakdown/prompts'), luFetch('traces'), luFetch('waste-candidates'),
      luFetch('breakdown/models'), luFetch('breakdown/context')
    ]);
    luRenderKPIs(sum);
    luRenderTimeseries(ts);
    luRenderFailureRate(ts);
    luRenderBreakdown($('lu-bk-callers'), callers);
    luRenderBreakdown($('lu-bk-profiles'), profiles);
    luRenderBreakdown($('lu-bk-models'), models);
    luRenderBreakdown($('lu-bk-context'), context);
    luRenderTraces(traces);
    luRenderHighTokenTraces(traces);
    luRenderFailedTraces(traces);
    luRenderPrompts(prompts);
    luRenderWaste(waste);
    luRenderWasteTypeCounts(waste);
    luPopulateFilters(callers, models, profiles);
  };

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.lu-tab').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.lu-tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        document.querySelectorAll('.lu-panel').forEach(p => p.style.display = 'none');
        const target = document.getElementById('lu-' + btn.dataset.tab);
        if (target) target.style.display = 'block';
      });
    });
    luRefresh();
  });
})();
