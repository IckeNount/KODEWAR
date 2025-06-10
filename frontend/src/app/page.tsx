import { TestQuery } from "./test-query";

export default function Home() {
  return (
    <main className='container mx-auto px-4 py-8'>
      <h1 className='text-3xl font-bold mb-8'>React Query Test</h1>
      <TestQuery />
    </main>
  );
}
