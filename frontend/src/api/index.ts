import { apiClient } from './client';
import type { 
  School, 
  Student, 
  Rule, 
  Assignment, 
  AssignmentRequest,
  AssignmentDetail 
} from '../types';

// 학교 API
export const schoolApi = {
  getAll: () => apiClient.get<School[]>('/api/schools/'),
  getById: (id: number) => apiClient.get<School>(`/api/schools/${id}`),
  create: (data: Partial<School>) => apiClient.post<School>('/api/schools/', data),
  update: (id: number, data: Partial<School>) => 
    apiClient.put<School>(`/api/schools/${id}`, data),
};

// 학생 API
export const studentApi = {
  getAll: (schoolId: number, grade?: number) => {
    const params = grade ? { school_id: schoolId, grade } : { school_id: schoolId };
    return apiClient.get<Student[]>('/api/students/', { params });
  },
  getById: (id: number) => apiClient.get<Student>(`/api/students/${id}`),
  create: (data: Partial<Student>) => apiClient.post<Student>('/api/students/', data),
  update: (id: number, data: Partial<Student>) => 
    apiClient.put<Student>(`/api/students/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/students/${id}`),
  uploadExcel: (schoolId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/api/students/upload-excel', formData, {
      params: { school_id: schoolId },
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// 규칙 API
export const ruleApi = {
  getAll: (schoolId: number) => 
    apiClient.get<Rule[]>('/api/rules/', { params: { school_id: schoolId } }),
  getExamples: () => apiClient.get('/api/rules/examples'),
  create: (data: Partial<Rule>) => apiClient.post<Rule>('/api/rules/', data),
  update: (id: number, data: Partial<Rule>) => 
    apiClient.put<Rule>(`/api/rules/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/rules/${id}`),
  toggle: (id: number) => apiClient.patch(`/api/rules/${id}/toggle`),
};

// 반편성 API
export const assignmentApi = {
  getAll: (schoolId: number) => 
    apiClient.get<Assignment[]>('/api/assignments/', { params: { school_id: schoolId } }),
  getById: (id: number) => apiClient.get<AssignmentDetail>(`/api/assignments/${id}`),
  generate: (data: AssignmentRequest) => 
    apiClient.post('/api/assignments/generate', data),
  delete: (id: number) => apiClient.delete(`/api/assignments/${id}`),
};

// 샘플 데이터 API
export const sampleApi = {
  downloadExcel: () => {
    return apiClient.get('/api/sample/generate-sample-excel', {
      responseType: 'blob',
    });
  },
  loadSampleData: (schoolId: number) =>
    apiClient.post(`/api/sample/load-sample-data/${schoolId}`),
  createSampleRules: (schoolId: number) =>
    apiClient.post(`/api/sample/create-sample-rules/${schoolId}`),
};

// 헬스 체크
export const healthCheck = () => apiClient.get('/health');

