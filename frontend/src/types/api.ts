export type Incident = {
  id: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  started_at?: string | null;
  detected_at?: string | null;
  resolved_at?: string | null;
  affected_services: string[];
  customer_impact: string;
  analysis_status: string;
  analysis_error?: string | null;
  report: InvestigationReport | Record<string, never>;
};

export type Evidence = {
  id: string;
  display_id: string;
  incident_id: string;
  evidence_type: string;
  source: string;
  service?: string | null;
  environment?: string | null;
  timestamp?: string | null;
  raw_content: string;
  normalized_content: Record<string, unknown>;
  metadata: Record<string, unknown>;
  ingestion_status: string;
};

export type TimelineEvent = {
  id: string;
  timestamp?: string | null;
  event_type: string;
  service?: string | null;
  title: string;
  description: string;
  evidence_ids: string[];
  confidence: string;
  source: string;
};

export type Hypothesis = {
  id: string;
  rank: number;
  title: string;
  description: string;
  confidence: string;
  status: string;
  supporting_evidence_ids: string[];
  contradicting_evidence_ids: string[];
  missing_evidence: string[];
  validation_steps: string[];
  generated_by: string;
};

export type RecommendedAction = {
  id: string;
  hypothesis_id?: string | null;
  action_type: string;
  title: string;
  description: string;
  risk_level: string;
  expected_result: string;
  prerequisites: string[];
  validation: string[];
  rollback_considerations: string;
  requires_approval: boolean;
  command_example?: string | null;
  status: string;
};

export type InvestigationReport = {
  executive_summary: string;
  confirmed_facts: string[];
  unknowns: string[];
  affected_components: string[];
  blast_radius: Record<string, unknown>;
  deterministic_findings: Record<string, unknown>;
  communication_update: Record<string, string>;
  postmortem_draft: Record<string, unknown>;
};

