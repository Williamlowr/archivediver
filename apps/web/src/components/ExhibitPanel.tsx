import { copy } from "../copy";
import { getWeakResultNotes } from "../exhibitUtils";
import type { ExhibitResponse } from "../types";

import { ArtifactCard } from "./ArtifactCard";
import { DevDetails } from "./DevDetails";
import { FeaturedArtifactCard } from "./FeaturedArtifactCard";
import { ResultNotice } from "./ResultNotice";
import { TimelinePanel } from "./TimelinePanel";

type ExhibitPanelProps = {
  exhibit: ExhibitResponse | null;
  isLoading: boolean;
  requestedArtifactCount: number | null;
};

export function ExhibitPanel({
  exhibit,
  isLoading,
  requestedArtifactCount,
}: ExhibitPanelProps) {
  if (!exhibit) {
    return (
      <section className="exhibit-panel exhibit-panel-empty">
        <ResultNotice
          tone={isLoading ? "loading" : "empty"}
          title={isLoading ? copy.loadingStateTitle : copy.emptyStateTitle}
          body={isLoading ? copy.loadingStateBody : copy.emptyStateBody}
          illustrationSrc="/assets/logo1-cropped.png"
          illustrationAlt=""
        />
        <div className="loading-stack" aria-hidden="true">
          <span className="loading-bar loading-bar-wide" />
          <span className="loading-bar" />
          <span className="loading-bar loading-bar-short" />
        </div>
      </section>
    );
  }

  const [featuredArtifact, ...secondaryArtifacts] = exhibit.artifacts;
  const weakResultNotes = getWeakResultNotes(exhibit, requestedArtifactCount);

  return (
    <section className={`exhibit-panel ${isLoading ? "is-refreshing" : ""}`}>
      <div className="exhibit-headline-row">
        <header className="exhibit-header">
          <p className="section-label">{copy.exhibitLabel}</p>
          <h2>{exhibit.title}</h2>
          <p className="intro">{exhibit.intro}</p>
        </header>
        <TimelinePanel timeline={exhibit.timeline} />
      </div>

      {weakResultNotes.length > 0 ? (
        <ResultNotice tone="muted" title={copy.resultNotesLabel} items={weakResultNotes} />
      ) : null}

      {exhibit.artifacts.length === 0 ? (
        <ResultNotice title={copy.emptyArtifacts} body={copy.emptyArtifactsBody} />
      ) : (
        <>
          {featuredArtifact ? <FeaturedArtifactCard artifact={featuredArtifact} /> : null}
          {secondaryArtifacts.length > 0 ? (
            <section className="artifact-section">
              <div className="section-heading">
                <h3>{copy.artifactsLabel}</h3>
              </div>
              <div className="artifact-grid">
                {secondaryArtifacts.map((artifact) => (
                  <ArtifactCard key={artifact.id} artifact={artifact} />
                ))}
              </div>
            </section>
          ) : null}
        </>
      )}

      <DevDetails dev={exhibit.dev} />

      {isLoading ? (
        <div className="exhibit-refresh-veil" aria-hidden="true">
          <div className="exhibit-refresh-bars">
            <span className="loading-bar loading-bar-wide" />
            <span className="loading-bar" />
            <span className="loading-bar loading-bar-short" />
          </div>
        </div>
      ) : null}
    </section>
  );
}
