import { apiClient } from './client';
import { Subject } from './types';

export interface SubjectsListResponse {
  subjects: Subject[];
  total: number;
}

export const subjectsApi = {
  getSubjects: async (params?: {
    subject_type?: string;
    major_code?: string;
    active_only?: boolean;
  }): Promise<SubjectsListResponse> => {
    const response = await apiClient.get<SubjectsListResponse>('/subjects', { params });
    return response.data;
  },

  getSubject: async (subjectCode: string): Promise<Subject> => {
    const response = await apiClient.get<Subject>(`/subjects/${subjectCode}`);
    return response.data;
  },
};