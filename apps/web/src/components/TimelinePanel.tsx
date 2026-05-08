import { copy } from "../copy";
import type { TimelineEntry } from "../types";

export function TimelinePanel({ timeline }: { timeline: TimelineEntry[] }) {
  return (
    <aside className="timeline-panel">
      <div className="section-heading">
        <h3>{copy.timelineLabel}</h3>
      </div>
      {timeline.length > 0 ? (
        <ol className="timeline-list">
          {timeline.map((entry) => (
            <li key={`${entry.date}-${entry.label}`} className="timeline-item">
              <span className="timeline-date">{entry.date}</span>
              <span className="timeline-label">{entry.label}</span>
            </li>
          ))}
        </ol>
      ) : (
        <p className="quiet-note">{copy.noTimeline}</p>
      )}
    </aside>
  );
}
