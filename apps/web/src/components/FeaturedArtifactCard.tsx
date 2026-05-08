import { copy } from "../copy";
import type { Artifact } from "../types";

import { ArtifactMedia, ArtifactSourceDetails, ArtifactTagRow } from "./ArtifactCard";

export function FeaturedArtifactCard({ artifact }: { artifact: Artifact }) {
  return (
    <article className="artifact-card artifact-card-featured" aria-label={artifact.title}>
      <ArtifactMedia artifact={artifact} featured />
      <div className="artifact-body artifact-body-featured">
        <div className="artifact-copy">
          <p className="artifact-label">{copy.featuredLabel}</p>
          <h3 className="artifact-title artifact-title-featured">{artifact.title}</h3>
          {artifact.caption.trim() ? <p className="artifact-caption">{artifact.caption}</p> : null}
        </div>
        <ArtifactSourceDetails artifact={artifact} />
        <ArtifactTagRow artifact={artifact} />
      </div>
    </article>
  );
}
