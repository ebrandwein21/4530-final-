// app.js
const API_URL = 'https://vv1zh748ti.execute-api.us-east-1.amazonaws.com/upload';

const uploadForm = document.getElementById('upload-form');
const statusBox = document.getElementById('status');

// Simple helper to show messages
function setStatus(message, isError = false) {
  statusBox.textContent = message;
  statusBox.classList.toggle('status-error', isError);
}

uploadForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const subjectIdInput = document.getElementById('uploadSubjectId');
  const fileInput = document.getElementById('csvFile');

  const subjectId = subjectIdInput.value.trim();
  const file = fileInput.files[0];

  if (!subjectId) {
    setStatus('Please enter a Player / Patient ID.', true);
    return;
  }

  if (!file) {
    setStatus('Please choose a CSV file to upload.', true);
    return;
  }

  try {
    setStatus('Uploading file, please wait...');

    // Read the CSV file as text
    const fileText = await file.text();

    const payload = {
      subjectId,
      filename: file.name,
      fileContent: fileText
    };

    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`API returned ${response.status}: ${text}`);
    }

    const data = await response.json().catch(() => ({}));

    setStatus(
      `Upload successful.\nS3 key: ${data.key || '(see Lambda logs)'}`,
      false
    );
  } catch (err) {
    console.error(err);
    setStatus(`Error uploading file:\n${err.message || 'Unknown error'}`, true);
  }
});
