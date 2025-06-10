"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/app/contexts/AuthContext";
import { UserProfile } from "@/app/types/profile";
import { api } from "@/app/lib/api";
import Image from "next/image";
import { Progress } from "@/app/components/ui/progress";
import { Card } from "@/app/components/ui/card";
import { Badge } from "@/app/components/ui/badge";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/app/components/ui/tabs";

export default function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await api.profile.getProfile();
        setProfile(data);
      } catch (error) {
        console.error("Failed to fetch profile:", error);
      } finally {
        setIsLoading(false);
      }
    };

    if (user) {
      fetchProfile();
    }
  }, [user]);

  if (isLoading) {
    return (
      <div className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white flex items-center justify-center'>
        <div className='animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500'></div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white flex items-center justify-center'>
        <div className='text-center'>
          <h1 className='text-2xl font-bold mb-4'>Profile Not Found</h1>
          <p className='text-gray-400'>Please try logging in again.</p>
        </div>
      </div>
    );
  }

  return (
    <main className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white p-8'>
      <div className='max-w-6xl mx-auto'>
        <div className='grid grid-cols-1 md:grid-cols-3 gap-8'>
          {/* Profile Card */}
          <Card className='bg-gray-800 p-6'>
            <div className='flex flex-col items-center'>
              <div className='relative w-32 h-32 mb-4'>
                <Image
                  src={profile.avatar || "/default-avatar.png"}
                  alt={profile.username}
                  fill
                  className='rounded-full object-cover'
                />
              </div>
              <h2 className='text-2xl font-bold'>{profile.username}</h2>
              <p className='text-gray-400'>Level {profile.level}</p>

              {/* Experience Progress */}
              <div className='w-full mt-4'>
                <div className='flex justify-between text-sm mb-1'>
                  <span>Experience</span>
                  <span>{profile.experience} / 1000</span>
                </div>
                <Progress value={(profile.experience / 1000) * 100} />
              </div>

              {/* Resources */}
              <div className='w-full mt-6 space-y-2'>
                <div className='flex justify-between'>
                  <span>Credits:</span>
                  <span className='text-yellow-400'>{profile.credits}</span>
                </div>
                <div className='flex justify-between'>
                  <span>Energy:</span>
                  <span className='text-green-400'>
                    {profile.resources.energy}
                  </span>
                </div>
                <div className='flex justify-between'>
                  <span>Materials:</span>
                  <span className='text-blue-400'>
                    {profile.resources.materials}
                  </span>
                </div>
              </div>
            </div>
          </Card>

          {/* Main Content */}
          <div className='md:col-span-2'>
            <Tabs defaultValue='progress' className='w-full'>
              <TabsList className='grid w-full grid-cols-3'>
                <TabsTrigger value='progress'>Progress</TabsTrigger>
                <TabsTrigger value='badges'>Badges</TabsTrigger>
                <TabsTrigger value='pvp'>PvP Stats</TabsTrigger>
              </TabsList>

              <TabsContent value='progress' className='mt-6'>
                <Card className='bg-gray-800 p-6'>
                  <h3 className='text-xl font-bold mb-4'>Mission Progress</h3>
                  <div className='space-y-4'>
                    {profile.completedMissions.map((mission) => (
                      <div
                        key={mission.missionId}
                        className='flex items-center justify-between p-4 bg-gray-700 rounded-lg'
                      >
                        <div>
                          <h4 className='font-medium'>
                            Mission {mission.missionId}
                          </h4>
                          <p className='text-sm text-gray-400'>
                            Status: {mission.status}
                          </p>
                        </div>
                        <div className='text-right'>
                          <p className='font-medium'>Score: {mission.score}</p>
                          {mission.completedAt && (
                            <p className='text-sm text-gray-400'>
                              Completed:{" "}
                              {new Date(
                                mission.completedAt
                              ).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              </TabsContent>

              <TabsContent value='badges' className='mt-6'>
                <Card className='bg-gray-800 p-6'>
                  <h3 className='text-xl font-bold mb-4'>Earned Badges</h3>
                  <div className='flex flex-wrap gap-2'>
                    {profile.badges.map((badge) => (
                      <Badge key={badge} variant='secondary'>
                        {badge}
                      </Badge>
                    ))}
                  </div>
                </Card>
              </TabsContent>

              <TabsContent value='pvp' className='mt-6'>
                <Card className='bg-gray-800 p-6'>
                  <h3 className='text-xl font-bold mb-4'>PvP Statistics</h3>
                  <div className='grid grid-cols-2 gap-4'>
                    <div className='p-4 bg-gray-700 rounded-lg'>
                      <p className='text-gray-400'>Wins</p>
                      <p className='text-2xl font-bold'>
                        {profile.pvpStats.wins}
                      </p>
                    </div>
                    <div className='p-4 bg-gray-700 rounded-lg'>
                      <p className='text-gray-400'>Losses</p>
                      <p className='text-2xl font-bold'>
                        {profile.pvpStats.losses}
                      </p>
                    </div>
                    <div className='p-4 bg-gray-700 rounded-lg'>
                      <p className='text-gray-400'>Rating</p>
                      <p className='text-2xl font-bold'>
                        {profile.pvpStats.rating}
                      </p>
                    </div>
                    <div className='p-4 bg-gray-700 rounded-lg'>
                      <p className='text-gray-400'>Rank</p>
                      <p className='text-2xl font-bold'>
                        {profile.pvpStats.rank || "Unranked"}
                      </p>
                    </div>
                  </div>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </main>
  );
}
