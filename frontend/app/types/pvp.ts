export interface PvPMatch {
  id: string;
  status: "waiting" | "in_progress" | "completed";
  players: {
    id: string;
    username: string;
    rating: number;
    ready: boolean;
  }[];
  winner?: string;
  startTime?: string;
  endTime?: string;
  duration?: number;
}

export interface PvPLobby {
  onlinePlayers: {
    id: string;
    username: string;
    rating: number;
    status: "idle" | "in_queue" | "in_match";
  }[];
  currentMatch?: PvPMatch;
}

export interface PvPHistory {
  id: string;
  opponent: {
    id: string;
    username: string;
    rating: number;
  };
  result: "win" | "loss" | "draw";
  ratingChange: number;
  timestamp: string;
  duration: number;
}
