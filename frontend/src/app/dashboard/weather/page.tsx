"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import { getApiErrorMessage, weatherApi } from "@/lib/api";

interface WeatherResult {
  advisory_text: string;
  temperature_c: number;
  humidity_percent: number;
  rainfall_mm: number;
  wind_speed_kmh: number;
  severity: string;
}

export default function WeatherPage() {
  const [lat, setLat] = useState("");
  const [lng, setLng] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<WeatherResult | null>(null);
  const [locating, setLocating] = useState(false);

  const useMyLocation = () => {
    if (!navigator.geolocation) {
      toast.error("Geolocation not supported by your browser.");
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLat(pos.coords.latitude.toFixed(5));
        setLng(pos.coords.longitude.toFixed(5));
        setLocating(false);
      },
      () => {
        toast.error("Could not get location. Please enter manually.");
        setLocating(false);
      }
    );
  };

  const getAdvisory = async () => {
    if (!lat || !lng) {
      toast.error("Please provide your location coordinates.");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const res = await weatherApi.advisory({
        lat: parseFloat(lat),
        lng: parseFloat(lng),
      });
      setResult(res.data);
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Could not fetch weather data. Please try again."));
    } finally {
      setLoading(false);
    }
  };

  const severityColor = (s: string) => {
    const map: Record<string, string> = {
      low: "bg-green-50 text-green-700 border-green-200",
      medium: "bg-yellow-50 text-yellow-700 border-yellow-200",
      high: "bg-orange-50 text-orange-700 border-orange-200",
      critical: "bg-red-50 text-red-700 border-red-200",
    };
    return map[s] || map.low;
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <span className="text-3xl">🌦️</span>
          <div>
            <h1 className="text-2xl font-bold text-slate-800">Weather Advisory</h1>
            <p className="text-slate-500 text-sm">Hyperlocal forecasts with farming guidance</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 space-y-4">
          <button
            onClick={useMyLocation}
            disabled={locating}
            className="w-full border border-primary-300 text-primary-600 py-3 rounded-xl font-medium hover:bg-primary-50 transition-colors text-sm"
          >
            {locating ? "Detecting location..." : "📍 Use My Current Location"}
          </button>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200" />
            </div>
            <div className="relative flex justify-center">
              <span className="bg-white px-3 text-xs text-slate-400">OR ENTER MANUALLY</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Latitude</label>
              <input
                value={lat}
                onChange={(e) => setLat(e.target.value)}
                placeholder="30.9010"
                className="w-full border border-slate-200 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Longitude</label>
              <input
                value={lng}
                onChange={(e) => setLng(e.target.value)}
                placeholder="75.8573"
                className="w-full border border-slate-200 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <button
            onClick={getAdvisory}
            disabled={loading}
            className="w-full bg-primary-600 text-white py-3 rounded-xl font-semibold hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            {loading ? "Fetching..." : "Get Weather Advisory"}
          </button>
        </div>

        {result && (
          <div className="mt-6 space-y-4">
            <div className={`rounded-2xl p-4 border ${severityColor(result.severity)}`}>
              Alert level: <span className="font-semibold capitalize">{result.severity}</span>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {[
                { label: "Temperature", value: `${result.temperature_c}°C`, icon: "🌡️" },
                { label: "Humidity", value: `${result.humidity_percent}%`, icon: "💧" },
                { label: "Rainfall", value: `${result.rainfall_mm} mm`, icon: "🌧️" },
                { label: "Wind Speed", value: `${result.wind_speed_kmh} km/h`, icon: "💨" },
              ].map((stat) => (
                <div key={stat.label} className="bg-white rounded-xl p-4 shadow-sm border border-slate-100">
                  <div className="text-2xl mb-1">{stat.icon}</div>
                  <div className="text-lg font-bold text-slate-800">{stat.value}</div>
                  <div className="text-xs text-slate-400">{stat.label}</div>
                </div>
              ))}
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
              <h3 className="font-semibold text-slate-700 mb-3">Farming Advisory</h3>
              <p className="text-slate-600 text-sm whitespace-pre-wrap">{result.advisory_text}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
