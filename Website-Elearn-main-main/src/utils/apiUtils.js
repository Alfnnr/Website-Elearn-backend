// utils/apiUtils.js
const API_BASE_URL = 'http://localhost:8000';

// Helper untuk membuat request dengan token
export const apiRequest = async (endpoint, options = {}) => {
  const token = localStorage.getItem('token');
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    
    // Jika token expired atau invalid, redirect ke login
    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      throw new Error('Session expired');
    }

    // Jika response tidak OK, throw error dengan detail
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response;
  } catch (error) {
    console.error('API Request Error:', error);
    throw error;
  }
};

// Helper khusus untuk GET request
export const apiGet = async (endpoint) => {
  const response = await apiRequest(endpoint, { method: 'GET' });
  return response.json();
};

// Helper khusus untuk POST request
export const apiPost = async (endpoint, data) => {
  const response = await apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return response.json();
};

// Helper khusus untuk PUT request
export const apiPut = async (endpoint, data) => {
  const response = await apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
  return response.json();
};

// Helper khusus untuk DELETE request
export const apiDelete = async (endpoint) => {
  const response = await apiRequest(endpoint, { method: 'DELETE' });
  return response.json();
};

// Helper khusus untuk upload file (FormData)
export const apiUpload = async (endpoint, formData, method = 'POST') => {
  const token = localStorage.getItem('token');
  
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  // JANGAN set Content-Type untuk FormData, browser akan set otomatis dengan boundary

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method,
      headers,
      body: formData,
    });

    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      throw new Error('Session expired');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('API Upload Error:', error);
    throw error;
  }
};

// Export API_BASE_URL jika dibutuhkan
export { API_BASE_URL };