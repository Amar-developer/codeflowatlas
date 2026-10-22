import assert from "node:assert/strict";
import { afterEach, test } from "node:test";
import { GET, POST } from "../app/api/auth/[action]/route.ts";

const originalFetch = globalThis.fetch;
const originalOrigin = process.env.AUTH_ORIGIN;
const originalApiUrl = process.env.API_INTERNAL_URL;

afterEach(() => {
  globalThis.fetch = originalFetch;
  if (originalOrigin === undefined) delete process.env.AUTH_ORIGIN;
  else process.env.AUTH_ORIGIN = originalOrigin;
  if (originalApiUrl === undefined) delete process.env.API_INTERNAL_URL;
  else process.env.API_INTERNAL_URL = originalApiUrl;
});

test("session lookup forwards the browser's session cookie", async () => {
  process.env.API_INTERNAL_URL = "http://api:8000";
  globalThis.fetch = async (url, options) => {
    assert.equal(url, "http://api:8000/auth/me");
    assert.equal(options.headers.cookie, "cfa_session=test-session");
    return Response.json({ email: "learner@example.com" });
  };

  const request = new Request("http://127.0.0.1:3001/api/auth/me", {
    headers: { cookie: "cfa_session=test-session" },
  });
  const response = await GET(request, { params: Promise.resolve({ action: "me" }) });

  assert.equal(response.status, 200);
  assert.equal((await response.json()).email, "learner@example.com");
});

test("login forwards the validated origin and preserves the session cookie", async () => {
  process.env.AUTH_ORIGIN = "http://127.0.0.1:3001";
  globalThis.fetch = async (_url, options) => {
    assert.equal(options.headers.origin, process.env.AUTH_ORIGIN);
    assert.equal(options.method, "POST");
    return new Response('{"email":"learner@example.com"}', {
      headers: {
        "content-type": "application/json",
        "set-cookie": "cfa_session=test-session; Path=/; HttpOnly; SameSite=Lax",
      },
    });
  };

  const request = new Request("http://127.0.0.1:3001/api/auth/login", {
    method: "POST",
    headers: { origin: process.env.AUTH_ORIGIN },
    body: JSON.stringify({ email: "learner@example.com", password: "example" }),
  });
  const response = await POST(request, { params: Promise.resolve({ action: "login" }) });

  assert.equal(response.status, 200);
  assert.match(response.headers.get("set-cookie"), /^cfa_session=/);
});

test("login rejects requests from a different origin before contacting the API", async () => {
  process.env.AUTH_ORIGIN = "http://127.0.0.1:3001";
  globalThis.fetch = async () => {
    throw new Error("The upstream API must not be called");
  };

  const request = new Request("http://127.0.0.1:3001/api/auth/login", {
    method: "POST",
    headers: { origin: "http://example.invalid" },
    body: "{}",
  });
  const response = await POST(request, { params: Promise.resolve({ action: "login" }) });

  assert.equal(response.status, 403);
});
