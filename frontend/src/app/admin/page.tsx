"use client";

import { useQuery } from "@tanstack/react-query";
import { MessageSquare, Microscope, Sprout, Users } from "lucide-react";
import { adminApi } from "@/lib/api";
import { useT } from "@/lib/i18n";

interface Stats {
  total_users: number;
  total_farmers: number;
  total_chat_messages: number;
  total_disease_reports: number;
}

export default function AdminOverviewPage() {
  const t = useT();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["admin", "stats"],
    queryFn: async () => (await adminApi.stats()).data as Stats,
  });

  const cards = [
    { key: "total_users", icon: Users, value: data?.total_users, color: "text-primary-700 bg-primary-50" },
    { key: "total_farmers", icon: Sprout, value: data?.total_farmers, color: "text-amber-700 bg-amber-50" },
    { key: "total_chats", icon: MessageSquare, value: data?.total_chat_messages, color: "text-blue-700 bg-blue-50" },
    { key: "total_disease_reports", icon: Microscope, value: data?.total_disease_reports, color: "text-rose-700 bg-rose-50" },
  ] as const;

  return (
    <div>
      <div className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-[12px] font-semibold uppercase tracking-[0.05em] text-[var(--color-primary-800)]">
            Monitoring overview
          </p>
          <h2 className="text-[28px] font-bold text-[var(--color-text-primary)]">{t("admin.title")}</h2>
          <p className="text-[14px] text-[var(--color-text-secondary)]">{t("admin.subtitle")}</p>
        </div>
        <div className="rounded-md border border-[var(--color-border-light)] bg-white px-3 py-2 text-[12px] text-[var(--color-text-secondary)]">
          Reporting period: Current season
        </div>
      </div>

      {isError ? (
        <div className="portal-card border-l-4 border-l-[var(--color-error)] p-4 text-[var(--color-error)]">
          {t("common.error")}
        </div>
      ) : (
        <div className="kpi-grid">
          {cards.map((card) => {
            const Icon = card.icon;
            return (
              <div key={card.key} className="kpi-card">
                <div className="mb-4 flex items-center justify-between gap-3">
                  <div className="text-[12px] font-medium uppercase tracking-[0.04em] text-[var(--color-text-secondary)]">
                    {t(`admin.${card.key}`)}
                  </div>
                  <div className={`flex h-9 w-9 items-center justify-center rounded-md ${card.color}`}>
                    <Icon size={20} />
                  </div>
                </div>
                <div className="text-[28px] font-bold leading-none text-[var(--color-text-primary)]">
                  {isLoading ? "-" : card.value ?? 0}
                </div>
                <div className="mt-2 text-[12px] text-[var(--color-success)]">
                  Available in service records
                </div>
              </div>
            );
          })}
        </div>
      )}

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="portal-card p-5">
          <h3 className="card-title">Service desk status</h3>
          <div className="mt-4 grid gap-3">
            {["Farmer account services", "Disease report review", "Market price data sync"].map((label) => (
              <div
                key={label}
                className="flex items-center justify-between gap-4 border-b border-[var(--color-border-light)] pb-3 last:border-b-0 last:pb-0"
              >
                <span className="text-[13px] text-[var(--color-text-secondary)]">{label}</span>
                <span className="badge-success">Operational</span>
              </div>
            ))}
          </div>
        </div>
        <div className="portal-card p-5">
          <h3 className="card-title">Review queue</h3>
          <p className="mt-2 text-[13px] leading-6 text-[var(--color-text-secondary)]">
            Use the user management section to review active farmers, officer access, and account
            status. Additional queues can be added here as service modules mature.
          </p>
        </div>
      </div>
    </div>
  );
}
