import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken =
        typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null;
      const originalRequest = error.config;
      const isRefreshRequest = originalRequest?.url?.includes("/api/v1/auth/refresh");

      if (refreshToken && !isRefreshRequest && !originalRequest?._retry) {
        try {
          originalRequest._retry = true;
          const res = await axios.post(
            `${API_BASE_URL}/api/v1/auth/refresh`,
            { refresh_token: refreshToken }
          );
          const { access_token, refresh_token } = res.data;
          localStorage.setItem("access_token", access_token);
          localStorage.setItem("refresh_token", refresh_token);
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api.request(originalRequest);
        } catch {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          if (typeof window !== "undefined") window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

export function getApiErrorMessage(error: unknown, fallback = "Request failed. Please try again.") {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return `Cannot connect to backend at ${API_BASE_URL}. Please make sure the backend server is running.`;
    }
    const detail = error.response.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map((item) => item.msg || String(item)).join(", ");
  }
  return fallback;
}

// Auth
export const authApi = {
  register: (data: { phone: string; password: string; full_name: string }) =>
    api.post("/api/v1/auth/register", data),
  login: (data: { phone: string; password: string }) =>
    api.post("/api/v1/auth/login", data),
  logout: () => api.post("/api/v1/auth/logout"),
  me: () => api.get("/api/v1/auth/me"),
  refresh: (refreshToken: string) =>
    api.post("/api/v1/auth/refresh", { refresh_token: refreshToken }),
};

// Chat
export const chatApi = {
  send: (data: { query: string; session_id?: string; language?: string; image_base64?: string }) =>
    api.post("/api/v1/chat/", data),
  history: (sessionId: string) => api.get(`/api/v1/chat/history/${sessionId}`),
};

// Farmer profile
export const farmerApi = {
  getProfile: () => api.get("/api/v1/farmers/profile"),
  createProfile: (data: object) => api.post("/api/v1/farmers/profile", data),
  updateProfile: (data: object) => api.patch("/api/v1/farmers/profile", data),
};

// Disease
export const diseaseApi = {
  detect: (data: { image_base64: string; crop_name?: string; session_id?: string; language?: string }) =>
    api.post("/api/v1/disease/detect", data),
};

// Market
export const marketApi = {
  getPrices: (data: { commodity: string; district: string; state: string }) =>
    api.post("/api/v1/market/prices", data),
};

// Weather
export const weatherApi = {
  advisory: (data: { lat: number; lng: number; session_id?: string }) =>
    api.post("/api/v1/weather/advisory", data),
};

// Schemes
export const schemesApi = {
  search: (data: { query?: string; state?: string; crop?: string; session_id?: string }) =>
    api.post("/api/v1/schemes/search", data),
};

// Soil
export const soilApi = {
  advisory: (data: {
    crop_name: string;
    soil_type?: string;
    ph_level?: number | null;
    nitrogen?: number | null;
    phosphorus?: number | null;
    potassium?: number | null;
    session_id?: string;
  }) => api.post("/api/v1/soil/advisory", data),
};

// Crops
export const cropsApi = {
  calendar: (cropName: string) => api.get(`/api/v1/crops/calendar/${cropName}`),
  advisory: (data: { crop_name: string; query?: string; session_id?: string }) =>
    api.post("/api/v1/crops/advisory", data),
};

// Notifications
export const notificationApi = {
  list: (limit = 20, offset = 0) =>
    api.get("/api/v1/notifications/", { params: { limit, offset } }),
  markRead: (id: string) => api.patch(`/api/v1/notifications/${id}/read`),
};

// Admin
export const adminApi = {
  stats: () => api.get("/api/v1/admin/stats"),
  listUsers: (limit = 50, offset = 0) =>
    api.get("/api/v1/admin/users", { params: { limit, offset } }),
  deactivateUser: (id: string) =>
    api.patch(`/api/v1/admin/users/${id}/deactivate`),
};
