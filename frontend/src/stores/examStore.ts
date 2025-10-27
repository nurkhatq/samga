import { create } from 'zustand';
import { examApi } from '@/lib/api/exam';
import { ExamStatus, Question, ExamResult, ExamStatusEnum } from '@/lib/api/types';

interface ExamState {
  currentExam: ExamStatus | null;
  questions: Question[];
  currentQuestionIndex: number;
  answers: Map<string, string[]>;
  isLoading: boolean;
  error: string | null;

  startExam: (majorCode: string) => Promise<string>;
  loadQuestions: (attemptId: string) => Promise<void>;
  submitAnswer: (questionId: string, selectedKeys: string[]) => Promise<void>;
  finishExam: (attemptId: string) => Promise<ExamResult>;
  setCurrentQuestion: (index: number) => void;
  clearExam: () => void;
}

export const useExamStore = create<ExamState>((set, get) => ({
  currentExam: null,
  questions: [],
  currentQuestionIndex: 0,
  answers: new Map(),
  isLoading: false,
  error: null,

  startExam: async (majorCode: string) => {
    set({ isLoading: true, error: null });
    try {
      const exam = await examApi.startExam({ major_code: majorCode });
      set({
        currentExam: {
          ...exam,
          status: ExamStatusEnum.IN_PROGRESS,
          answered_questions: 0,
          current_question_index: 0,
        },
        isLoading: false,
      });
      return exam.attempt_id;
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  loadQuestions: async (attemptId: string) => {
    set({ isLoading: true });
    try {
      const questions = await examApi.getExamQuestions(attemptId);
      set({ questions, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  submitAnswer: async (questionId: string, selectedKeys: string[]) => {
    const { currentExam, answers } = get();
    if (!currentExam) throw new Error('No active exam');

    try {
      await examApi.submitAnswer(currentExam.attempt_id, {
        question_id: questionId,
        selected_keys: selectedKeys,
      });

      // Update local state
      const newAnswers = new Map(answers);
      newAnswers.set(questionId, selectedKeys);
      
      set({
        answers: newAnswers,
        currentExam: {
          ...currentExam,
          answered_questions: newAnswers.size,
        },
      });
    } catch (error: any) {
      set({ error: error.message });
      throw error;
    }
  },

  finishExam: async (attemptId: string) => {
    set({ isLoading: true });
    try {
      const result = await examApi.finishExam(attemptId);
      set({ isLoading: false });
      return result;
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  setCurrentQuestion: (index: number) => {
    set({ currentQuestionIndex: index });
  },

  clearExam: () => {
    set({
      currentExam: null,
      questions: [],
      currentQuestionIndex: 0,
      answers: new Map(),
      error: null,
    });
  },
}));