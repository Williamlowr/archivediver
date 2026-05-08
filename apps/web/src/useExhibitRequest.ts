import { useState } from "react";

import type { ExhibitClient } from "./api";
import type { ExhibitRequest, ExhibitResponse } from "./types";

export function useExhibitRequest(client: ExhibitClient) {
  const [exhibit, setExhibit] = useState<ExhibitResponse | null>(null);
  const [resolvedRequest, setResolvedRequest] = useState<ExhibitRequest | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function requestExhibit(request: ExhibitRequest) {
    setError("");
    setIsLoading(true);

    try {
      const nextExhibit = await client.createExhibit(request);
      setExhibit(nextExhibit);
      setResolvedRequest(request);
    } catch (requestError) {
      const message =
        requestError instanceof Error ? requestError.message : "Unknown error";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  return {
    exhibit,
    resolvedRequest,
    error,
    isLoading,
    requestExhibit,
  };
}
