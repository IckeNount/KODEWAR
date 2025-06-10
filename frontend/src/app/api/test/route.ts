import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    message: "Hello from React Query!",
    timestamp: new Date().toISOString(),
  });
}
