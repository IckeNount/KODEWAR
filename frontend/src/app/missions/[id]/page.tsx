"use client";

import { useState, useEffect } from "react";
import { Toaster, toast } from "react-hot-toast";
import { CodeEditor } from "./CodeEditor";
import { ConsolePane } from "./ConsolePane";

interface ConsoleOutput {
  type: "stdout" | "stderr" | "error";
  content: string;
  timestamp: number;
}

export default function MissionPage({ params }: { params: { id: string } }) {
  const [code, setCode] = useState("");
  const [isPyodideReady, setIsPyodideReady] = useState(false);
  const [useLocalExecution, setUseLocalExecution] = useState(
    process.env.NEXT_PUBLIC_USE_PYODIDE === "true"
  );
  const [outputs, setOutputs] = useState<ConsoleOutput[]>([]);

  // Load execution mode preference from localStorage
  useEffect(() => {
    const savedMode = localStorage.getItem("useLocalExecution");
    if (savedMode !== null) {
      setUseLocalExecution(savedMode === "true");
    }
  }, []);

  // Save execution mode preference
  useEffect(() => {
    localStorage.setItem("useLocalExecution", useLocalExecution.toString());
  }, [useLocalExecution]);

  const handleExecutionResult = (result: {
    stdout: string;
    stderr: string;
  }) => {
    const newOutputs: ConsoleOutput[] = [];
    const timestamp = Date.now();

    if (result.stdout) {
      newOutputs.push({
        type: "stdout",
        content: result.stdout,
        timestamp,
      });
    }

    if (result.stderr) {
      newOutputs.push({
        type: "stderr",
        content: result.stderr,
        timestamp,
      });
    }

    setOutputs((prev) => [...prev, ...newOutputs]);
  };

  const handleExecutionError = (error: Error) => {
    setOutputs((prev) => [
      ...prev,
      {
        type: "error",
        content: error.message,
        timestamp: Date.now(),
      },
    ]);

    // Show toast for errors
    toast.error(error.message, {
      duration: 4000,
      position: "bottom-right",
    });
  };

  const handleClearConsole = () => {
    setOutputs([]);
  };

  return (
    <>
      <Toaster />
      <div className='flex h-screen bg-gray-900 text-white'>
        {/* Left side - Code Editor */}
        <div className='flex-1 flex flex-col'>
          <div className='flex items-center justify-between p-4 border-b border-gray-700'>
            <h1 className='text-xl font-mono'>Mission {params.id}</h1>
            <div className='flex items-center gap-4'>
              <div className='flex items-center gap-2'>
                <span className='text-sm text-gray-400'>Execution:</span>
                <button
                  onClick={() => setUseLocalExecution(!useLocalExecution)}
                  className='px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-sm'
                >
                  {useLocalExecution ? "Local" : "Server"}
                </button>
              </div>
            </div>
          </div>
          <div className='flex-1'>
            <CodeEditor
              code={code}
              onChange={setCode}
              useLocalExecution={useLocalExecution}
              isPyodideReady={isPyodideReady}
              onPyodideReady={() => setIsPyodideReady(true)}
              onExecutionResult={handleExecutionResult}
              onExecutionError={handleExecutionError}
            />
          </div>
        </div>

        {/* Right side - Console */}
        <div className='w-1/3 border-l border-gray-700'>
          <ConsolePane outputs={outputs} onClear={handleClearConsole} />
        </div>
      </div>
    </>
  );
}
