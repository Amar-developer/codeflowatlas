"use client";

import type { FormEvent } from "react";
import Link from "next/link";
import { useEffect, useState } from "react";

const ResetPasswordPage = () => {
    const [token, setToken] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");
    const [complete, setComplete] = useState(false);
    const [busy, setBusy] = useState(false);

    useEffect(() => {
        const value = new URLSearchParams(window.location.search).get("token");
        // Remove the token from the visible URL after reading it.
        if (!value) return;

        setToken(value);
        window.history.replaceState({}, "", "/reset-password");
    }, []);

    const submit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setBusy(true);
        setMessage("");

        try {
            const response = await fetch("/api/auth/reset-password", {
                method: "POST",
                headers: { "content-type": "application/json" },
                body: JSON.stringify({
                    token,
                    new_password: password,
                }),
            });

            if (!response.ok) {
                const result: { detail?: string } = await response
                    .json()
                    .catch(() => ({}));

                throw new Error(result.detail ?? "Could not set password.");
            }

            setComplete(true);
            setToken("");
            setPassword("");
            setMessage("Password set. You can now log in with email.");
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
            <h1 className="text-3xl font-bold">Set your password</h1>

            {!token && !complete && (
                <p className="mt-6 text-brand-300">
                    Reset link is missing. Request a new link.
                </p>
            )}

            {token && !complete && (
                <form onSubmit={submit} className="mt-8 space-y-5">
                    <label className="block text-sm">
                        New password
                        <input
                            type="password"
                            required
                            minLength={12}
                            maxLength={128}
                            autoComplete="new-password"
                            value={password}
                            onChange={(event) => setPassword(event.target.value)}
                            className="mt-2 w-full rounded-lg border border-white/20 bg-slate-900 p-3"
                        />
                    </label>

                    <button
                        disabled={busy}
                        className="w-full rounded-lg bg-brand-500 p-3 font-semibold text-white disabled:opacity-50"
                    >
                        {busy ? "Saving…" : "Set password"}
                    </button>
                </form>
            )}

            {message && <p role="status" className="mt-6">{message}</p>}

            <Link
                href={complete ? "/login" : "/forgot-password"}
                className="mt-8 text-brand-300"
            >
                {complete ? "Go to login" : "Request a new link"}
            </Link>
        </main>
    );
};

export default ResetPasswordPage;