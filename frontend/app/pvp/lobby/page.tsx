"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/app/contexts/AuthContext";
import { api } from "@/app/lib/api";
import { wsClient } from "@/app/lib/websocket";
import { PvPLobby, PvPMatch, PvPHistory } from "@/app/types/pvp";
import { Card } from "@/app/components/ui/card";
import { toast } from "react-hot-toast";
import { useRouter } from "next/navigation";

export default function PvPLobbyPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [lobby, setLobby] = useState<PvPLobby | null>(null);
  const [matchHistory, setMatchHistory] = useState<PvPHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isInQueue, setIsInQueue] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [lobbyData, historyData] = await Promise.all([
          api.pvp.getLobby(),
          api.pvp.getMatchHistory(),
        ]);
        setLobby(lobbyData);
        setMatchHistory(historyData);
      } catch (error) {
        console.error("Failed to fetch PvP data:", error);
        toast.error("Failed to load PvP lobby");
      } finally {
        setIsLoading(false);
      }
    };

    if (user) {
      fetchData();
    }
  }, [user]);

  useEffect(() => {
    if (!user) return;

    const unsubscribe = wsClient.subscribe((message) => {
      switch (message.type) {
        case "match_found":
          toast.success("Match found! Preparing for battle...");
          router.push(`/pvp/match/${message.payload.matchId}`);
          break;
        case "player_status":
          setLobby((prev) => {
            if (!prev) return prev;
            return {
              ...prev,
              onlinePlayers: prev.onlinePlayers.map((player) =>
                player.id === message.payload.playerId
                  ? { ...player, status: message.payload.status }
                  : player
              ),
            };
          });
          break;
      }
    });

    return () => {
      unsubscribe();
    };
  }, [user, router]);

  const handleQueueToggle = async () => {
    try {
      if (isInQueue) {
        await api.pvp.leaveQueue();
        toast.success("Left matchmaking queue");
      } else {
        await api.pvp.joinQueue();
        toast.success("Joined matchmaking queue");
      }
      setIsInQueue(!isInQueue);
    } catch (error) {
      console.error("Failed to toggle queue:", error);
      toast.error("Failed to update queue status");
    }
  };

  if (isLoading) {
    return (
      <div className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white flex items-center justify-center'>
        <div className='animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500'></div>
      </div>
    );
  }

  return (
    <main className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white p-8'>
      <div className='max-w-6xl mx-auto'>
        <div className='grid grid-cols-1 lg:grid-cols-3 gap-8'>
          {/* Queue Status */}
          <Card className='bg-gray-800 p-6'>
            <div className='text-center'>
              <h2 className='text-2xl font-bold mb-4'>Matchmaking</h2>
              <button
                onClick={handleQueueToggle}
                className={`w-full py-3 px-4 rounded-md text-white font-medium ${
                  isInQueue
                    ? "bg-red-600 hover:bg-red-700"
                    : "bg-blue-600 hover:bg-blue-700"
                }`}
              >
                {isInQueue ? "Leave Queue" : "Join Queue"}
              </button>
              {isInQueue && (
                <p className='mt-4 text-blue-400 animate-pulse'>
                  Searching for opponent...
                </p>
              )}
            </div>
          </Card>

          {/* Online Players */}
          <Card className='bg-gray-800 p-6 lg:col-span-2'>
            <h2 className='text-2xl font-bold mb-4'>Online Players</h2>
            <div className='space-y-4'>
              {lobby?.onlinePlayers.map((player) => (
                <div
                  key={player.id}
                  className='flex items-center justify-between p-4 bg-gray-700 rounded-lg'
                >
                  <div>
                    <h3 className='font-medium'>{player.username}</h3>
                    <p className='text-sm text-gray-400'>
                      Rating: {player.rating}
                    </p>
                  </div>
                  <div>
                    <span
                      className={`px-2 py-1 rounded-full text-xs ${
                        player.status === "in_match"
                          ? "bg-red-500"
                          : player.status === "in_queue"
                          ? "bg-yellow-500"
                          : "bg-green-500"
                      }`}
                    >
                      {player.status.replace("_", " ")}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Match History */}
          <Card className='bg-gray-800 p-6 lg:col-span-3'>
            <h2 className='text-2xl font-bold mb-4'>Match History</h2>
            <div className='space-y-4'>
              {matchHistory.map((match) => (
                <div
                  key={match.id}
                  className='flex items-center justify-between p-4 bg-gray-700 rounded-lg'
                >
                  <div>
                    <h3 className='font-medium'>
                      vs {match.opponent.username}
                    </h3>
                    <p className='text-sm text-gray-400'>
                      {new Date(match.timestamp).toLocaleDateString()}
                    </p>
                  </div>
                  <div className='text-right'>
                    <p
                      className={`font-medium ${
                        match.result === "win"
                          ? "text-green-400"
                          : match.result === "loss"
                          ? "text-red-400"
                          : "text-yellow-400"
                      }`}
                    >
                      {match.result.toUpperCase()}
                    </p>
                    <p className='text-sm text-gray-400'>
                      Rating: {match.ratingChange > 0 ? "+" : ""}
                      {match.ratingChange}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </main>
  );
}
