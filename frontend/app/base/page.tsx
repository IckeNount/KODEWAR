"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/app/contexts/AuthContext";
import { api } from "@/app/lib/api";
import {
  PlayerBase,
  Building,
  BuildingTemplate,
  Resource,
} from "@/app/types/base";
import { Card } from "@/app/components/ui/card";
import { toast } from "react-hot-toast";

const GRID_SIZE = 10;
const CELL_SIZE = 60;

const BUILDING_TEMPLATES: Record<string, BuildingTemplate> = {
  command_center: {
    type: "command_center",
    name: "Command Center",
    description: "The heart of your base. Required for other buildings.",
    baseCost: {
      credits: 1000,
      minerals: 500,
      energy: 200,
    },
    baseHealth: 1000,
    upgradeMultiplier: 1.5,
    constructionTime: 300,
    upgradeCooldown: 600,
    maxLevel: 5,
    sprite: "🏛️",
  },
  resource_collector: {
    type: "resource_collector",
    name: "Resource Collector",
    description: "Automatically collects resources over time.",
    baseCost: {
      credits: 500,
      minerals: 300,
      energy: 100,
    },
    baseProduction: {
      type: "credits",
      amount: 10,
    },
    baseHealth: 500,
    upgradeMultiplier: 1.3,
    constructionTime: 180,
    upgradeCooldown: 300,
    maxLevel: 10,
    sprite: "🏭",
  },
  defense_turret: {
    type: "defense_turret",
    name: "Defense Turret",
    description: "Protects your base from attacks.",
    baseCost: {
      credits: 800,
      minerals: 400,
      energy: 150,
    },
    baseHealth: 800,
    upgradeMultiplier: 1.4,
    constructionTime: 240,
    upgradeCooldown: 480,
    maxLevel: 8,
    sprite: "🏰",
  },
};

export default function BaseCampPage() {
  const { user } = useAuth();
  const [base, setBase] = useState<PlayerBase | null>(null);
  const [selectedBuilding, setSelectedBuilding] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isPlacing, setIsPlacing] = useState(false);

  useEffect(() => {
    const fetchBase = async () => {
      try {
        const baseData = await api.base.getBase();
        setBase(baseData);
      } catch (error) {
        console.error("Failed to fetch base:", error);
        toast.error("Failed to load base");
      } finally {
        setIsLoading(false);
      }
    };

    if (user) {
      fetchBase();
    }
  }, [user]);

  const handleCellClick = async (x: number, y: number) => {
    if (!base || !selectedBuilding || !isPlacing) return;

    try {
      const building = await api.base.placeBuilding(selectedBuilding, { x, y });
      setBase((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          buildings: [...prev.buildings, building],
        };
      });
      toast.success("Building placed successfully");
      setIsPlacing(false);
      setSelectedBuilding(null);
    } catch (error) {
      console.error("Failed to place building:", error);
      toast.error("Failed to place building");
    }
  };

  const handleUpgrade = async (buildingId: string) => {
    try {
      const updatedBuilding = await api.base.upgradeBuilding(buildingId);
      setBase((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          buildings: prev.buildings.map((b) =>
            b.id === buildingId ? updatedBuilding : b
          ),
        };
      });
      toast.success("Building upgraded successfully");
    } catch (error) {
      console.error("Failed to upgrade building:", error);
      toast.error("Failed to upgrade building");
    }
  };

  const handleRemove = async (buildingId: string) => {
    try {
      await api.base.removeBuilding(buildingId);
      setBase((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          buildings: prev.buildings.filter((b) => b.id !== buildingId),
        };
      });
      toast.success("Building removed successfully");
    } catch (error) {
      console.error("Failed to remove building:", error);
      toast.error("Failed to remove building");
    }
  };

  const handleCollectResources = async () => {
    try {
      const updatedResources = await api.base.collectResources();
      setBase((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          resources: updatedResources,
        };
      });
      toast.success("Resources collected successfully");
    } catch (error) {
      console.error("Failed to collect resources:", error);
      toast.error("Failed to collect resources");
    }
  };

  if (isLoading) {
    return (
      <div className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white flex items-center justify-center'>
        <div className='animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500'></div>
      </div>
    );
  }

  if (!base) {
    return (
      <div className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white flex items-center justify-center'>
        <div className='text-center'>
          <h1 className='text-2xl font-bold mb-4'>No Base Found</h1>
          <p className='text-gray-400 mb-4'>
            Create your first base to get started!
          </p>
          <button
            onClick={async () => {
              try {
                const newBase = await api.base.createBase("My Base");
                setBase(newBase);
                toast.success("Base created successfully");
              } catch (error) {
                console.error("Failed to create base:", error);
                toast.error("Failed to create base");
              }
            }}
            className='bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded'
          >
            Create Base
          </button>
        </div>
      </div>
    );
  }

  return (
    <main className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white p-8'>
      <div className='max-w-7xl mx-auto'>
        <div className='grid grid-cols-1 lg:grid-cols-4 gap-8'>
          {/* Resources Panel */}
          <Card className='bg-gray-800 p-6 lg:col-span-1'>
            <h2 className='text-2xl font-bold mb-4'>Resources</h2>
            <div className='space-y-4'>
              {base.resources.map((resource) => (
                <div
                  key={resource.type}
                  className='flex justify-between items-center p-3 bg-gray-700 rounded-lg'
                >
                  <div>
                    <p className='font-medium capitalize'>{resource.type}</p>
                    <p className='text-sm text-gray-400'>
                      +{resource.productionRate}/min
                    </p>
                  </div>
                  <p className='text-lg font-bold'>{resource.amount}</p>
                </div>
              ))}
              <button
                onClick={handleCollectResources}
                className='w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded'
              >
                Collect Resources
              </button>
            </div>
          </Card>

          {/* Building Grid */}
          <div className='lg:col-span-2'>
            <Card className='bg-gray-800 p-6'>
              <h2 className='text-2xl font-bold mb-4'>Base Grid</h2>
              <div
                className='grid gap-1'
                style={{
                  gridTemplateColumns: `repeat(${GRID_SIZE}, ${CELL_SIZE}px)`,
                  gridTemplateRows: `repeat(${GRID_SIZE}, ${CELL_SIZE}px)`,
                }}
              >
                {Array.from({ length: GRID_SIZE * GRID_SIZE }).map(
                  (_, index) => {
                    const x = index % GRID_SIZE;
                    const y = Math.floor(index / GRID_SIZE);
                    const building = base.buildings.find(
                      (b) => b.position.x === x && b.position.y === y
                    );

                    return (
                      <div
                        key={index}
                        onClick={() => handleCellClick(x, y)}
                        className={`border border-gray-700 flex items-center justify-center cursor-pointer hover:bg-gray-700 ${
                          isPlacing ? "bg-blue-900/20" : ""
                        }`}
                        style={{ width: CELL_SIZE, height: CELL_SIZE }}
                      >
                        {building && (
                          <div
                            className='w-full h-full flex items-center justify-center relative group'
                            title={`${
                              BUILDING_TEMPLATES[building.type].name
                            } (Level ${building.level})`}
                          >
                            <span className='text-2xl'>
                              {BUILDING_TEMPLATES[building.type].sprite}
                            </span>
                            <div className='absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-opacity flex items-center justify-center opacity-0 group-hover:opacity-100'>
                              <div className='space-x-2'>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleUpgrade(building.id);
                                  }}
                                  className='bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded text-sm'
                                  disabled={
                                    building.level >=
                                    BUILDING_TEMPLATES[building.type].maxLevel
                                  }
                                >
                                  ⬆️
                                </button>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleRemove(building.id);
                                  }}
                                  className='bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded text-sm'
                                >
                                  🗑️
                                </button>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  }
                )}
              </div>
            </Card>
          </div>

          {/* Building Selection */}
          <Card className='bg-gray-800 p-6 lg:col-span-1'>
            <h2 className='text-2xl font-bold mb-4'>Buildings</h2>
            <div className='space-y-4'>
              {Object.entries(BUILDING_TEMPLATES).map(([type, template]) => (
                <div
                  key={type}
                  className={`p-4 rounded-lg cursor-pointer transition-colors ${
                    selectedBuilding === type
                      ? "bg-blue-600"
                      : "bg-gray-700 hover:bg-gray-600"
                  }`}
                  onClick={() => {
                    setSelectedBuilding(type);
                    setIsPlacing(true);
                  }}
                >
                  <div className='flex items-center space-x-3'>
                    <span className='text-2xl'>{template.sprite}</span>
                    <div>
                      <h3 className='font-medium'>{template.name}</h3>
                      <p className='text-sm text-gray-400'>
                        Cost: {template.baseCost.credits} credits
                      </p>
                    </div>
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
