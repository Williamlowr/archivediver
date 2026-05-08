import { mockExhibit } from "./mockExhibit";
import type { ExhibitRequest, ExhibitResponse } from "./types";

export interface ExhibitClient {
  createExhibit(request: ExhibitRequest): Promise<ExhibitResponse>;
}

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ??
  import.meta.env.API_BASE_URL ??
  ""
).replace(/\/$/, "");

const EXHIBIT_ENDPOINT = API_BASE_URL ? `${API_BASE_URL}/api/exhibit` : "/api/exhibit";

/** Offline / UI tests: set VITE_USE_MOCK=true */
const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

export class MockExhibitClient implements ExhibitClient {
  async createExhibit(request: ExhibitRequest): Promise<ExhibitResponse> {
    await new Promise((resolve) => setTimeout(resolve, 250));

    return {
      ...mockExhibit,
      title: `Exhibit: ${toTitleCase(request.topic)}`,
      intro: buildIntro(request, mockExhibit.artifacts.length),
      dev: {
        ...mockExhibit.dev,
        tool_calls: [
          {
            tool: "search_artifacts",
            input: {
              query: request.topic,
              limit: request.artifactCount,
              period: request.timePeriod,
            },
            output_count: mockExhibit.artifacts.length,
          },
        ],
      },
    };
  }
}

export class HttpExhibitClient implements ExhibitClient {
  async createExhibit(request: ExhibitRequest): Promise<ExhibitResponse> {
    const response = await fetch(EXHIBIT_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Request failed with ${response.status}`);
    }

    return (await response.json()) as ExhibitResponse;
  }
}

export const exhibitClient: ExhibitClient = USE_MOCK
  ? new MockExhibitClient()
  : new HttpExhibitClient();

function buildIntro(request: ExhibitRequest, artifactCount: number): string {
  const periodClause = request.timePeriod ? ` from the ${request.timePeriod}` : "";
  const artifactWord = artifactCount === 1 ? "artifact" : "artifacts";

  return `A collection of ${artifactCount} ${artifactWord} exploring ${request.topic}${periodClause}.`;
}

function toTitleCase(value: string): string {
  return value
    .split(" ")
    .filter(Boolean)
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
}
