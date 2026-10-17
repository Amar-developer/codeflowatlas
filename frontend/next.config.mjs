/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  allowedDevOrigins: ["127.0.0.1"],
  async headers() {
    return ["/verify-email", "/reset-password"].map((source) => ({
      source,
      headers: [
        { key: "Referrer-Policy", value: "no-referrer" },
        { key: "Cache-Control", value: "no-store" },
      ],
    }));
  },
};

export default nextConfig;
