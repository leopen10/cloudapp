import axios from 'axios';

const API = axios.create({ baseURL: 'http://localhost:8000' });

API.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const login = (data) => API.post('/auth/login', data);
export const register = (data) => API.post('/auth/register', data);
export const getClients = () => API.get('/clients');
export const createClient = (data) => API.post('/clients', data);
export const getProjects = () => API.get('/projects');
export const getProject = (id) => API.get(`/projects/${id}`);
export const createProject = (data) => API.post('/projects', data);
export const updateProject = (id, data) => API.put(`/projects/${id}`, data);
export const deleteProject = (id) => API.delete(`/projects/${id}`);
export const getInvoices = () => API.get('/invoices');
export const getInvoicesByProject = (id) => API.get(`/invoices/project/${id}`);
export const payInvoice = (id) => API.post(`/invoices/${id}/pay`, {});
export const getNotifications = () => API.get('/notifications');
export const markRead = (id) => API.put(`/notifications/${id}/read`);