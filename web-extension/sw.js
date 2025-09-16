// Background service worker for Grade-Able
// For now we simulate backend scoring so you can test UI fast.
const api = typeof browser !== "undefined" ? browser : chrome;

// Helper function to send debug messages to content script for logging
function sendDebugLog(tabId, message, data = {}) {
  try {
    api.tabs.sendMessage(tabId, {
      type: "GRADEABLE_DEBUG_LOG",
      data: {
        message,
        details: data,
        timestamp: new Date().toISOString(),
        source: "ServiceWorker",
      },
    });
  } catch (error) {
    // Fallback to console if tab messaging fails
    console.log(`[Grade-Able][SW] ${message}`, data);
  }
}

// Helper function to send error messages to content script for logging
function sendErrorLog(tabId, message, error = {}) {
  try {
    api.tabs.sendMessage(tabId, {
      type: "GRADEABLE_ERROR_LOG",
      data: {
        message,
        error: error.message || error,
        stack: error.stack,
        timestamp: new Date().toISOString(),
        source: "ServiceWorker",
      },
    });
  } catch (err) {
    // Fallback to console if tab messaging fails
    console.error(`[Grade-Able][SW] ${message}`, error);
  }
}

api.runtime.onMessage.addListener((msg, sender) => {
  if (msg?.type === "GRADEABLE_SCAN" && sender?.tab?.id) {
    sendDebugLog(sender.tab.id, "GRADEABLE_SCAN received", {
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
    //   type: "GRADEABLE_RESULTS",
    //   data: dummy,
    // });

    // Concurrent processing with individual URL auditing and progressive
    // updates:
    (async () => {
      const results = msg.results || [];
      const tabId = sender.tab.id;

      sendDebugLog(tabId, "Starting concurrent analysis", {
        tabId,
        urlCount: results.length,
        urls: results.slice(0, 3).map((r) => r.url),
      });

      // Track completed analyses for progressive sorting
      const completedAnalyses = new Map();
      let completedCount = 0;

      // Send initial loading state
      api.tabs.sendMessage(tabId, {
        type: "GRADEABLE_ANALYSIS_STARTED",
        data: {
          totalUrls: results.length,
          message: `Starting analysis of ${results.length} URLs...`,
        },
      });

      // Function to analyze a single URL with retry mechanism
      const analyzeUrl = async (searchResult, index) => {
        const maxRetries = 3;
        const retryDelay = 1000; // 1 second

        for (let attempt = 1; attempt <= maxRetries; attempt++) {
          try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 45000); // 45 second timeout

            sendDebugLog(
              tabId,
              `Analyzing URL ${index + 1}/${results.length}`,
              {
                url: searchResult.url,
                attempt,
              }
            );

            const res = await fetch("http://localhost:8000/audit", {
              // const res = await fetch(
              //   "https://azn-intelligence-grade-abled.onrender.com/audit",
              //   {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
              },
              body: JSON.stringify({
                url: searchResult.url,
                timeout: 30,
              }),
              signal: controller.signal,
              mode: "cors",
              credentials: "omit",
            });
            clearTimeout(timeoutId);

            // ADD THIS DEBUG LOGGING
            const responseText = await res.text();
            sendDebugLog(
              tabId,
              `[Grade-Able][SW] Raw response for ${searchResult.url}:`,
              {
                status: res.status,
                statusText: res.statusText,
                headers: Object.fromEntries(res.headers.entries()),
                body: responseText,
              }
            );

            if (!res.ok) {
              sendDebugLog(tabId, `Non-200 response for ${searchResult.url}`, {
                status: res.status,
                statusText: res.statusText,
                responseBody: responseText,
              });
              throw new Error(
                `HTTP error! status: ${res.status} ${res.statusText}`
              );
            }

            const data = JSON.parse(responseText);
            sendDebugLog(
              tabId,
              `[Grade-Able][SW] Received analysis for ${searchResult.url}`,
              { data }
            );

            if (data.success && data.result) {
              const analysisResult = {
                ...searchResult,
                url: data.result.url,
                grade: data.result.grade,
                score: data.result.score,
                issues: data.result.issues || [],
                analysis_time: data.result.analysis_time_seconds,
                timestamp: data.result.timestamp,
                originalIndex: index,
              };

              completedAnalyses.set(searchResult.url, analysisResult);
              completedCount++;

              sendDebugLog(
                tabId,
                `Analysis completed (${completedCount}/${results.length})`,
                {
                  url: searchResult.url,
                  grade: data.result.grade,
                  score: data.result.score,
                  data: analysisResult,
                }
              );

              // Send progressive update with current completed analyses
              const sortedResults = Array.from(completedAnalyses.values()).sort(
                (a, b) => {
                  // Sort by score (descending), then by grade, then by
                  // original index
                  if (b.score !== a.score) return b.score - a.score;
                  const gradeOrder = { AAA: 4, AA: 3, A: 2, Fail: 1, Error: 0 };
                  if (gradeOrder[b.grade] !== gradeOrder[a.grade]) {
                    return gradeOrder[b.grade] - gradeOrder[a.grade];
                  }
                  return a.originalIndex - b.originalIndex;
                }
              );

              api.tabs.sendMessage(tabId, {
                type: "GRADEABLE_PROGRESS_UPDATE",
                data: {
                  completed: completedCount,
                  total: results.length,
                  results: sortedResults,
                  isComplete: completedCount === results.length,
                },
              });

              return analysisResult;
            } else {
              throw new Error(data.error || "Unknown analysis error");
            }
          } catch (err) {
            sendErrorLog(
              tabId,
              `Analysis attempt ${attempt} failed for ${searchResult.url}`,
              err
            );

            if (attempt === maxRetries) {
              // All retries exhausted, create error result
              const errorResult = {
                ...searchResult,
                url: searchResult.url,
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
                error: err.message,
                originalIndex: index,
              };

              completedAnalyses.set(searchResult.url, errorResult);
              completedCount++;

              sendErrorLog(
                tabId,
                `All retries exhausted for ${searchResult.url}`
              );

              // Send progress update with error result
              const sortedResults = Array.from(completedAnalyses.values()).sort(
                (a, b) => {
                  if (b.score !== a.score) return b.score - a.score;
                  const gradeOrder = { AAA: 4, AA: 3, A: 2, Fail: 1, Error: 0 };
                  if (gradeOrder[b.grade] !== gradeOrder[a.grade]) {
                    return gradeOrder[b.grade] - gradeOrder[a.grade];
                  }
                  return a.originalIndex - b.originalIndex;
                }
              );

              api.tabs.sendMessage(tabId, {
                type: "GRADEABLE_PROGRESS_UPDATE",
                data: {
                  completed: completedCount,
                  total: results.length,
                  results: sortedResults,
                  isComplete: completedCount === results.length,
                },
              });

              return errorResult;
            } else {
              // Wait before retrying
              await new Promise((resolve) => setTimeout(resolve, retryDelay));
            }
          }
        }
      };

      // Start concurrent analysis for all URLs
      const analysisPromises = results.map((searchResult, index) =>
        analyzeUrl(searchResult, index)
      );

      try {
        // Wait for all analyses to complete
        await Promise.allSettled(analysisPromises);

        // Send final results with complete sorting
        const finalResults = Array.from(completedAnalyses.values()).sort(
          (a, b) => {
            if (b.score !== a.score) return b.score - a.score;
            const gradeOrder = { AAA: 4, AA: 3, A: 2, Fail: 1, Error: 0 };
            if (gradeOrder[b.grade] !== gradeOrder[a.grade]) {
              return gradeOrder[b.grade] - gradeOrder[a.grade];
            }
            return a.originalIndex - b.originalIndex;
          }
        );

        sendDebugLog(tabId, "All analyses completed", {
          totalAnalyzed: finalResults.length,
          successfulAnalyses: finalResults.filter((r) => r.grade !== "Error")
            .length,
          averageScore:
            finalResults.length > 0
              ? Math.round(
                  finalResults.reduce((sum, r) => sum + r.score, 0) /
                    finalResults.length
                )
              : 0,
        });

        api.tabs.sendMessage(tabId, {
          type: "GRADEABLE_RESULTS",
          data: finalResults,
          summary: {
            total: finalResults.length,
            successful: finalResults.filter((r) => r.grade !== "Error").length,
            averageScore:
              finalResults.length > 0
                ? Math.round(
                    finalResults.reduce((sum, r) => sum + r.score, 0) /
                      finalResults.length
                  )
                : 0,
          },
        });
      } catch (error) {
        sendErrorLog(
          tabId,
          "Unexpected error during concurrent analysis",
          error
        );

        api.tabs.sendMessage(tabId, {
          type: "GRADEABLE_RESULTS",
          data: Array.from(completedAnalyses.values()),
          error: `Analysis completed with errors: ${error.message}`,
        });
      }
    })();
  }
});
