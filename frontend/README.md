# Frontend

This Next.js application lives beside the FastAPI backend in the same CodeFlowAtlas repository. Tailwind CSS v4 styles a responsive AI-lab themed landing page with a complete footer, visual flow and trace concept previews, and CSS motion that respects reduced-motion preferences. The page displays real API and database health and links to the live API documentation. Repository analysis, the AI guide, runtime traces, and experiments are clearly marked as planned. `app/globals.css` loads Tailwind and contains page-wide visual effects and animation rules; component layout and colors live in utility classes.

The root Compose file builds this folder with `frontend/Dockerfile`. It sets `API_INTERNAL_URL` for server-side health checks and `API_PUBLIC_URL` for the browser-facing API documentation link.

For live frontend updates in Docker, run `sudo docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build web` from the repository root. The development override builds the existing Dockerfile's dependency stage, runs the Next.js development server, and mounts `frontend/` into the container. Edits to frontend source files then update without another image build. The published web port still comes from `WEB_PORT` in the root `.env` file. Restart without the override to use the production image again.

For local development, use Node.js 20.9 or newer. Run `npm ci` yourself in this folder to install the locked dependencies, then `npm run dev`. Set both API URLs to the API address reachable from your host.
