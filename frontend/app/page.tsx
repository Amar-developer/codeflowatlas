export const dynamic = "force-dynamic";
import Link from "next/link";
import type { ReactNode } from "react";
import AuthHeader from "./components/AuthHeader";


const apiInternalUrl = process.env.API_INTERNAL_URL || "http://127.0.0.1:8000";
const apiPublicUrl = process.env.API_PUBLIC_URL || "http://127.0.0.1:8000";
const repositoryUrl = "https://github.com/Amar-developer/codeflowatlas";

const check = async (path: string): Promise<boolean> => {
  try {
    const response = await fetch(`${apiInternalUrl}${path}`, {
      cache: "no-store",
      signal: AbortSignal.timeout(3000),
    });
    return response.ok;
  } catch {
    return false;
  }
};

const Arrow = ({ diagonal = false }: { diagonal?: boolean }) => (
  <svg aria-hidden="true" className="size-4" fill="none" viewBox="0 0 20 20">
    {diagonal ? (
      <path
        d="M5 15 15 5M7 5h8v8"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.7"
      />
    ) : (
      <path
        d="M3 10h13m-5-5 5 5-5 5"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.7"
      />
    )}
  </svg>
);

const Brand = () => (
  <a
    aria-label="CodeFlowAtlas home"
    className="group inline-flex items-center gap-3"
    href="#top"
  >
    <span className="grid size-10 place-items-center rounded-xl border border-brand-400/30 bg-brand-500/10 shadow-lg shadow-brand-500/10 transition group-hover:border-brand-300/60 group-hover:shadow-brand-500/25">
      <svg
        aria-hidden="true"
        className="size-6 text-brand-400"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle cx="5" cy="6" r="2" fill="currentColor" />
        <circle cx="19" cy="6" r="2" fill="currentColor" />
        <circle cx="12" cy="18" r="2" fill="currentColor" />
        <path
          d="M7 6h10M6 8l5 8m7-8-5 8"
          stroke="currentColor"
          strokeWidth="1.4"
        />
      </svg>
    </span>
    <span className="text-lg font-bold tracking-tight text-white transition group-hover:text-brand-200">
      CodeFlowAtlas<span className="text-brand-400">.</span>
    </span>
  </a>
);

const Eyebrow = ({ children }: { children: ReactNode }) => (
  <p className="mb-5 flex items-center gap-3 text-xs font-bold uppercase tracking-widest text-brand-400">
    <span aria-hidden="true" className="h-px w-7 bg-brand-400" />
    {children}
  </p>
);

type StatusItemProps = {
  name: string;
  detail: string;
  ready: boolean;
};

const StatusItem = ({ name, detail, ready }: StatusItemProps) => (
  <div className="flex items-center gap-3">
    <span
      className={`relative size-2 shrink-0 rounded-full ${ready ? "bg-cyan-300" : "bg-brand-400"}`}
    >
      {ready && (
        <span className="status-ping absolute inset-0 rounded-full bg-cyan-300" />
      )}
    </span>
    <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
      <span className="text-sm font-semibold text-slate-100">{name}</span>
      <span className="text-xs text-slate-500">{detail}</span>
    </div>
    <span
      className={`ml-auto text-xs font-medium ${ready ? "text-cyan-300" : "text-brand-300"}`}
    >
      {ready ? "Online" : "Unavailable"}
    </span>
  </div>
);

type FlowNodeProps = {
  icon: ReactNode;
  label: string;
  sublabel: string;
  tone?: "brand" | "violet" | "cyan";
};

const FlowNode = ({
  icon,
  label,
  sublabel,
  tone = "brand",
}: FlowNodeProps) => (
  <div className="flow-node flex items-center gap-3 rounded-xl border border-white/10 bg-slate-900/90 p-3 shadow-xl shadow-black/20">
    <span
      className={`grid size-9 shrink-0 place-items-center rounded-lg text-xs font-bold ${tone === "violet" ? "bg-violet-400/15 text-violet-300" : tone === "cyan" ? "bg-cyan-400/15 text-cyan-300" : "bg-brand-400/15 text-brand-300"}`}
    >
      {icon}
    </span>
    <span className="min-w-0">
      <span className="block truncate text-sm font-semibold text-white">
        {label}
      </span>
      <span className="block truncate text-xs text-slate-500">{sublabel}</span>
    </span>
    <span
      className="ml-auto size-1.5 shrink-0 rounded-full bg-brand-300/70"
      aria-hidden="true"
    />
  </div>
);

const PreviewLabel = () => (
  <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-slate-300">
    <span aria-hidden="true" className="size-1.5 rounded-full bg-amber-300" />
    Concept preview · planned
  </span>
);

const workflow = [
  {
    number: "01",
    title: "Connect a project",
    detail:
      "Start with a supported GitHub or Bitbucket repository. CodeFlowAtlas pins a revision so every explanation points to the same source.",
    symbol: "↗",
  },
  {
    number: "02",
    title: "Choose a flow",
    detail:
      "Pick an API or feature and follow its route, functions, data access, and response in a source-linked graph or mind map.",
    symbol: "◇",
  },
  {
    number: "03",
    title: "Learn from evidence",
    detail:
      "Select a step, inspect its code, and ask the AI guide what it does. Unresolved paths stay visible instead of becoming guesses.",
    symbol: "✳",
  },
];

const questions = [
  {
    question: "Can I learn from a repository that has no database running?",
    answer:
      "Yes. The planned first experience uses source analysis to show supported API paths and explain code with file and line references. Database query times and bottlenecks need a running, instrumented application.",
  },
  {
    question: "Will a repository link show real performance numbers?",
    answer:
      "No. A link provides source evidence. Request duration, database timing, and errors appear only after a supported application runs in an approved isolated environment and produces telemetry.",
  },
  {
    question: "Who is this for?",
    answer:
      "Students and AI-assisted builders working on small real applications, including people who want to understand code generated with AI. The first deep analysis target is Python and FastAPI.",
  },
];

const HomePage = async () => {
  const [apiReady, databaseReady] = await Promise.all([
    check("/health/live"),
    check("/health/ready"),
  ]);

  return (
    <div
      id="top"
      className="site-shell min-h-screen overflow-hidden text-slate-100"
    >
      <div
        aria-hidden="true"
      className="site-glow pointer-events-none absolute left-1/2 top-0 h-[32rem] w-full -translate-x-1/2"
      />
      <header className="relative z-20 border-b border-white/10 bg-[#090b13]/75 backdrop-blur-xl">
        <nav
          aria-label="Main navigation"
          className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-5 py-4 sm:px-8 lg:px-10"
        >
          <Brand />
          <div className="hidden items-center gap-7 text-sm font-medium text-slate-400 lg:flex">
            <a className="nav-link" href="#how-it-works">How it works</a>
            <a className="nav-link" href="#visual-lab">Visual lab</a>
            <a className="nav-link" href="#capabilities">Capabilities</a>
          </div>
          <AuthHeader />
        </nav>
      </header>

      <main>
        <section
          className="relative mx-auto grid max-w-7xl items-center gap-16 px-5 pb-16 pt-16 sm:px-8  lg:grid-cols-[1.05fr_.95fr] lg:gap-14 lg:px-10 lg:pb-32"
          aria-labelledby="hero-title"
        >
          <div className="animate-rise relative z-10">
            <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-brand-400/25 bg-brand-500/10 px-3.5 py-2 text-xs font-semibold tracking-wide text-brand-200 shadow-sm shadow-brand-500/10">
              <span
                className="size-1.5 rounded-full bg-brand-400 shadow-[0_0_12px_#E23744]"
                aria-hidden="true"
              />{" "}
              A visual learning lab for your code
            </div>
            <h1
              id="hero-title"
              className="max-w-2xl text-4xl font-semibold leading-tight tracking-tight text-white sm:text-5xl lg:text-6xl"
            >
              See the system behind{" "}
              <span className="gradient-text">the code AI wrote.</span>
            </h1>
            <p className="mt-8 max-w-xl text-lg leading-8 text-slate-400">
              Turn an unfamiliar project into a map you can explore. Trace API
              paths back to source, understand each step, and learn with an AI
              guide that shows its evidence.
            </p>
            <div className="mt-10 flex flex-wrap gap-3">
              <Link
                className="inline-flex items-center gap-3 rounded-xl bg-brand-500 px-5 py-3.5 text-sm font-bold text-white shadow-lg shadow-brand-500/25 transition duration-300 hover:-translate-y-1 hover:bg-brand-400 hover:shadow-brand-500/40"
                href="/dashboard"
              >
                Open your workspace <Arrow />
              </Link>
              <a
                className="inline-flex items-center gap-3 rounded-xl border border-white/15 bg-white/5 px-5 py-3.5 text-sm font-semibold text-white backdrop-blur-sm transition duration-300 hover:-translate-y-1 hover:border-white/30 hover:bg-white/10"
                href="#visual-lab"
              >
                Explore the vision <Arrow diagonal />
              </a>
            </div>
            <p className="mt-5 text-xs text-slate-500">
              The dashboard is open as a design preview. Repository analysis and
              AI guidance are still being built.
            </p>
            <div className="mt-9 flex flex-wrap gap-x-6 gap-y-3 border-t border-white/10 pt-5 text-xs font-medium text-slate-400">
              <span><span className="mr-2 text-brand-400">✳</span> Source linked</span>
              <span><span className="mr-2 text-violet-300">✳</span> AI guided</span>
              <span><span className="mr-2 text-cyan-300">✳</span> Evidence aware</span>
            </div>
          </div>

          <div
            className="animate-rise-delayed relative mx-auto w-full max-w-xl lg:max-w-none"
            aria-label="Illustration of a planned code flow workspace"
          >
            <div
              aria-hidden="true"
              className="absolute -inset-10 rounded-full bg-gradient-to-br from-brand-500/20 via-violet-500/10 to-transparent blur-3xl"
            />
            <div className="hero-panel lab-window relative overflow-hidden rounded-3xl border border-white/15 bg-[#101522]/95 shadow-2xl shadow-black/40">
              <div className="flex items-center justify-between border-b border-white/10 bg-white/5 px-5 py-4">
                <div className="flex items-center gap-3">
                  <span className="flex gap-1.5" aria-hidden="true">
                    <i className="size-2 rounded-full bg-brand-400/70" />
                    <i className="size-2 rounded-full bg-amber-300/70" />
                    <i className="size-2 rounded-full bg-brand-300/70" />
                  </span>
                  <span className="text-xs font-semibold tracking-wide text-slate-300">
                    FLOW EXPLORER
                  </span>
                </div>
                <span className="rounded-md border border-white/10 px-2 py-1 text-xs text-slate-500">
                  demo / checkout
                </span>
              </div>
              <div className="lab-grid relative p-5 sm:p-7">
                <div className="mb-5 flex items-center justify-between gap-3">
                  <span className="text-xs font-semibold text-slate-400">
                    Feature path
                  </span>
                  <PreviewLabel />
                </div>
                <div className="grid gap-5 sm:grid-cols-5">
                  <div className="sm:col-span-3">
                    <FlowNode
                      icon="API"
                      label="POST /checkout"
                      sublabel="Route · app/routes.py:28"
                    />
                    <div
                      className="signal-connector ml-7 h-5 w-px bg-brand-300/30"
                      aria-hidden="true"
                    />
                    <FlowNode
                      icon="fn"
                      label="create_order()"
                      sublabel="Handler · app/routes.py:34"
                      tone="cyan"
                    />
                    <div
                      className="signal-connector ml-7 h-5 w-px bg-cyan-300/30"
                      aria-hidden="true"
                    />
                    <FlowNode
                      icon="db"
                      label="save_order()"
                      sublabel="Possible data access"
                      tone="violet"
                    />
                  </div>
                  <div className="flex flex-col gap-3 sm:col-span-2">
                    <div className="rounded-xl border border-violet-300/20 bg-violet-300/5 p-4">
                      <div className="mb-3 flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-violet-300">
                        <span className="size-2 rounded-full bg-violet-300" />{" "}
                        AI guide
                      </div>
                      <p className="text-sm leading-relaxed text-slate-300">
                        “This route appears to validate the request, then save
                        an order.”
                      </p>
                      <p className="mt-3 text-xs text-slate-500">
                        Illustrative source explanation
                      </p>
                    </div>
                    <div className="rounded-xl border border-white/10 bg-slate-950/70 p-4 text-xs text-slate-400">
                      <span className="font-semibold text-brand-300">
                        SOURCE LINKED
                      </span>
                      <p className="mt-2 leading-relaxed">
                        Open a node to inspect the code behind the flow.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="float-chip absolute -bottom-5 left-4 flex items-center gap-2 rounded-xl border border-brand-400/25 bg-[#171b29] px-4 py-3 text-xs font-semibold text-brand-200 shadow-xl shadow-black/30 sm:-left-5">
              <span className="size-2 rounded-full bg-brand-300" /> Learn one
              step at a time
            </div>
          </div>
        </section>

        <section
          id="status"
          className="border-y border-white/10 bg-white/[0.025]"
          aria-labelledby="status-title"
        >
          <div className="mx-auto grid max-w-7xl gap-7 px-5 py-6 sm:px-8 md:grid-cols-3 md:items-center lg:px-10">
            <div>
              <p
                id="status-title"
                className="text-xs font-bold uppercase tracking-widest text-slate-500"
              >
                Live foundation status
              </p>
              <p className="mt-1 text-sm text-slate-300">
                The service checks below are real.
              </p>
            </div>
            <StatusItem name="FastAPI" detail="service" ready={apiReady} />
            <StatusItem
              name="PostgreSQL"
              detail="connection"
              ready={databaseReady}
            />
          </div>
        </section>

        <section
          id="how-it-works"
          className="mx-auto max-w-7xl px-5 py-24 sm:px-8 lg:px-10 lg:py-32"
          aria-labelledby="workflow-title"
        >
          <div className="max-w-2xl">
            <Eyebrow>One project. A clearer picture.</Eyebrow>
            <h2
              id="workflow-title"
              className="text-4xl font-bold tracking-tight text-white sm:text-5xl"
            >
              From “what does this do?” to{" "}
              <span className="text-brand-400">“now I see it.”</span>
            </h2>
            <p className="mt-5 text-lg leading-relaxed text-slate-400">
              A guided path from unfamiliar source code to an explanation you
              can verify.
            </p>
          </div>
          <div className="mt-12 grid gap-4 md:grid-cols-3">
            {workflow.map((step) => (
              <article
                className="glass-card group relative flex min-h-72 flex-col overflow-hidden rounded-3xl border border-white/10 p-7 transition duration-300 hover:-translate-y-2 hover:border-brand-400/35 hover:shadow-2xl hover:shadow-brand-950/25"
                key={step.number}
              >
                <div className="mb-10 flex items-start justify-between">
                  <span className="font-mono text-sm text-brand-400">
                    {step.number} / 03
                  </span>
                  <span
                    aria-hidden="true"
                    className="grid size-12 place-items-center rounded-xl border border-brand-400/15 bg-brand-500/10 text-2xl text-brand-200 transition group-hover:border-brand-400/40 group-hover:bg-brand-500/15"
                  >
                    {step.symbol}
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-white">
                  {step.title}
                </h3>
                <p className="mt-4 text-sm leading-relaxed text-slate-400">
                  {step.detail}
                </p>
                <span className="mt-auto pt-7 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Planned workflow
                </span>
              </article>
            ))}
          </div>
        </section>

        <section
          id="visual-lab"
          className="relative border-y border-white/10 bg-gradient-to-b from-[#101420] via-[#111522] to-[#0c0f18] py-24 lg:py-32"
          aria-labelledby="lab-title"
        >
          <div className="mx-auto max-w-7xl px-5 sm:px-8 lg:px-10">
            <div className="mb-12 flex flex-wrap items-end justify-between gap-5">
              <div className="max-w-2xl">
                <Eyebrow>Visual learning workspace</Eyebrow>
                <h2
                  id="lab-title"
                  className="text-4xl font-bold tracking-tight text-white sm:text-5xl"
                >
                  See the system. Follow the evidence.
                </h2>
                <p className="mt-5 text-lg leading-relaxed text-slate-400">
                  The planned workspace puts source, explanation, and measured
                  behavior in distinct views so you can tell what the code
                  suggests from what actually happened.
                </p>
              </div>
              <PreviewLabel />
            </div>
            <div className="grid gap-4 lg:grid-cols-12">
              <div className="lab-grid overflow-hidden rounded-3xl border border-white/10 bg-[#0d111c]/90 p-6 shadow-xl shadow-black/20 lg:col-span-7 sm:p-8">
                <div className="mb-8 flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-widest text-brand-300">
                      01 / Source map
                    </p>
                    <h3 className="mt-2 text-xl font-semibold text-white">
                      A flow you can actually follow
                    </h3>
                  </div>
                  <span className="rounded-full border border-brand-300/20 bg-brand-300/5 px-3 py-1.5 text-xs text-brand-200">
                    Source inferred
                  </span>
                </div>
                <div className="relative mx-auto max-w-lg py-2">
                  <div
                    className="absolute bottom-10 left-6 top-10 w-px bg-gradient-to-b from-brand-300/50 via-cyan-300/40 to-violet-300/40"
                    aria-hidden="true"
                  />
                  <div className="relative space-y-5">
                    <FlowNode
                      icon="01"
                      label="POST /checkout"
                      sublabel="api/routes.py · request enters"
                    />
                    <FlowNode
                      icon="02"
                      label="validate_cart()"
                      sublabel="services/cart.py · checks the items"
                      tone="cyan"
                    />
                    <FlowNode
                      icon="03"
                      label="create_order()"
                      sublabel="services/order.py · prepares the order"
                      tone="violet"
                    />
                    <FlowNode
                      icon="04"
                      label="Order response"
                      sublabel="api/routes.py · returns the result"
                    />
                  </div>
                </div>
                <div className="mt-8 flex flex-wrap gap-3 text-xs text-slate-500">
                  <span className="rounded-full border border-white/10 px-3 py-1.5">
                    ↳ Clickable source links planned
                  </span>
                  <span className="rounded-full border border-white/10 px-3 py-1.5">
                    ↳ Unresolved paths visible
                  </span>
                </div>
              </div>
              <div className="grid gap-4 lg:col-span-5">
                <div className="glass-card rounded-3xl border border-white/10 p-6 sm:p-8">
                  <p className="text-xs font-bold uppercase tracking-widest text-violet-300">
                    02 / AI guide
                  </p>
                  <h3 className="mt-2 text-xl font-semibold text-white">
                    Ask why, then inspect why.
                  </h3>
                  <div className="mt-6 rounded-xl border border-white/10 bg-white/3 p-4">
                    <p className="text-xs font-semibold text-slate-500">
                      YOU ASK
                    </p>
                    <p className="mt-2 text-sm text-slate-200">
                      Where does this API save the order?
                    </p>
                  </div>
                  <div className="mt-3 rounded-xl border border-violet-300/20 bg-violet-300/5 p-4">
                    <p className="text-xs font-semibold text-violet-300">
                      ILLUSTRATIVE ANSWER
                    </p>
                    <p className="mt-2 text-sm leading-relaxed text-slate-300">
                      The handler appears to call{" "}
                      <code className="text-violet-200">create_order()</code>.
                      Open the linked source to check the persistence path.
                    </p>
                    <p className="mt-3 text-xs text-slate-500">
                      Source inference · no runtime claim
                    </p>
                  </div>
                </div>
                <div className="glass-card rounded-3xl border border-white/10 p-6 sm:p-8">
                  <p className="text-xs font-bold uppercase tracking-widest text-cyan-300">
                    03 / Evidence key
                  </p>
                  <div className="mt-5 space-y-4">
                    <div className="flex items-center gap-3 text-sm text-slate-300">
                      <span className="size-2.5 rounded-full bg-brand-300" />{" "}
                      Inferred from source
                    </div>
                    <div className="flex items-center gap-3 text-sm text-slate-300">
                      <span className="size-2.5 rounded-full bg-cyan-300" />{" "}
                      Observed in a trace
                    </div>
                    <div className="flex items-center gap-3 text-sm text-slate-300">
                      <span className="size-2.5 rounded-full bg-violet-300" />{" "}
                      AI hypothesis to test
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section
          id="capabilities"
          className="mx-auto max-w-7xl px-5 py-24 sm:px-8 lg:px-10 lg:py-32"
          aria-labelledby="capabilities-title"
        >
          <div className="max-w-2xl">
            <Eyebrow>Go deeper when your app can run</Eyebrow>
            <h2
              id="capabilities-title"
              className="text-4xl font-bold tracking-tight text-white sm:text-5xl"
            >
              From understanding to diagnosis.
            </h2>
            <p className="mt-5 text-lg leading-relaxed text-slate-400">
              Source-only learning comes first. A supported isolated runtime can
              later add actual traces, timings, and controlled experiments.
            </p>
          </div>
          <div className="mt-12 grid gap-4 md:grid-cols-3">
            <article className="glass-card overflow-hidden rounded-3xl border border-white/10 p-6 transition duration-300 hover:-translate-y-1 hover:border-cyan-300/25">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-widest text-cyan-300">
                  Runtime trace
                </span>
                <span className="text-xs text-slate-500">Planned</span>
              </div>
              <div className="mt-9 space-y-3 rounded-xl border border-white/10 bg-slate-950/70 p-4">
                <div className="h-3 w-10/12 rounded bg-cyan-300/70" />
                <div className="ml-5 h-3 w-7/12 rounded bg-cyan-300/45" />
                <div className="ml-10 h-3 w-5/12 rounded bg-violet-300/60" />
                <div className="ml-5 h-3 w-4/12 rounded bg-brand-300/50" />
              </div>
              <h3 className="mt-8 text-xl font-semibold text-white">
                See where a request goes.
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-slate-400">
                A trace waterfall links observed steps, errors, and real
                duration to the flow when instrumentation is available.
              </p>
            </article>
            <article className="glass-card overflow-hidden rounded-3xl border border-white/10 p-6 transition duration-300 hover:-translate-y-1 hover:border-violet-300/25">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-widest text-violet-300">
                  Data timing
                </span>
                <span className="text-xs text-slate-500">Planned</span>
              </div>
              <div className="mt-9 rounded-xl border border-white/10 bg-slate-950/70 p-4">
                <div className="flex h-20 items-end gap-2" aria-hidden="true">
                  <span className="h-6 w-full rounded-t bg-violet-300/30" />
                  <span className="h-10 w-full rounded-t bg-violet-300/40" />
                  <span className="h-7 w-full rounded-t bg-violet-300/40" />
                  <span className="h-16 w-full rounded-t bg-violet-300/70" />
                  <span className="h-9 w-full rounded-t bg-violet-300/40" />
                  <span className="h-12 w-full rounded-t bg-violet-300/50" />
                  <span className="h-8 w-full rounded-t bg-violet-300/30" />
                </div>
              </div>
              <h3 className="mt-8 text-xl font-semibold text-white">
                Find the slow step.
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-slate-400">
                Explore measured database and endpoint timing, then form a
                specific improvement to test.
              </p>
            </article>
            <article className="glass-card overflow-hidden rounded-3xl border border-white/10 p-6 transition duration-300 hover:-translate-y-1 hover:border-brand-300/25">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-widest text-brand-300">
                  System design lab
                </span>
                <span className="text-xs text-slate-500">Planned</span>
              </div>
              <div className="mt-9 rounded-xl border border-white/10 bg-slate-950/70 p-4">
                <svg
                  aria-hidden="true"
                  className="h-20 w-full"
                  preserveAspectRatio="none"
                  viewBox="0 0 300 80"
                >
                  <path
                    d="M0 57 35 53 70 54 105 41 140 42 175 22 210 34 245 15 300 28"
                    fill="none"
                    stroke="#E23744"
                    strokeWidth="2.5"
                  />
                  <path
                    d="M0 65 35 62 70 64 105 58 140 59 175 48 210 53 245 41 300 45"
                    fill="none"
                    stroke="#a78bfa"
                    strokeWidth="2"
                    strokeDasharray="5 5"
                  />
                </svg>
              </div>
              <h3 className="mt-8 text-xl font-semibold text-white">
                Test the tradeoff.
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-slate-400">
                Use bounded virtual-user and failure scenarios against approved
                isolated targets, then compare before and after.
              </p>
            </article>
          </div>
          <p className="mt-5 text-xs text-slate-500">
            Illustrative visuals only. No trace, database timing, or load result
            is being shown here.
          </p>
        </section>

        <section
          className="mx-auto max-w-7xl px-5 pb-24 sm:px-8 lg:px-10 lg:pb-32"
          aria-labelledby="faq-title"
        >
          <div className="grid gap-12 border-t border-white/10 pt-16 lg:grid-cols-3">
            <div>
              <Eyebrow>Questions worth asking</Eyebrow>
              <h2
                id="faq-title"
                className="text-3xl font-bold tracking-tight text-white sm:text-4xl"
              >
                Clarity starts here.
              </h2>
            </div>
            <div className="space-y-3 lg:col-span-2">
              {questions.map((item) => (
                <details
                  className="faq-item glass-card group rounded-2xl border border-white/10 px-5 py-4 transition hover:border-white/20"
                  key={item.question}
                >
                  <summary className="flex cursor-pointer list-none items-center justify-between gap-5 text-sm font-semibold text-white marker:hidden">
                    {item.question}
                    <span
                      aria-hidden="true"
                      className="text-xl text-brand-300 transition group-open:rotate-45"
                    >
                      +
                    </span>
                  </summary>
                  <p className="mt-4 max-w-2xl text-sm leading-relaxed text-slate-400">
                    {item.answer}
                  </p>
                </details>
              ))}
            </div>
          </div>
        </section>

        <section
          className="border-t border-white/10 bg-gradient-to-r from-brand-950/30 via-[#111522] to-violet-950/20 py-20"
          aria-labelledby="closing-title"
        >
          <div className="mx-auto flex max-w-7xl flex-col items-start justify-between gap-8 px-5 sm:px-8 lg:flex-row lg:items-center lg:px-10">
            <div>
              <Eyebrow>Start with the foundation</Eyebrow>
              <h2
                id="closing-title"
                className="max-w-xl text-3xl font-bold tracking-tight text-white sm:text-4xl"
              >
                Build a better mental model of your code.
              </h2>
              <p className="mt-4 max-w-xl text-sm leading-relaxed text-slate-400">
                Follow the open project as the visual learning workflow takes
                shape.
              </p>
            </div>
            <a
              className="inline-flex items-center gap-3 rounded-xl bg-brand-500 px-5 py-3.5 text-sm font-bold text-white shadow-lg shadow-brand-500/20 transition duration-300 hover:-translate-y-1 hover:bg-brand-400"
              href={repositoryUrl}
              rel="noreferrer"
              target="_blank"
            >
              Explore the repository <Arrow diagonal />
            </a>
          </div>
        </section>
      </main>

      <footer
        className="border-t border-white/10 bg-slate-950"
        aria-label="Footer"
      >
        <div className="mx-auto grid max-w-7xl gap-12 px-5 py-16 sm:grid-cols-2 sm:px-8 lg:grid-cols-4 lg:px-10">
          <div className="sm:col-span-2">
            <Brand />
            <p className="mt-5 max-w-sm text-sm leading-relaxed text-slate-400">
              A visual code-flow learning lab for students and AI-assisted
              builders. Trace ideas back to source and keep measured behavior
              separate from guesses.
            </p>
            <div className="mt-6 flex flex-wrap gap-2">
              <span className="rounded-full border border-white/10 px-3 py-1 text-xs text-slate-500">
                Python first
              </span>
              <span className="rounded-full border border-white/10 px-3 py-1 text-xs text-slate-500">
                Source linked
              </span>
              <span className="rounded-full border border-white/10 px-3 py-1 text-xs text-slate-500">
                Open development
              </span>
            </div>
          </div>
          <div>
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-300">
              Explore
            </h3>
            <ul className="mt-5 space-y-3 text-sm text-slate-400">
              <li>
                <a className="footer-link" href="#how-it-works">
                  How it works
                </a>
              </li>
              <li>
                <a className="footer-link" href="#visual-lab">
                  Visual lab
                </a>
              </li>
              <li>
                <a className="footer-link" href="#capabilities">
                  Capabilities
                </a>
              </li>
              <li>
                <a className="footer-link" href="#status">
                  Live status
                </a>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-300">
              Project
            </h3>
            <ul className="mt-5 space-y-3 text-sm text-slate-400">
              <li>
                <a
                  className="footer-link"
                  href={repositoryUrl}
                  rel="noreferrer"
                  target="_blank"
                >
                  GitHub repository ↗
                </a>
              </li>
              <li>
                <a
                  className="footer-link"
                  href={`${repositoryUrl}/blob/main/README.md`}
                  rel="noreferrer"
                  target="_blank"
                >
                  Read the project ↗
                </a>
              </li>
              <li>
                <a
                  className="footer-link"
                  href={`${repositoryUrl}/tree/main/docs`}
                  rel="noreferrer"
                  target="_blank"
                >
                  Documentation ↗
                </a>
              </li>
              <li>
                <a
                  className="footer-link"
                  href={`${apiPublicUrl}/docs`}
                  rel="noreferrer"
                  target="_blank"
                >
                  Live API docs ↗
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className="mx-auto flex max-w-7xl flex-col gap-3 border-t border-white/10 px-5 py-6 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-8 lg:px-10">
          <span>
            © {new Date().getFullYear()} CodeFlowAtlas. Built to make code
            easier to understand.
          </span>
          <span>Visual analysis is planned · Platform health is live</span>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
