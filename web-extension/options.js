// Options page script for AZN Intelligence extension
const api = typeof browser !== 'undefined' ? browser : chrome;

document.addEventListener('DOMContentLoaded', async () => {
  const serverUrlInput = document.getElementById('serverUrl');
  const saveBtn = document.getElementById('saveBtn');
  const status = document.getElementById('status');

  // Load existing options
  try {
    const result = await api.storage.sync.get(['serverUrl']);
    if (result.serverUrl) {
      serverUrlInput.value = result.serverUrl;
    } else {
      serverUrlInput.value = 'http://localhost:8000';
    }
  } catch (e) {
    console.error('Error loading options:', e);
    serverUrlInput.value = 'http://localhost:8000';
  }

  // Save options
  saveBtn.addEventListener('click', async () => {
    const serverUrl = serverUrlInput.value.trim();

    if (!serverUrl) {
      showStatus('Please enter a server URL', 'error');
      return;
    }

    // Basic URL validation
    try {
      new URL(serverUrl);
    } catch (e) {
      showStatus(
          'Please enter a valid URL (e.g., http://localhost:8000)', 'error');
      return;
    }

    try {
      await api.storage.sync.set({serverUrl});
      showStatus('Options saved successfully! 🎉', 'success');
    } catch (e) {
      console.error('Error saving options:', e);
      showStatus('Error saving options. Please try again.', 'error');
    }
  });

  function showStatus(message, type) {
    status.textContent = message;
    status.className = `status ${type}`;
    status.style.display = 'block';

    setTimeout(() => {
      status.style.display = 'none';
    }, 3000);
  }
});
