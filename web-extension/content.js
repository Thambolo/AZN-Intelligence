(function() {
// Cross-browser API shim
const api = typeof browser !== 'undefined' ? browser : chrome;

// Guard: only run on Google Search result pages
const {hostname, pathname, search} = window.location;
const isGoogle = /(^|\.)google\./i.test(hostname);
const isSearchPath =
    pathname.startsWith('/search') || pathname === '/';  // includes SPA loads
if (!isGoogle || !isSearchPath) {
  return;
}

const query = new URLSearchParams(search).get('q') || '';

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
    return;
  }
  applyDisplaySettings();
  const results = extractResults();
  if (!results.length) {
    if (retryTimer) clearTimeout(retryTimer);
    retryTimer = setTimeout(sendScan, 1000);
    return;
  }
  inFlight = true;
  sent = true;
  try {
    const maybePromise = api.runtime.sendMessage({
      type: 'GRADEABLE_SCAN',
      results,
    });
  } catch (e) {
    // Silently handle errors
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
      <div style="font-weight: bold; margin-bottom: 4px;">âš ï¸ Accessibility Analysis Failed</div>
      <div style="font-size: 12px; opacity: 0.9;">${error}</div>
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
    showAnalysisProgress(0, msg.data?.totalUrls || 0, 'Starting analysis...');
    return;
  }

  if (msg?.type === 'GRADEABLE_PROGRESS_UPDATE') {
    const {completed, total, results, isComplete} = msg.data || {};

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

  // Hide any progress indicators
  hideAnalysisProgress();

  if (error) {
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
  if (!data || data.length === 0) {
    return;
  }

  // Create URL to result mapping
  const urlToResult = new Map();
  data.forEach(result => {
    if (result.url) {
      urlToResult.set(result.url, result);
    }
  });

  // Track containers and their scores for sorting
  const containers = new Map();

  const headings = getResultHeadings();

  // Show what URLs we extract vs what server sent
  const domUrls = [];
  headings.forEach((h3, domIndex) => {
    const anchor = findAnchorForHeading(h3);
    if (anchor && anchor.href) {
      domUrls.push({
        domIndex,
        url: anchor.href,
        title: h3.textContent?.substring(0, 60) + '...',
        hasExistingBadge: !!h3.querySelector('.gradeable-badge')
      });
    }
  });

  domUrls.forEach(({domIndex, url, hasExistingBadge}) => {
    const serverResult = urlToResult.get(url);
  });

  let badgesCreated = 0;
  let badgesSkipped = 0;

  headings.forEach((h3, domIndex) => {
    // Skip if badge already exists
    if (h3.querySelector('.gradeable-badge')) {
      badgesSkipped++;
      return;
    }

    // Find the URL for this heading
    const anchor = findAnchorForHeading(h3);
    if (!anchor || !anchor.href) {
      return;
    }

    // Look up the result by URL
    const result = urlToResult.get(anchor.href);
    if (!result) {
      return;  // No analysis result for this URL
    }

    const badge = document.createElement('span');
    badge.className = 'gradeable-badge has-icon';
    badge.setAttribute('data-grade', result.grade);
    badge.setAttribute('role', 'note');
    badge.setAttribute(
        'aria-label',
        `Accessibility grade ${result.grade}, score ${result.score}`);

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
      })(result.grade);
      if (icon) badge.appendChild(icon);
    } catch {
    }

    badge.appendChild(
        document.createTextNode(` ${result.grade} (${result.score})`));
    h3.appendChild(badge);
    badgesCreated++;

    // Find container and assign score
    const container = findContainer(h3);
    if (container) {
      if (!container.id) {
        container.id = `gradeable-result-${domIndex}`;
      }
      const currentScore = containers.get(container);
      const newScore = result.score;

      // Use the highest score for containers with multiple results
      if (!containers.has(container) ||
          result.score > containers.get(container)) {
        containers.set(container, result.score);
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

// Function to sort results by score
function sortResultsByScore(data) {
  // This function is called but the sorting logic is already handled in
  // updateResultBadges Keep this as a stub for compatibility
  return;
}

// Function to show analysis progress - Epic Modern Design (Top-Right)
function showAnalysisProgress(completed, total, message) {
  let progressIndicator =
      document.getElementById('gradeable-progress-indicator');

  if (!progressIndicator) {
    // Create main progress indicator in top-right
    progressIndicator = document.createElement('div');
    progressIndicator.id = 'gradeable-progress-indicator';
    progressIndicator.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid transparent;
        border-radius: 20px;
        background: 
          linear-gradient(rgba(0, 0, 0, 0.95), rgba(0, 0, 0, 0.95)) padding-box,
          linear-gradient(135deg, #8b45c6 0%, #14b8a6 100%) border-box;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 
          0 15px 35px rgba(0, 0, 0, 0.2),
          0 0 0 1px rgba(255, 255, 255, 0.1),
          inset 0 0 0 1px rgba(255, 255, 255, 0.05);
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #f1f5f9;
        width: 280px;
        transform: translateX(320px);
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        animation: gradeable-pulse-subtle 3s ease-in-out infinite alternate;
      `;
    document.body.appendChild(progressIndicator);

    // Animate modal in from right
    requestAnimationFrame(() => {
      progressIndicator.style.transform = 'translateX(0)';
    });
  }

  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

  progressIndicator.innerHTML = `
      <div style="position: relative;">
        <!-- Floating Particles -->
        <div class="gradeable-particles" style="position: absolute; width: 100%; height: 100%; overflow: hidden; border-radius: 20px; pointer-events: none;">
          <div style="position: absolute; top: 15%; left: 10%; width: 3px; height: 3px; background: rgba(20, 184, 166, 0.9); border-radius: 50%; animation: gradeable-float1 3s ease-in-out infinite;"></div>
          <div style="position: absolute; top: 50%; right: 15%; width: 4px; height: 4px; background: rgba(241, 245, 249, 0.8); border-radius: 50%; animation: gradeable-float2 2.5s ease-in-out infinite;"></div>
          <div style="position: absolute; bottom: 25%; left: 20%; width: 2px; height: 2px; background: rgba(168, 85, 247, 0.9); border-radius: 50%; animation: gradeable-float3 4s ease-in-out infinite;"></div>
        </div>
        
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <!-- Compact Multi-layered Spinner -->
          <div class="gradeable-spinner" style="position: relative; width: 48px; height: 48px; flex-shrink: 0;">
            <div style="position: absolute; width: 48px; height: 48px; border: 2px solid rgba(255, 255, 255, 0.15); border-top: 2px solid #14b8a6; border-radius: 50%; animation: gradeable-spin 1s linear infinite;"></div>
            <div style="position: absolute; width: 36px; height: 36px; top: 6px; left: 6px; border: 2px solid rgba(255, 255, 255, 0.1); border-right: 2px solid #a855f7; border-radius: 50%; animation: gradeable-spin 1.5s linear infinite reverse;"></div>
            <div style="position: absolute; width: 24px; height: 24px; top: 12px; left: 12px; border: 2px solid rgba(255, 255, 255, 0.1); border-bottom: 2px solid #ffffff; border-radius: 50%; animation: gradeable-spin 2s linear infinite;"></div>
            
            <!-- Center Glow -->
            <div style="position: absolute; width: 12px; height: 12px; top: 18px; left: 18px; background: radial-gradient(circle, #14b8a6 0%, transparent 70%); border-radius: 50%; animation: gradeable-glow 2s ease-in-out infinite alternate;"></div>
          </div>
          
          <!-- Content -->
          <div style="flex: 1; min-width: 0;">
            <div style="font-size: 14px; font-weight: 600; margin-bottom: 4px; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #f1f5f9;">${
      message}</div>
            <div style="font-size: 12px; opacity: 0.85; color: #cbd5e1;">Analyzing patterns...</div>
          </div>
        </div>
        
        <!-- Epic Progress Bar -->
        <div class="gradeable-progress-bar" style="position: relative; width: 100%; height: 6px; background: rgba(71, 85, 105, 0.4); border-radius: 3px; overflow: hidden; margin-bottom: 8px;">
          <div class="gradeable-progress-fill" style="position: absolute; top: 0; left: 0; height: 100%; background: linear-gradient(90deg, #14b8a6 0%, #a855f7 50%, #ffffff 100%); border-radius: 3px; width: ${
      percentage}%; transition: width 0.5s cubic-bezier(0.4, 0.0, 0.2, 1); box-shadow: 0 0 8px rgba(20, 184, 166, 0.5);"></div>
          <div style="position: absolute; top: 0; left: 0; height: 100%; width: 100%; background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.2) 50%, transparent 100%); animation: gradeable-shimmer 1.5s ease-in-out infinite;"></div>
        </div>
        
        <!-- Percentage Display -->
        <div style="text-align: center;">
          <span class="gradeable-percentage" style="font-size: 18px; font-weight: 700; background: linear-gradient(45deg, #14b8a6, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">${
      percentage}%</span>
        </div>
      </div>
    `;

  // Add epic CSS animations if not already present
  if (!document.getElementById('gradeable-progress-styles')) {
    const style = document.createElement('style');
    style.id = 'gradeable-progress-styles';
    style.textContent = `
        @keyframes gradeable-spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        @keyframes gradeable-pulse-subtle {
          0% { 
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2), 
                        0 0 0 1px rgba(139, 69, 198, 0.3), 
                        inset 0 1px 0 rgba(241, 245, 249, 0.1), 
                        0 0 20px rgba(139, 69, 198, 0.15); 
          }
          100% { 
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), 
                        0 0 0 1px rgba(20, 184, 166, 0.4), 
                        inset 0 1px 0 rgba(241, 245, 249, 0.15), 
                        0 0 30px rgba(20, 184, 166, 0.2); 
          }
        }
        
        @keyframes gradeable-glow {
          0% { opacity: 0.6; transform: scale(1); }
          100% { opacity: 1; transform: scale(1.1); }
        }
        
        @keyframes gradeable-float1 {
          0%, 100% { transform: translateY(0px) translateX(0px); opacity: 0.7; }
          50% { transform: translateY(-12px) translateX(6px); opacity: 1; }
        }
        
        @keyframes gradeable-float2 {
          0%, 100% { transform: translateY(0px) translateX(0px); opacity: 0.5; }
          50% { transform: translateY(-8px) translateX(-4px); opacity: 0.9; }
        }
        
        @keyframes gradeable-float3 {
          0%, 100% { transform: translateY(0px) translateX(0px); opacity: 0.8; }
          50% { transform: translateY(-15px) translateX(8px); opacity: 0.6; }
        }
        
        @keyframes gradeable-shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        
        /* Hover effect for discoverability */
        #gradeable-progress-indicator:hover {
          transform: translateX(0) scale(1.02);
          box-shadow: 
            0 20px 45px rgba(0, 0, 0, 0.3),
            0 0 0 1px rgba(20, 184, 166, 0.5),
            inset 0 1px 0 rgba(241, 245, 249, 0.2),
            0 0 40px rgba(139, 69, 198, 0.3);
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
          #gradeable-progress-indicator {
            background: 
              linear-gradient(rgba(0, 0, 0, 0.98), rgba(0, 0, 0, 0.98)) padding-box,
              linear-gradient(135deg, #8b45c6 0%, #14b8a6 100%) border-box;
            border: 2px solid transparent;
            border-radius: 20px;
            color: #f1f5f9;
          }
          
          @keyframes gradeable-pulse-subtle {
            0% { 
              box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4), 
                          0 0 0 1px rgba(139, 69, 198, 0.4), 
                          inset 0 1px 0 rgba(241, 245, 249, 0.1), 
                          0 0 20px rgba(139, 69, 198, 0.2); 
            }
            100% { 
              box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5), 
                          0 0 0 1px rgba(20, 184, 166, 0.5), 
                          inset 0 1px 0 rgba(241, 245, 249, 0.15), 
                          0 0 30px rgba(20, 184, 166, 0.25); 
            }
          }
        }
        
        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {
          #gradeable-progress-indicator {
            animation: none;
            transition: transform 0.2s ease;
          }
          #gradeable-progress-indicator * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
          }
        }
      `;
    document.head.appendChild(style);
  }
}

// Function to hide analysis progress - Epic Slide Out
function hideAnalysisProgress() {
  const progressIndicator =
      document.getElementById('gradeable-progress-indicator');

  if (progressIndicator) {
    // Animate out to the right
    progressIndicator.style.transform = 'translateX(320px)';
    progressIndicator.style.opacity = '0.8';

    setTimeout(() => {
      progressIndicator.remove();
    }, 400);
  }
}

// Function to sort results by score
function sortResultsByScore(data) {
  if (!data || data.length === 0) {
    return;
  }

  const urlToResult = new Map(data.map((r) => [r.url, r]));
  const containers = new Map();

  // Build container map with scores - iterate through DOM headings and match by
  // URL
  const headings = getResultHeadings();

  headings.forEach((h3, index) => {
    const anchor = findAnchorForHeading(h3);
    if (!anchor || !anchor.href) {
      return;
    }

    const result = urlToResult.get(anchor.href);
    if (!result) {
      console.warn(
          `ðŸ“Š [${index}] No result for URL in sorting:`,
          anchor.href.substring(0, 60));
      return;
    }

    const container = findContainer(h3);
    if (container) {
      const currentScore = containers.get(container);
      const newScore = result.score;

      // Use the first result's score for the container (main result)
      // This ensures the main result determines the container's ranking
      if (!containers.has(container)) {
        containers.set(container, result.score);
        console.log(`ðŸ“¦ [${index}] Sorting container score: ${
            currentScore || 'none'} â†’ ${newScore} (main result)`);
      } else {
        console.log(`ðŸ“¦ [${index}] Container score kept: ${
            currentScore} (skipping sub-result: ${newScore})`);
      }
    } else {
    }
  });

  // Reorder containers by score descending
  const sortedContainers =
      Array.from(containers.entries()).sort((a, b) => b[1] - a[1]);

  // Find the appropriate parent container for reordering
  let parent = null;
  const possibleParents = [
    '#rso .MjjYud',  // Try specific MjjYud container first
    '#rso',          // Main search results container
    '#search',       // Fallback search container
    '.s'             // Legacy search container
  ];

  for (const selector of possibleParents) {
    parent = document.querySelector(selector);
    if (parent && sortedContainers.length > 0) {
      // Check if any of our containers are actually children of this parent
      const hasMatchingChildren = sortedContainers.some(([container]) => {
        let element = container;
        let depth = 0;
        while (element && element !== parent && depth < 10) {
          element = element.parentNode;
          depth++;
        }
        return element === parent;
      });

      if (hasMatchingChildren) {
        break;
      }
    }
    parent = null;  // Reset if not valid
  }

  // If no standard parent found, try to find the actual parent of our
  // containers
  if (!parent && sortedContainers.length > 0) {
    const firstContainer = sortedContainers[0][0];
    let testParent = firstContainer.parentNode;
    let depth = 0;

    while (testParent && depth < 5) {
      const childContainers = sortedContainers.filter(
          ([container]) => container.parentNode === testParent);
      if (childContainers.length > 1) {
        parent = testParent;
        break;
      }
      testParent = testParent.parentNode;
      depth++;
    }
  }

  if (parent && sortedContainers.length > 0) {
    let reorderedCount = 0;

    sortedContainers.forEach(([container, score], index) => {
      // More flexible parent checking - allow containers at different nesting
      // levels
      let isChildOfParent = false;
      let element = container;
      let depth = 0;

      while (element && depth < 10) {
        if (element.parentNode === parent) {
          isChildOfParent = true;
          break;
        }
        element = element.parentNode;
        depth++;
      }

      if (container && isChildOfParent) {
        // For nested containers, move the actual direct child of parent
        let elementToMove = container;
        while (elementToMove.parentNode !== parent &&
               elementToMove.parentNode) {
          elementToMove = elementToMove.parentNode;
        }

        parent.appendChild(elementToMove);
        reorderedCount++;
      }
    });
  }

  // Sort sub-URLs within containers
  let subUrlsProcessed = 0;
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
        rows.forEach((row, index) => {
          tbody.appendChild(row);
          subUrlsProcessed++;
        });
      }
    }
  });
}

// Function to show analysis summary
function showAnalysisSummary(summary) {
  const {total, successful, averageScore} = summary;

  // Could add a temporary summary notification here if desired
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
