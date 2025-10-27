'use client';

import { useEffect, useState } from 'react';
import { useExamStore } from '@/stores/examStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { RadioGroup, RadioGroupItem } from '@/components/ui/RadioGroup';
import { Label } from '@/components/ui/Label';
import { Progress } from '@/components/ui/Progress';

interface ExamSessionProps {
  attemptId: string;
}

export function ExamSession({ attemptId }: ExamSessionProps) {
  const {
    questions,
    currentQuestionIndex,
    answers,
    isLoading,
    submitAnswer,
    setCurrentQuestion,
    finishExam,
  } = useExamStore();

  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const [timeRemaining, setTimeRemaining] = useState<number>(0);

  const currentQuestion = questions[currentQuestionIndex];
  const currentAnswer = answers.get(currentQuestion?.id);

  useEffect(() => {
    if (currentQuestion) {
      setSelectedOptions(currentAnswer || []);
    }
  }, [currentQuestion, currentAnswer]);

  const handleOptionSelect = (value: string) => {
    if (currentQuestion?.question_type === 'multiple') {
      setSelectedOptions(prev =>
        prev.includes(value)
          ? prev.filter(v => v !== value)
          : [...prev, value]
      );
    } else {
      setSelectedOptions([value]);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!currentQuestion || selectedOptions.length === 0) return;

    try {
      await submitAnswer(currentQuestion.id, selectedOptions);
      
      // Move to next question or finish
      if (currentQuestionIndex < questions.length - 1) {
        setCurrentQuestion(currentQuestionIndex + 1);
        setSelectedOptions([]);
      } else {
        // Finish exam
        const result = await finishExam(attemptId);
        // Handle result display
      }
    } catch (error) {
      console.error('Failed to submit answer:', error);
    }
  };

  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  if (isLoading || !currentQuestion) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-lg">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Экзамен</h1>
          <p className="text-muted-foreground">
            Вопрос {currentQuestionIndex + 1} из {questions.length}
          </p>
        </div>
        <div className="text-right">
          <div className="text-lg font-semibold">
            {Math.floor(timeRemaining / 60)}:{(timeRemaining % 60).toString().padStart(2, '0')}
          </div>
          <div className="text-sm text-muted-foreground">Осталось времени</div>
        </div>
      </div>

      {/* Progress */}
      <Progress value={progress} className="w-full" />

      {/* Question */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">
            {currentQuestion.question_text}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <RadioGroup
            value={currentQuestion.question_type === 'multiple' ? undefined : selectedOptions[0]}
            onValueChange={handleOptionSelect}
          >
            {currentQuestion.options.map((option) => (
              <div key={option.key} className="flex items-center space-x-2">
                <RadioGroupItem
                  value={option.key}
                  id={`option-${option.key}`}
                  checked={selectedOptions.includes(option.key)}
                  onClick={() => handleOptionSelect(option.key)}
                />
                <Label htmlFor={`option-${option.key}`} className="flex-1 cursor-pointer">
                  {option.text}
                </Label>
              </div>
            ))}
          </RadioGroup>

          <div className="flex justify-between pt-4">
            <Button
              variant="outline"
              disabled={currentQuestionIndex === 0}
              onClick={() => setCurrentQuestion(currentQuestionIndex - 1)}
            >
              Назад
            </Button>
            
            <Button
              onClick={handleSubmitAnswer}
              disabled={selectedOptions.length === 0}
            >
              {currentQuestionIndex === questions.length - 1 ? 'Завершить экзамен' : 'Следующий вопрос'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}