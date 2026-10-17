type AuthRouteContext = {
  params: Promise<{ action: string }>;
};

const getActions = new Set(["me"]);

const postActions = new Set([
  "signup",
  "login",
  "logout",
  "verify-email",
  "resend-verification",
  "forgot-password",
  "reset-password",
]);

const forward = async (
  request: Request,
  { params }: AuthRouteContext,
): Promise<Response> => {
  const { action } = await params;
  const allowed = request.method === "GET" ? getActions : postActions;

  if (!allowed.has(action)) {
    return Response.json({ detail: "Not found" }, { status: 404 });
  }

  const origin = request.headers.get("origin");

  if (request.method === "POST" && origin !== process.env.AUTH_ORIGIN) {
    return Response.json(
      { detail: "Invalid origin" },
      { status: 403 },
    );
  }

  const apiUrl = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8081";

  try {
    const cookie = request.headers.get("cookie");

    const upstream = await fetch(`${apiUrl}/auth/${action}`, {
      method: request.method,
      headers: {
        ...(request.method === "POST"
          ? { "content-type": "application/json" }
          : {}),
        ...(origin ? { origin } : {}),
        ...(cookie ? { cookie } : {}),
      },
      body:
        request.method === "POST" && action !== "logout"
          ? await request.text()
          : undefined,
      cache: "no-store",
    });

    const headers = new Headers({
      "cache-control": "no-store",
      "content-type":
        upstream.headers.get("content-type") ?? "application/json",
    });

    const setCookie = upstream.headers.get("set-cookie");
    if (setCookie) {
      headers.set("set-cookie", setCookie);
    }

    return new Response(
      upstream.status === 204 ? null : await upstream.text(),
      {
        status: upstream.status,
        headers,
      },
    );
  } catch {
    return Response.json(
      { detail: "Authentication service is unavailable" },
      { status: 502 },
    );
  }
};

export const GET = forward;
export const POST = forward;
