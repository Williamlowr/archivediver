import { FormEvent, useState } from "react";

import { exhibitClient } from "./api";
import { copy } from "./copy";
import { ExhibitForm } from "./components/ExhibitForm";
import { ExhibitPanel } from "./components/ExhibitPanel";
import { SiteHeader } from "./components/SiteHeader";
import type { ExhibitRequest } from "./types";
import { useExhibitRequest } from "./useExhibitRequest";

const initialState: ExhibitRequest = {
  topic: "",
  timePeriod: null,
  artifactCount: 5,
};

export default function App() {
  const [form, setForm] = useState<ExhibitRequest>(initialState);
  const { exhibit, resolvedRequest, error, isLoading, requestExhibit } =
    useExhibitRequest(exhibitClient);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    await requestExhibit({
      topic: form.topic.trim(),
      timePeriod: form.timePeriod,
      artifactCount: form.artifactCount,
    });
  }

  return (
    <div className="page-shell">
      <main className="page">
        <SiteHeader />

        <section className="hero-panel">
          <div className="hero-copy">
            <p className="eyebrow">{copy.eyebrow}</p>
            <h1>{copy.heroTitle}</h1>
            <p className="hero-body">{copy.heroBody}</p>
            <p className="hero-note">
              Source metadata stays separate from generated captions, and the dev trace remains visible beneath the exhibit.
            </p>
          </div>

          <ExhibitForm
            artifactCount={form.artifactCount}
            error={error}
            isLoading={isLoading}
            timePeriod={form.timePeriod}
            topic={form.topic}
            onArtifactCountChange={(artifactCount) =>
              setForm((current) => ({ ...current, artifactCount }))
            }
            onSubmit={handleSubmit}
            onTimePeriodChange={(timePeriod) =>
              setForm((current) => ({ ...current, timePeriod }))
            }
            onTopicChange={(topic) => setForm((current) => ({ ...current, topic }))}
          />
        </section>

        <ExhibitPanel
          exhibit={exhibit}
          isLoading={isLoading}
          requestedArtifactCount={resolvedRequest?.artifactCount ?? null}
        />
      </main>
    </div>
  );
}
