export function authorizationCodeFromRedirect(input, redirectUri, expectedState) {
  let actual;
  try { actual = new URL(input.trim()); }
  catch { throw new Error('Paste the full callback URL, including https:// and the code parameter'); }
  const expected = new URL(redirectUri);
  if (actual.origin !== expected.origin || actual.pathname !== expected.pathname) throw new Error('Callback URL does not match INSTAGRAM_REDIRECT_URI');
  if (actual.searchParams.get('state') !== expectedState) throw new Error('Invalid authorization state');
  const error = actual.searchParams.get('error') || actual.searchParams.get('error_reason');
  if (error) throw new Error(`Instagram authorization failed: ${error}`);
  const code = actual.searchParams.get('code');
  if (!code) throw new Error('Authorization code missing from callback URL');
  return code.replace(/#_$/, '');
}
