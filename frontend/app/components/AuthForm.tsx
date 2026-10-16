"use client";

import type { FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

type AuthFormProps = {
  mode: "login" | "signup";
};

type ApiError = {
  detail?: unknown;
};

const AuthForm = ({ mode }: AuthFormProps) => {
  const router = useRouter();
  const isSignup = mode === "signup";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const response = await fetch(
        `/api/auth/${isSignup ? "signup" : "login"}`,
        {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            email,
            password,
            ...(isSignup ? { display_name: displayName || null } : {}),
          }),
        },
      );

      if (!response.ok) {
        const result: ApiError = await response
          .json()
          .catch(() => ({}));

        throw new Error(
          typeof result.detail === "string"
            ? result.detail
            : "Please check your information and try again.",
        );
      }

      if (isSignup) {
        router.push(`/verify-email?email=${encodeURIComponent(email)}`);
      } else {
        router.push("/dashboard");
        router.refresh();
      }
    } catch (cause: unknown) {
      setError(
        cause instanceof Error ? cause.message : "Something went wrong.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6 text-slate-100">
      <Link href="/" className="mb-8 text-sm text-rose-300">
        ← CodeFlowAtlas
      </Link>

      <h1 className="text-3xl font-bold">
        {isSignup ? "Create your account" : "Log in"}
      </h1>

      <form onSubmit={submit} className="mt-8 space-y-5">
        {isSignup && (
          <label className="block text-sm">
            Display name
            <input
              className="mt-2 w-full rounded-lg border border-white/20 bg-slate-900 p-3"
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
              maxLength={100}
              placeholder="Name"
              autoComplete="name"
            />
          </label>
        )}

        <label className="block text-sm">
          Email
          <input
            className="mt-2 w-full rounded-lg border border-white/20 bg-slate-900 p-3"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            autoComplete="email"
            placeholder="user@example.com"
            required
          />
        </label>

        <label className="block text-sm">
          Password
          <input
            className="mt-2 w-full rounded-lg border border-white/20 bg-slate-900 p-3"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete={isSignup ? "new-password" : "current-password"}
            minLength={isSignup ? 12 : 1}
            required
          />
        </label>

        {!isSignup && (
          <Link
            href="/forgot-password"
            className="block text-sm text-rose-300 underline"
          >
            Forgot password?
          </Link>
        )}


        {error && (
          <p role="alert" className="text-sm text-rose-300">
            {error}
          </p>
        )}

        {!isSignup && error === "Verify your email before logging in" && (
          <Link
            href={`/verify-email?email=${encodeURIComponent(email)}`}
            className="block text-sm text-rose-300 underline"
          >
            Resend verification email
          </Link>
        )}

        <button
          disabled={submitting}
          className="w-full rounded-lg bg-rose-500 p-3 font-semibold text-white transition hover:bg-rose-400 disabled:opacity-50"
        >
          {submitting
            ? "Please wait…"
            : isSignup
              ? "Create account"
              : "Log in"}
        </button>


        <div className="mt-8 space-y-3 border-t border-white/10 pt-6">
          {/* Google OAuth */}
          <a
            href="/api/auth/oauth/google"
            className="flex w-full items-center justify-center gap-3 rounded-lg border border-white/20 px-4 py-3 font-semibold text-white transition-colors hover:bg-white/5"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 48 48"
              className="h-5 w-5 shrink-0"
              aria-hidden="true"
            >
              <path
                fill="#EA4335"
                d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5Z"
                transform="translate(0 4)"
              />
              <path
                fill="#4285F4"
                d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.72 7.18l7.62 5.91c4.45-4.11 7.14-10.16 7.14-17.56Z"
                transform="translate(0 0)"
              />
              <path
                fill="#FBBC05"
                d="M10.53 28.59a14.4 14.4 0 0 1 0-9.18l-7.98-6.19a23.94 23.94 0 0 0 0 21.56l7.98-6.19Z"
                transform="translate(0 0)"
              />
              <path
                fill="#34A853"
                d="M24 48c6.48 0 11.93-2.13 15.9-5.89l-7.62-5.91c-2.12 1.42-4.84 2.26-8.28 2.26-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48Z"
              />
            </svg>

            <span>Continue with Google</span>
          </a>

          {/* GitHub OAuth */}
          <a
            href="/api/auth/oauth/github"
            className="flex w-full items-center justify-center gap-3 rounded-lg border border-white/20 px-4 py-3 font-semibold text-white transition-colors hover:bg-white/5"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
              className="h-5 w-5 shrink-0"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.44 9.8 8.2 11.39.6.11.82-.26.82-.58v-2.24c-3.34.73-4.04-1.42-4.04-1.42-.55-1.39-1.33-1.76-1.33-1.76-1.09-.75.08-.74.08-.74 1.2.08 1.83 1.23 1.83 1.23 1.07 1.84 2.8 1.31 3.49 1 .11-.78.42-1.31.76-1.61-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.23-3.22-.12-.3-.53-1.52.12-3.17 0 0 1.01-.32 3.3 1.23a11.5 11.5 0 0 1 6 0c2.29-1.55 3.3-1.23 3.3-1.23.65 1.65.24 2.87.12 3.17.77.84 1.23 1.91 1.23 3.22 0 4.61-2.8 5.62-5.48 5.92.43.37.81 1.1.81 2.22v3.3c0 .32.22.69.83.58A12 12 0 0 0 12 0Z"
              />
            </svg>

            <span>Continue with GitHub</span>
          </a>
        </div>

      </form>

      <p className="mt-6 text-sm text-slate-400">
        {isSignup ? "Already have an account?" : "New to CodeFlowAtlas?"}{" "}
        <Link
          className="text-rose-300"
          href={isSignup ? "/login" : "/signup"}
        >
          {isSignup ? "Log in" : "Create an account"}
        </Link>
      </p>
    </main>
  );
};

export default AuthForm;
