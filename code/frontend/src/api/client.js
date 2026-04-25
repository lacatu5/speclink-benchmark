const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8001/api";

async function request(path, options = {}) {
  const token = localStorage.getItem("token");
  const headers = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { ...headers, ...options.headers },
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data;
}

export async function register(username, email, password) {
  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });
}

export async function login(username, password) {
  const data = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  localStorage.setItem("token", data.token);
  return data;
}

export async function createTask(title, description = "", priority = 1) {
  return request("/tasks", {
    method: "POST",
    body: JSON.stringify({ title, description, priority }),
  });
}

export async function listTasks(status = null) {
  const query = status ? `?status=${status}` : "";
  return request(`/tasks${query}`);
}

export async function updateTaskStatus(taskId, status) {
  return request(`/tasks/${taskId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export async function deleteTask(taskId) {
  return request(`/tasks/${taskId}`, { method: "DELETE" });
}

export async function getTaskStats() {
  return request("/tasks/stats");
}
