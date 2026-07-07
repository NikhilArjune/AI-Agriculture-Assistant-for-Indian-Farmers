"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import Link from "next/link";
import toast from "react-hot-toast";
import { LockKeyhole, Phone, UserRound } from "lucide-react";
import { authApi } from "@/lib/api";
import { GovHeader } from "@/components/GovHeader";

const schema = z
  .object({
    full_name: z.string().min(2, "Name must be at least 2 characters"),
    phone: z.string().min(10, "Enter a valid phone number"),
    password: z.string().min(6, "Password must be at least 6 characters"),
    confirm_password: z.string(),
  })
  .refine((d) => d.password === d.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

type FormData = z.infer<typeof schema>;

export default function RegisterPage() {
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
      await authApi.register({
        full_name: data.full_name,
        phone: data.phone,
        password: data.password,
      });
      toast.success("Registration completed. Please sign in.");
      router.push("/login");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Registration failed.");
    }
  };

  return (
    <main className="min-h-screen bg-[var(--color-bg-secondary)]">
      <GovHeader />
      <section id="main-content" className="gov-container grid gap-8 py-10 lg:grid-cols-[0.85fr_1.15fr]">
        <div className="portal-card p-6">
          <p className="text-[12px] font-semibold uppercase tracking-[0.05em] text-[var(--color-primary-800)]">
            Beneficiary registration
          </p>
          <h1 className="mt-2 text-[28px] font-bold leading-tight text-[var(--color-text-primary)]">
            Create a farmer service account
          </h1>
          <p className="mt-3 text-[14px] leading-6 text-[var(--color-text-secondary)]">
            Register once to access advisory, market, weather, scheme and soil services from the
            farmer dashboard.
          </p>
          <ol className="mt-6 grid gap-3 text-[13px] text-[var(--color-text-secondary)]">
            {["Enter farmer details", "Verify mobile access", "Complete profile in dashboard"].map((step, index) => (
              <li key={step} className="flex items-center gap-3">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[var(--color-primary-800)] text-[12px] font-semibold text-white">
                  {index + 1}
                </span>
                {step}
              </li>
            ))}
          </ol>
        </div>

        <div className="portal-card p-6">
          <h2 className="card-title">Farmer registration form</h2>
          <p className="mb-5 mt-1 text-[13px] text-[var(--color-text-secondary)]">
            Please enter details as per your mobile registration record.
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4 md:grid-cols-2">
            <div className="md:col-span-2">
              <label className="form-label" htmlFor="full_name">
                Full name
              </label>
              <div className="relative">
                <UserRound
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)]"
                />
                <input
                  {...register("full_name")}
                  id="full_name"
                  type="text"
                  placeholder="Ramesh Kumar"
                  className="form-control pl-9"
                />
              </div>
              {errors.full_name && (
                <p className="mt-1 text-[12px] text-[var(--color-error)]">{errors.full_name.message}</p>
              )}
            </div>

            <div className="md:col-span-2">
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
                  placeholder="Create password"
                  className="form-control pl-9"
                />
              </div>
              {errors.password && (
                <p className="mt-1 text-[12px] text-[var(--color-error)]">{errors.password.message}</p>
              )}
            </div>

            <div>
              <label className="form-label" htmlFor="confirm_password">
                Confirm password
              </label>
              <input
                {...register("confirm_password")}
                id="confirm_password"
                type="password"
                placeholder="Re-enter password"
                className="form-control"
              />
              {errors.confirm_password && (
                <p className="mt-1 text-[12px] text-[var(--color-error)]">{errors.confirm_password.message}</p>
              )}
            </div>

            <button type="submit" disabled={isSubmitting} className="btn-primary md:col-span-2">
              {isSubmitting ? "Creating account..." : "Create account"}
            </button>
          </form>

          <p className="mt-5 text-center text-[13px] text-[var(--color-text-secondary)]">
            Already registered?{" "}
            <Link href="/login" className="font-medium text-[var(--color-info)] hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}
