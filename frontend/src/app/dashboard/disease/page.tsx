"use client";

import { useState, useRef } from "react";
import toast from "react-hot-toast";
import { diseaseApi } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";

interface DetectionResult {
  detected_plant: string;
  detected_disease: string;
  confidence: number;
  treatment_plan: string;
  prevention_tips: string;
  sources: string[];
  requires_human_help: boolean;
}

export default function DiseasePage() {
  const { lang, t } = useI18n();
  const [image, setImage] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [cropName, setCropName] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const b64 = (reader.result as string).split(",")[1];
      setImage(b64);
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const detect = async () => {
    if (!image) {
      toast.error("Please upload a crop photo first.");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const res = await diseaseApi.detect({
        image_base64: image,
        crop_name: cropName || undefined,
        language: lang,
      });
      setResult(res.data);
    } catch {
      toast.error("Detection failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const plant = result?.detected_plant?.trim();
  const showPlant = plant && plant.toLowerCase() !== "unknown";

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between gap-3 mb-6">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🔬</span>
            <div>
              <h1 className="text-2xl font-bold text-slate-800">{t("disease.title")}</h1>
              <p className="text-slate-500 text-sm">{t("disease.subtitle")}</p>
            </div>
          </div>
          <LanguageSwitcher />
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 space-y-5">
          <div
            onClick={() => inputRef.current?.click()}
            className="border-2 border-dashed border-primary-200 rounded-xl p-8 text-center cursor-pointer hover:border-primary-400 transition-colors"
          >
            {preview ? (
              <img src={preview} alt="Crop" className="max-h-48 mx-auto rounded-lg object-cover" />
            ) : (
              <>
                <div className="text-5xl mb-3">📷</div>
                <p className="text-slate-500">{t("disease.upload")}</p>
                <p className="text-slate-400 text-xs mt-1">JPG, PNG up to 10MB</p>
              </>
            )}
          </div>
          <input ref={inputRef} type="file" accept="image/*" className="hidden" onChange={handleFileChange} />

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">{t("disease.crop_name")}</label>
            <input
              value={cropName}
              onChange={(e) => setCropName(e.target.value)}
              placeholder="e.g. wheat, rice, tomato"
              className="w-full border border-slate-200 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <button
            onClick={detect}
            disabled={loading || !image}
            className="w-full bg-primary-600 text-white py-3 rounded-xl font-semibold hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            {loading ? t("disease.detecting") : t("disease.detect")}
          </button>
        </div>

        {result && (
          <div className="mt-6 bg-white rounded-2xl p-6 shadow-sm border border-slate-100 space-y-4">
            {showPlant && (
              <div className="flex items-center gap-2">
                <span className="text-xl">🌱</span>
                <span className="text-sm text-slate-500">{t("disease.identified")}:</span>
                <span className="text-sm font-semibold text-slate-800 capitalize">{plant}</span>
              </div>
            )}

            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-800 capitalize">{result.detected_disease}</h2>
              <span
                className={`text-sm px-3 py-1 rounded-full font-medium ${
                  result.confidence > 0.7 ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
                }`}
              >
                {(result.confidence * 100).toFixed(0)}% confidence
              </span>
            </div>

            <div>
              <h3 className="font-semibold text-slate-700 mb-2">{t("disease.treatment")}</h3>
              <p className="text-slate-600 text-sm whitespace-pre-wrap">{result.treatment_plan}</p>
            </div>

            {result.prevention_tips && (
              <div>
                <h3 className="font-semibold text-slate-700 mb-2">{t("disease.prevention")}</h3>
                <p className="text-slate-600 text-sm">{result.prevention_tips}</p>
              </div>
            )}

            {result.requires_human_help && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-800">
                {t("disease.kvk_hint")}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
