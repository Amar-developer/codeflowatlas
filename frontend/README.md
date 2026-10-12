# Frontend

This Next.js application lives beside the FastAPI backend in the same CodeFlowAtlas repository. The current home page displays API and database health, links to the API documentation, and marks future product capabilities as planned.

The root Compose file builds this folder with `frontend/Dockerfile`. It sets `API_INTERNAL_URL` for server-side health checks and `API_PUBLIC_URL` for the browser-facing API documentation link.

For local development, use Node.js 20.9 or newer, run `npm ci` and `npm run dev` here, and set both API URLs to the API address reachable from your host.
