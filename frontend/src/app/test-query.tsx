"use client";

import { useQuery } from "@tanstack/react-query";
import { toast } from "react-hot-toast";

interface TestData {
  message: string;
  timestamp: string;
}

export function TestQuery() {
  const { data, isLoading, error } = useQuery<TestData>({
    queryKey: ["test"],
    queryFn: async () => {
      const response = await fetch("/api/test");
      if (!response.ok) {
        throw new Error("Failed to fetch test data");
      }
      return response.json();
    },
  });

  if (isLoading) {
    return <div>Loading test data...</div>;
  }

  if (error) {
    toast.error("Failed to load test data");
    return <div className='text-red-500'>Error loading data</div>;
  }

  return (
    <div className='p-4 bg-gray-800 rounded-lg'>
      <h2 className='text-xl font-bold mb-2'>Test Query Result</h2>
      <div className='space-y-2'>
        <p>Message: {data?.message}</p>
        <p className='text-sm text-gray-400'>Timestamp: {data?.timestamp}</p>
      </div>
    </div>
  );
}
