import { apiClient } from './client';

export interface ProctoringEvent {
  event_type: string;
  proctoring_metadata?: any;
  timestamp?: string;
}

export interface ProctoringEventBatch {
  events: ProctoringEvent[];
}

export interface ProctoringEventResponse {
  created_count: number;
}

export const proctoringApi = {
  logEvents: async (attemptId: string, batch: ProctoringEventBatch): Promise<ProctoringEventResponse> => {
    const response = await apiClient.post<ProctoringEventResponse>(
      `/exam/${attemptId}/proctoring`,
      batch
    );
    return response.data;
  },
};