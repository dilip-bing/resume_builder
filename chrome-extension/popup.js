// popup.js

document.getElementById('generateBtn').addEventListener('click', async () => {
  const API_BASE = 'https://resume-optimizer-api-fvpd.onrender.com';
  const API_KEY = 'nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU';

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ['content.js']
  }, () => {
    chrome.tabs.sendMessage(tab.id, { action: 'getJobDescription' }, async (response) => {
      if (!response || !response.jobDescription) {
        document.getElementById('result').innerText = 'Could not find job description on this page.';
        return;
      }
      document.getElementById('result').innerText = 'Generating...';
      try {
        // 1. Generate Resume
        const resumeRes = await fetch(`${API_BASE}/api/v1/optimize`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
          },
          body: JSON.stringify({
            job_description: response.jobDescription,
            return_format: 'base64'
          })
        });
        if (!resumeRes.ok) throw new Error('Resume API error');
        const resumeData = await resumeRes.json();
        if (resumeData.status !== 'success' || !resumeData.resume_base64) throw new Error('Resume generation failed');

        // 2. Generate Cover Letter
        const coverRes = await fetch(`${API_BASE}/api/v1/generate-cover-letter`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
          },
          body: JSON.stringify({
            job_description: response.jobDescription,
            resume_text: '', // You can pass a summary or leave blank
            context: '',
            applicant_name: 'Dilip Kumar',
            applicant_email: 'dilip@example.com',
            applicant_phone: '+1-234-567-8900',
            return_format: 'base64'
          })
        });
        if (!coverRes.ok) throw new Error('Cover letter API error');
        const coverData = await coverRes.json();
        if (coverData.status !== 'success' || !coverData.cover_letter_base64) throw new Error('Cover letter generation failed');

        // 3. Provide download links
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML =
          `<a class="download-link" download="resume.docx" href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,${resumeData.resume_base64}">Download Resume</a>` +
          `<a class="download-link" download="cover_letter.docx" href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,${coverData.cover_letter_base64}">Download Cover Letter</a>`;
      } catch (e) {
        document.getElementById('result').innerText = 'Error generating documents.';
      }
    });
  });
});
