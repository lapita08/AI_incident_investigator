import type { Evidence } from "../types/api";

type Props = {
  id: string;
  evidence: Evidence[];
  onOpen: (item: Evidence) => void;
};

export function EvidenceLink({ id, evidence, onOpen }: Props) {
  const item = evidence.find((candidate) => candidate.display_id === id);
  return (
    <button className="evidence-link" type="button" onClick={() => item && onOpen(item)} disabled={!item} title={item ? "Open cited evidence" : "Evidence not loaded"}>
      {id}
    </button>
  );
}

