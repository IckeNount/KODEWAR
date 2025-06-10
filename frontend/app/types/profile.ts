export interface MissionProgress {
  missionId: string;
  status: "not_started" | "in_progress" | "completed";
  score: number;
  lastSubmittedCode?: string;
  completedAt?: string;
}

export interface PvPStats {
  wins: number;
  losses: number;
  rating: number;
  rank?: string;
}

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  avatar?: string;
  level: number;
  experience: number;
  credits: number;
  completedMissions: MissionProgress[];
  badges: string[];
  pvpStats: PvPStats;
  resources: {
    energy: number;
    materials: number;
    currency: number;
  };
  createdAt: string;
  lastActive: string;
}
