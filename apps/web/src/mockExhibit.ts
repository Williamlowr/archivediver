import type { ExhibitResponse } from "./types";

export const mockExhibit: ExhibitResponse = {
  title: "Exhibit: Apollo Program",
  intro:
    "A collection of 3 artifacts exploring apollo program from the 1900s.",
  artifacts: [
    {
      id: "edanmdm:nasm_A19940223000",
      title: "Model, Rocket, Saturn V, 1:34",
      date_display: "",
      date_indexed: ["1960s"],
      creator_display: "David P. Gianakos",
      description:
        "A scale model that condenses the drama and ambition of the Saturn V into an exhibit-ready object.",
      object_type: "Missiles; Rockets; Models",
      unit_code: "NASM",
      unit_name: "National Air and Space Museum",
      source_url: "http://n2t.net/ark:/65665/example",
      image_url:
        "https://ids.si.edu/ids/download?id=NASM-A19940223000-screen",
      thumbnail_url:
        "https://ids.si.edu/ids/download?id=NASM-A19940223000-thumb",
      image_alt: "Scale model of black and white Saturn V Rocket",
      rights: "CC0",
      subject_tags: ["Outer space", "Human spaceflight"],
      place_tags: ["United States of America"],
    },
    {
      id: "edanmdm:nasm_A19731231000",
      title: "Apollo Guidance Computer Component",
      date_display: "1968",
      date_indexed: ["1968"],
      creator_display: "MIT Instrumentation Laboratory",
      description: "",
      object_type: "Computers; Flight hardware",
      unit_code: "NASM",
      unit_name: "National Air and Space Museum",
      source_url: "http://n2t.net/ark:/65665/example-2",
      image_url: "https://images.unsplash.com/photo-1516849841032-87cbac4d88f7?auto=format&fit=crop&w=1200&q=80",
      thumbnail_url: "",
      image_alt: "Close-up of aerospace hardware",
      rights: "CC0",
      subject_tags: ["Computing"],
      place_tags: [],
    },
    {
      id: "edanmdm:nasm_A19710920000",
      title: "Mission Checklist Leaf",
      date_display: "1969",
      date_indexed: ["1969"],
      creator_display: "",
      description:
        "A working document used within the cadence of a crewed mission, shown as an intimate paper artifact.",
      object_type: "Documents",
      unit_code: "NASM",
      unit_name: "National Air and Space Museum",
      source_url: "http://n2t.net/ark:/65665/example-3",
      image_url: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=80",
      thumbnail_url: "",
      image_alt: "Document displayed in a museum-style presentation",
      rights: "",
      subject_tags: [],
      place_tags: ["United States of America"],
    },
  ],
  timeline: [
    { date: "1960s", label: "Model, Rocket, Saturn V, 1:34" },
    { date: "1968", label: "Apollo Guidance Computer Component" },
    { date: "1969", label: "Mission Checklist Leaf" },
  ],
  dev: {
    tool_calls: [
      {
        tool: "search_artifacts",
        input: { query: "apollo program", limit: 3, period: "1900s" },
        output_count: 3,
      },
    ],
    limitations: [
      "Descriptions and structured dates can be sparse across Smithsonian units.",
    ],
  },
};
