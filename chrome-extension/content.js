// Content script: Extract job description from the page
function extractJobDescription() {
  // Try to find a job description by common selectors
  const selectors = [
    '[data-job-description]',
    '.job-description',
    '#jobDescriptionText',
    'section[aria-label*="job description" i]',
    'article',
    'main',
    'body'
  ];
  for (const sel of selectors) {
    const el = document.querySelector(sel);
    if (el && el.innerText.length > 100) {
      return el.innerText.trim();
    }
  }
  // Fallback: grab the largest text block
  let maxText = '';
  document.querySelectorAll('p,div,section,article').forEach(el => {
    const text = el.innerText;
    if (text && text.length > maxText.length) maxText = text;
  });
  return maxText.trim();
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === 'getJobDescription') {
    const jobDesc = extractJobDescription();
    sendResponse({ jobDescription: jobDesc });
  }
  return true;
});
