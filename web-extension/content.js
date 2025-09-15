(function() {
// Cross-browser API shim
const api = typeof browser !== 'undefined' ? browser : chrome;
const LOG_PREFIX = '[Grade-Able]';

// Guard: only run on Google Search result pages
const {hostname, pathname, search} = window.location;
const isGoogle = /(^|\.)google\./i.test(hostname);
const isSearchPath =
    pathname.startsWith('/search') || pathname === '/';  // includes SPA loads
if (!isGoogle || !isSearchPath) {
  console.debug(LOG_PREFIX, 'No-op: not a Google results page', {
    hostname,
    pathname,
    href: location.href,
  });
  return;
}

const query = new URLSearchParams(search).get('q') || '';
console.debug(LOG_PREFIX, 'Init on Google page', {
  hostname,
  pathname,
  query,
});

async function applyDisplaySettings() {
  try {
    const data = (await api.storage?.sync?.get?.([
                   'gradeableHighContrast',
                   'gradeableCbPatterns',
                 ])) ||
        {gradeableHighContrast: false, gradeableCbPatterns: false};
    const root = document.documentElement;
    if (data.gradeableHighContrast)
      root.setAttribute('data-gradeable-high-contrast', '1');
    else
      root.removeAttribute('data-gradeable-high-contrast');
    if (data.gradeableCbPatterns)
      root.setAttribute('data-gradeable-cb-patterns', '1');
    else
      root.removeAttribute('data-gradeable-cb-patterns');
  } catch {
  }
}

function findAnchorForHeading(h3) {
  let a = h3.closest('a[href]');
  if (a) return a;
  a = h3.parentElement?.querySelector('a[href]');
  if (a) return a;
  let cur = h3.parentElement;
  for (let depth = 0; cur && depth < 5; depth += 1) {
    const candidate = cur.querySelector('a[href]');
    if (candidate) return candidate;
    cur = cur.parentElement;
  }
  return null;
}

function findContainer(h3) {
  return h3.closest('.A6K0A');
}

function getResultHeadings() {
  const allHeadings = Array.from(document.querySelectorAll('#search h3'));
  const seen = new Set();
  const filtered = [];
  for (const h3 of allHeadings) {
    const a = findAnchorForHeading(h3);
    if (!a || !a.href) continue;
    try {
      const href = a.href;
      if (seen.has(href)) continue;
      seen.add(href);
      filtered.push(h3);
    } catch {
    }
  }
  return filtered;
}

function extractResults() {
  const headings = getResultHeadings();
  const results = [];
  headings.slice(0, 20).forEach((h3, i) => {
    h3.setAttribute('data-gradeable-index', String(i));
    const a = findAnchorForHeading(h3);
    if (a && a.href)
      results.push({url: a.href, title: h3.innerText || '', nodeIndex: i});
  });
  console.debug(LOG_PREFIX, 'extractResults:', {
    headingCount: headings.length,
    resultCount: results.length,
  });
  return results;
}

let sent = false;
let inFlight = false;
let retryTimer = null;
let scanTimer = null;

function scheduleScan(delay = 400) {
  if (scanTimer) clearTimeout(scanTimer);
  scanTimer = setTimeout(sendScan, delay);
}

function sendScan() {
  if (sent || inFlight) {
    console.debug(LOG_PREFIX, 'sendScan: skipped', {sent, inFlight});
    return;
  }
  applyDisplaySettings();
  const results = extractResults();
  if (!results.length) {
    console.debug(LOG_PREFIX, 'sendScan: no results yet — retrying in 1s');
    if (retryTimer) clearTimeout(retryTimer);
    retryTimer = setTimeout(sendScan, 1000);
    return;
  }
  inFlight = true;
  sent = true;
  console.debug(LOG_PREFIX, 'Sending GRADEABLE_SCAN', {
    count: results.length,
    query,
  });
  try {
    const maybePromise = api.runtime.sendMessage({
      type: 'GRADEABLE_SCAN',
      results,
    });
    if (maybePromise && typeof maybePromise.catch === 'function') {
      maybePromise.catch(
          (e) => console.debug(LOG_PREFIX, 'sendMessage error', e?.message));
    }
  } catch (e) {
    console.debug(LOG_PREFIX, 'sendMessage threw', e?.message);
  }
}

function showTempErrorIndicator(error) {
  // Remove any existing error indicators first
  document.querySelectorAll('.gradeable-error-indicator')
      .forEach((n) => n.remove());

  const indicator = document.createElement('div');
  indicator.className = 'gradeable-error-indicator';
  indicator.setAttribute('role', 'alert');
  indicator.setAttribute('aria-live', 'assertive');
  indicator.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #ff4444;
      color: white;
      padding: 12px 16px;
      border-radius: 6px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      font-family: Arial, sans-serif;
      font-size: 14px;
      z-index: 10000;
      max-width: 300px;
      cursor: pointer;
    `;

  indicator.innerHTML = `
      <div style="font-weight: bold; margin-bottom: 4px;">⚠️ Accessibility Analysis Failed</div>
      <div style="font-size: 12px; opacity: 0.9;">${errorMessage}</div>
      <div style="font-size: 11px; margin-top: 8px; opacity: 0.7;">Click to dismiss</div>
    `;

  // Auto-hide after 10 seconds
  setTimeout(() => {
    if (indicator.parentNode) {
      indicator.remove();
    }
  }, 10000);

  // Click to dismiss
  indicator.addEventListener('click', () => indicator.remove());

  document.body.appendChild(indicator);
}

api.runtime.onMessage.addListener((msg) => {
  // Handle different message types for progressive updates
  if (msg?.type === 'GRADEABLE_ANALYSIS_STARTED') {
    inFlight = true;
    console.debug(LOG_PREFIX, 'Analysis started', {
      totalUrls: msg.data?.totalUrls || 0,
      message: msg.data?.message,
    });
    showAnalysisProgress(0, msg.data?.totalUrls || 0, 'Starting analysis...');
    return;
  }

  if (msg?.type === 'GRADEABLE_PROGRESS_UPDATE') {
    const {completed, total, results, isComplete} = msg.data || {};
    console.debug(LOG_PREFIX, 'Progress update', {
      completed,
      total,
      resultCount: results?.length || 0,
      isComplete,
    });

    // Update progress indicator
    showAnalysisProgress(
        completed, total, `Analyzing... ${completed}/${total} completed`);

    // Update badges for completed results
    if (results && results.length > 0) {
      updateResultBadges(results);
    }

    // If complete, clean up progress indicator and sort results
    if (isComplete) {
      inFlight = false;
      hideAnalysisProgress();
      sortResultsByScore(results);
    }
    return;
  }

  if (msg?.type !== 'GRADEABLE_RESULTS') return;

  const data = msg.data || [];
  const error = msg.error;
  const summary = msg.summary;
  inFlight = false;

  console.debug(LOG_PREFIX, 'Received GRADEABLE_RESULTS', {
    resultCount: data.length,
    hasError: !!error,
    error: error,
    summary: summary,
  });

  // Hide any progress indicators
  hideAnalysisProgress();

  if (error) {
    console.warn(LOG_PREFIX, 'Analysis failed:', error);
    showErrorIndicator(error);
    return;
  }

  // Update all badges and sort results
  updateResultBadges(data);
  sortResultsByScore(data);

  // Show summary if available
  if (summary) {
    showAnalysisSummary(summary);
  }
});

// Function to update result badges
function updateResultBadges(data) {
  if (!data || data.length === 0) return;

  const urlToResult = new Map(data.map((r) => [r.url, r]));
  const containers = new Map();
  data.forEach((r, idx) => {
    let h3 = document.querySelector(`h3[data-gradeable-index="${idx}"]`);
    if (!h3) h3 = getResultHeadings()[idx] || null;
    if (!h3) return;
    if (h3.querySelector('.gradeable-badge')) return;

    const badge = document.createElement('span');
    badge.className = 'gradeable-badge has-icon';
    badge.setAttribute('data-grade', r.grade);
    badge.setAttribute('role', 'note');
    badge.setAttribute(
        'aria-label', `Accessibility grade ${r.grade}, score ${r.score}`);

    try {
      const icon = (function iconForGrade(grade) {
        const svgNS = 'http://www.w3.org/2000/svg';
        const svg = document.createElementNS(svgNS, 'svg');
        svg.setAttribute('class', 'gradeable-icon');
        svg.setAttribute('width', '14');
        svg.setAttribute('height', '14');
        svg.setAttribute('viewBox', '0 0 24 24');
        svg.setAttribute('aria-hidden', 'true');
        svg.setAttribute('focusable', 'false');
        function el(name, attrs) {
          const n = document.createElementNS(svgNS, name);
          for (const k in attrs) n.setAttribute(k, attrs[k]);
          return n;
        }

        // AAA: use provided 16x16 filled icon
        if (grade === 'AAA') {
          svg.setAttribute('viewBox', '0 0 16 16');
          const pathD =
              'M16,8 C16,12.4183 12.4183,16 8,16 C3.58172,16 0,12.4183 0,8 C0,3.58172 3.58172,0 8,0 C12.4183,0 16,3.58172 16,8 Z M14,8 C14,11.3137 11.3137,14 8,14 C4.68629,14 2,11.3137 2,8 C2,4.68629 4.68629,2 8,2 C11.3137,2 14,4.68629 14,8 Z M8,12 C10.2091,12 12,10.2091 12,8 L4,8 C4,10.2091 5.79086,12 8,12 Z M5.25236,4.69961 C5.48034,4.56853 5.73877,4.4997 6.00175,4.49999902 C6.26472,4.50031 6.523,4.56974 6.75068,4.70134 C6.97835,4.83295 7.16743,5.0221 7.29895,5.24982 C7.43705,5.48895 7.35516,5.79476 7.11603,5.93286 C6.8769,6.07096 6.57109,5.98907 6.43299,5.74994 C6.38915,5.67403 6.32613,5.61098 6.25023,5.56711 C6.17434,5.52325 6.08825,5.5001 6.00059,5.49999902 C5.91293,5.4999 5.82679,5.52284 5.75079,5.56654 C5.6748,5.61023 5.61163,5.67313 5.56761,5.74894 C5.42896,5.98775 5.12296,6.06894 4.88415,5.93028 C4.64535,5.79162 4.56416,5.48563 4.70282,5.24682 C4.83486,5.0194 5.02437,4.83069 5.25236,4.69961 Z M10.0017,4.49999902 C9.73877,4.4997 9.48034,4.56853 9.25236,4.69961 C9.02437,4.83069 8.83486,5.0194 8.70282,5.24682 C8.56416,5.48563 8.64535,5.79162 8.88415,5.93028 C9.12296,6.06894 9.42896,5.98775 9.56761,5.74894 C9.61163,5.67313 9.6748,5.61023 9.75079,5.56654 C9.82679,5.52284 9.91293,5.4999 10.0006,5.49999902 C10.0882,5.5001 10.1743,5.52325 10.2502,5.56711 C10.3261,5.61098 10.3892,5.67403 10.433,5.74994 C10.5711,5.98907 10.8769,6.07096 11.116,5.93286 C11.3552,5.79476 11.4371,5.48895 11.2989,5.24982 C11.1674,5.0221 10.9784,4.83295 10.7507,4.70134 C10.523,4.56974 10.2647,4.50031 10.0017,4.49999902 Z';
          const p = el('path', {
            d: pathD,
            fill: 'currentColor',
            'fill-rule': 'evenodd',
          });
          svg.appendChild(p);
          return svg;
        }

        // Default face icon (nudge left)
        const g = el('g', {transform: 'translate(-0.8 0)'});
        g.appendChild(el('circle', {
          cx: '12',
          cy: '12',
          r: '10',
          fill: 'none',
          stroke: 'currentColor',
          'stroke-width': '3',
        }));
        g.appendChild(el('circle', {
          cx: '8.8',
          cy: '10',
          r: '1.5',
          fill: 'currentColor',
        }));
        g.appendChild(el('circle', {
          cx: '14.2',
          cy: '10',
          r: '1.5',
          fill: 'currentColor',
        }));

        if (grade === 'AA') {
          g.appendChild(el('path', {
            d: 'M8.5 15 C 11 16.5, 13 16.5, 15.5 15',
            fill: 'none',
            stroke: 'currentColor',
            'stroke-width': '1.8',
            'stroke-linecap': 'round',
            'stroke-linejoin': 'round',
          }));
          svg.appendChild(g);
          return svg;
        }
        if (grade === 'A') {
          g.appendChild(el('path', {
            d: 'M9 17h6',
            fill: 'none',
            stroke: 'currentColor',
            'stroke-width': '2',
            'stroke-linecap': 'round',
          }));
          svg.appendChild(g);
          return svg;
        }
        g.appendChild(el('path', {
          d: 'M8 16 C 10.5 16.5, 13.5 16.5, 17 22',
          fill: 'none',
          stroke: 'currentColor',
          'stroke-width': '2',
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round',
        }));
        svg.appendChild(g);
        return svg;
      })(r.grade);
      if (icon) badge.appendChild(icon);
    } catch {
    }

    badge.appendChild(document.createTextNode(` ${r.grade} (${r.score})`));
    h3.appendChild(badge);

    // Find container and assign score
    const container = findContainer(h3);
    if (container) {
      if (!container.id) {
        container.id = `gradeable-result-${idx}`;
      }
      // Use the score for this url, but for main, it's the first
      if (!containers.has(container)) {
        containers.set(container, r.score);
      }
    }
  });

  // Reorder containers by score descending
  const sortedContainers =
      Array.from(containers.entries()).sort((a, b) => b[1] - a[1]);
  const parent =
      document.querySelector('#rso .MjjYud') || document.querySelector('#rso');
  sortedContainers.forEach(([container]) => {
    parent.appendChild(container);
  });

  // Sort sub-URLs (sitelinks) within each container
  containers.forEach((score, container) => {
    const table = container.querySelector('table');
    if (table) {
      const tbody = table.querySelector('tbody');
      if (tbody) {
        const rows = Array.from(tbody.querySelectorAll('tr'));
        rows.sort((a, b) => {
          const h3a = a.querySelector('h3');
          const h3b = b.querySelector('h3');
          const sa = h3a ?
              urlToResult.get(findAnchorForHeading(h3a)?.href)?.score || 0 :
              0;
          const sb = h3b ?
              urlToResult.get(findAnchorForHeading(h3b)?.href)?.score || 0 :
              0;
          return sb - sa;
        });
        rows.forEach((row) => tbody.appendChild(row));
      }
    }
  });
}

// Function to show analysis progress
function showAnalysisProgress(completed, total, message) {
  let progressIndicator =
      document.getElementById('gradeable-progress-indicator');

  if (!progressIndicator) {
    progressIndicator = document.createElement('div');
    progressIndicator.id = 'gradeable-progress-indicator';
    progressIndicator.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #1a73e8;
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        max-width: 300px;
      `;
    document.body.appendChild(progressIndicator);
  }

  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
  progressIndicator.innerHTML = `
      <div style="display: flex; align-items: center; gap: 8px;">
        <div style="width: 16px; height: 16px; border: 2px solid #fff; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
        <div>
          <div style="font-weight: 500;">${message}</div>
          <div style="font-size: 12px; opacity: 0.9;">Progress: ${
      percentage}%</div>
        </div>
      </div>
    `;

  // Add CSS animation if not already present
  if (!document.getElementById('gradeable-progress-styles')) {
    const style = document.createElement('style');
    style.id = 'gradeable-progress-styles';
    style.textContent = `
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `;
    document.head.appendChild(style);
  }
}

// Function to hide analysis progress
function hideAnalysisProgress() {
  const progressIndicator =
      document.getElementById('gradeable-progress-indicator');
  if (progressIndicator) {
    progressIndicator.remove();
  }
}

// Function to sort results by score
function sortResultsByScore(data) {
  if (!data || data.length === 0) return;

  const urlToResult = new Map(data.map((r) => [r.url, r]));
  const containers = new Map();

  // Build container map with scores
  data.forEach((r, idx) => {
    let h3 = document.querySelector(`h3[data-gradeable-index="${idx}"]`);
    if (!h3) h3 = getResultHeadings()[idx] || null;
    if (!h3) return;

    const container = findContainer(h3);
    if (container) {
      if (!containers.has(container)) {
        containers.set(container, r.score);
      }
    }
  });

  // Reorder containers by score descending
  const sortedContainers =
      Array.from(containers.entries()).sort((a, b) => b[1] - a[1]);

  const parent =
      document.querySelector('#rso .MjjYud') || document.querySelector('#rso');
  if (parent && sortedContainers.length > 0) {
    sortedContainers.forEach(([container]) => {
      parent.appendChild(container);
    });
  }

  // Sort sub-URLs within containers
  containers.forEach((score, container) => {
    const table = container.querySelector('table');
    if (table) {
      const tbody = table.querySelector('tbody');
      if (tbody) {
        const rows = Array.from(tbody.querySelectorAll('tr'));
        rows.sort((a, b) => {
          const h3a = a.querySelector('h3');
          const h3b = b.querySelector('h3');
          const sa = h3a ?
              urlToResult.get(findAnchorForHeading(h3a)?.href)?.score || 0 :
              0;
          const sb = h3b ?
              urlToResult.get(findAnchorForHeading(h3b)?.href)?.score || 0 :
              0;
          return sb - sa;
        });
        rows.forEach((row) => tbody.appendChild(row));
      }
    }
  });
}

// Function to show analysis summary
function showAnalysisSummary(summary) {
  const {total, successful, averageScore} = summary;

  console.debug(LOG_PREFIX, 'Analysis Summary', {
    total,
    successful,
    averageScore,
    failureRate: total > 0 ? Math.round(((total - successful) / total) * 100) :
                             0,
  });

  // Could add a temporary summary notification here if desired
  if (total > 0) {
    const successRate = Math.round((successful / total) * 100);
    console.info(
        LOG_PREFIX,
        `Analysis completed: ${successful}/${
            total} URLs analyzed successfully (${
            successRate}%), Average score: ${averageScore}`);
  }
}

function showErrorIndicator(error) {
  let errorIndicator = document.getElementById('gradeable-error-indicator');

  if (!errorIndicator) {
    errorIndicator = document.createElement('div');
    errorIndicator.id = 'gradeable-error-indicator';
    errorIndicator.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #d32f2f;
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        max-width: 300px;
        cursor: pointer;
      `;
    errorIndicator.onclick = () => errorIndicator.remove();
    document.body.appendChild(errorIndicator);
  }

  errorIndicator.innerHTML = `
      <div style="font-weight: 500; margin-bottom: 4px;">Analysis Error</div>
      <div style="font-size: 12px; opacity: 0.9;">${error}</div>
      <div style="font-size: 11px; opacity: 0.7; margin-top: 4px;">Click to dismiss</div>
    `;

  // Auto-remove after 10 seconds
  setTimeout(() => {
    if (errorIndicator.parentNode) {
      errorIndicator.remove();
    }
  }, 10000);
}

window.addEventListener('GRADEABLE_EXTENSION_RESCAN', () => {
  sent = false;
  inFlight = false;
  setTimeout(sendScan, 200);
});

api.runtime.onMessage.addListener((msg) => {
  if (msg?.type === 'GRADEABLE_RESCAN') {
    document.querySelectorAll('.gradeable-badge').forEach((n) => n.remove());
    sent = false;
    inFlight = false;
    applyDisplaySettings();
    scheduleScan(200);
  }
});

if (document.readyState === 'complete' ||
    document.readyState === 'interactive') {
  applyDisplaySettings().finally(() => setTimeout(sendScan, 500));
} else {
  window.addEventListener(
      'DOMContentLoaded',
      () => applyDisplaySettings().finally(() => setTimeout(sendScan, 500)));
}

// ==== EMAIL MODAL FUNCTIONALITY ====

// Server configuration
const SERVER_URL = 'http://localhost:8000';

// Create and show email modal
function showEmailModal(url, grade, score) {
  // Remove any existing modal
  const existing = document.getElementById('gradeable-email-modal');
  if (existing) existing.remove();

  // Create modal HTML
  const modal = document.createElement('div');
  modal.id = 'gradeable-email-modal';
  modal.innerHTML = `
      <div class="gradeable-modal-backdrop">
        <div class="gradeable-modal-container">
          <div class="gradeable-modal-header">
            <h3>📧 Email Accessibility Report</h3>
            <button class="gradeable-modal-close">&times;</button>
          </div>
          <div class="gradeable-modal-body">
            <div class="gradeable-report-info">
              <div class="gradeable-report-url">${
      new URL(url).hostname.replace(/^www\./, '')}</div>
              <div class="gradeable-report-grade">
                <span class="gradeable-grade-badge grade-${
      grade.toLowerCase()}">${grade}</span>
                <span class="gradeable-score">${score}/100</span>
              </div>
            </div>
            <div class="gradeable-form-group">
              <label for="gradeable-email-input">Email Address</label>
              <input type="email" id="gradeable-email-input" placeholder="your.email@example.com" required>
            </div>
            <div class="gradeable-modal-actions">
              <button id="gradeable-send-btn" class="gradeable-btn-primary">Send Report</button>
              <button id="gradeable-cancel-btn" class="gradeable-btn-secondary">Cancel</button>
            </div>
          </div>
        </div>
      </div>
    `;

  // Add CSS styles
  const style = document.createElement('style');
  style.textContent = `
      #gradeable-email-modal {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }
      
      .gradeable-modal-backdrop {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(4px);
        display: flex;
        align-items: center;
        justify-content: center;
        animation: gradeable-fade-in 0.2s ease-out;
      }
      
      .gradeable-modal-container {
        background: white;
        border-radius: 12px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        max-width: 480px;
        width: 90%;
        max-height: 90vh;
        overflow: hidden;
        animation: gradeable-slide-up 0.3s ease-out;
      }
      
      .gradeable-modal-header {
        padding: 20px 24px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      
      .gradeable-modal-header h3 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
      }
      
      .gradeable-modal-close {
        background: none;
        border: none;
        color: white;
        font-size: 24px;
        cursor: pointer;
        padding: 0;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        transition: background-color 0.2s;
      }
      
      .gradeable-modal-close:hover {
        background: rgba(255, 255, 255, 0.1);
      }
      
      .gradeable-modal-body {
        padding: 24px;
      }
      
      .gradeable-report-info {
        background: #f8fafc;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 24px;
        border-left: 4px solid #667eea;
      }
      
      .gradeable-report-url {
        font-weight: 500;
        color: #1e293b;
        margin-bottom: 8px;
        word-break: break-all;
      }
      
      .gradeable-report-grade {
        display: flex;
        align-items: center;
        gap: 8px;
      }
      
      .gradeable-grade-badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
      }
      
      .gradeable-grade-badge.grade-aaa { background: #22c55e; color: white; }
      .gradeable-grade-badge.grade-aa { background: #3b82f6; color: white; }
      .gradeable-grade-badge.grade-a { background: #f59e0b; color: white; }
      .gradeable-grade-badge.grade-b { background: #ef4444; color: white; }
      .gradeable-grade-badge.grade-c { background: #7c2d12; color: white; }
      
      .gradeable-score {
        font-weight: 500;
        color: #64748b;
      }
      
      .gradeable-form-group {
        margin-bottom: 24px;
      }
      
      .gradeable-form-group label {
        display: block;
        font-weight: 500;
        color: #374151;
        margin-bottom: 8px;
        font-size: 14px;
      }
      
      #gradeable-email-input {
        width: 100%;
        padding: 12px;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        font-size: 16px;
        transition: border-color 0.2s, box-shadow 0.2s;
        box-sizing: border-box;
      }
      
      #gradeable-email-input:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      }
      
      .gradeable-modal-actions {
        display: flex;
        gap: 12px;
        justify-content: flex-end;
      }
      
      .gradeable-btn-primary, .gradeable-btn-secondary {
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 500;
        cursor: pointer;
        border: none;
        font-size: 14px;
        transition: all 0.2s;
      }
      
      .gradeable-btn-primary {
        background: #667eea;
        color: white;
      }
      
      .gradeable-btn-primary:hover {
        background: #5a6fd8;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
      }
      
      .gradeable-btn-secondary {
        background: #f1f5f9;
        color: #64748b;
      }
      
      .gradeable-btn-secondary:hover {
        background: #e2e8f0;
      }
      
      @keyframes gradeable-fade-in {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      
      @keyframes gradeable-slide-up {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
    `;

  document.head.appendChild(style);
  document.body.appendChild(modal);

  // Add event listeners
  const emailInput = document.getElementById('gradeable-email-input');
  const sendBtn = document.getElementById('gradeable-send-btn');
  const cancelBtn = document.getElementById('gradeable-cancel-btn');
  const closeBtn = modal.querySelector('.gradeable-modal-close');
  const backdrop = modal.querySelector('.gradeable-modal-backdrop');

  // Close modal functions
  const closeModal = () => {
    modal.remove();
    style.remove();
  };

  // Close on backdrop click
  backdrop.addEventListener('click', (e) => {
    if (e.target === backdrop) closeModal();
  });

  // Close button
  closeBtn.addEventListener('click', closeModal);
  cancelBtn.addEventListener('click', closeModal);

  // Send button
  sendBtn.addEventListener('click', async () => {
    const email = emailInput.value.trim();
    if (!email || !email.includes('@')) {
      showNotification('Please enter a valid email address', 'error');
      emailInput.focus();
      return;
    }

    sendBtn.textContent = 'Sending...';
    sendBtn.disabled = true;

    try {
      const response = await fetch(`${SERVER_URL}/send-report`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({email: email, url: url})
      });

      if (response.ok) {
        const result = await response.json();
        showNotification('Report sent successfully! 📧', 'success');
        closeModal();
      } else {
        const error = await response.text();
        showNotification(`Failed to send report: ${error}`, 'error');
      }
    } catch (error) {
      console.error('Send report error:', error);
      showNotification(
          'Network error. Please check if the server is running.', 'error');
    }

    sendBtn.textContent = 'Send Report';
    sendBtn.disabled = false;
  });

  // Focus email input
  setTimeout(() => emailInput.focus(), 100);

  // Enter key to send
  emailInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      sendBtn.click();
    }
  });
}

// Show notification at top right
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className =
      `gradeable-notification gradeable-notification-${type}`;
  notification.textContent = message;

  // Add notification CSS if not exists
  if (!document.getElementById('gradeable-notification-styles')) {
    const style = document.createElement('style');
    style.id = 'gradeable-notification-styles';
    style.textContent = `
        .gradeable-notification {
          position: fixed;
          top: 20px;
          right: 20px;
          z-index: 10001;
          padding: 12px 16px;
          border-radius: 8px;
          color: white;
          font-weight: 500;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
          animation: gradeable-notification-slide-in 0.3s ease-out;
          max-width: 300px;
        }
        
        .gradeable-notification-success {
          background: #22c55e;
        }
        
        .gradeable-notification-error {
          background: #ef4444;
        }
        
        .gradeable-notification-info {
          background: #3b82f6;
        }
        
        @keyframes gradeable-notification-slide-in {
          from {
            opacity: 0;
            transform: translateX(100px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `;
    document.head.appendChild(style);
  }

  document.body.appendChild(notification);

  // Auto remove after 4 seconds
  setTimeout(() => {
    notification.style.animation =
        'gradeable-notification-slide-in 0.3s ease-out reverse';
    setTimeout(() => notification.remove(), 300);
  }, 4000);
}

// Add click handlers to existing badges
function addBadgeClickHandlers() {
  document.addEventListener('click', (e) => {
    if (e.target.closest('.gradeable-badge')) {
      e.preventDefault();
      e.stopPropagation();

      const badge = e.target.closest('.gradeable-badge');
      const grade = badge.getAttribute('data-grade') || 'Unknown';
      const ariaLabel = badge.getAttribute('aria-label') || '';
      const scoreMatch = ariaLabel.match(/score (\d+)/);
      const score = scoreMatch ? scoreMatch[1] : '0';

      // Find the URL from the nearest heading
      const container =
          badge.closest('.tF2Cxc, .g, .rc') || badge.parentElement;
      let url = 'Unknown URL';

      if (container) {
        const link = container.querySelector('a[href]');
        if (link && link.href) {
          // Send the full URL instead of just hostname
          url = link.href;
        }
      }

      showEmailModal(url, grade, score);
    }
  });
}

// Initialize badge click handlers
addBadgeClickHandlers();

const observer = new MutationObserver(() => {
  scheduleScan(600);
});
observer.observe(document.documentElement, {
  childList: true,
  subtree: true,
});
})();
