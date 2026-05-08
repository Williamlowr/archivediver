import { copy } from "../copy";
import type { DevInfo } from "../types";

function formatToolInput(input: Record<string, unknown>) {
  const parts = Object.entries(input)
    .filter(([, value]) => value !== null && value !== undefined && value !== "")
    .map(([key, value]) => `${key}: ${String(value)}`);

  return parts.join(" · ");
}

export function DevDetails({ dev }: { dev: DevInfo }) {
  return (
    <details className="dev-panel" open data-testid="dev-details">
      <summary>
        <span>{copy.devLabel}</span>
        <span className="dev-hint">{copy.devHint}</span>
      </summary>
      <div className="dev-body">
        <section className="dev-section">
          <h4>Tool Calls</h4>
          {dev.tool_calls.length > 0 ? (
            <ul className="dev-tool-list">
              {dev.tool_calls.map((toolCall, index) => (
                <li key={`${toolCall.tool}-${index}`} className="dev-tool-item">
                  <div className="dev-tool-header">
                    <strong>{toolCall.tool}</strong>
                    <span>Result count: {toolCall.output_count}</span>
                  </div>
                  <p className="quiet-note">{formatToolInput(toolCall.input)}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="quiet-note">{copy.noToolCalls}</p>
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
