// Основные типы из OpenAPI спецификации
export interface User {
  id: number;
  username: string;
  full_name: string;
  major_code?: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface Major {
  code: string;
  title_kk: string;
  title_ru?: string;
  magistracy_type: MagistracyType;
  categories: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Subject {
  code: string;
  title_kk: string;
  title_ru?: string;
  subject_type: SubjectType;
  major_code?: string;
  is_active: boolean;
  questions_count: number;
  created_at: string;
  updated_at: string;
}

export interface Question {
  id: string;
  subject_code: string;
  question_text: string;
  difficulty: QuestionDifficulty;
  question_type: QuestionType;
  points: number;
  time_seconds: number;
  explanation?: string;
  tags: string[];
  options: QuestionOption[];
}

export interface QuestionOption {
  key: string;
  text: string;
}

export interface ExamStartResponse {
  attempt_id: string;
  mode: ExamMode;
  started_at: string;
  time_limit_minutes?: number;
  total_questions: number;
}

export interface ExamStatus {
  attempt_id: string;
  mode: ExamMode;
  status: ExamStatusEnum;
  started_at: string;
  completed_at?: string;
  time_limit_minutes?: number;
  time_remaining_seconds?: number;
  total_questions: number;
  answered_questions: number;
  current_question_index: number;
}

export interface ExamResult {
  attempt_id: string;
  mode: ExamMode;
  status: ExamStatusEnum;
  started_at: string;
  completed_at: string;
  total_questions: number;
  answered_questions: number;
  correct_answers: number;
  score_percentage: number;
  passed: boolean;
  proctoring_copy_paste_count: number;
  proctoring_tab_switches_count: number;
  proctoring_console_opens_count: number;
  proctoring_suspicious: boolean;
}

// Enums
export enum UserRole {
  STUDENT = 'student',
  ADMIN = 'admin',
  MODERATOR = 'moderator',
}

export enum MagistracyType {
  PROFILE = 'profile',
  SCIENTIFIC_PEDAGOGICAL = 'scientific_pedagogical',
}

export enum SubjectType {
  GENERAL = 'general',
  PROFILE = 'profile',
}

export enum QuestionDifficulty {
  A = 'A',
  B = 'B',
  C = 'C',
}

export enum QuestionType {
  SINGLE = 'single',
  MULTIPLE = 'multiple',
}

export enum ExamMode {
  PRACTICE = 'practice',
  EXAM = 'exam',
}

export enum ExamStatusEnum {
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  EXPIRED = 'expired',
  CANCELLED = 'cancelled',
}

export interface UserStatisticsResponse {
  total_attempts: number;
  practice_attempts: number;
  exam_attempts: number;
  average_score: number;
  total_questions_answered: number;
  correct_answers_percentage: number;
  subject_stats: {
    subject_code: string;
    attempts: number;
    average_score: number;
  }[];
  recent_attempts: ExamResult[];
}

export interface SubmitAnswerRequest {
  question_id: string;
  selected_keys: string[];
}

export interface SubmitAnswerResponse {
  is_correct: boolean;
  correct_keys: string[];
  explanation?: string;
}