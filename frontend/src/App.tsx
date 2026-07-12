import { useCallback, useEffect, useState } from "react";
import { Dashboard } from "./pages/Dashboard";
import { IncidentWorkspace } from "./pages/IncidentWorkspace";
import { api } from "./services/api";
import type { Evidence, Hypothesis, Incident, RecommendedAction, TimelineEvent } from "./types/api";
import "./styles.css";

export default function App() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [activeId, setActiveId] = useState<string>();
  const [active, setActive] = useState<Incident>();
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [hypotheses, setHypotheses] = useState<Hypothesis[]>([]);
  const [actions, setActions] = useState<RecommendedAction[]>([]);
  const [error, setError] = useState<string>();

  const refreshList = useCallback(async (selectFirst = false) => {
    const rows = await api.incidents();
    setIncidents(rows);
    if (selectFirst && rows[0]) setActiveId(rows[0].id);
  }, []);

  const refreshWorkspace = useCallback(async (id = activeId) => {
    if (!id) return;
    const [incident, evidenceRows, timelineRows, hypothesisRows, actionRows] = await Promise.all([
      api.incident(id),
      api.evidence(id),
      api.timeline(id),
      api.hypotheses(id),
      api.actions(id)
    ]);
    setActive(incident);
    setEvidence(evidenceRows);
    setTimeline(timelineRows);
    setHypotheses(hypothesisRows);
    setActions(actionRows);
  }, [activeId]);

  useEffect(() => {
    refreshList(true).catch((err: Error) => setError(err.message));
  }, [refreshList]);

  useEffect(() => {
    refreshWorkspace().catch((err: Error) => setError(err.message));
  }, [activeId, refreshWorkspace]);

  async function loadSample(scenarioId: string) {
    const incident = await api.loadSample(scenarioId);
    await refreshList();
    setActiveId(incident.id);
  }

  async function createIncident() {
    const incident = await api.createIncident({
      title: "New investigation workspace",
      description: "Add evidence and run analysis.",
      severity: "sev3",
      status: "investigating",
      affected_services: []
    });
    await refreshList();
    setActiveId(incident.id);
  }

  async function analyze() {
    if (!activeId) return;
    await api.analyze(activeId);
    await refreshWorkspace(activeId);
    await refreshList();
  }

  async function updateHypothesis(hypothesisId: string, status: string) {
    if (!activeId) return;
    await api.updateHypothesis(activeId, hypothesisId, status);
    await refreshWorkspace(activeId);
  }

  return (
    <div className="app-shell">
      <Dashboard incidents={incidents} activeIncidentId={activeId} onSelect={setActiveId} onLoadSample={(id) => loadSample(id).catch((err: Error) => setError(err.message))} onCreate={() => createIncident().catch((err: Error) => setError(err.message))} />
      {active ? (
        <IncidentWorkspace
          incident={active}
          evidence={evidence}
          timeline={timeline}
          hypotheses={hypotheses}
          actions={actions}
          onAnalyze={() => analyze().catch((err: Error) => setError(err.message))}
          onHypothesisStatus={(id, status) => updateHypothesis(id, status).catch((err: Error) => setError(err.message))}
          onRefreshOutputs={() => refreshWorkspace().catch((err: Error) => setError(err.message))}
        />
      ) : (
        <main className="empty-state">
          <h1>Open or load an incident workspace</h1>
          <p>Use the demo scenarios to review the investigation flow without an external LLM key.</p>
        </main>
      )}
      {error && <div className="toast" role="alert">{error}<button type="button" onClick={() => setError(undefined)}>Dismiss</button></div>}
    </div>
  );
}
