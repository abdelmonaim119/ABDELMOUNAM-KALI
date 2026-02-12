const form = document.getElementById('contact-form');
const statusText = document.getElementById('form-status');

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const payload = {
    name: (formData.get('name') || '').toString().trim(),
    email: (formData.get('email') || '').toString().trim(),
    message: (formData.get('message') || '').toString().trim(),
  };

  if (!payload.name || !payload.email || !payload.message) {
    statusText.textContent = 'Please fill in all fields.';
    return;
  }

  statusText.textContent = 'Sending...';
  const response = await fetch('/api/contact', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (response.ok) {
    statusText.textContent = data.message;
    form.reset();
  } else {
    statusText.textContent = data.error || 'An error occurred.';
  }
});
