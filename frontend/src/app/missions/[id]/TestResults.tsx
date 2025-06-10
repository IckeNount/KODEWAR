"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface TestCase {
  id: string;
  name: string;
  code: string;
  expectedOutput: string;
  points: number;
}

interface TestResultsProps {
  testCases: TestCase[];
  passedTests: string[];
  failedTests: string[];
  score: number;
  onHintRequest: () => void;
  hintsUnlocked: number;
  totalHints: number;
}

export function TestResults({
  testCases,
  passedTests,
  failedTests,
  score,
  onHintRequest,
  hintsUnlocked,
  totalHints,
}: TestResultsProps) {
  const [expandedTest, setExpandedTest] = useState<string | null>(null);

  const getTestStatus = (testId: string) => {
    if (passedTests.includes(testId)) return "passed";
    if (failedTests.includes(testId)) return "failed";
    return "pending";
  };

  return (
    <div className='bg-gray-800 rounded-lg p-4 space-y-4'>
      {/* Score Display */}
      <div className='flex items-center justify-between'>
        <div className='text-2xl font-bold'>
          Score:{" "}
          <span
            className={score === 100 ? "text-green-500" : "text-yellow-500"}
          >
            {score}%
          </span>
        </div>
        <div className='text-sm text-gray-400'>
          Hints: {hintsUnlocked}/{totalHints}
        </div>
      </div>

      {/* Test Cases */}
      <div className='space-y-2'>
        {testCases.map((test) => {
          const status = getTestStatus(test.id);
          return (
            <div
              key={test.id}
              className='bg-gray-700 rounded p-3 cursor-pointer'
              onClick={() =>
                setExpandedTest(expandedTest === test.id ? null : test.id)
              }
            >
              <div className='flex items-center justify-between'>
                <div className='flex items-center space-x-2'>
                  <div
                    className={`w-3 h-3 rounded-full ${
                      status === "passed"
                        ? "bg-green-500"
                        : status === "failed"
                        ? "bg-red-500"
                        : "bg-gray-500"
                    }`}
                  />
                  <span className='font-medium'>{test.name}</span>
                </div>
                <div className='text-sm text-gray-400'>
                  {test.points} points
                </div>
              </div>

              <AnimatePresence>
                {expandedTest === test.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className='mt-2 overflow-hidden'
                  >
                    <div className='text-sm text-gray-300 space-y-2'>
                      <div>
                        <div className='font-medium'>Test Code:</div>
                        <pre className='bg-gray-800 p-2 rounded mt-1 overflow-x-auto'>
                          {test.code}
                        </pre>
                      </div>
                      <div>
                        <div className='font-medium'>Expected Output:</div>
                        <pre className='bg-gray-800 p-2 rounded mt-1 overflow-x-auto'>
                          {test.expectedOutput}
                        </pre>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>

      {/* Hint Request Button */}
      {failedTests.length > 0 && hintsUnlocked < totalHints && (
        <button
          onClick={onHintRequest}
          className='w-full py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm font-medium'
        >
          Request Hint ({hintsUnlocked + 1}/{totalHints})
        </button>
      )}

      {/* Completion Message */}
      {score === 100 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className='text-center py-4'
        >
          <div className='text-2xl font-bold text-green-500 mb-2'>
            Mission Complete! 🎉
          </div>
          <div className='text-gray-400'>
            Great job! You&apos;ve passed all the tests.
          </div>
        </motion.div>
      )}
    </div>
  );
}
