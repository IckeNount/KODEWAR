import Link from "next/link";

export default function Home() {
  return (
    <main className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white'>
      <div className='container mx-auto px-4 py-8'>
        <header className='mb-8'>
          <h1 className='text-4xl font-bold mb-2'>KODEWAR</h1>
          <p className='text-gray-400'>Your Space Adventure Awaits</p>
        </header>

        <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
          {/* Mission Control Card */}
          <div className='bg-gray-800 rounded-lg p-6 hover:bg-gray-700 transition-colors'>
            <h2 className='text-2xl font-semibold mb-4'>Mission Control</h2>
            <div className='space-y-4'>
              <div className='flex justify-between'>
                <span>Oxygen Level:</span>
                <span className='text-green-400'>100%</span>
              </div>
              <div className='flex justify-between'>
                <span>Energy:</span>
                <span className='text-blue-400'>75%</span>
              </div>
              <Link
                href='/missions'
                className='block w-full bg-blue-600 text-white text-center py-2 rounded hover:bg-blue-700 transition-colors'
              >
                View Missions
              </Link>
            </div>
          </div>

          {/* Resources Card */}
          <div className='bg-gray-800 rounded-lg p-6 hover:bg-gray-700 transition-colors'>
            <h2 className='text-2xl font-semibold mb-4'>Resources</h2>
            <div className='space-y-4'>
              <div className='flex justify-between'>
                <span>Credits:</span>
                <span>1,000</span>
              </div>
              <div className='flex justify-between'>
                <span>Materials:</span>
                <span>500</span>
              </div>
              <Link
                href='/inventory'
                className='block w-full bg-green-600 text-white text-center py-2 rounded hover:bg-green-700 transition-colors'
              >
                View Inventory
              </Link>
            </div>
          </div>

          {/* Base Status Card */}
          <div className='bg-gray-800 rounded-lg p-6 hover:bg-gray-700 transition-colors'>
            <h2 className='text-2xl font-semibold mb-4'>Base Status</h2>
            <div className='space-y-4'>
              <div className='flex justify-between'>
                <span>Defense Level:</span>
                <span className='text-yellow-400'>Level 1</span>
              </div>
              <div className='flex justify-between'>
                <span>Planet Type:</span>
                <span>Unassigned</span>
              </div>
              <Link
                href='/base'
                className='block w-full bg-purple-600 text-white text-center py-2 rounded hover:bg-purple-700 transition-colors'
              >
                Manage Base
              </Link>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className='mt-8'>
          <h2 className='text-2xl font-semibold mb-4'>Quick Actions</h2>
          <div className='grid grid-cols-2 md:grid-cols-4 gap-4'>
            <Link
              href='/missions/tutorial'
              className='bg-blue-600 text-white text-center py-3 rounded hover:bg-blue-700 transition-colors'
            >
              Start Tutorial
            </Link>
            <Link
              href='/pvp'
              className='bg-red-600 text-white text-center py-3 rounded hover:bg-red-700 transition-colors'
            >
              PvP Arena
            </Link>
            <Link
              href='/profile'
              className='bg-gray-600 text-white text-center py-3 rounded hover:bg-gray-700 transition-colors'
            >
              Profile
            </Link>
            <Link
              href='/leaderboard'
              className='bg-yellow-600 text-white text-center py-3 rounded hover:bg-yellow-700 transition-colors'
            >
              Leaderboard
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
