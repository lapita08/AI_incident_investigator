import { Activity, AlertTriangle, Database, Plus } from "lucide-react";
import type { Incident } from "../types/api";
import { StatusBadge } from "../components/StatusBadge";

type Props = {
  incidents: Incident[];
  activeIncidentId?: string;
  onSelect: (incidentId: string) => void;
  onLoadSample: (scenarioId: string) => void;
  onCreate: () => void;
};

export function Dashboard({ incidents, activeIncidentId, onSelect, onLoadSample, onCreate }: Props) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <Activity size={22} />
        <div>
          <strong>AI Incident Investigator</strong>
          <span>Evidence-first SRE workspace</span>
        </div>
      </div>
      <button className="primary" type="button" onClick={onCreate}>
        <Plus size={16} /> New incident
      </button>
      <div className="sample-actions">
        <button type="button" onClick={() => onLoadSample("db-latency-incident")}>
          <Database size={16} /> Load DB latency demo
        </button>
        <button type="button" onClick={() => onLoadSample("memory-leak-incident")}>
          <AlertTriangle size={16} /> Load memory demo
        </button>
      </div>
      <h2>Recent incidents</h2>
      <div className="incident-list">
        {incidents.map((incident) => (
          <button className={incident.id === activeIncidentId ? "incident-row active" : "incident-row"} key={incident.id} type="button" onClick={() => onSelect(incident.id)}>
            <span>{incident.title}</span>
            <small>
              <StatusBadge label={incident.severity} tone={incident.severity === "sev1" ? "bad" : "warn"} />
              <StatusBadge label={incident.status} />
            </small>
            <small>{incident.affected_services.join(", ") || "No services yet"}</small>
          </button>
        ))}
      </div>
    </aside>
  );
}

