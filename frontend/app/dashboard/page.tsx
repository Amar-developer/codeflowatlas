"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import AuthHeader from "../components/AuthHeader";
import type { AuthUser } from "../types/auth";

type DashboardState =
  | { status: "loading" }
  | { status: "ready"; user: AuthUser }
  | { status: "error" };

const DashboardPage = () => {
  const router = useRouter();
  const [state, setState] = useState<DashboardState>({
    status: "loading",
  });

  useEffect(() => {
    const loadUser = async () => {
      try {
        const response = await fetch("/api/auth/me", {
          cache: "no-store",
          credentials: "same-origin",
          signal: AbortSignal.timeout(8000),
        });

        if (response.status === 401) {
          router.replace("/login");
          return;
        }

        if (!response.ok) {
          throw new Error(`Session check failed: ${response.status}`);
        }

        const user: AuthUser = await response.json();
        setState({ status: "ready", user });
      } catch {
        setState({ status: "error" });
      }
    };

    void loadUser();
  }, [router]);

  return (
    <>
      <header className="flex items-center justify-between border-b border-white/10 px-6 py-4">
        <Link href="/" className="font-bold text-rose-300">
          CodeFlowAtlas.
        </Link>
        <AuthHeader />
      </header>

      <main className="mx-auto max-w-3xl px-6 py-16 text-slate-100">
        <h1 className="text-3xl font-bold">Dashboard</h1>

        {state.status === "loading" && (
          <p className="mt-4">Checking your session…</p>
        )}

        {state.status === "error" && (
          <p role="alert" className="mt-4 text-rose-300">
            Could not check your session. Check the API connection and refresh.
          </p>
        )}

        {state.status === "ready" && (
          <div className="mt-4 space-y-4">
            <p>
              Welcome, {state.user.display_name || state.user.email}.
            </p>

            <div className="flex gap-3">
              <a
                href="/api/auth/oauth/google/link"
                className="rounded border border-white/20 px-4 py-2"
              >
                Connect Google
              </a>

              <a
                href="/api/auth/oauth/github/link"
                className="rounded border border-white/20 px-4 py-2"
              >
                Connect GitHub
              </a>
            </div>
          </div>
        )}
      </main>
    </>
  );
};

export default DashboardPage;