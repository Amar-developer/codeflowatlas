type Context = {
  params: Promise<{ id: string }>;
};

const forward = async (
  request: Request,
  { params }: Context,
): Promise<Response> => {
  const { id } = await params;

  if (!/^[0-9a-fA-F-]{36}$/.test(id)) {
    return Response.json({ detail: "Invalid project ID" }, { status: 400 });
  }

  const origin = request.headers.get("origin");

  if (request.method === "DELETE" && origin !== process.env.AUTH_ORIGIN) {
    return Response.json({ detail: "Invalid origin" }, { status: 403 });
  }

  const apiBase = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8081";
  const cookie = request.headers.get("cookie");

  try {
    const upstream = await fetch(`${apiBase}/projects/${id}`, {
      method: request.method,
      headers: {
        ...(cookie ? { cookie } : {}),
        ...(origin ? { origin } : {}),
      },
      cache: "no-store",
    });

    return new Response(
      upstream.status === 204 ? null : await upstream.text(),
      {
        status: upstream.status,
        headers: {
          "content-type":
            upstream.headers.get("content-type") ?? "application/json",
          "cache-control": "no-store",
        },
      },
    );
  } catch {
    return Response.json(
      { detail: "Repository service is unavailable" },
      { status: 502 },
    );
  }
};

export const GET = forward;
export const DELETE = forward;