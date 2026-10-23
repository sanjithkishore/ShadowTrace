const API_URL = "http://127.0.0.1:8000";

export async function searchBugs(query, language) {
  const response = await fetch(`${API_URL}/api/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query,
      language,
      limit: 5,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Unable to search for bugs.");
  }

  return response.json();
}

// Check whether the backend is running
export async function checkBackendHealth() {
  const response = await fetch(`${API_URL}/health`);

  if (!response.ok) {
    throw new Error("Backend is unavailable");
  }

  return response.json();
}

