import { create } from 'zustand';
import { practiceApi } from '@/lib/api/practice';
import { Question, SubmitAnswerResponse } from '@/lib/api/types';

interface PracticeState {
  // Current session
  currentSubject: string | null;
  questions: Question[];
  currentQuestionIndex: number;
  currentFeedback: SubmitAnswerResponse | null;
  
  // Statistics
  stats: {
    totalAnswered: number;
    correctAnswers: number;
    accuracy: number;
    currentStreak: number;
    bestStreak: number;
  };
  
  // Loading states
  isLoading: boolean;
  error: string | null;

  // Actions
  loadQuestions: (subjectCode: string, offset: number) => Promise<void>;
  submitAnswer: (questionId: string, selectedKeys: string[]) => Promise<void>;
  nextQuestion: () => void;
  setCurrentQuestion: (index: number) => void;
  clearSession: () => void;
  updateStats: (isCorrect: boolean) => void;
}

export const usePracticeStore = create<PracticeState>((set, get) => ({
  currentSubject: null,
  questions: [],
  currentQuestionIndex: 0,
  currentFeedback: null,
  stats: {
    totalAnswered: 0,
    correctAnswers: 0,
    accuracy: 0,
    currentStreak: 0,
    bestStreak: 0,
  },
  isLoading: false,
  error: null,

  loadQuestions: async (subjectCode: string, offset: number = 0) => {
    set({ isLoading: true, error: null });
    try {
      const response = await practiceApi.getQuestions(subjectCode, offset, 20);
      set({
        currentSubject: subjectCode,
        questions: response.questions,
        currentQuestionIndex: 0,
        isLoading: false,
      });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  submitAnswer: async (questionId: string, selectedKeys: string[]) => {
    const { currentSubject, updateStats } = get();
    if (!currentSubject) throw new Error('No active practice session');

    set({ isLoading: true });
    try {
      const feedback = await practiceApi.submitAnswer(currentSubject, {
        question_id: questionId,
        selected_keys: selectedKeys,
      });

      // Update statistics
      if (feedback.is_correct !== undefined) {
        updateStats(feedback.is_correct);
      }

      set({
        currentFeedback: feedback,
        isLoading: false,
      });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  nextQuestion: () => {
    const { currentQuestionIndex, questions } = get();
    if (currentQuestionIndex < questions.length - 1) {
      set({
        currentQuestionIndex: currentQuestionIndex + 1,
        currentFeedback: null,
      });
    } else {
      // Load more questions or end session
      get().loadQuestions(get().currentSubject!, questions.length);
    }
  },

  setCurrentQuestion: (index: number) => {
    set({ currentQuestionIndex: index, currentFeedback: null });
  },

  clearSession: () => {
    set({
      currentSubject: null,
      questions: [],
      currentQuestionIndex: 0,
      currentFeedback: null,
      stats: {
        totalAnswered: 0,
        correctAnswers: 0,
        accuracy: 0,
        currentStreak: 0,
        bestStreak: 0,
      },
    });
  },

  updateStats: (isCorrect: boolean) => {
    const { stats } = get();
    
    const newTotalAnswered = stats.totalAnswered + 1;
    const newCorrectAnswers = stats.correctAnswers + (isCorrect ? 1 : 0);
    const newAccuracy = (newCorrectAnswers / newTotalAnswered) * 100;
    
    const newCurrentStreak = isCorrect ? stats.currentStreak + 1 : 0;
    const newBestStreak = Math.max(stats.bestStreak, newCurrentStreak);

    set({
      stats: {
        totalAnswered: newTotalAnswered,
        correctAnswers: newCorrectAnswers,
        accuracy: Math.round(newAccuracy),
        currentStreak: newCurrentStreak,
        bestStreak: newBestStreak,
      },
    });
  },
}));