const API_BASE_URL = 'http://localhost:8002';

export const api = {
  async getStatus() {
    const response = await fetch(`${API_BASE_URL}/status`);
    return response.json();
  },

  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    return response.json();
  },

  async startAutomation(config) {
    const response = await fetch(`${API_BASE_URL}/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
    return response.json();
  },

  async stopAutomation() {
    const response = await fetch(`${API_BASE_URL}/stop`, {
      method: 'POST'
    });
    return response.json();
  },

  async getActivities(limit = 50) {
    const response = await fetch(`${API_BASE_URL}/activities?limit=${limit}`);
    return response.json();
  },

  async clearActivities() {
    const response = await fetch(`${API_BASE_URL}/activities`, {
      method: 'DELETE'
    });
    return response.json();
  }
};
