import { useState, useEffect } from "react";
import { loadPyodide, PyodideInterface } from "@pyodide/pyodide";
import { toast } from "react-hot-toast";

interface PyodideResult {
  stdout: string;
  stderr: string;
  success: boolean;
  executionTime: number;
}

interface TestCase {
  id: string;
  name: string;
  code: string;
  expectedOutput: string;
  points: number;
}

interface MissionExecutionResult {
  passedTests: string[];
  failedTests: string[];
  score: number;
  executionTime: number;
  stdout: string;
  stderr: string;
}

export function usePyodide() {
  const [pyodide, setPyodide] = useState<PyodideInterface | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Initialize Pyodide
  useEffect(() => {
    let mounted = true;

    const initPyodide = async () => {
      try {
        const pyodideInstance = await loadPyodide({
          indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/",
        });

        if (mounted) {
          setPyodide(pyodideInstance);
          setIsReady(true);
        }
      } catch (err) {
        if (mounted) {
          const error =
            err instanceof Error ? err : new Error("Failed to load Pyodide");
          setError(error);
          toast.error(
            "Local execution engine unavailable, falling back to server",
            {
              duration: 4000,
              position: "bottom-right",
            }
          );
        }
      }
    };

    initPyodide();

    return () => {
      mounted = false;
      if (pyodide) {
        pyodide.terminate();
      }
    };
  }, []);

  // Set up stdout/stderr handlers
  useEffect(() => {
    if (pyodide) {
      const stdoutHandler = { write: () => {} };
      const stderrHandler = { write: () => {} };

      pyodide.setStdout(stdoutHandler);
      pyodide.setStderr(stderrHandler);
    }
  }, [pyodide]);

  const run = async (
    code: string,
    timeout: number = 2000
  ): Promise<PyodideResult> => {
    if (!pyodide) {
      throw new Error("Pyodide not initialized");
    }

    const startTime = performance.now();
    let stdout = "";
    let stderr = "";

    try {
      // Capture stdout/stderr
      pyodide.setStdout({
        write: (text: string) => {
          stdout += text;
        },
      });

      pyodide.setStderr({
        write: (text: string) => {
          stderr += text;
        },
      });

      // Run the code with timeout
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error("Execution timed out")), timeout);
      });

      await Promise.race([pyodide.runPythonAsync(code), timeoutPromise]);

      return {
        stdout,
        stderr,
        success: true,
        executionTime: performance.now() - startTime,
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      return {
        stdout,
        stderr: errorMessage,
        success: false,
        executionTime: performance.now() - startTime,
      };
    }
  };

  const runMissionTests = async (
    code: string,
    testCases: TestCase[],
    timeout: number = 2000
  ): Promise<MissionExecutionResult> => {
    const passedTests: string[] = [];
    const failedTests: string[] = [];
    let totalPoints = 0;
    let earnedPoints = 0;
    let totalExecutionTime = 0;

    for (const test of testCases) {
      const testCode = `${code}\n\n${test.code}`;
      const result = await run(testCode, timeout);
      totalExecutionTime += result.executionTime;

      if (
        result.success &&
        result.stdout.trim() === test.expectedOutput.trim()
      ) {
        passedTests.push(test.id);
        earnedPoints += test.points;
      } else {
        failedTests.push(test.id);
      }
      totalPoints += test.points;
    }

    const score =
      totalPoints > 0 ? Math.round((earnedPoints / totalPoints) * 100) : 0;

    return {
      passedTests,
      failedTests,
      score,
      executionTime: totalExecutionTime,
      stdout: "",
      stderr: "",
    };
  };

  return {
    run,
    runMissionTests,
    isReady,
    error,
  };
}
