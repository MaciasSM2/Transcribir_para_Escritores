/**
 * URL base del backend — se lee desde .env.local para facilitar despliegues.
 * En desarrollo: NEXT_PUBLIC_API_URL=http://localhost:8000
 */
export const API_BASE = process.env.NEXT_PUBLIC_API_URL 
  ? `${process.env.NEXT_PUBLIC_API_URL}/api/v1` 
  : 'http://localhost:8000/api/v1';

export const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${API_BASE}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  const response = await fetch(url, defaultOptions);
  
  if (response.status === 401) {
    console.error("🔒 Error de Autorización detectado. Revisa las dependencias del Backend.");
  }

  return response;
};
