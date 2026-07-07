import type { Metadata } from "next";
import { Toaster } from "react-hot-toast";
import "./globals.css";
import { QueryProvider } from "@/providers/QueryProvider";
import { I18nProvider } from "@/lib/i18n";

export const metadata: Metadata = {
  title: "Krishi Sahayak — AI Agriculture Assistant",
  description: "AI-powered farming advice for Indian farmers in their language",
  keywords: ["agriculture", "farming", "India", "AI", "krishi", "sahayak"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <QueryProvider>
          <I18nProvider>
            {children}
            <Toaster position="top-right" />
          </I18nProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
