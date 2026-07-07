"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, LayoutDashboard, ShieldCheck, Users } from "lucide-react";
import { authApi } from "@/lib/api";
import { useT } from "@/lib/i18n";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const t = useT();
  const [status, setStatus] = useState<"checking" | "ok" | "denied">("checking");

  useEffect(() => {
    authApi
      .me()
      .then((res) => setStatus(res.data.role === "admin" ? "ok" : "denied"))
      .catch(() => router.push("/login"));
  }, [router]);

  if (status === "checking") {
    return (
      <div className="min-h-screen bg-[var(--color-bg-secondary)] p-8">
        <div className="portal-card mx-auto mt-20 max-w-md p-6 text-center text-[var(--color-text-secondary)]">
          {t("common.loading")}
        </div>
      </div>
    );
  }

  if (status === "denied") {
    return (
      <div className="min-h-screen bg-[var(--color-bg-secondary)] p-8">
        <div className="portal-card mx-auto mt-20 max-w-md p-6 text-center">
          <p className="text-[var(--color-text-secondary)]">{t("admin.forbidden")}</p>
          <Link href="/dashboard" className="mt-4 inline-flex text-[14px] font-medium text-[var(--color-info)] hover:underline">
            {t("admin.back_to_app")}
          </Link>
        </div>
      </div>
    );
  }

  const navItems = [
    { href: "/admin", icon: LayoutDashboard, label: t("admin.nav_overview") },
    { href: "/admin/users", icon: Users, label: t("admin.nav_users") },
  ];

  return (
    <div className="min-h-screen bg-[var(--color-bg-secondary)]">
      <div className="identity-bar">
        <div className="gov-container flex items-center justify-between">
          <span>Government of India | Officer Console</span>
          <LanguageSwitcher />
        </div>
      </div>
      <div className="flex min-h-[calc(100vh-32px)]">
        <aside className="hidden w-64 shrink-0 bg-[var(--color-primary-900)] text-white lg:flex lg:flex-col">
          <div className="border-b border-white/15 px-5 py-5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-white/10">
                <ShieldCheck size={22} />
              </div>
              <div>
                <div className="text-[16px] font-semibold">{t("admin.title")}</div>
                <div className="text-[12px] text-white/70">Agriculture service monitoring</div>
              </div>
            </div>
          </div>
          <nav className="flex-1 px-3 py-4" aria-label="Admin navigation">
            {navItems.map((item) => {
              const active = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`mb-1 flex items-center gap-3 rounded-md px-3 py-2.5 text-[14px] font-medium transition-colors ${
                    active ? "bg-white text-[var(--color-primary-900)]" : "text-white/80 hover:bg-white/10 hover:text-white"
                  }`}
                >
                  <Icon size={18} />
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <Link
            href="/dashboard"
            className="flex items-center gap-2 border-t border-white/15 px-5 py-4 text-[13px] text-white/75 hover:text-white"
          >
            <ArrowLeft size={16} />
            {t("admin.back_to_app")}
          </Link>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="border-b border-[var(--color-border-light)] bg-white px-5 py-4 lg:px-8">
            <p className="text-[12px] text-[var(--color-text-muted)]">Home / Officer Console</p>
            <h1 className="text-[22px] font-bold text-[var(--color-text-primary)]">{t("admin.title")}</h1>
          </header>
          <main className="flex-1 p-5 lg:p-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
