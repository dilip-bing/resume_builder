const DEFAULT_SETTINGS = {
  apiBase: 'https://resume-optimizer-api-fvpd.onrender.com',
  apiKey: 'nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU',
  applicantName: 'Dilip Kumar Thirukonda Chandrasekaran',
  applicantEmail: 'dthirukondac@binghamton.edu',
  applicantPhone: '(607) 624-9390',
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
  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId },
    func: () => {
      function extractJobDescription() {
        const normalize = (txt) => (txt || '').replace(/\s+/g, ' ').trim();

        function cleanMainDescription(rawText) {
          if (!rawText) return '';

          const lines = rawText
            .split(/\r?\n/)
            .map((l) => l.trim())
            .filter(Boolean);

          const hardStopTerms = [
            'similar jobs', 'related jobs', 'recommended jobs', 'jobs you may like',
            'people also viewed', 'more jobs', 'job alerts', 'about the company',
            'benefits', 'equal opportunity', 'privacy policy', 'terms of use',
            'report this job', 'share this job'
          ];

          const noisyLineTerms = [
            'save job', 'apply now', 'easy apply', 'follow company', 'posted',
            'views', 'applicants', 'promoted', 'message the job poster'
          ];

          const kept = [];
          for (const line of lines) {
            const lower = line.toLowerCase();

            if (hardStopTerms.some((t) => lower.includes(t))) break;
            if (noisyLineTerms.some((t) => lower === t || lower.startsWith(`${t} `))) continue;
            if (line.length < 3) continue;
            if (line.includes('•') && line.length < 40) continue;

            kept.push(line);
          }

          let text = kept.join('\n').trim();
          if (text.length > 12000) text = text.slice(0, 12000);
          return text;
        }

        // 1) If user highlights the main JD text, always prefer that.
        const selectedText = (window.getSelection && window.getSelection().toString() || '').trim();
        if (selectedText.length > 200) {
           return cleanMainDescription(selectedText);
        }

        const positiveTerms = [
          'job description', 'responsibilities', 'requirements', 'qualifications',
          'minimum qualifications', 'preferred qualifications', 'what you will do',
          'what you ll do', 'about the role', 'experience', 'skills', 'about this job'
        ];
        const negativeTerms = [
          'similar jobs', 'related jobs', 'people also viewed', 'recommended jobs',
          'jobs you may like', 'more jobs', 'search results', 'filters', 'saved jobs'
        ];

        function termHits(text, terms) {
          const lower = text.toLowerCase();
          let hits = 0;
          for (const t of terms) {
            if (lower.includes(t)) hits += 1;
          }
          return hits;
        }

        function elementSignal(el) {
          const marker = `${el.id || ''} ${(el.className || '').toString()} ${el.getAttribute('aria-label') || ''}`.toLowerCase();
          return /job|description|details|posting|jd/.test(marker) ? 1 : 0;
        }

        function scoreElement(el) {
          const text = normalize(el.innerText || '');
          if (text.length < 250) return { score: -9999, text };

          const links = el.querySelectorAll('a').length;
          const pos = termHits(text, positiveTerms);
          const neg = termHits(text, negativeTerms);
          const rect = el.getBoundingClientRect();

          let score = 0;
          score += Math.min(40, text.length / 250);         // enough detail
          score += pos * 8;                                  // JD language present
          score -= neg * 10;                                 // listing/reco language present
          score += elementSignal(el) * 20;                   // id/class hints
          score += Math.max(-20, 18 - links * 2);            // too many links => likely listing

          // Main content tends to be wide and near center viewport.
          if (rect.width > 450) score += 8;
          if (rect.top >= -200 && rect.top <= 1400) score += 6;

          const cx = rect.left + rect.width / 2;
          if (cx > window.innerWidth * 0.2 && cx < window.innerWidth * 0.8) score += 5;

          return { score, text };
        }

        const selectors = [
          '[data-job-description]',
          '[id*="jobDescription" i]',
          '[class*="job-description" i]',
          '[class*="jobDescription" i]',
          '[class*="description" i]',
          '[id*="description" i]',
          'section[aria-label*="job description" i]',
          'main',
          'article'
        ];

        const candidates = new Set();
        for (const sel of selectors) {
          document.querySelectorAll(sel).forEach((el) => candidates.add(el));
        }

        // Add nearby likely containers without scanning every node on the page.
        document.querySelectorAll('section, div').forEach((el) => {
          const marker = `${el.id || ''} ${(el.className || '').toString()}`.toLowerCase();
          if (/job|description|detail|posting/.test(marker)) candidates.add(el);
        });

        let bestText = '';
        let bestScore = -9999;
        candidates.forEach((el) => {
            const { score, text } = scoreElement(el);
          if (score > bestScore) {
            bestScore = score;
            bestText = text;
          }
        });

        // Fallback: largest readable block if scoring found nothing good.
        if (bestText.length < 250) {
          let maxText = '';
          document.querySelectorAll('main, article, section').forEach((node) => {
            const txt = normalize(node.innerText || '');
            if (txt.length > maxText.length) maxText = txt;
          });
            const title = normalize(document.querySelector('h1') && document.querySelector('h1').innerText || '');
            return cleanMainDescription(`${title}\n${maxText}`);
        }

          const title = normalize(document.querySelector('h1') && document.querySelector('h1').innerText || '');
          return cleanMainDescription(`${title}\n${bestText}`);
      }

      return extractJobDescription();
    }
  });

  const jd = (result || '').trim();

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

  // If users previously saved empty strings, keep project defaults for critical fields.
  if (!settings.apiBase || !settings.apiBase.trim()) settings.apiBase = DEFAULT_SETTINGS.apiBase;
  if (!settings.apiKey || !settings.apiKey.trim()) settings.apiKey = DEFAULT_SETTINGS.apiKey;
  if (!settings.applicantName || !settings.applicantName.trim()) settings.applicantName = DEFAULT_SETTINGS.applicantName;
  if (!settings.applicantEmail || !settings.applicantEmail.trim()) settings.applicantEmail = DEFAULT_SETTINGS.applicantEmail;
  if (!settings.applicantPhone || !settings.applicantPhone.trim()) settings.applicantPhone = DEFAULT_SETTINGS.applicantPhone;
  if (!settings.coverContext || !settings.coverContext.trim()) settings.coverContext = DEFAULT_SETTINGS.coverContext;

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
