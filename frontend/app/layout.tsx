import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";
import Providers from "./components/Providers";
import { AuthProvider } from "./contexts/AuthContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "KODEWAR - Space Adventure Coding Game",
  description: "Learn Python through an exciting space adventure game",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang='en'>
      <body className={inter.className}>
        <Providers>
          <AuthProvider>
            {children}
            <Toaster position='top-right' />
          </AuthProvider>
        </Providers>
      </body>
    </html>
  );
}
