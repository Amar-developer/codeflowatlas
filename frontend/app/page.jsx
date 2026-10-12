export const dynamic = 'force-dynamic';

const apiInternalUrl = process.env.API_INTERNAL_URL || 'http://127.0.0.1:8000';
const apiPublicUrl = process.env.API_PUBLIC_URL || 'http://127.0.0.1:8000';

async function check(path) {
  try {
    const response = await fetch(`${apiInternalUrl}${path}`, {
      cache: 'no-store',
      signal: AbortSignal.timeout(3000),
    });
    return response.ok;
  } catch {
    return false;
  }
}

const capabilities = [
  { number: '01', title: 'Repository import', detail: 'Pin a Git revision and analyze source safely.', status: 'Planned' },
  { number: '02', title: 'API and code graph', detail: 'Trace endpoints through functions and dependencies.', status: 'Planned' },
  { number: '03', title: 'Runtime tracing', detail: 'Compare static relationships with observed spans.', status: 'Planned' },
  { number: '04', title: 'Experiment lab', detail: 'Run controlled load and failure scenarios.', status: 'Planned' },
  { number: '05', title: 'Evidence and AI', detail: 'Explain bottlenecks with inspectable sources.', status: 'Planned' },
];

export default async function HomePage() {
  const [apiReady, databaseReady] = await Promise.all([
    check('/health/live'),
    check('/health/ready'),
  ]);

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">{'{ }'}</span>
          <span>CodeFlowAtlas</span>
        </div>
        <span className="phase">Foundation build</span>
      </header>

      <section className="hero" aria-labelledby="hero-title">
        <div className="hero-copy">
          <p className="eyebrow">REPOSITORY INTELLIGENCE LAB</p>
          <h1 id="hero-title">Understand what the code actually does.</h1>
          <p className="intro">
            Connect source analysis, API paths, runtime traces, and controlled experiments
            in one engineering workspace. The foundation is live; the analysis workflow is next.
          </p>
          <div className="hero-actions">
            <a className="button-primary" href={`${apiPublicUrl}/docs`} target="_blank" rel="noreferrer">
              Open API documentation <span aria-hidden="true">↗</span>
            </a>
            <span className="hero-note">Python · FastAPI · PostgreSQL · Next.js</span>
          </div>
        </div>
        <div className="signal-panel" aria-label="Platform status">
          <div className="panel-head">
            <span>PLATFORM STATUS</span>
            <span className="panel-indicator" aria-hidden="true" />
          </div>
          <div className="status-row">
            <div><strong>FastAPI service</strong><small>Backend process</small></div>
            <span className={apiReady ? 'status online' : 'status offline'}>{apiReady ? 'Online' : 'Unavailable'}</span>
          </div>
          <div className="status-row">
            <div><strong>PostgreSQL</strong><small>Database connection</small></div>
            <span className={databaseReady ? 'status online' : 'status offline'}>{databaseReady ? 'Online' : 'Unavailable'}</span>
          </div>
          <div className="panel-foot">Live status from the CodeFlowAtlas API</div>
        </div>
      </section>

      <section className="workflow" aria-labelledby="workflow-title">
        <div className="section-heading">
          <div>
            <p className="eyebrow">THE PRODUCT PATH</p>
            <h2 id="workflow-title">From repository to evidence.</h2>
          </div>
          <span className="section-caption">Build sequence</span>
        </div>
        <div className="steps">
          {capabilities.map((item) => (
            <article className="step" key={item.number}>
              <span className="step-number">{item.number}</span>
              <div className="step-body">
                <h3>{item.title}</h3>
                <p>{item.detail}</p>
              </div>
              <span className="step-status">{item.status}</span>
            </article>
          ))}
        </div>
      </section>

      <footer className="footer">
        <span>CodeFlowAtlas engineering workspace</span>
        <span>Static inference · Runtime observation · Grounded explanation</span>
      </footer>
    </main>
  );
}
