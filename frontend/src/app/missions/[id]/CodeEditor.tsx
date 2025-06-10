"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { usePyodide } from "./usePyodide";
import { editor } from "monaco-editor";
import { toast } from "react-hot-toast";

interface TestCase {
  id: string;
  name: string;
  code: string;
  expectedOutput: string;
  points: number;
}

interface CodeEditorProps {
  code: string;
  onChange: (code: string) => void;
  missionId: string;
  testCases: TestCase[];
  onSubmissionComplete: (result: {
    score: number;
    passedTests: string[];
    failedTests: string[];
  }) => void;
}

export function CodeEditor({
  code,
  onChange,
  missionId,
  testCases,
  onSubmissionComplete,
}: CodeEditorProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isEditorReady, setIsEditorReady] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [testResults, setTestResults] = useState<{
    passed: string[];
    failed: string[];
  } | null>(null);
  const { runMissionTests, isReady: isPyodideReady } = usePyodide();

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

      // Add keyboard shortcut for Submit
      editorRef.current.addCommand(
        monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
        () => {
          handleSubmit();
        }
      );

      setIsEditorReady(true);
    };

    initEditor();

    return () => {
      editorRef.current?.dispose();
    };
  }, []);

  // Update editor content when code prop changes
  useEffect(() => {
    if (editorRef.current && code !== editorRef.current.getValue()) {
      editorRef.current.setValue(code);
    }
  }, [code]);

  const handleSubmit = useCallback(async () => {
    if (!isEditorReady || isSubmitting) return;

    const code = editorRef.current!.getValue();
    if (!code.trim()) {
      toast.error("Please write some code first!");
      return;
    }

    setIsSubmitting(true);
    setTestResults(null);

    try {
      // First try local execution with Pyodide
      if (isPyodideReady) {
        const result = await runMissionTests(code, testCases);
        setTestResults({
          passed: result.passedTests,
          failed: result.failedTests,
        });
        onSubmissionComplete({
          score: result.score,
          passedTests: result.passedTests,
          failedTests: result.failedTests,
        });
        return;
      }

      // Fallback to server execution
      const response = await fetch(
        `/api/missions/${missionId}/submit_attempt`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code }),
        }
      );

      if (!response.ok) {
        throw new Error(`Server error: ${response.statusText}`);
      }

      const result = await response.json();
      setTestResults({
        passed: result.passed_tests,
        failed: result.failed_tests,
      });
      onSubmissionComplete({
        score: result.score,
        passedTests: result.passed_tests,
        failedTests: result.failed_tests,
      });
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to submit code"
      );
    } finally {
      setIsSubmitting(false);
    }
  }, [
    isEditorReady,
    isSubmitting,
    isPyodideReady,
    runMissionTests,
    testCases,
    missionId,
    onSubmissionComplete,
  ]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault();
        handleSubmit();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleSubmit]);

  return (
    <div className='h-full flex flex-col'>
      <div className='flex-1' ref={containerRef} />
      <div className='p-4 border-t border-gray-700'>
        <div className='flex justify-between items-center'>
          <button
            onClick={handleSubmit}
            disabled={!isEditorReady || isSubmitting}
            className='px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded'
          >
            {isSubmitting ? "Submitting..." : "Submit"}
          </button>
          {testResults && (
            <div className='text-sm'>
              <span className='text-green-500'>
                Passed: {testResults.passed.length}
              </span>
              {" / "}
              <span className='text-red-500'>
                Failed: {testResults.failed.length}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
