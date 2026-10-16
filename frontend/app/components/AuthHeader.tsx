"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import type { AuthUser } from "../types/auth";

type AuthState =
  | { status: "loading" }
  | { status: "guest" }
  | { status: "member"; user: AuthUser }
  | { status: "error" };

const AuthHeader = () => {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({ status: "loading" });

  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await fetch("/api/auth/me", {
          cache: "no-store",
          credentials: "same-origin",
          signal: AbortSignal.timeout(8000),
        });

        if (response.status === 401) {
          setState({ status: "guest" });
          return;
        }

        if (!response.ok) {
          throw new Error(`Session check failed: ${response.status}`);
        }

        const user: AuthUser = await response.json();
        setState({ status: "member", user });
      } catch {
        setState({ status: "error" });
      }
    };

    void checkSession();
  }, []);

  const logout = async () => {
    try {
      const response = await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "same-origin",
      });

      if (!response.ok) {
        throw new Error("Logout failed");
      }

      setState({ status: "guest" });
      router.push("/");
      router.refresh();
    } catch {
      setState({ status: "error" });
    }
  };

  if (state.status === "loading") {
    return <span className="text-sm text-slate-400">Checking account…</span>;
  }

  if (state.status === "error") {
    return (
      <span role="status" className="text-sm text-rose-300">
        Account unavailable
      </span>
    );
  }

  if (state.status === "guest") {
    return (
      <div className="flex items-center gap-2">
        <Link
          href="/login"
          className="rounded-full px-3 py-2 text-sm font-semibold text-slate-200 hover:text-rose-300"
        >
          Log in
        </Link>
        <Link
          href="/signup"
          className="rounded-full bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-400"
        >
          Sign up
        </Link>
      </div>
    );
  }

  const name =
    state.user.display_name?.trim() ||
    state.user.email.split("@")[0];

  const initials = name
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();

  return (
    <div className="flex items-center gap-3">
      <Link
        href="/dashboard"
        className="flex items-center gap-2 rounded-full text-sm font-semibold text-slate-100 hover:text-rose-300"
      >
        <span
          aria-hidden="true"
          className="grid size-9 place-items-center rounded-full bg-rose-500 font-bold text-white"
        >
          {initials}
        </span>
        <span className="hidden max-w-32 truncate sm:inline">{name}</span>
      </Link>

      <button
        type="button"
        onClick={logout}
        className="text-xs text-slate-400 hover:text-white"
      >
        Log out
      </button>
    </div>
  );
};

export default AuthHeader;
