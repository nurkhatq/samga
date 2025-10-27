import { create } from 'zustand';

interface ProctoringState {
  violations: number;
  isSuspicious: boolean;
  violationHistory: string[];
  
  addViolation: (type: string) => void;
  reset: () => void;
  checkSuspicious: () => boolean;
}

export const useProctoringStore = create<ProctoringState>((set, get) => ({
  violations: 0,
  isSuspicious: false,
  violationHistory: [],

  addViolation: (type: string) => {
    const { violationHistory } = get();
    
    const newHistory = [...violationHistory, `${type}_${Date.now()}`];
    
    // Keep only violations from last 5 minutes
    const recentHistory = newHistory.filter(violation => {
      const timestamp = parseInt(violation.split('_')[1]);
      return Date.now() - timestamp < 5 * 60 * 1000;
    });

    const newViolations = recentHistory.length;
    const isSuspicious = newViolations >= 3; // More than 3 violations in 5 minutes

    set({
      violations: newViolations,
      isSuspicious,
      violationHistory: recentHistory,
    });
  },

  reset: () => {
    set({
      violations: 0,
      isSuspicious: false,
      violationHistory: [],
    });
  },

  checkSuspicious: () => {
    const { violationHistory } = get();
    return violationHistory.length >= 3;
  },
}));