async function uploadFile(file) {
  const response = await fetch(
    'https://vv1zh748ti.execute-api.us-east-1.amazonaws.com/upload?fileName=' +
    encodeURIComponent(file.name)
  );

  if (!response.ok) {
    throw new Error('Failed to get pre-signed URL');
  }

  const { uploadURL } = await response.json();

  await fetch(uploadURL, {
    method: 'PUT',
    body: file,
    headers: {
      'Content-Type': file.type
    }
  });

  console.log('Upload successful');
}

const fileInput = document.getElementById('file-chooser');
fileInput.addEventListener('change', (event) => {
  const file = event.target.files[0];
  if (file) {
    uploadFile(file).catch(console.error);
  }
});
