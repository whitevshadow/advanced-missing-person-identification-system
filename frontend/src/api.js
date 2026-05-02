import axios from "axios";

const api = axios.create({
  // Use relative path so frontend and backend can be served from the same origin
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
});

const AUTH_TOKEN_KEY = "ampis_auth_token";

export function getStoredAuthToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
    return;
  }

  localStorage.removeItem(AUTH_TOKEN_KEY);
  delete api.defaults.headers.common.Authorization;
}

const existingToken = getStoredAuthToken();
if (existingToken) {
  setAuthToken(existingToken);
}

export async function fetchMissingPersons() {
  const response = await api.get("/missing-persons");
  return response.data;
}

export async function fetchMatches() {
  const response = await api.get("/sightings/matches");
  return response.data;
}

export async function fetchAlerts() {
  const response = await api.get("/sightings/alerts");
  return response.data;
}

export async function registerMissingPerson(payload) {
  const formData = new FormData();
  formData.append("name", payload.name);
  if (payload.heightCm) {
    formData.append("height_cm", payload.heightCm);
  }
  formData.append("physical_features", payload.physicalFeatures || "");
  formData.append("last_known_city", payload.lastKnownCity);
  formData.append("reporter_email", payload.reporterEmail);

  payload.images.forEach((image) => {
    formData.append("images", image);
  });

  const response = await api.post("/missing-persons", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function reportSighting(payload) {
  const formData = new FormData();
  formData.append("image", payload.image);
  formData.append("observed_features", payload.observedFeatures || "");
  formData.append("current_city", payload.currentCity);
  formData.append("description", payload.description || "");

  const response = await api.post("/sightings/report", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function submitFeedback(payload) {
  const response = await api.post("/feedback", payload);
  return response.data;
}

export async function registerUser(payload) {
  const response = await api.post("/auth/register", payload);
  return response.data;
}

export async function loginUser(payload) {
  const response = await api.post("/auth/login", payload);
  return response.data;
}

export async function fetchCurrentUser() {
  const response = await api.get("/auth/me");
  return response.data;
}
