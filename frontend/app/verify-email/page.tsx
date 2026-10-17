"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type ApiError = {
  detail?: unknown;
};

const VerifyEmailPage = () => {
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [verified, setVerified] = useState(false);

  useEffect(() => {
    const query = new URLSearchParams(window.location.search);
    const value = query.get("token") ?? "";
    setToken(value);
    setEmail(query.get("email") ?? "");

    if (value) {
      window.history.replaceState({}, "", "/verify-email");
    }
    if (query.get("delivery") === "failed") {
      setMessage(
        "Your account was created, but the email could not be sent. Request a new link.",
      );
    }
  }, []);

  const verify = async () => {
    setBusy(true);
    setMessage("");

    try {
      const response = await fetch("/api/auth/verify-email", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ token }),
      });

      if (!response.ok) {
        const result: ApiError = await response
          .json()
          .catch(() => ({}));

        throw new Error(
          typeof result.detail === "string"
            ? result.detail
            : "Verification failed.",
        );
      }

      setVerified(true);
      setMessage("Email verified. You can now log in.");
    } catch (cause: unknown) {
      setMessage(
        cause instanceof Error ? cause.message : "Verification failed.",
      );
    } finally {
      setBusy(false);
    }
  };

  const resend = async () => {
    setBusy(true);
    setMessage("");

    try {
      const response = await fetch("/api/auth/resend-verification", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        throw new Error("Could not request another email.");
      }

      setMessage(
        "If this account needs verification, a new email was sent.",
      );
    } catch (cause: unknown) {
      setMessage(
        cause instanceof Error
          ? cause.message
          : "Could not request another email.",
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6 text-slate-100">
      <h1 className="text-3xl font-bold">Verify your email</h1>
      <p className="mt-4 text-slate-400">
        Open the verification link in your email.
      </p>

      {token && !verified && (
        <button
          type="button"
          onClick={verify}
          disabled={busy}
          className="mt-8 rounded-lg bg-brand-500 p-3 font-semibold text-white transition hover:bg-brand-400 disabled:opacity-50"
        >
          Verify email
        </button>
      )}

      <div className="mt-8 space-y-3">
        <input
          type="email"
          aria-label="Email for a new verification link"
          placeholder="Your email"
          className="w-full rounded-lg border border-white/20 bg-slate-900 p-3"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />

        <button
          type="button"
          onClick={resend}
          disabled={busy || !email}
          className="text-brand-300 disabled:opacity-50"
        >
          Resend verification email
        </button>
      </div>

      {message && (
        <p role="status" className="mt-6">
          {message}
        </p>
      )}

      <Link href="/login" className="mt-8 text-brand-300">
        Go to login
      </Link>
    </main>
  );
};

export default VerifyEmailPage;
