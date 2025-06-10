"use client";

import { useState, useRef } from "react";
import { editor } from "monaco-editor";
import { useSubmitAttempt } from "./useSubmitAttempt";
import { TestResults } from "./TestResults";
import { MonacoEditor } from "./MonacoEditor";
import { toast } from "react-hot-toast";

interface TestCase {
  id: string;
  name: string;
  code: string;
  expectedOutput: string;
  points: number;
}

interface CodePlaygroundProps {
  missionId: string;
  testCases: TestCase[];
  starterCode: string;
  hintsUnlocked: number;
  totalHints: number;
  onHintRequest: () => void;
}

export function CodePlayground({
  missionId,
  testCases,
  starterCode,
  hintsUnlocked,
  totalHints,
  onHintRequest,
}: CodePlaygroundProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const [isEditorReady, setIsEditorReady] = useState(false);
  const [testResults, setTestResults] = useState<{
    score: number;
    passedTests: string[];
    failedTests: string[];
    stdout: string;
    stderr: string;
  } | null>(null);

  const submitAttempt = useSubmitAttempt(missionId);

  const handleEditorDidMount = (editor: editor.IStandaloneCodeEditor) => {
    editorRef.current = editor;
    setIsEditorReady(true);
    editor.setValue(starterCode);
  };

  const handleSubmit = () => {
    if (!isEditorReady || submitAttempt.isPending) return;

    const code = editorRef.current!.getValue();
    if (!code.trim()) {
      toast.error("Please write some code first!");
      return;
    }

    submitAttempt.mutate(code, {
      onSuccess: (data) => {
        setTestResults({
          score: data.score,
          passedTests: data.passed_tests,
          failedTests: data.failed_tests,
          stdout: data.stdout,
          stderr: data.stderr,
        });
      },
    });
  };

  return (
    <div className='grid grid-cols-1 lg:grid-cols-2 gap-8'>
      {/* Code Editor */}
      <div className='h-[600px] bg-gray-900 rounded-lg overflow-hidden'>
        <div className='flex justify-between items-center p-4 bg-gray-800'>
          <h3 className='text-lg font-medium'>Code Editor</h3>
          <button
            onClick={handleSubmit}
            disabled={submitAttempt.isPending || !isEditorReady}
            className='px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded text-sm font-medium'
          >
            {submitAttempt.isPending ? "Running..." : "Run Code"}
          </button>
        </div>
        <div className='h-[calc(100%-4rem)]'>
          <MonacoEditor onMount={handleEditorDidMount} />
        </div>
      </div>

      {/* Test Results */}
      <div>
        {testResults ? (
          <TestResults
            testCases={testCases}
            passedTests={testResults.passedTests}
            failedTests={testResults.failedTests}
            score={testResults.score}
            onHintRequest={onHintRequest}
            hintsUnlocked={hintsUnlocked}
            totalHints={totalHints}
          />
        ) : (
          <div className='bg-gray-800 rounded-lg p-4 text-center text-gray-400'>
            Submit your code to see test results
          </div>
        )}
      </div>
    </div>
  );
}
