import { apiClient } from './client';
import { ExamStartResponse, Question, SubmitAnswerResponse, SubmitAnswerRequest } from './types';

export interface PracticeStartRequest {
  subject_code: string;
}

export interface GetQuestionsResponse {
  questions: Question[];
  total: number;
  offset: number;
  limit: number;
  has_more: boolean;
}

export const practiceApi = {
  startPractice: async (data: PracticeStartRequest): Promise<ExamStartResponse> => {
    const response = await apiClient.post<ExamStartResponse>('/practice/start', data);
    return response.data;
  },

  getQuestions: async (
    subjectCode: string,
    offset: number = 0,
    limit: number = 20
  ): Promise<GetQuestionsResponse> => {
    const response = await apiClient.get<GetQuestionsResponse>(
      `/practice/${subjectCode}/questions`,
      { params: { offset, limit } }
    );
    return response.data;
  },

  submitAnswer: async (
    subjectCode: string,
    data: SubmitAnswerRequest
  ): Promise<SubmitAnswerResponse> => {
    const response = await apiClient.post<SubmitAnswerResponse>(
      `/practice/${subjectCode}/submit-answer`,
      data
    );
    return response.data;
  },

  getStats: async (subjectCode: string) => {
    const response = await apiClient.get(`/practice/${subjectCode}/stats`);
    return response.data;
  },

  finishPractice: async (subjectCode: string) => {
    const response = await apiClient.post(`/practice/${subjectCode}/finish`);
    return response.data;
  },
};