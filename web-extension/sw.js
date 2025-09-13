// Background service worker for A11ySearchRanker
// For now we simulate backend scoring so you can test UI fast.
const api = typeof browser !== "undefined" ? browser : chrome;

api.runtime.onMessage.addListener((msg, sender) => {
  if (msg?.type === "A11Y_SCAN" && sender?.tab?.id) {
    console.debug("[A11ySearchRanker][SW] A11Y_SCAN received", {
      tabId: sender.tab.id,
      resultCount: (msg.results || []).length,
      sample: (msg.results || []).slice(0, 3),
    });

    // Dummy response - replace with backend call when ready
    // const dummy = (msg.results || []).map((r, i) => ({
    //   url: r.url,
    //   grade: ["A", "AA", "AAA", "Fail"][i % 4],
    //   score: Math.floor(Math.random() * 100),
    // }));

    // api.tabs.sendMessage(sender.tab.id, {
    //   type: "A11Y_RESULTS",
    //   data: dummy,
    // });

    // Example backend integration with retry mechanism:
    (async () => {
      const maxRetries = 3;
      const retryDelay = 2000; // 2 seconds

      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
          const urls = (msg.results || []).map((r) => r.url);
          console.debug("[A11ySearchRanker][SW] Sending to backend", {
            attempt,
            urlCount: urls.length,
            urls: urls.slice(0, 3),
          });

          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

          const res = await fetch("http://localhost:8000/audit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ urls }),
            signal: controller.signal,
          });

          clearTimeout(timeoutId);

          if (!res.ok) {
            throw new Error(
              `Server responded with ${res.status}: ${res.statusText}`
            );
          }

          const data = await res.json();
          console.debug("[A11ySearchRanker][SW] Backend response", {
            attempt,
            resultCount: data.results?.length || 0,
          });

          api.tabs.sendMessage(sender.tab.id, {
            type: "A11Y_RESULTS",
            data: data.results || [],
          });
          return; // Success, exit retry loop
        } catch (err) {
          console.error(
            `[A11ySearchRanker][SW] Attempt ${attempt} failed:`,
            err
          );

          if (attempt === maxRetries) {
            // All retries exhausted, send error response
            console.error("[A11ySearchRanker][SW] All retries exhausted");

            const fallbackResults = (msg.results || []).map((r, i) => ({
              url: r.url,
              grade: "Error",
              score: 0,
              issues: [
                {
                  component: "Connection",
                  message: `Failed to analyze after ${maxRetries} attempts: ${err.message}`,
                  passed: 0,
                  total: 1,
                },
              ],
            }));

            api.tabs.sendMessage(sender.tab.id, {
              type: "A11Y_RESULTS",
              data: fallbackResults,
              error: `Failed after ${maxRetries} attempts: ${err.message}`,
            });
          } else {
            // Wait before retrying
            console.debug(
              `[A11ySearchRanker][SW] Retrying in ${retryDelay}ms...`
            );
            await new Promise((resolve) => setTimeout(resolve, retryDelay));
          }
        }
      }
    })();
  }
});
