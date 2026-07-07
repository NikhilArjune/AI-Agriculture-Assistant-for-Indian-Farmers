"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, ExternalLink, Landmark, Search } from "lucide-react";
import toast from "react-hot-toast";
import { getApiErrorMessage, schemesApi } from "@/lib/api";

interface Scheme {
  scheme_id: string;
  scheme_name: string;
  ministry: string;
  benefits: string;
  eligibility_criteria: string;
  application_url: string;
  is_eligible?: boolean;
}

interface SchemeResult {
  schemes: Scheme[];
  advisory_text: string;
}

export default function SchemesPage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SchemeResult | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);

  const search = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await schemesApi.search({ query });
      setResult(res.data);
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Could not fetch schemes. Please try again."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-2xl">
        <div className="mb-6 flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-lg bg-primary-50 text-primary-700">
            <Landmark className="h-7 w-7" aria-hidden="true" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800">Government Schemes</h1>
            <p className="text-sm text-slate-500">Find subsidies and schemes you're eligible for</p>
          </div>
        </div>

        <div className="space-y-4 rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && search()}
            placeholder="e.g. crop insurance, organic farming, drip irrigation subsidy"
            className="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button
            onClick={search}
            disabled={loading}
            className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-primary-600 py-3 font-semibold text-white transition-colors hover:bg-primary-700 disabled:opacity-50"
          >
            <Search className="h-4 w-4" aria-hidden="true" />
            {loading ? "Searching..." : "Search Schemes"}
          </button>
        </div>

        {result && (
          <div className="mt-6 space-y-4">
            {result.advisory_text && (
              <div className="rounded-2xl border border-primary-100 bg-primary-50 p-5">
                <p className="text-sm text-primary-800">{result.advisory_text}</p>
              </div>
            )}

            {result.schemes.map((scheme) => (
              <div
                key={scheme.scheme_id}
                className="overflow-hidden rounded-2xl border border-slate-100 bg-white shadow-sm"
              >
                <button
                  type="button"
                  className="flex w-full cursor-pointer items-start justify-between p-5 text-left"
                  onClick={() => setExpanded(expanded === scheme.scheme_id ? null : scheme.scheme_id)}
                >
                  <span className="flex-1">
                    <span className="mb-1 flex items-center gap-2">
                      <span className="font-semibold text-slate-800">{scheme.scheme_name}</span>
                      {scheme.is_eligible !== undefined && (
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs ${
                            scheme.is_eligible
                              ? "bg-green-100 text-green-700"
                              : "bg-slate-100 text-slate-500"
                          }`}
                        >
                          {scheme.is_eligible ? "Eligible" : "Check criteria"}
                        </span>
                      )}
                    </span>
                    <span className="text-xs text-slate-400">{scheme.ministry}</span>
                  </span>
                  <span className="ml-4 text-slate-400">
                    {expanded === scheme.scheme_id ? (
                      <ChevronUp className="h-5 w-5" aria-hidden="true" />
                    ) : (
                      <ChevronDown className="h-5 w-5" aria-hidden="true" />
                    )}
                  </span>
                </button>

                {expanded === scheme.scheme_id && (
                  <div className="space-y-3 border-t border-slate-50 px-5 pb-5 pt-4">
                    <div>
                      <p className="mb-1 text-xs font-semibold uppercase text-slate-500">Benefits</p>
                      <p className="text-sm text-slate-700">{scheme.benefits}</p>
                    </div>
                    <div>
                      <p className="mb-1 text-xs font-semibold uppercase text-slate-500">Eligibility</p>
                      <p className="text-sm text-slate-700">{scheme.eligibility_criteria}</p>
                    </div>
                    {scheme.application_url && (
                      <a
                        href={scheme.application_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-sm font-medium text-primary-600 hover:underline"
                      >
                        Apply Online
                        <ExternalLink className="h-4 w-4" aria-hidden="true" />
                      </a>
                    )}
                  </div>
                )}
              </div>
            ))}

            {result.schemes.length === 0 && (
              <p className="py-8 text-center text-slate-400">No schemes found. Try a different search term.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
