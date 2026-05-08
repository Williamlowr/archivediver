import { useState } from "react";

type ResultNoticeProps = {
  body?: string;
  illustrationAlt?: string;
  illustrationSrc?: string;
  items?: string[];
  title: string;
  tone?: "empty" | "loading" | "muted";
};

export function ResultNotice({
  body,
  illustrationAlt = "",
  illustrationSrc,
  items,
  title,
  tone = "empty",
}: ResultNoticeProps) {
  const [showIllustration, setShowIllustration] = useState(Boolean(illustrationSrc));

  return (
    <section className={`result-notice result-notice-${tone}`}>
      {showIllustration && illustrationSrc ? (
        <img
          className="notice-illustration"
          src={illustrationSrc}
          alt={illustrationAlt}
          onError={() => setShowIllustration(false)}
        />
      ) : null}
      <div className="notice-content">
        <h3>{title}</h3>
        {body ? <p>{body}</p> : null}
        {items && items.length > 0 ? (
          <ul className="notice-list">
            {items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        ) : null}
      </div>
    </section>
  );
}
