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
    const { gradeableHighContrast = false, gradeableCbPatterns = false } =
      (await api.storage?.sync?.get?.([
        "gradeableHighContrast",
        "gradeableCbPatterns",
      ])) || {};
    // Set attributes on :root of the page; content script will also read storage at inject time
    await api.scripting?.executeScript?.({
      target: { tabId },
      func: (opts) => {
        try {
          const root = document.documentElement;
          if (opts.high) root.setAttribute("data-gradeable-high-contrast", "1");
          else root.removeAttribute("data-gradeable-high-contrast");
          if (opts.cb) root.setAttribute("data-gradeable-cb-patterns", "1");
          else root.removeAttribute("data-gradeable-cb-patterns");
        } catch {}
      },
      args: [{ high: gradeableHighContrast, cb: gradeableCbPatterns }],
    });
  }

  btn.addEventListener("click", async () => {
    try {
      const [tab] = await api.tabs.query({ active: true, currentWindow: true });
      if (!tab?.id) return;
      await applySettingsToTab(tab.id);
      console.log("[Grade-Able][Popup] Rescan clicked", {
        tabId: tab.id,
        url: tab.url,
      });
      const send = api.tabs.sendMessage(tab.id, { type: "GRADEABLE_RESCAN" });
      if (send && typeof send.catch === "function") {
        await send.catch((e) =>
          console.log("[Grade-Able][Popup] sendMessage error:", e?.message)
        );
      } else if (typeof api.runtime?.lastError !== "undefined") {
        api.tabs.sendMessage(tab.id, { type: "GRADEABLE_RESCAN" }, () => {
          const err = api.runtime.lastError;
          if (err)
            console.log("[Grade-Able][Popup] sendMessage error:", err.message);
        });
      }
    } catch (err) {
      console.log("[Grade-Able][Popup] Rescan failed:", err?.message || err);
    }
  });

  // Load settings into UI
  (async () => {
    try {
      const data =
        (await api.storage?.sync?.get?.([
          "gradeableHighContrast",
          "gradeableCbPatterns",
        ])) || {};
      if (highContrast) highContrast.checked = !!data.gradeableHighContrast;
      if (cbPatterns) cbPatterns.checked = !!data.gradeableCbPatterns;
    } catch {}
  })();

  async function saveAndApply() {
    try {
      await api.storage?.sync?.set?.({
        gradeableHighContrast: !!highContrast?.checked,
        gradeableCbPatterns: !!cbPatterns?.checked,
      });
      const [tab] = await api.tabs.query({ active: true, currentWindow: true });
      if (tab?.id) await applySettingsToTab(tab.id);
    } catch {}
  }

  highContrast?.addEventListener("change", saveAndApply);
  cbPatterns?.addEventListener("change", saveAndApply);
});
