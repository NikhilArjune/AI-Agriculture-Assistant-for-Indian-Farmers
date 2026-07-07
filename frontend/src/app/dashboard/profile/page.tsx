"use client";

import { useEffect, useState } from "react";
import { UserRound } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import { farmerApi, getApiErrorMessage } from "@/lib/api";
import { INDIA_STATE_DISTRICTS, INDIA_STATES } from "@/lib/indiaLocations";

const schema = z.object({
  full_name: z.string().min(2),
  preferred_lang: z.enum(["en", "hi", "te", "ta", "mr", "pa", "bn", "kn"]),
  farm_size_acres: z.coerce.number().min(0),
  soil_type: z.string(),
  irrigation_type: z.enum(["drip", "flood", "rainfed", "sprinkler"]),
  state: z.string().min(1, "Select a state."),
  district: z.string().min(1, "Select a district."),
  village: z.string().optional(),
  primary_crops: z.string(),
});

type FormData = z.infer<typeof schema>;

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "Hindi" },
  { code: "te", label: "Telugu" },
  { code: "ta", label: "Tamil" },
  { code: "mr", label: "Marathi" },
  { code: "pa", label: "Punjabi" },
  { code: "bn", label: "Bengali" },
  { code: "kn", label: "Kannada" },
];

export default function ProfilePage() {
  const [isNew, setIsNew] = useState(true);
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { preferred_lang: "en", irrigation_type: "rainfed", state: "", district: "" },
  });

  const selectedState = watch("state");
  const districts = selectedState ? INDIA_STATE_DISTRICTS[selectedState] || [] : [];

  useEffect(() => {
    farmerApi
      .getProfile()
      .then((res) => {
        const p = res.data;
        reset({
          full_name: p.full_name,
          preferred_lang: p.preferred_lang,
          farm_size_acres: p.farm_size_acres,
          soil_type: p.soil_type,
          irrigation_type: p.irrigation_type,
          state: p.location?.state || "",
          district: p.location?.district || "",
          village: p.location?.village || "",
          primary_crops: (p.primary_crops || []).join(", "),
        });
        setIsNew(false);
      })
      .catch(() => setIsNew(true));
  }, [reset]);

  const onSubmit = async (data: FormData) => {
    const payload = {
      full_name: data.full_name,
      preferred_lang: data.preferred_lang,
      farm_size_acres: data.farm_size_acres,
      soil_type: data.soil_type,
      irrigation_type: data.irrigation_type,
      location: {
        state: data.state,
        district: data.district,
        village: data.village || "",
        coordinates: { lat: 0, lng: 0 },
      },
      primary_crops: data.primary_crops.split(",").map((c) => c.trim()).filter(Boolean),
    };

    try {
      if (isNew) {
        await farmerApi.createProfile(payload);
        setIsNew(false);
        toast.success("Profile created!");
      } else {
        await farmerApi.updateProfile(payload);
        toast.success("Profile updated!");
      }
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Failed to save profile."));
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-2xl">
        <div className="mb-6 flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-lg bg-primary-50 text-primary-700">
            <UserRound className="h-7 w-7" aria-hidden="true" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800">Farmer Profile</h1>
            <p className="text-sm text-slate-500">Your profile helps the AI give personalized advice</p>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5 rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Full Name</label>
            <input {...register("full_name")} className="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            {errors.full_name && <p className="mt-1 text-xs text-red-500">{errors.full_name.message}</p>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Preferred Language</label>
            <select {...register("preferred_lang")} className="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
              {LANGUAGES.map((language) => (
                <option key={language.code} value={language.code}>
                  {language.label}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">State</label>
              <select
                {...register("state")}
                onChange={(event) => {
                  setValue("state", event.target.value, { shouldValidate: true });
                  setValue("district", "", { shouldValidate: true });
                }}
                className="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select state</option>
                {INDIA_STATES.map((state) => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </select>
              {errors.state && <p className="mt-1 text-xs text-red-500">{errors.state.message}</p>}
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">District</label>
              <select
                {...register("district")}
                disabled={!selectedState}
                className="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-slate-50 disabled:text-slate-400"
              >
                <option value="">{selectedState ? "Select district" : "Select state first"}</option>
                {districts.map((district) => (
                  <option key={district} value={district}>
                    {district}
                  </option>
                ))}
              </select>
              {errors.district && <p className="mt-1 text-xs text-red-500">{errors.district.message}</p>}
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Village</label>
            <input {...register("village")} placeholder="e.g. Khanna" className="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Farm Size (acres)</label>
              <input {...register("farm_size_acres")} type="number" step="0.1" placeholder="3.5" className="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Soil Type</label>
              <input {...register("soil_type")} placeholder="loamy, clay, sandy..." className="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Irrigation Type</label>
            <select {...register("irrigation_type")} className="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
              <option value="rainfed">Rainfed</option>
              <option value="drip">Drip</option>
              <option value="flood">Flood</option>
              <option value="sprinkler">Sprinkler</option>
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Primary Crops (comma-separated)</label>
            <input {...register("primary_crops")} placeholder="wheat, rice, maize" className="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-xl bg-primary-600 py-3 font-semibold text-white transition-colors hover:bg-primary-700 disabled:opacity-50"
          >
            {isSubmitting ? "Saving..." : isNew ? "Create Profile" : "Update Profile"}
          </button>
        </form>
      </div>
    </div>
  );
}
