import axios from 'axios';
import { getToken } from '../utils/auth';

const api = axios.create({
    baseURL: '/api/v1',
});

api.interceptors.request.use((config) => {
    const token = getToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const login = async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    const response = await api.post('/auth/token', formData);
    return response.data;
};

export const register = async (email, password) => {
    const response = await api.post('/auth/users', {
        email,
        password,
        is_active: true,
        is_superuser: false
    });
    return response.data;
};

export const getHoneypots = async () => {
    const response = await api.get('/honeypots/');
    return response.data;
};

export const getMetrics = async (type) => {
    const response = await api.get(`/metrics/${type}`);
    return response.data;
};

export default api;
