"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { CodeEditor } from "./CodeEditor";
import { TestResults } from "./TestResults";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";

interface Mission {
  id: string;
  title: string;
  description: string;
  starterCode: string;
  testCases: {
    id: string;
    name: string;
    code: string;
    expectedOutput: string;
    points: number;
  }[];
  hints: {
    id: string;
    text: string;
    unlockAfterAttempts: number;
  }[];
}

interface MissionProgress {
  isCompleted: boolean;
  bestScore: number;
  hintsUnlocked: number;
}

export default function MissionPage() {
  const { id } = useParams();
  const queryClient = useQueryClient();
  const [code, setCode] = useState("");
  const [testResults, setTestResults] = useState<{
    score: number;
    passedTests: string[];
    failedTests: string[];
  } | null>(null);

  // Fetch mission data
  const { data: mission, isLoading: isLoadingMission } = useQuery<Mission>({
    queryKey: ["mission", id],
    queryFn: async () => {
      const response = await fetch(`/api/missions/${id}`);
      if (!response.ok) throw new Error("Failed to fetch mission");
      return response.json();
    },
  });

  // Fetch mission progress
  const { data: progress, isLoading: isLoadingProgress } =
    useQuery<MissionProgress>({
      queryKey: ["missionProgress", id],
      queryFn: async () => {
        const response = await fetch(`/api/missions/${id}/progress`);
        if (!response.ok) throw new Error("Failed to fetch progress");
        return response.json();
      },
    });

  // Request hint mutation
  const { mutate: requestHint } = useMutation({
    mutationFn: async () => {
      const response = await fetch(`/api/missions/${id}/request_hint`, {
        method: "POST",
      });
      if (!response.ok) throw new Error("Failed to request hint");
      return response.json();
    },
    onSuccess: () => {
      toast.success("New hint unlocked!");
      // Refetch progress to update hints
      queryClient.invalidateQueries({ queryKey: ["missionProgress", id] });
    },
    onError: () => {
      toast.error("Failed to unlock hint");
    },
  });

  // Initialize code from mission data
  useEffect(() => {
    if (mission?.starterCode) {
      setCode(mission.starterCode);
    }
  }, [mission?.starterCode]);

  if (isLoadingMission || isLoadingProgress) {
    return (
      <div className='flex items-center justify-center h-screen'>
        <div className='text-xl'>Loading mission...</div>
      </div>
    );
  }

  if (!mission) {
    return (
      <div className='flex items-center justify-center h-screen'>
        <div className='text-xl text-red-500'>Mission not found</div>
      </div>
    );
  }

  return (
    <div className='container mx-auto px-4 py-8'>
      <div className='mb-8'>
        <h1 className='text-3xl font-bold mb-2'>{mission.title}</h1>
        <p className='text-gray-400'>{mission.description}</p>
      </div>

      <div className='grid grid-cols-1 lg:grid-cols-2 gap-8'>
        {/* Code Editor */}
        <div className='h-[600px] bg-gray-900 rounded-lg overflow-hidden'>
          <CodeEditor
            code={code}
            onChange={setCode}
            missionId={id as string}
            testCases={mission.testCases}
            onSubmissionComplete={setTestResults}
          />
        </div>

        {/* Test Results */}
        <div>
          {testResults ? (
            <TestResults
              testCases={mission.testCases}
              passedTests={testResults.passedTests}
              failedTests={testResults.failedTests}
              score={testResults.score}
              onHintRequest={requestHint}
              hintsUnlocked={progress?.hintsUnlocked ?? 0}
              totalHints={mission.hints.length}
            />
          ) : (
            <div className='bg-gray-800 rounded-lg p-4 text-center text-gray-400'>
              Submit your code to see test results
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
