import type { FormEvent } from "react";

import { copy, periodOptions } from "../copy";

type ExhibitFormProps = {
  artifactCount: number;
  error: string;
  isLoading: boolean;
  timePeriod: string | null;
  topic: string;
  onArtifactCountChange: (value: number) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onTimePeriodChange: (value: string | null) => void;
  onTopicChange: (value: string) => void;
};

export function ExhibitForm({
  artifactCount,
  error,
  isLoading,
  timePeriod,
  topic,
  onArtifactCountChange,
  onSubmit,
  onTimePeriodChange,
  onTopicChange,
}: ExhibitFormProps) {
  return (
    <form className="hero-form" onSubmit={onSubmit}>
      <label className="field">
        <span>{copy.topicLabel}</span>
        <input
          name="topic"
          value={topic}
          placeholder={copy.topicPlaceholder}
          onChange={(event) => onTopicChange(event.target.value)}
          required
        />
      </label>

      <div className="field">
        <span>{copy.periodLabel}</span>
        <div className="chip-row" role="radiogroup" aria-label={copy.periodLabel}>
          {periodOptions.map((option) => {
            const selected = timePeriod === option.value;

            return (
              <button
                key={option.label}
                className={selected ? "chip chip-active" : "chip"}
                type="button"
                role="radio"
                aria-checked={selected}
                onClick={() => onTimePeriodChange(option.value)}
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
          name="artifactCount"
          value={artifactCount}
          onChange={(event) => onArtifactCountChange(Number(event.target.value))}
        >
          {Array.from({ length: 10 }, (_, index) => index + 1).map((count) => (
            <option key={count} value={count}>
              {count}
            </option>
          ))}
        </select>
      </label>

      <button className="submit-button" disabled={isLoading || !topic.trim()}>
        {isLoading ? copy.loadingLabel : copy.buildLabel}
      </button>

      {error ? <p className="error-message">{`${copy.errorPrefix} ${error}`}</p> : null}
    </form>
  );
}
