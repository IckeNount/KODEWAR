export type BuildingType =
  | "command_center"
  | "resource_collector"
  | "defense_turret"
  | "research_lab"
  | "barracks";

export type ResourceType =
  | "credits"
  | "minerals"
  | "energy"
  | "research_points";

export interface Building {
  id: string;
  type: BuildingType;
  level: number;
  position: {
    x: number;
    y: number;
  };
  health: number;
  maxHealth: number;
  constructionProgress?: number;
  lastUpgradeTime?: string;
  upgradeCooldown?: number;
}

export interface Resource {
  type: ResourceType;
  amount: number;
  productionRate: number;
  lastCollectionTime: string;
}

export interface PlayerBase {
  id: string;
  userId: string;
  name: string;
  buildings: Building[];
  resources: Resource[];
  gridSize: {
    width: number;
    height: number;
  };
  lastUpdated: string;
}

export interface BuildingTemplate {
  type: BuildingType;
  name: string;
  description: string;
  baseCost: {
    credits: number;
    minerals: number;
    energy: number;
  };
  baseProduction?: {
    type: ResourceType;
    amount: number;
  };
  baseHealth: number;
  upgradeMultiplier: number;
  constructionTime: number;
  upgradeCooldown: number;
  maxLevel: number;
  sprite: string;
}
