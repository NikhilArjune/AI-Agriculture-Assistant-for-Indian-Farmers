"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { adminApi } from "@/lib/api";
import { useT } from "@/lib/i18n";

interface AdminUser {
  id: string;
  phone: string;
  email?: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
}

export default function AdminUsersPage() {
  const t = useT();
  const queryClient = useQueryClient();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["admin", "users"],
    queryFn: async () => (await adminApi.listUsers()).data as AdminUser[],
  });

  const deactivate = useMutation({
    mutationFn: (id: string) => adminApi.deactivateUser(id),
    onSuccess: () => {
      toast.success(t("admin.deactivated"));
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "stats"] });
    },
    onError: () => toast.error(t("common.error")),
  });

  const formatDate = (iso: string) => {
    try {
      return new Date(iso).toLocaleDateString();
    } catch {
      return iso;
    }
  };

  return (
    <div>
      <div className="mb-5">
        <p className="text-[12px] font-semibold uppercase tracking-[0.05em] text-[var(--color-primary-800)]">
          Beneficiary and officer records
        </p>
        <h2 className="text-[28px] font-bold text-[var(--color-text-primary)]">{t("admin.users_title")}</h2>
        <p className="text-[14px] text-[var(--color-text-secondary)]">{t("admin.users_subtitle")}</p>
      </div>

      {isLoading ? (
        <div className="portal-card p-5 text-[var(--color-text-secondary)]">{t("common.loading")}</div>
      ) : isError ? (
        <div className="portal-card border-l-4 border-l-[var(--color-error)] p-4 text-[var(--color-error)]">
          {t("common.error")}
        </div>
      ) : !data || data.length === 0 ? (
        <div className="portal-card p-8 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-[var(--color-primary-50)] text-[var(--color-primary-800)]">
            0
          </div>
          <p className="font-medium text-[var(--color-text-primary)]">{t("common.no_results")}</p>
          <p className="mt-1 text-[13px] text-[var(--color-text-secondary)]">
            Registered farmer and officer accounts will appear here.
          </p>
        </div>
      ) : (
        <div className="portal-card overflow-x-auto">
          <table className="w-full min-w-[760px] border-separate border-spacing-0 text-[13px]">
            <thead>
              <tr className="bg-[var(--color-bg-secondary)] text-left text-[12px] uppercase tracking-[0.04em] text-[var(--color-text-secondary)]">
                <th className="border-b-2 border-[var(--color-border)] px-4 py-3 font-semibold">{t("admin.col_phone")}</th>
                <th className="border-b-2 border-[var(--color-border)] px-4 py-3 font-semibold">{t("admin.col_email")}</th>
                <th className="border-b-2 border-[var(--color-border)] px-4 py-3 font-semibold">{t("admin.col_role")}</th>
                <th className="border-b-2 border-[var(--color-border)] px-4 py-3 font-semibold">{t("admin.col_status")}</th>
                <th className="border-b-2 border-[var(--color-border)] px-4 py-3 font-semibold">{t("admin.col_joined")}</th>
                <th className="border-b-2 border-[var(--color-border)] px-4 py-3 text-right font-semibold">
                  {t("admin.col_actions")}
                </th>
              </tr>
            </thead>
            <tbody>
              {data.map((u) => (
                <tr key={u.id} className="hover:bg-[var(--color-primary-50)]">
                  <td className="border-b border-[var(--color-border-light)] px-4 py-3 font-medium text-[var(--color-text-primary)]">
                    {u.phone}
                  </td>
                  <td className="border-b border-[var(--color-border-light)] px-4 py-3 text-[var(--color-text-secondary)]">
                    {u.email || "-"}
                  </td>
                  <td className="border-b border-[var(--color-border-light)] px-4 py-3">
                    <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.03em] text-slate-600">
                      {u.role}
                    </span>
                  </td>
                  <td className="border-b border-[var(--color-border-light)] px-4 py-3">
                    <span
                      className={
                        u.is_active
                          ? "badge-success"
                          : "rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.03em] text-slate-600"
                      }
                    >
                      {u.is_active ? t("admin.active") : t("admin.inactive")}
                    </span>
                  </td>
                  <td className="border-b border-[var(--color-border-light)] px-4 py-3 text-[var(--color-text-secondary)]">
                    {formatDate(u.created_at)}
                  </td>
                  <td className="border-b border-[var(--color-border-light)] px-4 py-3 text-right">
                    {u.is_active && u.role !== "admin" && (
                      <button
                        onClick={() => deactivate.mutate(u.id)}
                        disabled={deactivate.isPending}
                        className="text-[12px] font-medium text-[var(--color-error)] hover:underline disabled:opacity-50"
                      >
                        {t("admin.deactivate")}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
