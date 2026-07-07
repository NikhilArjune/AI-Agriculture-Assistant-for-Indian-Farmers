"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import Link from "next/link";
import toast from "react-hot-toast";
import { LockKeyhole, Phone } from "lucide-react";
import { authApi } from "@/lib/api";
import { GovHeader } from "@/components/GovHeader";

const schema = z.object({
  phone: z.string().min(10, "Enter a valid phone number"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

type FormData = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    try {
      const res = await authApi.login(data);
      localStorage.setItem("access_token", res.data.access_token);
      localStorage.setItem("refresh_token", res.data.refresh_token);
      toast.success("Signed in successfully");
      router.push("/dashboard");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Login failed. Check credentials.");
    }
  };

  return (
    <main className="min-h-screen bg-[var(--color-bg-secondary)]">
      <GovHeader />
      <section id="main-content" className="gov-container grid gap-8 py-10 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="portal-card p-6">
          <p className="text-[12px] font-semibold uppercase tracking-[0.05em] text-[var(--color-primary-800)]">
            Farmer portal access
          </p>
          <h1 className="mt-2 text-[28px] font-bold leading-tight text-[var(--color-text-primary)]">
            Sign in to Krishi Sahayak
          </h1>
          <p className="mt-3 text-[14px] leading-6 text-[var(--color-text-secondary)]">
            Use your registered mobile number to access advisory services, scheme guidance,
            disease reports and market information.
          </p>
          <div className="mt-6 rounded-md border border-[var(--color-border-light)] bg-[var(--color-primary-50)] p-4 text-[13px] leading-6 text-[var(--color-primary-900)]">
            Keep your mobile number active for important weather alerts and application updates.
          </div>
        </div>

        <div className="portal-card p-6">
          <h2 className="card-title">Registered user login</h2>
          <p className="mb-5 mt-1 text-[13px] text-[var(--color-text-secondary)]">
            Fields marked as required must be completed.
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4">
            <div>
              <label className="form-label" htmlFor="phone">
                Mobile number
              </label>
              <div className="relative">
                <Phone
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)]"
                />
                <input
                  {...register("phone")}
                  id="phone"
                  type="tel"
                  placeholder="9876543210"
                  className="form-control pl-9"
                />
              </div>
              {errors.phone && <p className="mt-1 text-[12px] text-[var(--color-error)]">{errors.phone.message}</p>}
            </div>

            <div>
              <label className="form-label" htmlFor="password">
                Password
              </label>
              <div className="relative">
                <LockKeyhole
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)]"
                />
                <input
                  {...register("password")}
                  id="password"
                  type="password"
                  placeholder="Enter password"
                  className="form-control pl-9"
                />
              </div>
              {errors.password && (
                <p className="mt-1 text-[12px] text-[var(--color-error)]">{errors.password.message}</p>
              )}
            </div>

            <button type="submit" disabled={isSubmitting} className="btn-primary mt-2 w-full">
              {isSubmitting ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <p className="mt-5 text-center text-[13px] text-[var(--color-text-secondary)]">
            New farmer?{" "}
            <Link href="/register" className="font-medium text-[var(--color-info)] hover:underline">
              Register for services
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}
