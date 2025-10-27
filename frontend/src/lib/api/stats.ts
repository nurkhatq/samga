import { apiClient } from './client';
import { UserStatisticsResponse } from './types';

export const statsApi = {
  getUserStats: async (): Promise<UserStatisticsResponse> => {
    const response = await apiClient.get<UserStatisticsResponse>('/stats/my');
    return response.data;
  },
};