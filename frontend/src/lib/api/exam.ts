import { apiClient } from './client';
import { ExamStartResponse, ExamStatus, ExamResult, Question } from './types';

export interface ExamStartRequest {
  major_code: string;
}

export interface SubmitAnswerRequest {
  question_id: string;
  selected_keys: string[];
}

export interface SubmitAnswerResponse {
  question_id: string;
  is_correct?: boolean;
  correct_keys?: string[];
  explanation?: string;
}

export const examApi = {
  startExam: async (data: ExamStartRequest): Promise<ExamStartResponse> => {
    const response = await apiClient.post<ExamStartResponse>('/exam/start', data);
    return response.data;
  },

  getExamStatus: async (attemptId: string): Promise<ExamStatus> => {
    const response = await apiClient.get<ExamStatus>(`/exam/${attemptId}`);
    return response.data;
  },

  getExamQuestions: async (attemptId: string): Promise<Question[]> => {
    const response = await apiClient.get<Question[]>(`/exam/${attemptId}/questions`);
    return response.data;
  },

  submitAnswer: async (
    attemptId: string,
    data: SubmitAnswerRequest
  ): Promise<SubmitAnswerResponse> => {
    const response = await apiClient.post<SubmitAnswerResponse>(
      `/exam/${attemptId}/answer`,
      data
    );
    return response.data;
  },

  finishExam: async (attemptId: string): Promise<ExamResult> => {
    const response = await apiClient.post<ExamResult>(`/exam/${attemptId}/submit`);
    return response.data;
  },
};