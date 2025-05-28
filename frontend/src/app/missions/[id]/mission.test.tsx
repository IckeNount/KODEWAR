import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import MissionPage from "./page";
import { usePyodide } from "./usePyodide";

// Mock the usePyodide hook
vi.mock("./usePyodide", () => ({
  usePyodide: vi.fn(() => ({
    run: vi.fn(),
    isReady: true,
    error: null,
  })),
}));

// Mock fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

interface TestData {
  id: string;
  title: string;
  description: string;
}

describe("MissionPage", () => {
  const mockData: TestData = {
    id: "1",
    title: "Test Mission",
    description: "Test Description",
  };

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it("renders mission title", () => {
    render(<MissionPage params={{ id: mockData.id }} />);
    expect(screen.getByText(`Mission ${mockData.id}`)).toBeInTheDocument();
  });

  it("should handle local execution", async () => {
    const mockRun = vi.fn().mockResolvedValue({
      stdout: "Hello from Pyodide",
      stderr: "",
    });

    (usePyodide as ReturnType<typeof vi.fn>).mockReturnValue({
      run: mockRun,
      isReady: true,
      error: null,
    });

    render(<MissionPage params={{ id: "1" }} />);

    // Set local execution mode
    const toggleButton = screen.getByText("Server");
    fireEvent.click(toggleButton);
    expect(screen.getByText("Local")).toBeInTheDocument();

    // Run code
    const runButton = screen.getByText("Run");
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(mockRun).toHaveBeenCalled();
    });
  });

  it("should handle server execution", async () => {
    const mockResponse = { result: "ok" };
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    render(<MissionPage params={{ id: "1" }} />);

    // Run code
    const runButton = screen.getByText("Run");
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith("/api/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: "" }),
      });
    });
  });

  it("should handle execution errors", async () => {
    const mockError = new Error("Test error");
    mockFetch.mockRejectedValueOnce(mockError);

    render(<MissionPage params={{ id: "1" }} />);

    // Run code
    const runButton = screen.getByText("Run");
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText("Test error")).toBeInTheDocument();
    });
  });
});
