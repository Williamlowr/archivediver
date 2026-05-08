import { copy } from "./copy";
import type { Artifact, ExhibitResponse } from "./types";

export function getArtifactDisplayDate(artifact: Artifact) {
  return artifact.date_display || artifact.date_indexed[0] || "";
}

export function getArtifactTags(artifact: Artifact) {
  return [...artifact.subject_tags, ...artifact.place_tags].filter(Boolean).slice(0, 4);
}

export function getWeakResultNotes(
  exhibit: ExhibitResponse,
  requestedArtifactCount: number | null,
) {
  if (exhibit.artifacts.length === 0) {
    return [];
  }

  const notes: string[] = [];

  if (
    typeof requestedArtifactCount === "number" &&
    exhibit.artifacts.length < requestedArtifactCount
  ) {
    notes.push(copy.weakResultsCountNote);
  }

  if (exhibit.timeline.length === 0) {
    notes.push(copy.weakResultsTimelineNote);
  }

  if (exhibit.artifacts.some((artifact) => !artifact.caption.trim())) {
    notes.push(copy.weakResultsCaptionNote);
  }

  return notes;
}
