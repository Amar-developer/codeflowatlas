"use client";

import type { FormEvent } from "react";
import Link from "next/link";
import { useState } from "react";

const ForgotPasswordPage = () => {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setBusy(true);
    setMessage("");

    try {
      const response = await fetch("/api/auth/forgot-password", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        throw new Error("Could not request a reset link.");
      }

      setMessage(
        "If this email has an account, a password link has been sent.",
      );
    } catch (error: unknown) {
      setMessage(
        error instanceof Error ? error.message : "Something went wrong.",
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6 text-slate-100">
      <h1 className="text-3xl font-bold">Set or reset password</h1>
      <p className="mt-3 text-slate-400">
        You can also use this if you first joined with Google or GitHub.
      </p>

      <form onSubmit={submit} className="mt-8 space-y-5">
        <label className="block text-sm">
          Email
          <input
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="mt-2 w-full rounded-lg border border-white/20 bg-slate-900 p-3"
          />
        </label>

        <button
          disabled={busy}
          className="w-full rounded-lg bg-brand-500 p-3 font-semibold text-white disabled:opacity-50"
        >
          {busy ? "Sending…" : "Email me a link"}
        </button>
      </form>

      {message && <p role="status" className="mt-6">{message}</p>}

      <Link href="/login" className="mt-8 text-brand-300">
        Back to login
      </Link>
    </main>
  );
};

export default ForgotPasswordPage;