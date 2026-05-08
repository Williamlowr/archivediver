import { vi } from "vitest";

vi.stubEnv("VITE_USE_MOCK", "true");

import "@testing-library/jest-dom/vitest";
