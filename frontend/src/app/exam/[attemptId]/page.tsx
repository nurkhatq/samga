'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useExamStore } from '@/stores/examStore';
import { ExamSession } from '@/components/exam/ExamSession';
import { ProctoringProvider } from '@/components/proctoring/ProctoringProvider';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Loader2, AlertTriangle } from 'lucide-react';

export default function ExamPage() {
  const params = useParams();
  const router = useRouter();
  const attemptId = params.attemptId as string;
  
  const {
    currentExam,
    questions,
    isLoading,
    loadQuestions,
    clearExam,
  } = useExamStore();

  const [hasProctoring, setHasProctoring] = useState(false);

  useEffect(() => {
    if (attemptId) {
      loadQuestions(attemptId);
    }
  }, [attemptId, loadQuestions]);

  useEffect(() => {
    // Initialize proctoring when exam starts
    if (currentExam && questions.length > 0) {
      setHasProctoring(true);
    }
  }, [currentExam, questions]);

  const handleExit = () => {
    if (confirm('Вы уверены, что хотите выйти? Прогресс будет сохранен.')) {
      clearExam();
      router.push('/dashboard');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-lg">Загрузка экзамена...</p>
        </div>
      </div>
    );
  }

  if (!currentExam) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Экзамен не найден</h2>
            <p className="text-gray-600 mb-4">
              Не удалось загрузить данные экзамена. Пожалуйста, попробуйте снова.
            </p>
            <Button onClick={() => router.push('/exam/start')}>
              Вернуться к выбору экзамена
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <ProctoringProvider attemptId={attemptId} enabled={hasProctoring}>
      <div className="min-h-screen bg-gray-50">
        {/* Exam Header */}
        <div className="bg-white border-b shadow-sm">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-xl font-bold text-gray-900">Пробный экзамен</h1>
                <p className="text-sm text-gray-600">
                  {currentExam.mode === 'exam' ? 'Режим экзамена' : 'Режим практики'}
                </p>
              </div>
              
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className="text-lg font-semibold text-gray-900">
                    Вопрос {currentExam.current_question_index + 1} / {currentExam.total_questions}
                  </div>
                  <div className="text-sm text-gray-500">
                    Отвечено: {currentExam.answered_questions}
                  </div>
                </div>
                
                <Button variant="outline" onClick={handleExit}>
                  Выйти
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Exam Content */}
        <ExamSession attemptId={attemptId} />
      </div>
    </ProctoringProvider>
  );
}