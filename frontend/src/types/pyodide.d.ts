declare module "@pyodide/pyodide" {
  export interface PyodideInterface {
    runPython: (code: string) => unknown;
    runPythonAsync: (code: string) => Promise<unknown>;
    loadPackage: (packages: string | string[]) => Promise<void>;
    loadedPackages: { [key: string]: string };
    globals: { [key: string]: unknown };
    setStderr: (options: { write: (msg: string) => void }) => void;
    setStdout: (options: { write: (msg: string) => void }) => void;
    terminate: () => void;
  }

  export function loadPyodide(options?: {
    indexURL?: string;
    fullStdLib?: boolean;
    stdin?: () => string;
    stdout?: (msg: string) => void;
    stderr?: (msg: string) => void;
  }): Promise<PyodideInterface>;
}
