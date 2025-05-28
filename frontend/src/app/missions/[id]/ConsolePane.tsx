"use client";

import { useEffect, useRef } from "react";

interface ConsoleOutput {
  type: "stdout" | "stderr" | "error";
  content: string;
  timestamp: number;
}

interface ConsolePaneProps {
  outputs?: ConsoleOutput[];
  onClear?: () => void;
}

export function ConsolePane({ outputs = [], onClear }: ConsolePaneProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new outputs arrive
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [outputs]);

  return (
    <div className='h-full flex flex-col bg-gray-900'>
      <div className='flex items-center justify-between p-4 border-b border-gray-700'>
        <h2 className='text-lg font-mono'>Console</h2>
        <button
          onClick={onClear}
          className='text-sm text-gray-400 hover:text-white'
        >
          Clear
        </button>
      </div>

      <div
        ref={containerRef}
        className='flex-1 overflow-auto p-4 font-mono text-sm'
      >
        {outputs.length === 0 ? (
          <div className='text-gray-500'>Awaiting execution...</div>
        ) : (
          outputs.map((output) => (
            <div
              key={output.timestamp}
              className={`p-2 ${
                output.type === "stderr"
                  ? "text-red-400"
                  : output.type === "error"
                  ? "text-red-500"
                  : "text-gray-300"
              }`}
            >
              {output.content}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
