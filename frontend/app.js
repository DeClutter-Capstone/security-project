// Shared frontend helpers for IEA.

// API base is same-origin (backend serves the frontend).
const API = "";

function getToken() {
  return sessionStorage.getItem("session_token");
}

function getUsername() {
  return sessionStorage.getItem("username");
}

function isAdmin() {
  return sessionStorage.getItem("is_admin") === "true";
}

function logoutLocal() {
  sessionStorage.clear();
  window.location.href = "index.html";
}

// fetch wrapper that injects the Authorization header and redirects to the
// login page on 401.
async function apiFetch(url, options = {}) {
  const opts = { ...options };
  opts.headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) {
    opts.headers["Authorization"] = "Bearer " + token;
  }
  const res = await fetch(API + url, opts);
  if (res.status === 401) {
    sessionStorage.clear();
    window.location.href = "index.html";
    throw new Error("Unauthorized");
  }
  return res;
}

// JSON helper.
async function apiJson(url, body, method = "POST") {
  const res = await apiFetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  return res;
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = "index.html";
  }
}
