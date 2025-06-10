"use client";

import { useState } from "react";
import Link from "next/link";
import CodeEditor from "./CodeEditor";
import { loadPyodide } from "@pyodide/pyodide";

interface MissionData {
  id: number;
  title: string;
  description: string;
  instructions: string;
  initialCode: string;
  testCases: Array<{
    input: string;
    expected: string;
  }>;
}

interface MissionPageProps {
  missionData: MissionData;
}

export default function MissionPage({ missionData }: MissionPageProps) {
  const [code, setCode] = useState(missionData.initialCode);
  const [output, setOutput] = useState<string>("Ready to run code...");
  const [isRunning, setIsRunning] = useState(false);

  const runCode = async () => {
    setIsRunning(true);
    setOutput("Running code...");

    try {
      const pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/",
      });

      // Add mock functions for the mission
      pyodide.runPython(`
        def thrust(power):
            if not 0 <= power <= 100:
                raise ValueError("Power must be between 0 and 100")
            return f"Thrust set to {power}%"

        def get_altitude():
            return 500  # Mock current altitude

        def get_target_altitude():
            return 1000  # Mock target altitude
      `);

      // Run the user's code
      const result = await pyodide.runPythonAsync(code);
      setOutput(result?.toString() || "Code executed successfully");
    } catch (error) {
      setOutput(
        `Error: ${error instanceof Error ? error.message : String(error)}`
      );
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <main className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white'>
      <div className='container mx-auto px-4 py-8'>
        <header className='mb-8'>
          <div className='flex justify-between items-center'>
            <div>
              <h1 className='text-4xl font-bold mb-2'>{missionData.title}</h1>
              <p className='text-gray-400'>{missionData.description}</p>
            </div>
            <Link
              href='/missions'
              className='bg-gray-700 text-white px-4 py-2 rounded hover:bg-gray-600 transition-colors'
            >
              Back to Missions
            </Link>
          </div>
        </header>

        <div className='grid grid-cols-1 lg:grid-cols-2 gap-8'>
          {/* Mission Instructions */}
          <div className='bg-gray-800 rounded-lg p-6'>
            <h2 className='text-2xl font-semibold mb-4'>Instructions</h2>
            <div className='prose prose-invert'>
              <pre className='whitespace-pre-wrap text-gray-300'>
                {missionData.instructions}
              </pre>
            </div>
          </div>

          {/* Code Editor */}
          <div className='bg-gray-800 rounded-lg p-6'>
            <h2 className='text-2xl font-semibold mb-4'>Code Editor</h2>
            <div className='h-[500px] border border-gray-700 rounded-lg overflow-hidden'>
              <CodeEditor
                initialCode={missionData.initialCode}
                onChange={(value) => setCode(value || "")}
              />
            </div>
            <div className='mt-4 flex gap-4'>
              <button
                onClick={runCode}
                disabled={isRunning}
                className={`bg-blue-600 text-white px-6 py-2 rounded transition-colors ${
                  isRunning
                    ? "opacity-50 cursor-not-allowed"
                    : "hover:bg-blue-700"
                }`}
              >
                {isRunning ? "Running..." : "Run Code"}
              </button>
              <button className='bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700 transition-colors'>
                Submit Solution
              </button>
            </div>
          </div>
        </div>

        {/* Output Console */}
        <div className='mt-8 bg-gray-800 rounded-lg p-6'>
          <h2 className='text-2xl font-semibold mb-4'>Output</h2>
          <div className='bg-black rounded-lg p-4 font-mono text-sm'>
            <p
              className={
                output.startsWith("Error") ? "text-red-400" : "text-gray-400"
              }
            >
              {output}
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
