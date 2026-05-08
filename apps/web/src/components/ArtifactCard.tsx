import { useState } from "react";

import { copy } from "../copy";
import { getArtifactDisplayDate, getArtifactTags } from "../exhibitUtils";
import type { Artifact } from "../types";

type ArtifactCardProps = {
  artifact: Artifact;
};

export function ArtifactMedia({
  artifact,
  featured = false,
}: ArtifactCardProps & { featured?: boolean }) {
  const [hasImageError, setHasImageError] = useState(false);

  if (hasImageError || !artifact.image_url) {
    return (
      <div
        className={`artifact-media artifact-media-fallback ${
          featured ? "artifact-media-featured" : "artifact-media-standard"
        }`}
      >
        <div className="fallback-copy">
          <span className="fallback-label">{copy.imageFallbackLabel}</span>
          <strong>{artifact.title}</strong>
          {artifact.unit_name ? <span>{artifact.unit_name}</span> : null}
        </div>
      </div>
    );
  }

  return (
    <div
      className={`artifact-media ${
        featured ? "artifact-media-featured" : "artifact-media-standard"
      }`}
    >
      <img
        className="artifact-image"
        src={artifact.image_url}
        alt={artifact.image_alt}
        onError={() => setHasImageError(true)}
      />
    </div>
  );
}

export function ArtifactSourceDetails({ artifact }: ArtifactCardProps) {
  const metadataRows = [
    { label: copy.dateLabel, value: getArtifactDisplayDate(artifact) },
    { label: copy.creatorLabel, value: artifact.creator_display },
    { label: copy.museumLabel, value: artifact.unit_name },
    { label: copy.objectTypeLabel, value: artifact.object_type },
    { label: copy.rightsLabel, value: artifact.rights },
  ].filter((row) => row.value);

  return (
    <section className="artifact-source">
      {metadataRows.length > 0 ? (
        <dl className="artifact-source-grid">
          {metadataRows.map((row) => (
            <div key={row.label} className="artifact-source-item">
              <dt>{row.label}</dt>
              <dd>{row.value}</dd>
            </div>
          ))}
        </dl>
      ) : null}

      {artifact.source_url ? (
        <a
          className="artifact-source-link"
          href={artifact.source_url}
          target="_blank"
          rel="noreferrer"
        >
          {copy.sourceLinkLabel}
        </a>
      ) : null}
    </section>
  );
}

export function ArtifactTagRow({ artifact }: ArtifactCardProps) {
  const tags = getArtifactTags(artifact);

  if (tags.length === 0) {
    return null;
  }

  return (
    <ul className="artifact-tag-row">
      {tags.map((tag) => (
        <li key={tag}>{tag}</li>
      ))}
    </ul>
  );
}

export function ArtifactCard({ artifact }: ArtifactCardProps) {
  return (
    <article className="artifact-card artifact-card-standard" aria-label={artifact.title}>
      <ArtifactMedia artifact={artifact} />
      <div className="artifact-body">
        <div className="artifact-copy">
          <h4 className="artifact-title">{artifact.title}</h4>
          {artifact.caption.trim() ? <p className="artifact-caption">{artifact.caption}</p> : null}
        </div>
        <ArtifactSourceDetails artifact={artifact} />
        <ArtifactTagRow artifact={artifact} />
      </div>
    </article>
  );
}
