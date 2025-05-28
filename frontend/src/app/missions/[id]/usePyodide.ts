import { useState, useEffect } from "react";
import { loadPyodide, PyodideInterface } from "@pyodide/pyodide";
import { toast } from "react-hot-toast";

interface PyodideResult {
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
    // We only want to run this cleanup on unmount, not on every pyodide change
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

  const run = async (code: string): Promise<PyodideResult> => {
    if (!pyodide) {
      throw new Error("Pyodide not initialized");
    }

    try {
      // Capture stdout/stderr
      let stdout = "";
      let stderr = "";

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
        setTimeout(() => reject(new Error("Execution timed out")), 10000);
      });

      await Promise.race([pyodide.runPythonAsync(code), timeoutPromise]);

      return { stdout, stderr };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      return {
        stdout: "",
        stderr: errorMessage,
      };
    }
  };

  return {
    run,
    isReady,
    error,
  };
}
