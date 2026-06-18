import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

// Transactions
export const scoreTransaction = (data: any) =>
  api.post('/api/transactions/score', data);

export const getRecentTransactions = (limit = 50) =>
  api.get(`/api/transactions/recent?limit=${limit}`);

export const getTransaction = (id: string) =>
  api.get(`/api/transactions/${id}`);

// Cases
export const getOpenCases = () =>
  api.get('/api/cases/open');

export const createCase = (transactionId: string) =>
  api.post(`/api/cases/create/${transactionId}`);

export const approveCase = (caseId: string, notes = '') =>
  api.post(`/api/cases/${caseId}/approve`, { analyst_notes: notes });

export const blockCase = (caseId: string, notes = '') =>
  api.post(`/api/cases/${caseId}/block`, { analyst_notes: notes });