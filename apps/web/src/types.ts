export type ExhibitRequest = {
  topic: string;
  timePeriod: string | null;
  artifactCount: number;
};

export type Artifact = {
  id: string;
  title: string;
  caption: string;
  date_display: string;
  date_indexed: string[];
  creator_display: string;
  description: string;
  object_type: string;
  unit_code: string;
  unit_name: string;
  source_url: string;
  image_url: string;
  thumbnail_url: string;
  image_alt: string;
  rights: string;
  subject_tags: string[];
  place_tags: string[];
};

export type TimelineEntry = {
  date: string;
  label: string;
};

export type ToolCallRecord = {
  tool: string;
  input: Record<string, unknown>;
  output_count: number;
};

export type DevInfo = {
  tool_calls: ToolCallRecord[];
  limitations: string[];
  notices: string[];
};

export type ExhibitResponse = {
  title: string;
  intro: string;
  artifacts: Artifact[];
  timeline: TimelineEntry[];
  dev: DevInfo;
};
