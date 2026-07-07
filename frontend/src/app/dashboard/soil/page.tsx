"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import { getApiErrorMessage, soilApi } from "@/lib/api";

interface SoilResult {
  advisory_text: string;
  fertilizer_plan: string;
  deficiencies: string[];
  recommendations: string[];
  requires_human_help: boolean;
}

const SOIL_TYPES = ["loamy", "clay", "sandy", "silt", "clayey loam", "black cotton", "red laterite", "alluvial"];
const CROPS = ["wheat", "rice", "maize", "cotton", "mustard", "tomato", "sugarcane", "soybean", "groundnut"];

export default function SoilPage() {
  const [cropName, setCropName] = useState("");
  const [soilType, setSoilType] = useState("");
  const [ph, setPh] = useState("");
  const [nitrogen, setNitrogen] = useState("");
  const [phosphorus, setPhosphorus] = useState("");
  const [potassium, setPotassium] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SoilResult | null>(null);

  const getAdvisory = async () => {
    if (!cropName) {
      toast.error("Please select a crop.");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const res = await soilApi.advisory({
        crop_name: cropName,
        soil_type: soilType,
        ph_level: ph ? parseFloat(ph) : null,
        nitrogen: nitrogen ? parseFloat(nitrogen) : null,
        phosphorus: phosphorus ? parseFloat(phosphorus) : null,
        potassium: potassium ? parseFloat(potassium) : null,
      });
      setResult(res.data);
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Could not get soil advisory. Please try again."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <span className="text-3xl">🌱</span>
          <div>
            <h1 className="text-2xl font-bold text-slate-800">Soil Advisory</h1>
            <p className="text-slate-500 text-sm">Fertilizer plans based on your soil health data</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Crop *</label>
              <select
                value={cropName}
                onChange={(e) => setCropName(e.target.value)}
                className="w-full border border-slate-200 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select crop</option>
                {CROPS.map((c) => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Soil Type</label>
              <select
                value={soilType}
                onChange={(e) => setSoilType(e.target.value)}
                className="w-full border border-slate-200 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select type</option>
                {SOIL_TYPES.map((s) => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
              </select>
            </div>
          </div>

          <div>
            <p className="text-sm font-medium text-slate-700 mb-2">Soil Test Results (optional — from Soil Health Card)</p>
            <div className="grid grid-cols-2 gap-4">
              {[
                { label: "pH Level", value: ph, set: setPh, placeholder: "6.5" },
                { label: "Nitrogen (kg/ha)", value: nitrogen, set: setNitrogen, placeholder: "120" },
                { label: "Phosphorus (kg/ha)", value: phosphorus, set: setPhosphorus, placeholder: "30" },
                { label: "Potassium (kg/ha)", value: potassium, set: setPotassium, placeholder: "200" },
              ].map((field) => (
                <div key={field.label}>
                  <label className="block text-xs text-slate-500 mb-1">{field.label}</label>
                  <input
                    type="number"
                    step="0.1"
                    value={field.value}
                    onChange={(e) => field.set(e.target.value)}
                    placeholder={field.placeholder}
                    className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={getAdvisory}
            disabled={loading}
            className="w-full bg-primary-600 text-white py-3 rounded-xl font-semibold hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            {loading ? "Analyzing..." : "Get Soil Advisory"}
          </button>
        </div>

        {result && (
          <div className="mt-6 space-y-4">
            {result.deficiencies.length > 0 && (
              <div className="bg-red-50 border border-red-100 rounded-2xl p-5">
                <h3 className="font-semibold text-red-700 mb-2">Deficiencies Detected</h3>
                <div className="flex flex-wrap gap-2">
                  {result.deficiencies.map((d) => (
                    <span key={d} className="bg-red-100 text-red-700 text-xs px-3 py-1 rounded-full capitalize">{d}</span>
                  ))}
                </div>
              </div>
            )}

            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
              <h3 className="font-semibold text-slate-700 mb-3">Advisory</h3>
              <p className="text-slate-600 text-sm whitespace-pre-wrap">{result.advisory_text}</p>
            </div>

            {result.fertilizer_plan && (
              <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
                <h3 className="font-semibold text-slate-700 mb-3">Fertilizer Plan</h3>
                <p className="text-slate-600 text-sm whitespace-pre-wrap">{result.fertilizer_plan}</p>
              </div>
            )}

            {result.requires_human_help && (
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800">
                For precise recommendations, get a certified soil test from your nearest KVK or agricultural lab.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
