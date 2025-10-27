import { apiClient } from './client';
import { Major } from './types';

export interface MajorsListResponse {
  majors: Major[];
  total: number;
}

export const majorsApi = {
  getMajors: async (params?: {
    active_only?: boolean;
    offset?: number;
    limit?: number;
  }): Promise<MajorsListResponse> => {
    const response = await apiClient.get<MajorsListResponse>('/majors', { params });
    return response.data;
  },

  getMajor: async (majorCode: string): Promise<Major> => {
    const response = await apiClient.get<Major>(`/majors/${majorCode}`);
    return response.data;
  },
};