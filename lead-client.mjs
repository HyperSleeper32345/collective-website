// Adapter for the existing Collective /api/lead contract. No direct database access.
// A UUID receipt distinguishes persistence from the endpoint's honeypot OK response.
export function isRecordedLead(response, body) {
  return response.ok && body?.ok === true && typeof body.id === 'string' &&
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(body.id);
}

export async function submitLead(payload, { fetcher = fetch, endpoint = '/api/lead' } = {}) {
  if (endpoint !== '/api/lead') throw new Error('Unsupported enquiry endpoint.');
  if (typeof payload.message !== 'string' || payload.message.length > 4000) {
    throw new Error('Please shorten your enquiry before sending.');
  }
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetcher(endpoint, {
      method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload), signal: controller.signal
    });
    const body = await response.json().catch(() => null);
    if (!isRecordedLead(response, body)) {
      if (response.status === 429) throw new Error('Please wait a little before trying again, or email David directly.');
      if (response.status === 422) throw new Error('Please check your name, email and enquiry, then try again.');
      throw new Error('We could not confirm that your enquiry was received. Your details are still here; you can prepare an email instead.');
    }
    return { recorded: true }; // Do not expose the CRM identifier to browser analytics.
  } catch (error) {
    if (error.name === 'AbortError' || error instanceof TypeError) {
      throw new Error('We could not confirm that your enquiry was received. Your details are still here; you can prepare an email instead.');
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}
