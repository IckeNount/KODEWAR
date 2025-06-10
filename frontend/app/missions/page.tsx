import Link from "next/link";

const missions = [
  {
    id: 1,
    title: "Tutorial: First Flight",
    description:
      "Learn the basics of Python by controlling your first spaceship",
    difficulty: "Beginner",
    rewards: ["100 Credits", "Basic Ship Controls"],
    status: "available",
  },
  {
    id: 2,
    title: "Mission: Resource Collection",
    description:
      "Practice loops and conditionals while gathering space resources",
    difficulty: "Beginner",
    rewards: ["200 Credits", "Resource Scanner"],
    status: "locked",
  },
  {
    id: 3,
    title: "Mission: Asteroid Field",
    description:
      "Navigate through an asteroid field using functions and variables",
    difficulty: "Intermediate",
    rewards: ["300 Credits", "Shield Generator"],
    status: "locked",
  },
];

export default function MissionsPage() {
  return (
    <main className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white'>
      <div className='container mx-auto px-4 py-8'>
        <header className='mb-8'>
          <h1 className='text-4xl font-bold mb-2'>Missions</h1>
          <p className='text-gray-400'>
            Complete missions to earn rewards and progress your journey
          </p>
        </header>

        <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
          {missions.map((mission) => (
            <div
              key={mission.id}
              className={`bg-gray-800 rounded-lg p-6 ${
                mission.status === "locked"
                  ? "opacity-50 cursor-not-allowed"
                  : "hover:bg-gray-700 transition-colors"
              }`}
            >
              <div className='flex justify-between items-start mb-4'>
                <h2 className='text-2xl font-semibold'>{mission.title}</h2>
                <span
                  className={`px-2 py-1 rounded text-sm ${
                    mission.difficulty === "Beginner"
                      ? "bg-green-600"
                      : "bg-yellow-600"
                  }`}
                >
                  {mission.difficulty}
                </span>
              </div>

              <p className='text-gray-400 mb-4'>{mission.description}</p>

              <div className='mb-4'>
                <h3 className='text-sm font-semibold mb-2'>Rewards:</h3>
                <ul className='list-disc list-inside text-gray-300'>
                  {mission.rewards.map((reward, index) => (
                    <li key={index}>{reward}</li>
                  ))}
                </ul>
              </div>

              {mission.status === "available" ? (
                <Link
                  href={`/missions/${mission.id}`}
                  className='block w-full bg-blue-600 text-white text-center py-2 rounded hover:bg-blue-700 transition-colors'
                >
                  Start Mission
                </Link>
              ) : (
                <button
                  disabled
                  className='block w-full bg-gray-600 text-white text-center py-2 rounded cursor-not-allowed'
                >
                  Locked
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
