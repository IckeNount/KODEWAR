"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { usePyodide } from "./usePyodide";
import { editor } from "monaco-editor";

interface CodeEditorProps {
  code: string;
  onChange: (code: string) => void;
  useLocalExecution: boolean;
  isPyodideReady: boolean;
  onPyodideReady: () => void;
  onExecutionResult: (result: { stdout: string; stderr: string }) => void;
  onExecutionError: (error: Error) => void;
}

export function CodeEditor({
  code,
  onChange,
  useLocalExecution,
  isPyodideReady,
  onPyodideReady,
  onExecutionResult,
  onExecutionError,
}: CodeEditorProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isEditorReady, setIsEditorReady] = useState(false);
  const { run: runPyodide, isReady: isPyodideLoaded } = usePyodide();

  // Initialize Monaco editor
  useEffect(() => {
    if (!containerRef.current || editorRef.current) return;

    const initEditor = async () => {
      const monaco = await import("monaco-editor");

      editorRef.current = monaco.editor.create(containerRef.current!, {
        value: code,
        language: "python",
        theme: "vs-dark",
        automaticLayout: true,
        minimap: { enabled: false },
        fontSize: 14,
        lineNumbers: "on",
        scrollBeyondLastLine: false,
        tabSize: 4,
      });

      editorRef.current.onDidChangeModelContent(() => {
        onChange(editorRef.current!.getValue());
      });

      // Add keyboard shortcut for Run
      editorRef.current.addCommand(
        monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
        () => {
          handleRun();
        }
      );

      setIsEditorReady(true);
    };

    initEditor();

    return () => {
      editorRef.current?.dispose();
    };
    // We only want to run this once on mount, not on every prop change
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Update editor content when code prop changes
  useEffect(() => {
    if (editorRef.current && code !== editorRef.current.getValue()) {
      editorRef.current.setValue(code);
    }
  }, [code, onChange]);

  // Handle Pyodide ready state
  useEffect(() => {
    if (isPyodideLoaded) {
      onPyodideReady();
    }
  }, [isPyodideLoaded, onPyodideReady]);

  const handleRun = useCallback(async () => {
    if (!isEditorReady) return;

    const code = editorRef.current!.getValue();
    if (!code.trim()) return;

    try {
      if (useLocalExecution) {
        if (!isPyodideReady) {
          throw new Error("Local execution engine not ready");
        }
        const result = await runPyodide(code);
        onExecutionResult(result);
      } else {
        const response = await fetch("/api/submit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code }),
        });

        if (!response.ok) {
          throw new Error(`Server error: ${response.statusText}`);
        }

        const result = await response.json();
        onExecutionResult({
          stdout: JSON.stringify(result, null, 2),
          stderr: "",
        });
      }
    } catch (error) {
      onExecutionError(
        error instanceof Error ? error : new Error("Unknown error")
      );
    }
  }, [
    isEditorReady,
    useLocalExecution,
    isPyodideReady,
    runPyodide,
    onExecutionResult,
    onExecutionError,
  ]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault();
        handleRun();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleRun]);

  return (
    <div className='h-full flex flex-col'>
      <div className='flex-1' ref={containerRef} />
      <div className='p-4 border-t border-gray-700'>
        <button
          onClick={handleRun}
          disabled={!isEditorReady || (useLocalExecution && !isPyodideReady)}
          className='px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded'
        >
          Run
        </button>
      </div>
    </div>
  );
}
