"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import AuthHeader from "../components/AuthHeader";
import type { AuthUser } from "../types/auth";
import RepositoryImport from "../components/RepositoryImport";

type DashboardState =
  | { status: "loading" }
  | { status: "ready"; user: AuthUser }
  | { status: "error" };

const views = [
  { number: "01", icon: "◫", title: "Repository overview", detail: "Languages, framework and discovered entry points" },
  { number: "02", icon: "◇", title: "API flow explorer", detail: "Follow a route through functions and data access" },
  { number: "03", icon: "✳", title: "AI code guide", detail: "Ask questions with source references and uncertainty" },
];

const exampleFlow = [
  { kind: "API", title: "POST /checkout", detail: "Route", color: "brand" },
  { kind: "fn", title: "create_order()", detail: "Handler", color: "sky" },
  { kind: "db", title: "save_order()", detail: "Possible data access", color: "violet" },
];

const DashboardPage = () => {
  const router = useRouter();
  const [state, setState] = useState<DashboardState>({ status: "loading" });
  const [linkNotice, setLinkNotice] = useState<{ text: string; error: boolean } | null>(null);

  useEffect(() => {
    const query = new URLSearchParams(window.location.search);
    const linked = query.get("linked");
    const error = query.get("link_error");
    const errors: Record<string, string> = {
      provider_already_linked: "This provider account belongs to another CodeFlowAtlas user.",
      provider_already_connected: "A different account from this provider is already connected.",
      login_required: "Your session expired. Log in and try again.",
      link_failed: "Could not connect this provider. Please try again.",
      email_unverified: "Verify your email with the provider before connecting it.",
      oauth_cancelled: "Connection was cancelled.",
      oauth_failed: "Provider connection failed. Please try again.",
    };
    if (error) {
      setLinkNotice({ text: errors[error] ?? "Could not connect this provider.", error: true });
    } else if (linked === "google" || linked === "github") {
      setLinkNotice({ text: `${linked === "google" ? "Google" : "GitHub"} connected successfully.`, error: false });
    }
    if (error || linked) window.history.replaceState({}, "", "/dashboard");
  }, []);

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
        if (!response.ok) throw new Error(`Session check failed: ${response.status}`);
        const user: AuthUser = await response.json();
        setState({ status: "ready", user });
      } catch {
        setState({ status: "error" });
      }
    };
    void loadUser();
  }, [router]);

  return (
    <div className="dashboard-shell min-h-screen text-slate-100">
      <header className="border-b border-white/10 bg-[#0b0d17]/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-4 sm:px-8">
          <Link href="/" className="flex items-center gap-3 font-bold tracking-tight text-white">
            <span className="grid size-9 place-items-center rounded-xl border border-brand-400/30 bg-brand-500/10 text-brand-300">◇</span>
            <span>CodeFlowAtlas<span className="text-brand-400">.</span></span>
          </Link>
          <AuthHeader />
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl lg:grid-cols-[15rem_minmax(0,1fr)]">
        <aside className="border-b border-white/10 px-5 py-6 sm:px-8 lg:min-h-[calc(100vh-74px)] lg:border-b-0 lg:border-r lg:px-5">
          <p className="mb-4 px-3 text-xs font-bold uppercase tracking-widest text-slate-500">Workspace</p>
          <nav aria-label="Dashboard navigation" className="flex flex-wrap gap-1 lg:flex-col">
            <Link href="/dashboard" aria-current="page" className="flex items-center gap-3 rounded-xl border border-brand-400/20 bg-brand-500/10 px-3 py-2.5 text-sm font-semibold text-brand-200"><span aria-hidden="true">◫</span> Overview</Link>
            <a href="#workspace-preview" className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-slate-400 transition hover:bg-white/5 hover:text-white"><span aria-hidden="true">◇</span> Flow preview</a>
            <a href="#account" className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-slate-400 transition hover:bg-white/5 hover:text-white"><span aria-hidden="true">◎</span> Account</a>
          </nav>
          <div className="mt-10 hidden rounded-2xl border border-white/10 bg-white/[0.03] p-4 lg:block">
            <p className="text-xs font-bold uppercase tracking-widest text-brand-300">Current stage</p>
            <p className="mt-2 text-sm font-semibold text-white">Your workspace is taking shape</p>
            <p className="mt-2 text-xs leading-5 text-slate-400">Repository import and source analysis are the next product features.</p>
          </div>
        </aside>

        <main className="min-w-0 px-5 py-8 sm:px-8 lg:px-10 lg:py-10">
          {linkNotice && <div role={linkNotice.error ? "alert" : "status"} className={`mb-7 rounded-xl border px-4 py-3 text-sm ${linkNotice.error ? "border-brand-400/30 bg-brand-500/10 text-brand-200" : "border-sky-400/30 bg-sky-500/10 text-sky-200"}`}>{linkNotice.text}</div>}
          {state.status === "loading" && <div role="status" className="rounded-2xl border border-white/10 bg-white/[0.03] p-8 text-slate-300">Checking your session…</div>}
          {state.status === "error" && <div role="alert" className="rounded-2xl border border-brand-400/30 bg-brand-500/10 p-8 text-brand-200">Could not check your session. Check the API connection and refresh.</div>}

          {state.status === "ready" && (
            <>
              <div className="flex flex-wrap items-end justify-between gap-5">
                <div>
                  <p className="text-xs font-bold uppercase tracking-widest text-brand-300">Your workspace / Overview</p>
                  <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl">Welcome back, {state.user.display_name?.trim() || state.user.email.split("@")[0]}.</h1>
                  <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">Explore how CodeFlowAtlas will connect your repository, API paths and source code in one visual workspace.</p>
                </div>
                <span className="rounded-full border border-amber-300/20 bg-amber-300/10 px-3 py-1.5 text-xs font-semibold text-amber-200">Design preview · Core analysis coming next</span>
              </div>

              <RepositoryImport />

              <section id="workspace-preview" className="mt-10" aria-labelledby="preview-title">
                <div className="flex flex-wrap items-end justify-between gap-3">
                  <div><p className="text-xs font-bold uppercase tracking-widest text-slate-500">Explore the concept</p><h2 id="preview-title" className="mt-2 text-xl font-semibold text-white">A flow you can inspect, step by step</h2></div>
                  <span className="text-xs text-slate-500">Illustrative example · no repository analyzed</span>
                </div>
                <div className="mt-5 grid gap-4 xl:grid-cols-[minmax(0,1.4fr)_minmax(16rem,1fr)]">
                  <div className="dashboard-grid rounded-2xl border border-white/10 bg-[#101522] p-5 sm:p-6">
                    <div className="mb-6 flex flex-wrap items-center justify-between gap-3"><span className="text-xs font-bold uppercase tracking-widest text-slate-400">Example: checkout flow</span><span className="rounded-full border border-brand-400/20 bg-brand-500/10 px-2.5 py-1 text-xs text-brand-200">Source view · preview</span></div>
                    <div className="max-w-md">
                      {exampleFlow.map((step, index) => (
                        <div key={step.title}>
                          <div className="flex items-center gap-3 rounded-xl border border-white/10 bg-[#121929] p-3 shadow-lg shadow-black/10">
                            <span className={`grid size-9 shrink-0 place-items-center rounded-lg text-xs font-bold ${step.color === "brand" ? "bg-brand-400/15 text-brand-300" : step.color === "sky" ? "bg-sky-400/15 text-sky-300" : "bg-violet-400/15 text-violet-300"}`}>{step.kind}</span>
                            <span className="min-w-0"><strong className="block truncate text-sm text-white">{step.title}</strong><span className="block text-xs text-slate-500">{step.detail}</span></span>
                            <span className="ml-auto text-slate-500" aria-hidden="true">↗</span>
                          </div>
                          {index < exampleFlow.length - 1 && <div aria-hidden="true" className="ml-7 h-5 w-px bg-brand-300/30" />}
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="flex flex-col rounded-2xl border border-white/10 bg-[#101522] p-5 sm:p-6">
                    <span className="text-xs font-bold uppercase tracking-widest text-violet-300">AI guide · planned</span>
                    <h3 className="mt-4 text-lg font-semibold text-white">Understand the “why” behind each step.</h3>
                    <p className="mt-3 text-sm leading-6 text-slate-400">Select a node to see relevant code, follow its relationships, and ask a question. Answers will cite source evidence and mark uncertain paths.</p>
                    <div className="mt-auto pt-7"><div className="rounded-xl border border-violet-300/20 bg-violet-400/5 p-4 text-sm leading-6 text-slate-300">“Where does the order get saved?”<span className="mt-2 block text-xs text-slate-500">Example question · no AI response generated</span></div></div>
                  </div>
                </div>
              </section>

              <section className="mt-10" aria-labelledby="roadmap-title">
                <p className="text-xs font-bold uppercase tracking-widest text-slate-500">What this space will contain</p>
                <h2 id="roadmap-title" className="mt-2 text-xl font-semibold text-white">One place to understand your project</h2>
                <div className="mt-5 grid gap-4 md:grid-cols-3">{views.map((view) => <article key={view.number} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5"><div className="flex items-start justify-between"><span className="grid size-10 place-items-center rounded-xl bg-brand-500/10 text-xl text-brand-300" aria-hidden="true">{view.icon}</span><span className="font-mono text-xs text-slate-600">{view.number}</span></div><h3 className="mt-5 text-sm font-semibold text-white">{view.title}</h3><p className="mt-2 text-xs leading-5 text-slate-400">{view.detail}</p><span className="mt-5 inline-block text-xs font-semibold text-slate-500">Planned</span></article>)}</div>
              </section>

              <section id="account" className="mt-10 rounded-2xl border border-white/10 bg-white/[0.03] p-5 sm:p-6" aria-labelledby="account-title">
                <div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-widest text-slate-500">Account</p><h2 id="account-title" className="mt-2 text-xl font-semibold text-white">Connect another sign-in option</h2><p className="mt-2 text-sm text-slate-400">Signed in as {state.user.email}</p></div></div>
                <div className="mt-6 flex flex-wrap gap-3"><a href="/api/auth/oauth/google/link" className="rounded-xl border border-white/15 bg-white/5 px-4 py-2.5 text-sm font-semibold text-white transition hover:border-brand-400/40 hover:bg-white/10">Connect Google ↗</a><a href="/api/auth/oauth/github/link" className="rounded-xl border border-white/15 bg-white/5 px-4 py-2.5 text-sm font-semibold text-white transition hover:border-brand-400/40 hover:bg-white/10">Connect GitHub ↗</a></div>
              </section>
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default DashboardPage;
