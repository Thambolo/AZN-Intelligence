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
    const dummy = (msg.results || []).map((r, i) => ({
      url: r.url,
      grade: ["A", "AA", "AAA", "Fail"][i % 4],
      score: Math.floor(Math.random() * 100),
    }));

    api.tabs.sendMessage(sender.tab.id, {
      type: "A11Y_RESULTS",
      data: dummy,
    });

    // Example backend integration (disabled by default):
    // (async () => {
    //   try {
    //     const urls = (msg.results || []).map((r) => r.url);
    //     const res = await fetch("http://localhost:8000/audit", {
    //       method: "POST",
    //       headers: { "Content-Type": "application/json" },
    //       body: JSON.stringify({ urls }),
    //     });
    //     const data = await res.json();
    //     api.tabs.sendMessage(sender.tab.id, { type: "A11Y_RESULTS", data });
    //   } catch (err) {
    //     console.error("[A11ySearchRanker][SW] Backend error", err);
    //   }
    // })();
  }
});
