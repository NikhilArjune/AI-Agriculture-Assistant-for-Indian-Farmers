import Link from "next/link";

export function GovFooter() {
  return (
    <footer className="gov-footer">
      <div className="gov-container grid gap-8 py-8 md:grid-cols-[1.4fr_1fr_1fr]">
        <div>
          <h2 className="text-[16px] font-semibold">Krishi Sahayak</h2>
          <p className="mt-2 max-w-xl text-[13px] leading-6 text-white/80">
            Farmer advisory and agriculture service portal for crop guidance, weather alerts,
            mandi prices, soil support, disease reporting, and scheme discovery.
          </p>
        </div>
        <div>
          <h3 className="text-[13px] font-semibold uppercase tracking-[0.04em] text-white/90">
            Services
          </h3>
          <div className="mt-3 grid gap-2 text-[13px] text-white/80">
            <Link href="/dashboard/chat">Advisory Desk</Link>
            <Link href="/dashboard/schemes">Government Schemes</Link>
            <Link href="/dashboard/market">Market Intelligence</Link>
          </div>
        </div>
        <div>
          <h3 className="text-[13px] font-semibold uppercase tracking-[0.04em] text-white/90">
            Portal
          </h3>
          <div className="mt-3 grid gap-2 text-[13px] text-white/80">
            <Link href="/login">Farmer Login</Link>
            <Link href="/register">Register Farmer</Link>
            <Link href="/admin">Officer Dashboard</Link>
          </div>
        </div>
      </div>
      <div className="border-t border-white/15 py-3">
        <div className="gov-container flex flex-col gap-2 text-[12px] text-white/70 sm:flex-row sm:items-center sm:justify-between">
          <span>Content managed by Krishi Sahayak Agriculture Services Portal.</span>
          <span>Last reviewed: July 2026</span>
        </div>
      </div>
    </footer>
  );
}
