type Context = {
  params: Promise<{ id: string; endpointId: string }>;
};

export async function GET(
  request: Request,
  { params }: Context,
): Promise<Response> {
  const { id, endpointId } = await params;
  const uuid =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

  if (!uuid.test(id) || !uuid.test(endpointId)) {
    return Response.json(
      { detail: "Invalid project or endpoint ID" },
      { status: 400 },
    );
  }

  const apiBase = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8081";
  const cookie = request.headers.get("cookie");

  const depth = new URL(request.url).searchParams.get("depth") ?? "1";

  if (!["1", "2", "3"].includes(depth)) {
    return Response.json(
      { detail: "Depth must be 1, 2, or 3" },
      { status: 400 },
    );
  }

  try {
    const upstream = await fetch(
      `${apiBase}/projects/${id}/endpoints/${endpointId}/flow?depth=${depth}`,
      {
        headers: cookie ? { cookie } : {},
        cache: "no-store",
        signal: AbortSignal.timeout(10000),
      },
    );

    return new Response(await upstream.text(), {
      status: upstream.status,
      headers: {
        "content-type": "application/json",
        "cache-control": "no-store",
      },
    });
  } catch {
    return Response.json(
      { detail: "Could not reach the flow service. Try again." },
      { status: 502 },
    );
  }
}
