"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  BadgeIndianRupee,
  CloudSun,
  FileCheck2,
  Leaf,
  LogOut,
  MessageSquareText,
  Microscope,
  UserRound,
} from "lucide-react";
import { authApi } from "@/lib/api";
import { useT } from "@/lib/i18n";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";

const NAV_ITEMS = [
  { href: "/dashboard/chat", icon: MessageSquareText, tKey: "nav.chat", helper: "Ask crop and seasonal questions" },
  { href: "/dashboard/disease", icon: Microscope, tKey: "nav.disease", helper: "Report crop symptoms" },
  { href: "/dashboard/profile", icon: UserRound, tKey: "nav.profile", helper: "Manage farmer and farm details" },
  { href: "/dashboard/weather", icon: CloudSun, tKey: "nav.weather", helper: "View local alerts and forecast" },
  { href: "/dashboard/market", icon: BadgeIndianRupee, tKey: "nav.market", helper: "Compare mandi prices" },
  { href: "/dashboard/schemes", icon: FileCheck2, tKey: "nav.schemes", helper: "Check eligibility and guidance" },
  { href: "/dashboard/soil", icon: Leaf, tKey: "nav.soil", helper: "Review soil health support" },
];

export default function DashboardPage() {
  const router = useRouter();
  const t = useT();
  const [userName, setUserName] = useState("");
  const [role, setRole] = useState("");

  useEffect(() => {
    authApi
      .me()
      .then((res) => {
        setUserName(res.data.phone);
        setRole(res.data.role);
      })
      .catch(() => router.push("/login"));
  }, [router]);

  return (
    <main className="min-h-screen bg-[var(--color-bg-secondary)]">
      <header className="border-b border-[var(--color-border-light)] bg-white">
        <div className="identity-bar">
          <div className="gov-container flex items-center justify-between">
            <span>Government of India</span>
            <LanguageSwitcher />
          </div>
        </div>
        <div className="gov-container flex flex-col gap-4 py-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-[12px] font-medium uppercase tracking-[0.04em] text-[var(--color-text-secondary)]">
              Farmer service dashboard
            </p>
            <h1 className="text-[22px] font-bold text-[var(--color-text-primary)]">Krishi Sahayak</h1>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            {role === "admin" && (
              <Link href="/admin" className="btn-secondary btn-sm">
                Officer dashboard
              </Link>
            )}
            <span className="rounded-md bg-[var(--color-primary-50)] px-3 py-1.5 text-[13px] font-medium text-[var(--color-primary-900)]">
              {userName || "Registered user"}
            </span>
            <button
              onClick={() => {
                authApi.logout().finally(() => {
                  localStorage.removeItem("access_token");
                  localStorage.removeItem("refresh_token");
                  router.push("/login");
                });
              }}
              className="btn-secondary btn-sm"
            >
              <LogOut size={15} className="mr-2" />
              {t("nav.logout")}
            </button>
          </div>
        </div>
      </header>

      <div className="gov-container grid gap-6 py-6 lg:grid-cols-[240px_1fr]">
        <aside className="portal-card h-fit overflow-hidden">
          <div className="border-b border-[var(--color-border-light)] bg-[var(--color-primary-900)] px-4 py-3 text-white">
            <p className="text-[13px] font-semibold">Service Menu</p>
          </div>
          <nav className="grid p-2" aria-label="Dashboard services">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex items-center gap-3 rounded-md px-3 py-2.5 text-[13px] font-medium text-[var(--color-text-secondary)] hover:bg-[var(--color-primary-50)] hover:text-[var(--color-primary-900)]"
                >
                  <Icon size={17} />
                  {t(item.tKey)}
                </Link>
              );
            })}
          </nav>
        </aside>

        <section id="main-content">
          <div className="mb-5">
            <p className="text-[13px] text-[var(--color-text-muted)]">Home / Farmer Dashboard</p>
            <h2 className="mt-1 text-[28px] font-bold text-[var(--color-text-primary)]">
              {t("dashboard.welcome")}
            </h2>
            <p className="mt-1 text-[14px] text-[var(--color-text-secondary)]">{t("dashboard.prompt")}</p>
          </div>

          <div className="kpi-grid mb-5">
            {[
              ["Open advisories", "7", "Updated today"],
              ["Weather alerts", "3", "District level"],
              ["Scheme matches", "12", "Based on profile"],
              ["Market updates", "18", "Nearby mandis"],
            ].map(([label, value, hint]) => (
              <div key={label} className="kpi-card">
                <div className="text-[12px] font-medium uppercase tracking-[0.04em] text-[var(--color-text-secondary)]">
                  {label}
                </div>
                <div className="mt-2 text-[28px] font-bold leading-none text-[var(--color-text-primary)]">{value}</div>
                <div className="mt-2 text-[12px] text-[var(--color-success)]">{hint}</div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className="portal-card group p-5 transition-colors hover:border-[var(--color-primary-700)]"
                >
                  <div className="flex items-start gap-4">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-[var(--color-primary-50)] text-[var(--color-primary-800)]">
                      <Icon size={21} />
                    </div>
                    <div>
                      <div className="text-[15px] font-semibold text-[var(--color-text-primary)] group-hover:text-[var(--color-primary-800)]">
                        {t(item.tKey)}
                      </div>
                      <p className="mt-1 text-[13px] leading-5 text-[var(--color-text-secondary)]">{item.helper}</p>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </section>
      </div>
    </main>
  );
}
