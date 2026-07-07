"use client";

import { useEffect, useRef, useState } from "react";
import { Globe, Check, ChevronDown } from "lucide-react";
import { LANGUAGES, useI18n } from "@/lib/i18n";

export function LanguageSwitcher() {
  const { lang, setLang } = useI18n();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const current = LANGUAGES.find((l) => l.code === lang) ?? LANGUAGES[0];

  // Close on outside click.
  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 text-sm text-slate-600 hover:text-primary-700 px-2 py-1.5 rounded-lg hover:bg-primary-50 transition-colors"
        aria-label="Change language"
      >
        <Globe size={16} />
        <span className="font-devanagari">{current.native}</span>
        <ChevronDown size={14} className={open ? "rotate-180 transition-transform" : "transition-transform"} />
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-44 bg-white rounded-xl shadow-lg border border-slate-100 py-1 z-50">
          {LANGUAGES.map((l) => (
            <button
              key={l.code}
              onClick={() => {
                setLang(l.code);
                setOpen(false);
              }}
              className="w-full flex items-center justify-between px-4 py-2 text-sm text-slate-700 hover:bg-primary-50 transition-colors"
            >
              <span>
                <span className="font-devanagari">{l.native}</span>
                <span className="text-slate-400 text-xs ml-2">{l.label}</span>
              </span>
              {l.code === lang && <Check size={15} className="text-primary-600" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
