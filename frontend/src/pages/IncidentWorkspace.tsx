import { CheckCircle2, Download, FileText, Play, ShieldAlert, XCircle } from "lucide-react";
import { useMemo, useState } from "react";
import { EvidenceLink } from "../components/EvidenceLink";
import { StatusBadge } from "../components/StatusBadge";
import type { Evidence, Hypothesis, Incident, RecommendedAction, TimelineEvent } from "../types/api";

type Tab = "overview" | "timeline" | "evidence" | "signals" | "hypotheses" | "actions" | "communications" | "postmortem";

type Props = {
  incident: Incident;
  evidence: Evidence[];
  timeline: TimelineEvent[];
  hypotheses: Hypothesis[];
  actions: RecommendedAction[];
  onAnalyze: () => void;
  onHypothesisStatus: (hypothesisId: string, status: string) => void;
  onRefreshOutputs: () => void;
};

export function IncidentWorkspace({ incident, evidence, timeline, hypotheses, actions, onAnalyze, onHypothesisStatus, onRefreshOutputs }: Props) {
  const [tab, setTab] = useState<Tab>("overview");
  const [openEvidence, setOpenEvidence] = useState<Evidence | null>(null);
  const leading = hypotheses[0];
  const report = incident.report;
  const findings = (report as { deterministic_findings?: Record<string, unknown> }).deterministic_findings ?? {};
  const progress = [
    ["Ingested evidence", evidence.length > 0],
    ["Parsed logs", evidence.some((item) => item.evidence_type === "log")],
    ["Built timeline", timeline.length > 0],
    ["Detected anomalies", Array.isArray(findings.metric_anomalies) && findings.metric_anomalies.length > 0],
    ["Generated hypotheses", hypotheses.length > 0],
    ["Produced report", Boolean((report as { executive_summary?: string }).executive_summary)]
  ];
  const duration = useMemo(() => {
    if (!incident.started_at) return "Unknown duration";
    const end = incident.resolved_at ? new Date(incident.resolved_at) : new Date();
    const minutes = Math.max(0, Math.round((end.getTime() - new Date(incident.started_at).getTime()) / 60000));
    return `${minutes}m`;
  }, [incident.started_at, incident.resolved_at]);

  return (
    <main className="workspace">
      <header className="incident-header">
        <div>
          <h1>{incident.title}</h1>
          <p>{incident.description}</p>
          <div className="chips">
            <StatusBadge label={incident.severity} tone={incident.severity === "sev1" ? "bad" : "warn"} />
            <StatusBadge label={incident.status} />
            <StatusBadge label={duration} />
            {incident.affected_services.map((service) => (
              <StatusBadge key={service} label={service} tone="neutral" />
            ))}
          </div>
        </div>
        <div className="header-actions">
          <button type="button" onClick={onAnalyze}>
            <Play size={16} /> Run investigation
          </button>
          <a className="button" href={`/api/v1/incidents/${incident.id}/export?format=markdown`} target="_blank" rel="noreferrer">
            <Download size={16} /> Export
          </a>
        </div>
      </header>

      <section className="progress-strip">
        {progress.map(([label, done]) => (
          <div className="progress-item" key={String(label)}>
            {done ? <CheckCircle2 size={17} /> : <XCircle size={17} />}
            <span>{label}</span>
          </div>
        ))}
      </section>

      <nav className="tabs">
        {(["overview", "timeline", "evidence", "signals", "hypotheses", "actions", "communications", "postmortem"] as Tab[]).map((name) => (
          <button className={tab === name ? "active" : ""} key={name} type="button" onClick={() => setTab(name)}>
            {name}
          </button>
        ))}
      </nav>

      {tab === "overview" && (
        <section className="panel-grid">
          <article>
            <h2>Current situation</h2>
            <p>{(report as { executive_summary?: string }).executive_summary ?? "Run the investigation to generate an evidence-backed summary."}</p>
          </article>
          <article>
            <h2>Confirmed facts</h2>
            <List values={(report as { confirmed_facts?: string[] }).confirmed_facts ?? []} fallback="No confirmed facts generated yet." />
          </article>
          <article>
            <h2>Unknowns</h2>
            <List values={(report as { unknowns?: string[] }).unknowns ?? []} fallback="Unknowns will appear after analysis." />
          </article>
          <article>
            <h2>Leading hypothesis</h2>
            {leading ? <p>{leading.title}</p> : <p>No hypothesis generated yet.</p>}
          </article>
        </section>
      )}

      {tab === "timeline" && (
        <section className="table-panel">
          {timeline.map((event) => (
            <div className="timeline-row" key={event.id}>
              <time>{event.timestamp ? new Date(event.timestamp).toLocaleString() : "No timestamp"}</time>
              <strong>{event.title}</strong>
              <span>{event.service ?? "unknown service"}</span>
              <p>{event.description}</p>
              <div>{event.evidence_ids.map((id) => <EvidenceLink key={id} id={id} evidence={evidence} onOpen={setOpenEvidence} />)}</div>
            </div>
          ))}
        </section>
      )}

      {tab === "evidence" && (
        <section className="evidence-grid">
          {evidence.map((item) => (
            <button className="evidence-card" key={item.id} type="button" onClick={() => setOpenEvidence(item)}>
              <strong>{item.display_id}</strong>
              <span>{item.evidence_type} · {item.source}</span>
              <small>{item.service ?? "unknown service"} · {item.ingestion_status}</small>
              <pre>{JSON.stringify(item.normalized_content, null, 2).slice(0, 420)}</pre>
            </button>
          ))}
        </section>
      )}

      {tab === "signals" && <Signals findings={findings} />}

      {tab === "hypotheses" && (
        <section className="hypothesis-list">
          {hypotheses.map((hypothesis) => (
            <article key={hypothesis.id}>
              <div className="row-between">
                <h2>{hypothesis.rank}. {hypothesis.title}</h2>
                <StatusBadge label={hypothesis.confidence} tone={hypothesis.confidence === "high" ? "good" : "warn"} />
              </div>
              <p>{hypothesis.description}</p>
              <h3>Supporting evidence</h3>
              <div>{hypothesis.supporting_evidence_ids.map((id) => <EvidenceLink key={id} id={id} evidence={evidence} onOpen={setOpenEvidence} />)}</div>
              <h3>Contradicting evidence</h3>
              <div>{hypothesis.contradicting_evidence_ids.length ? hypothesis.contradicting_evidence_ids.map((id) => <EvidenceLink key={id} id={id} evidence={evidence} onOpen={setOpenEvidence} />) : "None cited"}</div>
              <h3>Missing evidence</h3>
              <List values={hypothesis.missing_evidence} />
              <h3>Validation steps</h3>
              <List values={hypothesis.validation_steps} />
              <div className="actions-inline">
                <button type="button" onClick={() => onHypothesisStatus(hypothesis.id, "confirmed")}>Confirm</button>
                <button type="button" onClick={() => onHypothesisStatus(hypothesis.id, "rejected")}>Reject</button>
                <StatusBadge label={hypothesis.status} />
              </div>
            </article>
          ))}
        </section>
      )}

      {tab === "actions" && (
        <section className="action-columns">
          {["diagnostic", "mitigation", "recovery"].map((kind) => (
            <article key={kind}>
              <h2>{kind}</h2>
              {actions.filter((action) => action.action_type === kind).map((action) => (
                <div className="action-card" key={action.id}>
                  <div className="row-between"><strong>{action.title}</strong><StatusBadge label={action.risk_level} tone={action.risk_level === "high" || action.risk_level === "critical" ? "bad" : "warn"} /></div>
                  <p>{action.description}</p>
                  {action.requires_approval && <p className="warning"><ShieldAlert size={16} /> Human approval required</p>}
                  <small>{action.expected_result}</small>
                </div>
              ))}
            </article>
          ))}
        </section>
      )}

      {tab === "communications" && (
        <section className="panel-grid">
          <button type="button" onClick={onRefreshOutputs}><FileText size={16} /> Generate drafts</button>
          {Object.entries((report as { communication_update?: Record<string, string> }).communication_update ?? {}).map(([kind, text]) => (
            <article key={kind}><h2>{kind}</h2><p>{text}</p><StatusBadge label="draft requires review" tone="warn" /></article>
          ))}
        </section>
      )}

      {tab === "postmortem" && (
        <section className="table-panel">
          <pre>{JSON.stringify((report as { postmortem_draft?: Record<string, unknown> }).postmortem_draft ?? {}, null, 2)}</pre>
        </section>
      )}

      {openEvidence && (
        <div className="modal-backdrop" onClick={() => setOpenEvidence(null)}>
          <dialog open onClick={(event) => event.stopPropagation()}>
            <div className="row-between"><h2>{openEvidence.display_id}</h2><button type="button" onClick={() => setOpenEvidence(null)}>Close</button></div>
            <p>{openEvidence.evidence_type} from {openEvidence.source}</p>
            <h3>Normalized</h3>
            <pre>{JSON.stringify(openEvidence.normalized_content, null, 2)}</pre>
            <h3>Raw</h3>
            <pre>{openEvidence.raw_content}</pre>
          </dialog>
        </div>
      )}
    </main>
  );
}

function List({ values, fallback = "None" }: { values: string[]; fallback?: string }) {
  if (!values.length) return <p>{fallback}</p>;
  return <ul>{values.map((value) => <li key={value}>{value}</li>)}</ul>;
}

function Signals({ findings }: { findings: Record<string, unknown> }) {
  return (
    <section className="panel-grid">
      {Object.entries(findings).map(([key, value]) => (
        <article key={key}>
          <h2>{key.replace(/_/g, " ")}</h2>
          <pre>{JSON.stringify(value, null, 2)}</pre>
        </article>
      ))}
      {!Object.keys(findings).length && <p>No deterministic findings yet.</p>}
    </section>
  );
}
