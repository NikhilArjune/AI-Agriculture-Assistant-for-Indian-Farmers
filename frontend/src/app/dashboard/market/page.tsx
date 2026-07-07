"use client";

import { useState } from "react";
import { TrendingUp } from "lucide-react";
import toast from "react-hot-toast";
import { getApiErrorMessage, marketApi } from "@/lib/api";
import { INDIA_STATE_DISTRICTS, INDIA_STATES } from "@/lib/indiaLocations";

interface MarketResult {
  commodity: string;
  district: string;
  prices: {
    mandi_name: string;
    min_price: number;
    max_price: number;
    modal_price: number;
    unit: string;
    price_date: string;
    source_status?: string;
  }[];
  recommendation: string;
  trend: string;
  sources?: string[];
}

const COMMODITIES = [
  "wheat",
  "rice",
  "maize",
  "cotton",
  "mustard",
  "tomato",
  "onion",
  "potato",
  "soybean",
  "sugarcane",
];

export default function MarketPage() {
  const [commodity, setCommodity] = useState("");
  const [district, setDistrict] = useState("");
  const [state, setState] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MarketResult | null>(null);

  const districts = state ? INDIA_STATE_DISTRICTS[state] || [] : [];

  const search = async () => {
    if (!commodity || !district || !state) {
      toast.error("Please select commodity, state, and district.");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const res = await marketApi.getPrices({ commodity, district, state });
      setResult(res.data);
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Could not fetch market prices. Please try again."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-2xl">
        <div className="mb-6 flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-lg bg-primary-50 text-primary-700">
            <TrendingUp className="h-7 w-7" aria-hidden="true" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800">Market Prices</h1>
            <p className="text-sm text-slate-500">Real-time mandi prices with AI sell/hold advice</p>
          </div>
        </div>

        <div className="space-y-4 rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Commodity</label>
            <select
              value={commodity}
              onChange={(e) => setCommodity(e.target.value)}
              className="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Select commodity</option>
              {COMMODITIES.map((c) => (
                <option key={c} value={c}>
                  {c.charAt(0).toUpperCase() + c.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">State</label>
              <select
                value={state}
                onChange={(e) => {
                  setState(e.target.value);
                  setDistrict("");
                }}
                className="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select state</option>
                {INDIA_STATES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">District</label>
              <select
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                disabled={!state}
                className="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-slate-50 disabled:text-slate-400"
              >
                <option value="">{state ? "Select district" : "Select state first"}</option>
                {districts.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button
            onClick={search}
            disabled={loading}
            className="w-full rounded-xl bg-primary-600 py-3 font-semibold text-white transition-colors hover:bg-primary-700 disabled:opacity-50"
          >
            {loading ? "Fetching..." : "Get Prices"}
          </button>
        </div>

        {result && (
          <div className="mt-6 space-y-4">
            {result.prices.length === 0 && (
              <div className="rounded-2xl border border-amber-100 bg-amber-50 p-6 shadow-sm">
                <h2 className="mb-2 font-bold text-amber-900">No live mandi price rows found</h2>
                <p className="text-sm text-amber-800">
                  Source: {result.sources?.join(", ") || "unknown"}
                  {result.trend ? ` | Trend: ${result.trend}` : ""}
                </p>
                {result.recommendation && (
                  <p className="mt-3 whitespace-pre-wrap text-sm text-amber-900">{result.recommendation}</p>
                )}
              </div>
            )}

            {result.prices.length > 0 && (
              <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
                <h2 className="mb-4 font-bold text-slate-800">
                  {result.commodity.toUpperCase()} - {result.district} Mandis
                </h2>
                <div className="mb-4 rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-600">
                  Source: {result.sources?.join(", ") || result.prices[0]?.source_status || "unknown"}
                  {result.trend ? ` | Trend: ${result.trend}` : ""}
                </div>
                <div className="space-y-3">
                  {result.prices.map((p, i) => (
                    <div key={i} className="flex items-center justify-between border-b border-slate-50 py-3 last:border-0">
                      <div>
                        <p className="font-medium text-slate-700">{p.mandi_name}</p>
                        <p className="text-xs text-slate-400">
                          per {p.unit}
                          {p.price_date ? ` | ${p.price_date}` : ""}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-primary-700">Rs. {p.modal_price.toLocaleString()}</p>
                        <p className="text-xs text-slate-400">Rs. {p.min_price} - Rs. {p.max_price}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.prices.length > 0 && result.recommendation && (
              <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
                <h3 className="mb-2 font-semibold text-slate-700">AI Recommendation</h3>
                <p className="whitespace-pre-wrap text-sm text-slate-600">{result.recommendation}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
