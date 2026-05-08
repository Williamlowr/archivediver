import { useState } from "react";

import { copy } from "../copy";

export function SiteHeader() {
  const [showMark, setShowMark] = useState(true);

  return (
    <header className="site-header">
      <div className="site-brand">
        {showMark ? (
          <img
            className="site-mark"
            src="/assets/logo2-cropped.png"
            alt=""
            aria-hidden="true"
            onError={() => setShowMark(false)}
          />
        ) : null}
        <div className="site-brand-text">
          <p className="site-kicker">{copy.eyebrow}</p>
          <p className="site-name">{copy.brand}</p>
          <p className="site-summary">Smithsonian facts, generated captions, one readable exhibit panel.</p>
        </div>
      </div>
    </header>
  );
}
