type Context = {
  params: Promise<{ provider: string }>;
};

export const GET = async (
  _request: Request,
  { params }: Context,
): Promise<Response> => {
  const { provider } = await params;

  if (provider !== "google" && provider !== "github") {
    return Response.json({ detail: "Unknown provider" }, { status: 404 });
  }

  const apiUrl = process.env.API_PUBLIC_URL;
  if (!apiUrl) {
    return Response.json({ detail: "OAuth is not configured" }, { status: 503 });
  }

  return Response.redirect(
    `${apiUrl.replace(/\/$/, "")}/auth/oauth/${provider}/link/start`,
    302,
  );
};