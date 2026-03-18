const DEFAULT_SETTINGS = {
  apiBase: 'https://resume-optimizer-api-fvpd.onrender.com',
  apiKey: '',
  applicantName: 'Dilip Kumar',
  applicantEmail: '',
  applicantPhone: '',
  coverContext: 'Passionate about technology and eager to contribute to innovative projects',
  personalLocation: ''
};

let settings = { ...DEFAULT_SETTINGS };

const el = {
  jobDescription: document.getElementById('jobDescription'),
  charMeta: document.getElementById('charMeta'),
  personalLocation: document.getElementById('personalLocation'),
  extractBtn: document.getElementById('extractBtn'),
  clearBtn: document.getElementById('clearBtn'),
  optimizeBtn: document.getElementById('optimizeBtn'),
  coverLetterBtn: document.getElementById('coverLetterBtn'),
  status: document.getElementById('status'),
  apiBase: document.getElementById('apiBase'),
  apiKey: document.getElementById('apiKey'),
  applicantName: document.getElementById('applicantName'),
  applicantEmail: document.getElementById('applicantEmail'),
  applicantPhone: document.getElementById('applicantPhone'),
  coverContext: document.getElementById('coverContext'),
  saveSettingsBtn: document.getElementById('saveSettingsBtn')
};

function updateCharMeta() {
  el.charMeta.textContent = `${el.jobDescription.value.trim().length} characters`;
}

function showStatus(message, type = 'ok') {
  el.status.className = '';
  el.status.classList.add(type);
  el.status.textContent = message;
}

function setBusy(isBusy) {
  el.extractBtn.disabled = isBusy;
  el.clearBtn.disabled = isBusy;
  el.optimizeBtn.disabled = isBusy;
  el.coverLetterBtn.disabled = isBusy;
  el.saveSettingsBtn.disabled = isBusy;
}

function base64ToBlob(base64, mimeType) {
  const binary = atob(base64);
  const len = binary.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i += 1) bytes[i] = binary.charCodeAt(i);
  return new Blob([bytes], { type: mimeType });
}

async function saveBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  try {
    await chrome.downloads.download({ url, filename, saveAs: true });
  } finally {
    setTimeout(() => URL.revokeObjectURL(url), 30000);
  }
}

async function getActiveTabId() {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tabs || !tabs[0] || typeof tabs[0].id !== 'number') {
    throw new Error('No active tab found.');
  }
  return tabs[0].id;
}

async function extractFromPage() {
  const tabId = await getActiveTabId();
  await chrome.scripting.executeScript({
    target: { tabId },
    files: ['content.js']
  });

  const response = await chrome.tabs.sendMessage(tabId, { action: 'getJobDescription' });
  const jd = response && response.jobDescription ? response.jobDescription.trim() : '';

  if (!jd || jd.length < 120) {
    showStatus('Could not confidently detect job description. Please paste manually.', 'warn');
    return;
  }

  el.jobDescription.value = jd;
  updateCharMeta();
  showStatus('Job description extracted from current page.', 'ok');
}

async function loadSettings() {
  const data = await chrome.storage.local.get('resumeExtSettings');
  settings = { ...DEFAULT_SETTINGS, ...(data.resumeExtSettings || {}) };

  el.apiBase.value = settings.apiBase;
  el.apiKey.value = settings.apiKey;
  el.applicantName.value = settings.applicantName;
  el.applicantEmail.value = settings.applicantEmail;
  el.applicantPhone.value = settings.applicantPhone;
  el.coverContext.value = settings.coverContext;
  el.personalLocation.value = settings.personalLocation;
}

async function persistSettings() {
  settings = {
    apiBase: el.apiBase.value.trim(),
    apiKey: el.apiKey.value.trim(),
    applicantName: el.applicantName.value.trim(),
    applicantEmail: el.applicantEmail.value.trim(),
    applicantPhone: el.applicantPhone.value.trim(),
    coverContext: el.coverContext.value.trim(),
    personalLocation: el.personalLocation.value.trim()
  };

  await chrome.storage.local.set({ resumeExtSettings: settings });
  showStatus('Settings saved.', 'ok');
}

function getJobDescriptionInput() {
  return el.jobDescription.value.trim();
}

async function callApi(path, payload) {
  if (!settings.apiBase || !settings.apiKey) {
    throw new Error('Please set API Base URL and API Key in Settings first.');
  }

  const resp = await fetch(`${settings.apiBase}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': settings.apiKey
    },
    body: JSON.stringify(payload)
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`API error ${resp.status}: ${text}`);
  }

  return resp.json();
}

async function optimizeAndDownloadResume() {
  const jobDescription = getJobDescriptionInput();
  if (!jobDescription) {
    showStatus('Please provide a job description first.', 'warn');
    return;
  }

  setBusy(true);
  showStatus('Optimizing resume and generating DOCX...', 'ok');
  try {
    const data = await callApi('/api/v1/optimize', {
      job_description: jobDescription,
      job_location: el.personalLocation.value.trim(),
      return_format: 'base64'
    });

    if (data.status !== 'success' || !data.resume_base64) {
      throw new Error(data.message || 'Resume optimization failed.');
    }

    const blob = base64ToBlob(
      data.resume_base64,
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    );
    const filename = data.filename || 'resume_optimized.docx';
    await saveBlob(blob, filename);

    showStatus('Resume optimized and downloaded.', 'ok');
  } catch (err) {
    showStatus(`Resume generation failed: ${err.message}`, 'error');
  } finally {
    setBusy(false);
  }
}

async function generateAndDownloadCoverLetter() {
  const jobDescription = getJobDescriptionInput();
  if (!jobDescription) {
    showStatus('Please provide a job description first.', 'warn');
    return;
  }

  setBusy(true);
  showStatus('Generating cover letter DOCX...', 'ok');
  try {
    const data = await callApi('/api/v1/generate-cover-letter', {
      job_description: jobDescription,
      resume_text: '',
      context: settings.coverContext,
      applicant_name: settings.applicantName,
      applicant_email: settings.applicantEmail,
      applicant_phone: settings.applicantPhone,
      return_format: 'base64'
    });

    if (data.status !== 'success' || !data.cover_letter_base64) {
      throw new Error(data.message || 'Cover letter generation failed.');
    }

    const blob = base64ToBlob(
      data.cover_letter_base64,
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    );
    const filename = data.filename || 'cover_letter.docx';
    await saveBlob(blob, filename);

    showStatus('Cover letter generated and downloaded.', 'ok');
  } catch (err) {
    showStatus(`Cover letter generation failed: ${err.message}`, 'error');
  } finally {
    setBusy(false);
  }
}

async function init() {
  await loadSettings();
  updateCharMeta();

  try {
    await extractFromPage();
  } catch (err) {
    showStatus('Could not auto-extract from page. Paste job description manually.', 'warn');
  }
}

el.jobDescription.addEventListener('input', updateCharMeta);
el.extractBtn.addEventListener('click', async () => {
  setBusy(true);
  try {
    await extractFromPage();
  } catch (err) {
    showStatus(`Extraction failed: ${err.message}`, 'error');
  } finally {
    setBusy(false);
  }
});
el.clearBtn.addEventListener('click', () => {
  el.jobDescription.value = '';
  updateCharMeta();
  showStatus('Job description cleared.', 'ok');
});
el.saveSettingsBtn.addEventListener('click', persistSettings);
el.optimizeBtn.addEventListener('click', async () => {
  await persistSettings();
  await optimizeAndDownloadResume();
});
el.coverLetterBtn.addEventListener('click', async () => {
  await persistSettings();
  await generateAndDownloadCoverLetter();
});

init();
