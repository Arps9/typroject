import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Compliance Audit Manager",
  description:
    "AI-Assisted Smart Compliance Reporting and Audit Management System",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
