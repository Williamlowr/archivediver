import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { vi } from "vitest";

const { mockCreateExhibit } = vi.hoisted(() => ({
  mockCreateExhibit: vi.fn(),
}));

vi.mock("./api", () => ({
  exhibitClient: {
    createExhibit: mockCreateExhibit,
  },
}));

import App from "./App";
import { copy } from "./copy";

function createArtifact(overrides: Record<string, unknown> = {}) {
  return {
    id: "edanmdm:nasm_A19940223000",
    title: "Model, Rocket, Saturn V, 1:34",
    caption:
      "This scale model condenses the Saturn V into a study object for the exhibit.",
    date_display: "1969",
    date_indexed: ["1969"],
    creator_display: "David P. Gianakos",
    description: "Source description should not appear in the UI body.",
    object_type: "Missiles; Rockets; Models",
    unit_code: "NASM",
    unit_name: "National Air and Space Museum",
    source_url: "https://example.com/object",
    image_url: "https://example.com/image.jpg",
    thumbnail_url: "",
    image_alt: "Scale model of Saturn V rocket",
    rights: "CC0",
    subject_tags: ["Human spaceflight"],
    place_tags: ["United States of America"],
    ...overrides,
  };
}

function createExhibit(overrides: Record<string, unknown> = {}) {
  return {
    title: "Apollo: Engineering a Moon Landing",
    intro: "Three artifacts trace the technology and ambition behind Apollo.",
    artifacts: [createArtifact()],
    timeline: [{ date: "1969", label: "Model, Rocket, Saturn V, 1:34" }],
    dev: {
      tool_calls: [
        {
          tool: "search_artifacts",
          input: { query: "apollo program", limit: 3, period: "1900s" },
          output_count: 1,
        },
      ],
      limitations: [],
    },
    ...overrides,
  };
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;

  const promise = new Promise<T>((nextResolve, nextReject) => {
    resolve = nextResolve;
    reject = nextReject;
  });

  return { promise, resolve, reject };
}

describe("App", () => {
  beforeEach(() => {
    mockCreateExhibit.mockReset();
    mockCreateExhibit.mockResolvedValue(createExhibit());
  });

  test("renders hero defaults and chip behavior", () => {
    render(<App />);

    expect(screen.getByLabelText(copy.topicLabel)).toHaveValue("");
    expect(screen.getByLabelText(copy.countLabel)).toHaveValue("5");
    expect(screen.getByRole("radio", { name: "Any" })).toHaveAttribute(
      "aria-checked",
      "true",
    );

    fireEvent.click(screen.getByRole("radio", { name: "1900s" }));

    expect(screen.getByRole("radio", { name: "1900s" })).toHaveAttribute(
      "aria-checked",
      "true",
    );
  });

  test("submits the Stage 2 request shape", async () => {
    render(<App />);

    fireEvent.change(screen.getByLabelText(copy.topicLabel), {
      target: { value: "apollo program" },
    });
    fireEvent.click(screen.getByRole("radio", { name: "1900s" }));
    fireEvent.change(screen.getByLabelText(copy.countLabel), {
      target: { value: "3" },
    });

    fireEvent.click(screen.getByRole("button", { name: copy.buildLabel }));

    await waitFor(() => {
      expect(mockCreateExhibit).toHaveBeenCalledWith({
        topic: "apollo program",
        timePeriod: "1900s",
        artifactCount: 3,
      });
    });
  });

  test("shows the loading label and keeps the current exhibit visible during refresh", async () => {
    const secondRequest = deferred<unknown>();

    mockCreateExhibit
      .mockResolvedValueOnce(createExhibit())
      .mockReturnValueOnce(secondRequest.promise);

    render(<App />);

    fireEvent.change(screen.getByLabelText(copy.topicLabel), {
      target: { value: "apollo program" },
    });
    fireEvent.click(screen.getByRole("button", { name: copy.buildLabel }));

    expect(
      await screen.findByRole("heading", {
        level: 2,
        name: "Apollo: Engineering a Moon Landing",
      }),
    ).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(copy.topicLabel), {
      target: { value: "apollo guidance computer" },
    });
    fireEvent.click(screen.getByRole("button", { name: copy.buildLabel }));

    expect(screen.getByRole("button", { name: copy.loadingLabel })).toBeDisabled();
    expect(
      screen.getByRole("heading", {
        level: 2,
        name: "Apollo: Engineering a Moon Landing",
      }),
    ).toBeInTheDocument();

    secondRequest.resolve(createExhibit({ title: "Apollo Guidance Computer" }));

    expect(
      await screen.findByRole("heading", {
        level: 2,
        name: "Apollo Guidance Computer",
      }),
    ).toBeInTheDocument();
  });

  test("renders generated captions, source metadata, and an open dev panel", async () => {
    mockCreateExhibit.mockResolvedValueOnce(
      createExhibit({
        dev: {
          tool_calls: [
            {
              tool: "search_artifacts",
              input: { query: "apollo program", limit: 5 },
              output_count: 5,
            },
          ],
          limitations: ["Timeline is sparse for this result set."],
        },
      }),
    );

    render(<App />);

    fireEvent.change(screen.getByLabelText(copy.topicLabel), {
      target: { value: "apollo program" },
    });
    fireEvent.click(screen.getByRole("button", { name: copy.buildLabel }));

    expect(
      await screen.findByText(
        "This scale model condenses the Saturn V into a study object for the exhibit.",
      ),
    ).toBeInTheDocument();
    expect(screen.queryByText("Source description should not appear in the UI body.")).toBeNull();
    expect(screen.getByRole("link", { name: copy.sourceLinkLabel })).toHaveAttribute(
      "href",
      "https://example.com/object",
    );
    expect(screen.getByTestId("dev-details")).toHaveAttribute("open");
    expect(screen.getByText("Tool Calls")).toBeInTheDocument();
    expect(screen.getByText("Timeline is sparse for this result set.")).toBeInTheDocument();
  });

  test("renders the empty-artifacts state while keeping the exhibit header visible", async () => {
    mockCreateExhibit.mockResolvedValueOnce(
      createExhibit({
        artifacts: [],
        timeline: [],
      }),
    );

    render(<App />);

    fireEvent.change(screen.getByLabelText(copy.topicLabel), {
      target: { value: "apollo program" },
    });
    fireEvent.click(screen.getByRole("button", { name: copy.buildLabel }));

    expect(
      await screen.findByRole("heading", {
        level: 2,
        name: "Apollo: Engineering a Moon Landing",
      }),
    ).toBeInTheDocument();
    expect(screen.getByText(copy.emptyArtifacts)).toBeInTheDocument();
  });

  test("shows weak-result notes and hides empty metadata fields", async () => {
    mockCreateExhibit.mockResolvedValueOnce(
      createExhibit({
        artifacts: [
          createArtifact({
            caption: "",
            date_display: "",
            date_indexed: [],
            creator_display: "",
            object_type: "",
            rights: "",
          }),
        ],
        timeline: [],
        dev: {
          tool_calls: [
            {
              tool: "search_artifacts",
              input: { query: "apollo program", limit: 3 },
              output_count: 1,
            },
          ],
          limitations: [],
        },
      }),
    );

    render(<App />);

    fireEvent.change(screen.getByLabelText(copy.topicLabel), {
      target: { value: "apollo program" },
    });
    fireEvent.change(screen.getByLabelText(copy.countLabel), {
      target: { value: "3" },
    });
    fireEvent.click(screen.getByRole("button", { name: copy.buildLabel }));

    expect(await screen.findByText(copy.resultNotesLabel)).toBeInTheDocument();
    expect(screen.getByText(copy.weakResultsCountNote)).toBeInTheDocument();
    expect(screen.getByText(copy.weakResultsTimelineNote)).toBeInTheDocument();
    expect(screen.getByText(copy.weakResultsCaptionNote)).toBeInTheDocument();

    const card = screen.getByRole("article", { name: /Model, Rocket, Saturn V, 1:34/i });
    expect(within(card).queryByText(copy.objectTypeLabel)).toBeNull();
    expect(within(card).queryByText(copy.rightsLabel)).toBeNull();
  });

  test("falls back to an image placeholder when artifact media fails", async () => {
    render(<App />);

    fireEvent.change(screen.getByLabelText(copy.topicLabel), {
      target: { value: "apollo program" },
    });
    fireEvent.click(screen.getByRole("button", { name: copy.buildLabel }));

    const image = await screen.findByRole("img", {
      name: "Scale model of Saturn V rocket",
    });

    fireEvent.error(image);

    expect(screen.getByText(copy.imageFallbackLabel)).toBeInTheDocument();
    expect(
      within(
        screen.getByRole("article", { name: "Model, Rocket, Saturn V, 1:34" }),
      ).getAllByText("Model, Rocket, Saturn V, 1:34").length,
    ).toBeGreaterThan(0);
  });
});
