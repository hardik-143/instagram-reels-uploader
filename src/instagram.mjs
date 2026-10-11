const graph = 'https://graph.instagram.com/v26.0';

async function jsonRequest(url, options = {}) {
  const response = await fetch(url, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok || body.error) {
    const message = body.error?.message || body.error_message || response.statusText;
    throw new Error(`Instagram API ${response.status}: ${message}`);
  }
  return body;
}

export async function exchangeCode({ code, appId, appSecret, redirectUri }) {
  const body = new URLSearchParams({ client_id: appId, client_secret: appSecret, grant_type: 'authorization_code', redirect_uri: redirectUri, code });
  return jsonRequest('https://api.instagram.com/oauth/access_token', { method: 'POST', body });
}

export async function exchangeLongLived(shortToken, appSecret) {
  const url = new URL('https://graph.instagram.com/access_token');
  url.search = new URLSearchParams({ grant_type: 'ig_exchange_token', client_secret: appSecret, access_token: shortToken }).toString();
  return jsonRequest(url);
}

export async function refreshToken(token) {
  const url = new URL('https://graph.instagram.com/refresh_access_token');
  url.search = new URLSearchParams({ grant_type: 'ig_refresh_token', access_token: token }).toString();
  return jsonRequest(url);
}

export async function profile(token) {
  return jsonRequest(`${graph}/me?fields=id,username,account_type`, { headers: { Authorization: `Bearer ${token}` } });
}

export async function createContainer(userId, token, videoUrl, caption) {
  const body = new URLSearchParams({ media_type: 'REELS', video_url: videoUrl, caption, share_to_feed: 'true' });
  return jsonRequest(`${graph}/${encodeURIComponent(userId)}/media`, { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body });
}

export async function containerStatus(containerId, token) {
  return jsonRequest(`${graph}/${encodeURIComponent(containerId)}?fields=status_code,status`, { headers: { Authorization: `Bearer ${token}` } });
}

export async function publishContainer(userId, containerId, token) {
  const body = new URLSearchParams({ creation_id: containerId });
  return jsonRequest(`${graph}/${encodeURIComponent(userId)}/media_publish`, { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body });
}

export async function publishedMedia(mediaId, token) {
  return jsonRequest(`${graph}/${encodeURIComponent(mediaId)}?fields=id,permalink`, { headers: { Authorization: `Bearer ${token}` } });
}
