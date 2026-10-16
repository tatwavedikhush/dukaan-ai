import { useEffect, useState } from 'react';

type HealthState =
  | { status: 'loading' }
  | { status: 'success'; message: string }
  | { status: 'failure'; message: string };

export default function App() {
  const [health, setHealth] = useState<HealthState>({ status: 'loading' });

  useEffect(() => {
    fetch('/health')
      .then(async (response) => {
        if (!response.ok) throw new Error(`Request failed (${response.status})`);
        const body = (await response.json()) as { status?: string };
        setHealth({ status: 'success', message: body.status ?? 'ok' });
      })
      .catch((error: unknown) => {
        setHealth({
          status: 'failure',
          message: error instanceof Error ? error.message : 'Unable to reach the backend',
        });
      });
  }, []);

  return (
    <main className="shell">
      <section className="card" aria-live="polite">
        <p className="eyebrow">DukaanAI</p>
        <h1>Welcome to your shop dashboard</h1>
        <p className="subtitle">Frontend placeholder · backend connection check</p>
        <div className={`status status-${health.status}`}>
          <span className="dot" />
          {health.status === 'loading' && 'Checking backend health…'}
          {health.status === 'success' && `Backend is healthy (${health.message})`}
          {health.status === 'failure' && `Backend unavailable: ${health.message}`}
        </div>
      </section>
    </main>
  );
}
