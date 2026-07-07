import Link from "next/link";
import {
  ArrowRight,
  BadgeIndianRupee,
  CloudSun,
  FileCheck2,
  Leaf,
  MessageSquareText,
  Microscope,
} from "lucide-react";
import { GovFooter } from "@/components/GovFooter";
import { GovHeader } from "@/components/GovHeader";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-white">
      <GovHeader />

      <section id="main-content" className="border-b border-[var(--color-border-light)] bg-[var(--color-bg-secondary)]">
        <div className="gov-container grid gap-8 py-10 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
          <div>
            <p className="mb-3 inline-flex rounded-full bg-[var(--color-accent-100)] px-3 py-1 text-[12px] font-medium uppercase tracking-[0.04em] text-[var(--color-accent-700)]">
              National farmer service platform
            </p>
            <h1 className="max-w-3xl text-[34px] font-bold leading-tight text-[var(--color-text-primary)] md:text-[42px]">
              Agriculture advisory and beneficiary support for Indian farmers
            </h1>
            <p className="mt-4 max-w-2xl text-[16px] leading-7 text-[var(--color-text-secondary)]">
              Access crop guidance, disease reporting, weather alerts, market prices, soil
              advisory, and scheme eligibility support through one official service window.
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Link href="/register" className="btn-primary h-11 px-6">
                Register Farmer <ArrowRight size={16} className="ml-2" />
              </Link>
              <Link href="/login" className="btn-secondary h-11 px-6">
                Sign in to Portal
              </Link>
            </div>
          </div>

          <div className="portal-card overflow-hidden">
            <div className="field-visual" aria-label="Illustration of agriculture service coverage">
              <div className="sun" />
              <div className="field-row row-one" />
              <div className="field-row row-two" />
              <div className="field-row row-three" />
              <div className="advisory-panel">
                <p className="text-[11px] font-semibold uppercase tracking-[0.04em] text-[var(--color-text-secondary)]">
                  Advisory status
                </p>
                <p className="mt-1 text-[20px] font-bold text-[var(--color-primary-900)]">
                  24x7
                </p>
                <p className="text-[12px] text-[var(--color-text-secondary)]">
                  Crop, weather, soil and scheme desk
                </p>
              </div>
            </div>
            <div className="grid grid-cols-3 border-t border-[var(--color-border-light)] bg-white text-center">
              {[
                ["8", "Languages"],
                ["6", "Core services"],
                ["24x7", "Advisory"],
              ].map(([value, label]) => (
                <div key={label} className="border-r border-[var(--color-border-light)] px-3 py-4 last:border-r-0">
                  <div className="text-[22px] font-bold text-[var(--color-primary-900)]">{value}</div>
                  <div className="text-[12px] font-medium uppercase tracking-[0.04em] text-[var(--color-text-secondary)]">
                    {label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="gov-container py-10">
        <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-[12px] font-semibold uppercase tracking-[0.05em] text-[var(--color-primary-800)]">
              Service discovery
            </p>
            <h2 className="section-title">Key farmer services</h2>
          </div>
          <Link href="/dashboard" className="text-[14px] font-medium text-[var(--color-info)] hover:underline">
            View farmer dashboard
          </Link>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature) => {
            const Icon = feature.icon;
            return (
              <Link
                key={feature.title}
                href={feature.href}
                className="portal-card group p-5 transition-colors hover:border-[var(--color-primary-700)]"
              >
                <div className="flex items-start gap-4">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-md bg-[var(--color-primary-50)] text-[var(--color-primary-800)]">
                    <Icon size={22} />
                  </div>
                  <div>
                    <h3 className="card-title group-hover:text-[var(--color-primary-800)]">
                      {feature.title}
                    </h3>
                    <p className="mt-1 text-[13px] leading-6 text-[var(--color-text-secondary)]">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      <section className="border-y border-[var(--color-border-light)] bg-[var(--color-bg-secondary)]">
        <div className="gov-container grid gap-6 py-10 lg:grid-cols-[0.8fr_1.2fr]">
          <div>
            <p className="text-[12px] font-semibold uppercase tracking-[0.05em] text-[var(--color-primary-800)]">
              Important updates
            </p>
            <h2 className="section-title">Farmer information desk</h2>
            <p className="mt-2 text-[14px] leading-6 text-[var(--color-text-secondary)]">
              Latest advisories and service notices are listed for quick access.
            </p>
          </div>
          <div className="portal-card divide-y divide-[var(--color-border-light)]">
            {UPDATES.map((item) => (
              <div key={item.title} className="grid gap-2 p-4 sm:grid-cols-[120px_1fr_auto] sm:items-center">
                <span className={item.badge === "Advisory" ? "badge-success" : "badge-warning"}>
                  {item.badge}
                </span>
                <div>
                  <h3 className="text-[14px] font-semibold text-[var(--color-text-primary)]">{item.title}</h3>
                  <p className="text-[13px] text-[var(--color-text-secondary)]">{item.body}</p>
                </div>
                <Link href={item.href} className="text-[13px] font-medium text-[var(--color-info)] hover:underline">
                  Open
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      <GovFooter />
    </main>
  );
}

const FEATURES = [
  {
    icon: MessageSquareText,
    href: "/dashboard/chat",
    title: "Crop Advisory Desk",
    description: "Seasonal sowing, irrigation, nutrient and harvest guidance based on farmer profile.",
  },
  {
    icon: Microscope,
    href: "/dashboard/disease",
    title: "Disease Reporting",
    description: "Submit crop images and receive structured diagnostic guidance and treatment steps.",
  },
  {
    icon: CloudSun,
    href: "/dashboard/weather",
    title: "Weather Alerts",
    description: "Weather-linked advisories for rainfall, heat, wind, and crop protection planning.",
  },
  {
    icon: BadgeIndianRupee,
    href: "/dashboard/market",
    title: "Mandi Price Intelligence",
    description: "Track market rates and compare nearby mandis before selling produce.",
  },
  {
    icon: FileCheck2,
    href: "/dashboard/schemes",
    title: "Scheme Eligibility",
    description: "Find relevant agriculture schemes, subsidies and application guidance.",
  },
  {
    icon: Leaf,
    href: "/dashboard/soil",
    title: "Soil Health Support",
    description: "Review soil parameters and receive nutrient recommendations for better productivity.",
  },
];

const UPDATES = [
  {
    badge: "Advisory",
    title: "Monsoon preparedness advisory",
    body: "Farmers are advised to review drainage, seed treatment and weather alerts.",
    href: "/dashboard/weather",
  },
  {
    badge: "Scheme",
    title: "Check agriculture scheme eligibility",
    body: "Beneficiary guidance is available for crop, equipment and soil support services.",
    href: "/dashboard/schemes",
  },
  {
    badge: "Advisory",
    title: "Mandi price review before sale",
    body: "Compare modal prices across markets before finalizing produce sale.",
    href: "/dashboard/market",
  },
];
