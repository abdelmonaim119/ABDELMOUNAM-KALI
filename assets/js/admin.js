const oauthStatus = document.getElementById('oauth-status');

fetch('/api/status')
  .then((response) => response.json())
  .then((data) => {
    const authText = data.authenticated
      ? 'Authenticated. token.json is present.'
      : 'Not authenticated. Click the button below to sign in.';

    oauthStatus.textContent = `${authText} Policy: only ${data.owner} can make changes.`;
  })
  .catch(() => {
    oauthStatus.textContent = 'Could not check authentication status.';
  });
