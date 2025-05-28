import "@testing-library/jest-dom";
import { vi } from "vitest";

// Mock Monaco editor
vi.mock("monaco-editor", () => ({
  editor: {
    create: vi.fn(() => ({
      onDidChangeModelContent: vi.fn(),
      getValue: vi.fn(() => ""),
      setValue: vi.fn(),
      dispose: vi.fn(),
      addCommand: vi.fn(),
    })),
    KeyMod: { CtrlCmd: 1 },
    KeyCode: { Enter: 1 },
  },
}));

// Mock next/dynamic
vi.mock("next/dynamic", () => ({
  default: () => () => null,
}));

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, "localStorage", { value: localStorageMock });
