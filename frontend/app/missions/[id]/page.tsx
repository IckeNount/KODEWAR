"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/app/contexts/AuthContext";
import { api } from "@/app/lib/api";
import { MissionProgress } from "@/app/types/profile";
import { toast } from "react-hot-toast";

interface Mission {
  id: string;
  title: string;
  description: string;
  difficulty: string;
  points: number;
  testCases: {
    input: string;
    expectedOutput: string;
  }[];
}

export default function MissionPage({ params }: { params: { id: string } }) {
  const { user } = useAuth();
  const [mission, setMission] = useState<Mission | null>(null);
  const [progress, setProgress] = useState<MissionProgress | null>(null);
  const [code, setCode] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const fetchMissionAndProgress = async () => {
      try {
        const [missionData, progressData] = await Promise.all([
          api.missions.getMission(params.id),
          api.progress.getMissionProgress(params.id),
        ]);
        setMission(missionData);
        setProgress(progressData);
        if (progressData.lastSubmittedCode) {
          setCode(progressData.lastSubmittedCode);
        }
      } catch (error) {
        console.error("Failed to fetch mission data:", error);
        toast.error("Failed to load mission");
      } finally {
        setIsLoading(false);
      }
    };

    if (user) {
      fetchMissionAndProgress();
    }
  }, [user, params.id]);

  const handleSubmit = async () => {
    if (!code.trim()) {
      toast.error("Please write some code first");
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await api.progress.submitMissionSolution(params.id, code);
      setProgress(result);

      if (result.status === "completed") {
        toast.success("Mission completed! 🎉");
      } else {
        toast.error("Solution incorrect. Try again!");
      }
    } catch (error) {
      console.error("Failed to submit solution:", error);
      toast.error("Failed to submit solution");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white flex items-center justify-center'>
        <div className='animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500'></div>
      </div>
    );
  }

  if (!mission) {
    return (
      <div className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white flex items-center justify-center'>
        <div className='text-center'>
          <h1 className='text-2xl font-bold mb-4'>Mission Not Found</h1>
          <p className='text-gray-400'>
            The mission you're looking for doesn't exist.
          </p>
        </div>
      </div>
    );
  }

  return (
    <main className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white p-8'>
      <div className='max-w-6xl mx-auto'>
        <div className='grid grid-cols-1 lg:grid-cols-2 gap-8'>
          {/* Mission Info */}
          <div className='space-y-6'>
            <div>
              <h1 className='text-3xl font-bold mb-2'>{mission.title}</h1>
              <div className='flex items-center space-x-4 text-sm text-gray-400'>
                <span>Difficulty: {mission.difficulty}</span>
                <span>Points: {mission.points}</span>
                {progress && (
                  <span className='text-blue-400'>
                    Status: {progress.status}
                  </span>
                )}
              </div>
            </div>

            <div className='prose prose-invert'>
              <p>{mission.description}</p>
            </div>

            <div>
              <h2 className='text-xl font-bold mb-4'>Test Cases</h2>
              <div className='space-y-4'>
                {mission.testCases.map((testCase, index) => (
                  <div
                    key={index}
                    className='bg-gray-800 p-4 rounded-lg space-y-2'
                  >
                    <div>
                      <span className='text-gray-400'>Input:</span>
                      <pre className='mt-1 text-sm'>{testCase.input}</pre>
                    </div>
                    <div>
                      <span className='text-gray-400'>Expected Output:</span>
                      <pre className='mt-1 text-sm'>
                        {testCase.expectedOutput}
                      </pre>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Code Editor */}
          <div className='space-y-4'>
            <div className='bg-gray-800 rounded-lg overflow-hidden'>
              <div className='bg-gray-700 px-4 py-2 flex justify-between items-center'>
                <span className='text-sm font-medium'>Solution</span>
                <span className='text-xs text-gray-400'>Python</span>
              </div>
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className='w-full h-[400px] bg-gray-900 text-white p-4 font-mono text-sm focus:outline-none'
                placeholder='Write your solution here...'
              />
            </div>

            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className={`w-full py-3 px-4 rounded-md text-white font-medium ${
                isSubmitting
                  ? "bg-blue-600 opacity-50 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-700"
              }`}
            >
              {isSubmitting ? "Submitting..." : "Submit Solution"}
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
