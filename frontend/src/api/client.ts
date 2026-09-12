import axios from 'axios';

const API_BASE = (process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

export const scoreTransaction = (data: unknown) =>
  api.post('/api/transactions/score', data);

export const getRecentTransactions = (_limit = 50) =>
  api.get('/api/transactions/recent');

export const getTransaction = (id: string) =>
  api.get(`/api/transactions/${encodeURIComponent(id)}`);

export const getOpenCases = () =>
  api.get('/api/cases/open');

export const createCase = (transactionId: string) =>
  api.post(`/api/cases/create/${encodeURIComponent(transactionId)}`);

export const approveCase = (caseId: string, notes = '') =>
  api.post(`/api/cases/${encodeURIComponent(caseId)}/approve`, { analyst_notes: notes });

export const blockCase = (caseId: string, notes = '') =>
  api.post(`/api/cases/${encodeURIComponent(caseId)}/block`, { analyst_notes: notes });

export const getMonitoringSummary = () =>
  api.get('/api/monitoring');

export const getModelHealth = () =>
  api.get('/api/models/health');

export const getSystemHealth = () =>
  api.get('/health');
