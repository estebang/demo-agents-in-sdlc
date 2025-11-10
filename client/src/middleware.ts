import { defineMiddleware } from "astro:middleware";

// Get server URL from environment variable with fallback for local development
const API_SERVER_URL = process.env.API_SERVER_URL || 'http://localhost:5100';

/**
 * Middleware to handle API requests by forwarding them to the backend server.
 * 
 * This middleware intercepts requests to /api/* routes and forwards them to the
 * configured API server (defaulting to localhost:5100 for local development).
 * Non-API requests are passed through to regular Astro handling.
 * 
 * @param {Object} context - The Astro middleware context object
 * @param {Function} next - The next middleware function in the chain
 * @returns {Promise<Response>} The response from either the API server or next middleware
 */
export const onRequest = defineMiddleware(async (context, next) => {
  
  // Guard clause: if not an API request, pass through to regular Astro handling
  if (!context.request.url.includes('/api/')) {
    return await next();
  }
  
  const url = new URL(context.request.url);
  const apiPath = url.pathname + url.search;
  
  // Create a new request to the backend server
  const serverRequest = new Request(`${API_SERVER_URL}${apiPath}`, {
    method: context.request.method,
    headers: context.request.headers,
    body: context.request.method !== 'GET' && context.request.method !== 'HEAD' ? 
          await context.request.clone().arrayBuffer() : undefined,
  });
  
  try {
    // Forward the request to the API server
    const response = await fetch(serverRequest);
    const data = await response.arrayBuffer();
    
    // Return the response from the API server
    return new Response(data, {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    });
  } catch (error) {
    console.error('Error forwarding request to API:', error);
    return new Response(JSON.stringify({ error: 'Failed to reach API server' }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' }
    });
  }
});