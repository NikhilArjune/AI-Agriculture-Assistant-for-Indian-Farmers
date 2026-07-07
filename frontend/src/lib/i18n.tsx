"use client";

import { createContext, useContext, useEffect, useState } from "react";

export const LANGUAGES = [
  { code: "en", label: "English", native: "English" },
  { code: "hi", label: "Hindi", native: "हिन्दी" },
  { code: "te", label: "Telugu", native: "తెలుగు" },
  { code: "ta", label: "Tamil", native: "தமிழ்" },
  { code: "mr", label: "Marathi", native: "मराठी" },
  { code: "pa", label: "Punjabi", native: "ਪੰਜਾਬੀ" },
  { code: "bn", label: "Bengali", native: "বাংলা" },
  { code: "kn", label: "Kannada", native: "ಕನ್ನಡ" },
] as const;

export type LangCode = (typeof LANGUAGES)[number]["code"];

const STORAGE_KEY = "preferred_lang";
type Dict = Record<string, unknown>;

interface I18nContextValue {
  lang: LangCode;
  setLang: (lang: LangCode) => void;
  t: (key: string) => string;
}

const I18nContext = createContext<I18nContextValue | null>(null);

// English is bundled so there is always a synchronous fallback.
let enDict: Dict | null = null;

function lookup(dict: Dict | null, key: string): string | undefined {
  if (!dict) return undefined;
  const value = key.split(".").reduce<unknown>((acc, part) => {
    if (acc && typeof acc === "object" && part in (acc as Dict)) {
      return (acc as Dict)[part];
    }
    return undefined;
  }, dict);
  return typeof value === "string" ? value : undefined;
}

async function loadDict(lang: LangCode): Promise<Dict> {
  try {
    const res = await fetch(`/locales/${lang}/common.json`, { cache: "force-cache" });
    if (!res.ok) return {};
    return (await res.json()) as Dict;
  } catch {
    return {};
  }
}

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<LangCode>("en");
  const [dict, setDict] = useState<Dict>({});

  // Restore saved language on mount.
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY) as LangCode | null;
    if (saved && LANGUAGES.some((l) => l.code === saved)) {
      setLangState(saved);
    }
  }, []);

  // Load the English fallback once, and the active dictionary on change.
  useEffect(() => {
    let active = true;
    (async () => {
      if (!enDict) enDict = await loadDict("en");
      const active_dict = lang === "en" ? enDict : await loadDict(lang);
      if (active) setDict(active_dict ?? {});
    })();
    return () => {
      active = false;
    };
  }, [lang]);

  const setLang = (next: LangCode) => {
    localStorage.setItem(STORAGE_KEY, next);
    setLangState(next);
    if (typeof document !== "undefined") document.documentElement.lang = next;
  };

  const t = (key: string): string => lookup(dict, key) ?? lookup(enDict, key) ?? key;

  return (
    <I18nContext.Provider value={{ lang, setLang, t }}>{children}</I18nContext.Provider>
  );
}

export function useI18n(): I18nContextValue {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}

/** Convenience hook returning just the translate function. */
export function useT(): (key: string) => string {
  return useI18n().t;
}
