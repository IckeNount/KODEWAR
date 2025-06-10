"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/app/contexts/AuthContext";
import { api } from "@/app/lib/api";
import { wsClient } from "@/app/lib/websocket";
import { PvPMatch } from "@/app/types/pvp";
import { Card } from "@/app/components/ui/card";
import { toast } from "react-hot-toast";
import { useRouter } from "next/navigation";

export default function PvPMatchPage({ params }: { params: { id: string } }) {
  const { user } = useAuth();
  const router = useRouter();
  const [match, setMatch] = useState<PvPMatch | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [timeLeft, setTimeLeft] = useState<number | null>(null);

  useEffect(() => {
    const fetchMatch = async () => {
      try {
        const matchData = await api.pvp.getMatch(params.id);
        setMatch(matchData);
        if (matchData.startTime) {
          const startTime = new Date(matchData.startTime).getTime();
          const now = Date.now();
          const elapsed = Math.floor((now - startTime) / 1000);
          setTimeLeft(Math.max(0, 300 - elapsed)); // 5 minutes match duration
        }
      } catch (error) {
        console.error("Failed to fetch match data:", error);
        toast.error("Failed to load match");
        router.push("/pvp/lobby");
      } finally {
        setIsLoading(false);
      }
    };

    if (user) {
      fetchMatch();
    }
  }, [user, params.id, router]);

  useEffect(() => {
    if (!user || !match) return;

    const unsubscribe = wsClient.subscribe((message) => {
      if (
        message.type === "match_update" &&
        message.payload.matchId === params.id
      ) {
        setMatch((prev) => {
          if (!prev) return prev;
          return { ...prev, ...message.payload };
        });
      }
    });

    return () => {
      unsubscribe();
    };
  }, [user, match, params.id]);

  useEffect(() => {
    if (!timeLeft) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev === null || prev <= 0) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft]);

  if (isLoading) {
    return (
      <div className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white flex items-center justify-center'>
        <div className='animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500'></div>
      </div>
    );
  }

  if (!match) {
    return (
      <div className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white flex items-center justify-center'>
        <div className='text-center'>
          <h1 className='text-2xl font-bold mb-4'>Match Not Found</h1>
          <p className='text-gray-400'>
            The match you're looking for doesn't exist.
          </p>
        </div>
      </div>
    );
  }

  const currentPlayer = match.players.find((p) => p.id === user?.id);
  const opponent = match.players.find((p) => p.id !== user?.id);

  return (
    <main className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white p-8'>
      <div className='max-w-6xl mx-auto'>
        <div className='grid grid-cols-1 gap-8'>
          {/* Match Status */}
          <Card className='bg-gray-800 p-6'>
            <div className='text-center'>
              <h2 className='text-2xl font-bold mb-4'>Battle Arena</h2>
              <div className='flex justify-center items-center space-x-4'>
                <div className='text-center'>
                  <h3 className='font-medium'>{currentPlayer?.username}</h3>
                  <p className='text-sm text-gray-400'>
                    Rating: {currentPlayer?.rating}
                  </p>
                </div>
                <div className='text-3xl font-bold'>VS</div>
                <div className='text-center'>
                  <h3 className='font-medium'>{opponent?.username}</h3>
                  <p className='text-sm text-gray-400'>
                    Rating: {opponent?.rating}
                  </p>
                </div>
              </div>
              {timeLeft !== null && (
                <div className='mt-4'>
                  <p className='text-lg font-medium'>
                    Time Remaining: {Math.floor(timeLeft / 60)}:
                    {(timeLeft % 60).toString().padStart(2, "0")}
                  </p>
                </div>
              )}
            </div>
          </Card>

          {/* Battle UI Placeholder */}
          <Card className='bg-gray-800 p-6'>
            <div className='text-center'>
              <h3 className='text-xl font-bold mb-4'>Battle in Progress</h3>
              <p className='text-gray-400'>
                The battle system is under development. Check back soon for the
                full experience!
              </p>
            </div>
          </Card>

          {/* Ready Status */}
          <Card className='bg-gray-800 p-6'>
            <div className='text-center'>
              <h3 className='text-xl font-bold mb-4'>Player Status</h3>
              <div className='grid grid-cols-2 gap-4'>
                <div>
                  <p className='font-medium'>{currentPlayer?.username}</p>
                  <span
                    className={`inline-block px-2 py-1 rounded-full text-xs ${
                      currentPlayer?.ready ? "bg-green-500" : "bg-yellow-500"
                    }`}
                  >
                    {currentPlayer?.ready ? "Ready" : "Not Ready"}
                  </span>
                </div>
                <div>
                  <p className='font-medium'>{opponent?.username}</p>
                  <span
                    className={`inline-block px-2 py-1 rounded-full text-xs ${
                      opponent?.ready ? "bg-green-500" : "bg-yellow-500"
                    }`}
                  >
                    {opponent?.ready ? "Ready" : "Not Ready"}
                  </span>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </main>
  );
}
