import Link from "next/link";
import { Bell, Search, ShieldCheck } from "lucide-react";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";

const navItems = [
  { href: "/", label: "Home" },
  { href: "/dashboard", label: "Farmer Services" },
  { href: "/dashboard/schemes", label: "Schemes" },
  { href: "/dashboard/market", label: "Market Prices" },
  { href: "/dashboard/weather", label: "Weather Advisory" },
  { href: "/admin", label: "Officer Login" },
];

export function GovHeader() {
  return (
    <header className="gov-header">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <div className="identity-bar">
        <div className="gov-container flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="tricolor-mark" aria-hidden="true" />
            <span>Government of India</span>
          </div>
          <div className="hidden items-center gap-4 sm:flex">
            <a href="#main-content" className="hover:underline">
              Skip
            </a>
            <span>Screen Reader Access</span>
            <span aria-label="Font size controls">-A A A+</span>
            <LanguageSwitcher />
          </div>
        </div>
      </div>

      <div className="main-gov-header">
        <div className="gov-container flex flex-col gap-4 py-4 md:flex-row md:items-center md:justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="emblem-mark" aria-hidden="true">
              <ShieldCheck size={24} />
            </div>
            <div>
              <p className="text-[12px] font-medium uppercase tracking-[0.04em] text-[var(--color-text-secondary)]">
                Ministry of Agriculture and Farmers Welfare
              </p>
              <div className="text-[20px] font-semibold leading-tight text-[var(--color-text-primary)]">
                Krishi Sahayak
              </div>
              <p className="font-devanagari text-[13px] text-[var(--color-text-secondary)]">
                किसान सेवा एवं कृषि परामर्श पोर्टल
              </p>
            </div>
          </Link>

          <div className="flex items-center gap-3">
            <label className="relative hidden sm:block">
              <span className="sr-only">Search services</span>
              <Search
                size={16}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)]"
              />
              <input
                className="h-9 w-56 rounded-md border border-[var(--color-border)] bg-white pl-9 pr-3 text-[13px] outline-none focus:border-[var(--color-primary-700)] focus:ring-2 focus:ring-green-100"
                placeholder="Search schemes, advisory"
              />
            </label>
            <button className="icon-button" aria-label="Notifications">
              <Bell size={18} />
            </button>
            <Link href="/login" className="btn-secondary btn-sm">
              Login
            </Link>
          </div>
        </div>
      </div>

      <nav className="gov-nav" aria-label="Primary navigation">
        <div className="gov-container flex gap-1 overflow-x-auto">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className="gov-nav-item">
              {item.label}
            </Link>
          ))}
        </div>
      </nav>
    </header>
  );
}
