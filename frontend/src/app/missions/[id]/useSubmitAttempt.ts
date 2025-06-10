import {
  useMutation,
  useQueryClient,
  UseMutationResult,
} from "@tanstack/react-query";
import { toast } from "react-hot-toast";

interface SubmitAttemptResponse {
  score: number;
  passed_tests: string[];
  failed_tests: string[];
  stdout: string;
  stderr: string;
  next_hint?: string;
}

export function useSubmitAttempt(
  missionId: string
): UseMutationResult<SubmitAttemptResponse, Error, string> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (code: string) => {
      const response = await fetch(
        `/api/missions/${missionId}/submit_attempt`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to submit code");
      }

      return response.json() as Promise<SubmitAttemptResponse>;
    },
    onSuccess: (data) => {
      // Invalidate mission progress to update hints
      queryClient.invalidateQueries({
        queryKey: ["missionProgress", missionId],
      });

      // Show success message with score
      toast.success(`Submission complete! Score: ${data.score}%`);

      // If a new hint was unlocked, show it
      if (data.next_hint) {
        toast.success("New hint unlocked!", {
          duration: 5000,
        });
      }
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Submission failed");
    },
  });
}
