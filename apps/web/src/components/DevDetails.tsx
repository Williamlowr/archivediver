import { copy } from "../copy";
import type { DevInfo, ToolCallRecord } from "../types";

const TOOL_SECTIONS = [
  { key: "search_items", label: "Search" },
  { key: "get_item_details", label: "Item Details" },
  { key: "get_item_media", label: "Item Media" },
] as const;

function formatToolInput(input: Record<string, unknown>) {
  const parts = Object.entries(input)
    .filter(([, value]) => value !== null && value !== undefined && value !== "")
    .map(([key, value]) => `${key}: ${String(value)}`);
  return parts.join(" · ");
}

function ToolSection({ label, calls }: { label: string; calls: ToolCallRecord[] }) {
  if (calls.length === 0) return null;
  return (
    <div className="dev-tool-section">
      <p className="dev-tool-section-label">{label}</p>
      {calls.map((tc, i) => (
        <div key={i} className="dev-tool-item">
          <div className="dev-tool-header">
            <strong>{tc.tool}</strong>
            <span>Result count: {tc.output_count}</span>
          </div>
          <p className="quiet-note">{formatToolInput(tc.input)}</p>
        </div>
      ))}
    </div>
  );
}

export function DevDetails({ dev }: { dev: DevInfo }) {
  const hasAnyCalls = dev.tool_calls.length > 0;

  return (
    <details className="dev-panel" open data-testid="dev-details">
      <summary>
        <span>{copy.devLabel}</span>
        <span className="dev-hint">{copy.devHint}</span>
      </summary>
      <div className="dev-body">
        <section className="dev-section">
          <h4>Tool Calls</h4>
          {!hasAnyCalls ? (
            <p className="quiet-note">{copy.noToolCalls}</p>
          ) : (
            <div className="dev-tool-list">
              {TOOL_SECTIONS.map(({ key, label }) => (
                <ToolSection
                  key={key}
                  label={label}
                  calls={dev.tool_calls.filter((tc) => tc.tool === key)}
                />
              ))}
            </div>
          )}
        </section>

        <section className="dev-section">
          <h4>Limitations</h4>
          {dev.limitations.length > 0 ? (
            <ul className="notice-list dev-limitations">
              {dev.limitations.map((limitation) => (
                <li key={limitation}>{limitation}</li>
              ))}
            </ul>
          ) : (
            <p className="quiet-note">{copy.noLimitations}</p>
          )}
        </section>
      </div>
    </details>
  );
}
