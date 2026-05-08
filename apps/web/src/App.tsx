import { FormEvent, useState } from "react";

import { exhibitClient } from "./api";
import { copy, periodOptions } from "./copy";
import type { Artifact, ExhibitResponse } from "./types";

type FormState = {
  topic: string;
  period: string | null;
  count: number;
};

const initialState: FormState = {
  topic: "",
  period: null,
  count: 5,
};

export default function App() {
  const [form, setForm] = useState<FormState>(initialState);
  const [exhibit, setExhibit] = useState<ExhibitResponse | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const nextExhibit = await exhibitClient.createExhibit({
        topic: form.topic.trim(),
        period: form.period,
        count: form.count,
      });

      setExhibit(nextExhibit);
    } catch (submitError) {
      const message =
        submitError instanceof Error ? submitError.message : "Unknown error";
      setError(`${copy.errorPrefix} ${message}`);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="page-shell">
      <main className="page">
        <section className="hero-panel">
          <div className="hero-copy">
            <p className="eyebrow">{copy.eyebrow}</p>
            <h1>{copy.heroTitle}</h1>
            <p className="hero-body">{copy.heroBody}</p>
          </div>

          <form className="hero-form" onSubmit={handleSubmit}>
            <label className="field">
              <span>{copy.topicLabel}</span>
              <input
                name="topic"
                value={form.topic}
                placeholder={copy.topicPlaceholder}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    topic: event.target.value,
                  }))
                }
                required
              />
            </label>

            <div className="field">
              <span>{copy.periodLabel}</span>
              <div className="chip-row" role="radiogroup" aria-label={copy.periodLabel}>
                {periodOptions.map((option) => {
                  const selected = form.period === option.value;

                  return (
                    <button
                      key={option.label}
                      className={selected ? "chip chip-active" : "chip"}
                      type="button"
                      role="radio"
                      aria-checked={selected}
                      onClick={() =>
                        setForm((current) => ({
                          ...current,
                          period: option.value,
                        }))
                      }
                    >
                      {option.label}
                    </button>
                  );
                })}
              </div>
            </div>

            <label className="field field-count">
              <span>{copy.countLabel}</span>
              <select
                name="count"
                value={form.count}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    count: Number(event.target.value),
                  }))
                }
              >
                {Array.from({ length: 10 }, (_, index) => index + 1).map((count) => (
                  <option key={count} value={count}>
                    {count}
                  </option>
                ))}
              </select>
            </label>

            <button className="submit-button" disabled={isLoading || !form.topic.trim()}>
              {isLoading ? copy.loadingLabel : copy.buildLabel}
            </button>

            {error ? <p className="error-message">{error}</p> : null}
          </form>
        </section>

        <section className="results-panel">
          {exhibit ? <ExhibitView exhibit={exhibit} /> : <EmptyState />}
        </section>
      </main>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="empty-state">
      <p>{copy.noResultsYet}</p>
    </div>
  );
}

function ExhibitView({ exhibit }: { exhibit: ExhibitResponse }) {
  return (
    <>
      <header className="exhibit-header">
        <p className="section-label">{copy.exhibitLabel}</p>
        <h2>{exhibit.title}</h2>
        <p className="intro">{exhibit.intro}</p>
      </header>

      {exhibit.artifacts.length > 0 ? (
        <section>
          <div className="section-heading">
            <h3>{copy.artifactsLabel}</h3>
          </div>
          <div className="artifact-grid">
            {exhibit.artifacts.map((artifact) => (
              <ArtifactCard key={artifact.id} artifact={artifact} />
            ))}
          </div>
        </section>
      ) : (
        <div className="empty-state">
          <p>{copy.emptyArtifacts}</p>
        </div>
      )}

      <section className="timeline-panel">
        <div className="section-heading">
          <h3>{copy.timelineLabel}</h3>
        </div>
        {exhibit.timeline.length > 0 ? (
          <ol className="timeline-list">
            {exhibit.timeline.map((entry) => (
              <li key={`${entry.date}-${entry.label}`} className="timeline-item">
                <span className="timeline-date">{entry.date}</span>
                <span className="timeline-label">{entry.label}</span>
              </li>
            ))}
          </ol>
        ) : (
          <p className="quiet-note">{copy.noTimeline}</p>
        )}
      </section>

      <details className="dev-panel">
        <summary>
          <span>{copy.devLabel}</span>
          <span className="dev-hint">{copy.devHint}</span>
        </summary>
        <div className="dev-body">
          <div>
            <h4>Tool Calls</h4>
            <ul className="dev-list">
              {exhibit.dev.tool_calls.map((toolCall, index) => (
                <li key={`${toolCall.tool}-${index}`}>
                  <strong>{toolCall.tool}</strong>
                  <span>
                    query: {String(toolCall.input.query ?? "")}
                    {toolCall.input.period ? `, period: ${String(toolCall.input.period)}` : ""}
                    , count: {toolCall.output_count}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4>Limitations</h4>
            {exhibit.dev.limitations.length > 0 ? (
              <ul className="dev-list">
                {exhibit.dev.limitations.map((limitation) => (
                  <li key={limitation}>{limitation}</li>
                ))}
              </ul>
            ) : (
              <p className="quiet-note">{copy.noLimitations}</p>
            )}
          </div>
        </div>
      </details>
    </>
  );
}

function ArtifactCard({ artifact }: { artifact: Artifact }) {
  const caption = artifact.description || artifact.title;
  const displayDate = artifact.date_display || artifact.date_indexed[0] || "";
  const metadata = [
    displayDate,
    artifact.creator_display,
    artifact.unit_name,
  ].filter(Boolean);
  const tags = [...artifact.subject_tags, ...artifact.place_tags].slice(0, 4);

  return (
    <article className="artifact-card">
      <div className="artifact-image-wrap">
        <img className="artifact-image" src={artifact.image_url} alt={artifact.image_alt} />
      </div>
      <div className="artifact-body">
        <h4>{artifact.title}</h4>
        <p className="artifact-caption">{caption}</p>

        {metadata.length > 0 ? <p className="artifact-meta">{metadata.join(" · ")}</p> : null}

        <div className="artifact-details">
          {artifact.object_type ? (
            <p>
              <span>{copy.objectTypeLabel}:</span> {artifact.object_type}
            </p>
          ) : null}
          {artifact.rights ? (
            <p>
              <span>{copy.rightsLabel}:</span> {artifact.rights}
            </p>
          ) : null}
          <p>
            <span>{copy.sourceLabel}:</span>{" "}
            <a href={artifact.source_url} target="_blank" rel="noreferrer">
              {artifact.unit_code || "Smithsonian"}
            </a>
          </p>
        </div>

        {tags.length > 0 ? (
          <ul className="tag-row">
            {tags.map((tag) => (
              <li key={tag}>{tag}</li>
            ))}
          </ul>
        ) : null}
      </div>
    </article>
  );
}
