const api = typeof browser !== "undefined" ? browser : chrome;

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("rescan");
  const highContrast = document.getElementById("highContrast");
  const cbPatterns = document.getElementById("cbPatterns");
  if (!btn) return;

  // Prevent FOUC focus outline in popup (previous inline code)
  try {
    btn.focus({ preventScroll: true });
    if (document.activeElement === btn) document.activeElement.blur();
  } catch {}

  async function applySettingsToTab(tabId) {
    const { a11yHighContrast = false, a11yCbPatterns = false } =
      (await api.storage?.sync?.get?.([
        "a11yHighContrast",
        "a11yCbPatterns",
      ])) || {};
    // Set attributes on :root of the page; content script will also read storage at inject time
    await api.scripting?.executeScript?.({
      target: { tabId },
      func: (opts) => {
        try {
          const root = document.documentElement;
          if (opts.high) root.setAttribute("data-a11y-high-contrast", "1");
          else root.removeAttribute("data-a11y-high-contrast");
          if (opts.cb) root.setAttribute("data-a11y-cb-patterns", "1");
          else root.removeAttribute("data-a11y-cb-patterns");
        } catch {}
      },
      args: [{ high: a11yHighContrast, cb: a11yCbPatterns }],
    });
  }

  btn.addEventListener("click", async () => {
    try {
      const [tab] = await api.tabs.query({ active: true, currentWindow: true });
      if (!tab?.id) return;
      await applySettingsToTab(tab.id);
      console.log("[A11ySearchRanker][Popup] Rescan clicked", {
        tabId: tab.id,
        url: tab.url,
      });
      const send = api.tabs.sendMessage(tab.id, { type: "A11Y_RESCAN" });
      if (send && typeof send.catch === "function") {
        await send.catch((e) =>
          console.log(
            "[A11ySearchRanker][Popup] sendMessage error:",
            e?.message
          )
        );
      } else if (typeof api.runtime?.lastError !== "undefined") {
        api.tabs.sendMessage(tab.id, { type: "A11Y_RESCAN" }, () => {
          const err = api.runtime.lastError;
          if (err)
            console.log(
              "[A11ySearchRanker][Popup] sendMessage error:",
              err.message
            );
        });
      }
    } catch (err) {
      console.log(
        "[A11ySearchRanker][Popup] Rescan failed:",
        err?.message || err
      );
    }
  });

  // Load settings into UI
  (async () => {
    try {
      const data =
        (await api.storage?.sync?.get?.([
          "a11yHighContrast",
          "a11yCbPatterns",
        ])) || {};
      if (highContrast) highContrast.checked = !!data.a11yHighContrast;
      if (cbPatterns) cbPatterns.checked = !!data.a11yCbPatterns;
    } catch {}
  })();

  async function saveAndApply() {
    try {
      await api.storage?.sync?.set?.({
        a11yHighContrast: !!highContrast?.checked,
        a11yCbPatterns: !!cbPatterns?.checked,
      });
      const [tab] = await api.tabs.query({ active: true, currentWindow: true });
      if (tab?.id) await applySettingsToTab(tab.id);
    } catch {}
  }

  highContrast?.addEventListener("change", saveAndApply);
  cbPatterns?.addEventListener("change", saveAndApply);
});
