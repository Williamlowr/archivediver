import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";

import App from "./App";
import { copy } from "./copy";

describe("App", () => {
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

  test("shows loading label while building exhibit", async () => {
    render(<App />);

    fireEvent.change(screen.getByLabelText(copy.topicLabel), {
      target: { value: "apollo program" },
    });

    fireEvent.click(screen.getByRole("button", { name: copy.buildLabel }));

    expect(screen.getByRole("button", { name: copy.loadingLabel })).toBeDisabled();

    await screen.findByText("Exhibit: Apollo Program");
  });

  test("renders the mock exhibit and dev details", async () => {
    render(<App />);

    fireEvent.change(screen.getByLabelText(copy.topicLabel), {
      target: { value: "apollo program" },
    });

    fireEvent.click(screen.getByRole("button", { name: copy.buildLabel }));

    expect(await screen.findByText("Exhibit: Apollo Program")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", {
        level: 4,
        name: "Model, Rocket, Saturn V, 1:34",
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", {
        level: 3,
        name: copy.timelineLabel,
      }),
    ).toBeInTheDocument();

    fireEvent.click(screen.getByText(copy.devLabel));

    expect(await screen.findByText("search_artifacts")).toBeInTheDocument();
  });

  test("falls back to title when artifact description is missing", async () => {
    render(<App />);

    fireEvent.change(screen.getByLabelText(copy.topicLabel), {
      target: { value: "apollo program" },
    });

    fireEvent.click(screen.getByRole("button", { name: copy.buildLabel }));

    await screen.findByText("Exhibit: Apollo Program");

    const cardHeading = screen.getByRole("heading", {
      level: 4,
      name: "Apollo Guidance Computer Component",
    });
    const card = cardHeading.closest(".artifact-card");

    expect(card).not.toBeNull();
    expect(within(card as HTMLElement).getAllByText("Apollo Guidance Computer Component").length)
      .toBeGreaterThan(1);
  });

  test("keeps a quiet empty state before the first search", () => {
    render(<App />);

    expect(screen.getByText(copy.noResultsYet)).toBeInTheDocument();
  });

  test("completes a full mock request cycle", async () => {
    render(<App />);

    fireEvent.change(screen.getByLabelText(copy.topicLabel), {
      target: { value: "civil rights movement" },
    });
    fireEvent.click(screen.getByRole("radio", { name: "1900s" }));
    fireEvent.change(screen.getByLabelText(copy.countLabel), {
      target: { value: "3" },
    });

    fireEvent.click(screen.getByRole("button", { name: copy.buildLabel }));

    await waitFor(() => {
      expect(screen.getByText("Exhibit: Civil Rights Movement")).toBeInTheDocument();
    });
  });
});
