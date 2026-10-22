const apiBase = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8081";

const forward = async (request: Request): Promise<Response> => {
  const origin = request.headers.get("origin");

  if (request.method === "POST" && origin !== process.env.AUTH_ORIGIN) {
    return Response.json({ detail: "Invalid origin" }, { status: 403 });
  }

  const path = request.method === "POST" ? "/projects/import" : "/projects";
  const cookie = request.headers.get("cookie");

  try {
    const upstream = await fetch(`${apiBase}${path}`, {
      method: request.method,
      headers: {
        ...(cookie ? { cookie } : {}),
        ...(origin ? { origin } : {}),
        ...(request.method === "POST"
          ? { "content-type": "application/json" }
          : {}),
      },
      body: request.method === "POST" ? await request.text() : undefined,
      cache: "no-store",
    });

    return new Response(await upstream.text(), {
      status: upstream.status,
      headers: {
        "content-type":
          upstream.headers.get("content-type") ?? "application/json",
        "cache-control": "no-store",
      },
    });
  } catch {
    return Response.json(
      { detail: "Repository service is unavailable" },
      { status: 502 },
    );
  }
};

export const GET = forward;
export const POST = forward;