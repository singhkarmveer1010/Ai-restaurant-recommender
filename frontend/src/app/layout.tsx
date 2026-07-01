import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "AI Restaurant Recommender | Lumina Gastronomy",
  description:
    "AI-powered restaurant recommendations using Groq LLM and verified Zomato reviews. Experience premium dining discovery with custom taste and ambiance preferences.",
  keywords: [
    "restaurant recommender",
    "AI dining",
    "Zomato",
    "Groq LLM",
    "food discovery",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark h-full">
      <head>
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
        />
      </head>
      <body className={`${inter.variable} h-full antialiased bg-[#0a0a0f] text-[#e6e0e9]`}>
        {children}
      </body>
    </html>
  );
}
