import "./globals.css";
import Link from "next/link";
import type { ReactNode } from "react";

export const metadata = {
  title: "HealthProfile",
  description: "Synthetic HealthTech profile builder (demo, no real patient data)",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="nav">
          <strong>HealthProfile</strong>
          <nav>
            <Link href="/register">Register</Link>
            <Link href="/login">Login</Link>
            <Link href="/profile">My profile</Link>
            <Link href="/admin/login">Admin</Link>
          </nav>
        </header>
        <main className="container">{children}</main>
      </body>
    </html>
  );
}