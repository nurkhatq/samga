'use client';

import { useState, useEffect } from 'react';
import { usePracticeStore } from '@/stores/practiceStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { RadioGroup, RadioGroupItem } from '@/components/ui/RadioGroup';
import type { Question, QuestionOption } from '@/lib/api/types';
import { Label } from '@/components/ui/Label';
import { Progress } from '@/components/ui/Progress';
import { CheckCircle2, XCircle, Lightbulb } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PracticeSessionProps {
  subjectCode: string;
}

export function PracticeSession({ subjectCode }: PracticeSessionProps) {
  const {
    questions,
    currentQuestionIndex,
    currentFeedback,
    isLoading,
    loadQuestions,
    submitAnswer,
    nextQuestion,
    stats,
  } = usePracticeStore();

  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const [showExplanation, setShowExplanation] = useState(false);

  const currentQuestion = questions[currentQuestionIndex];

  useEffect(() => {
    loadQuestions(subjectCode, 0);
  }, [subjectCode, loadQuestions]);

  useEffect(() => {
    setSelectedOptions([]);
    setShowExplanation(false);
  }, [currentQuestionIndex]);

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

    await submitAnswer(currentQuestion.id, selectedOptions);
    setShowExplanation(true);
  };

  const handleNextQuestion = () => {
    nextQuestion();
    setShowExplanation(false);
  };

  const progress = ((currentQuestionIndex + 1) / Math.max(questions.length, 1)) * 100;

  if (isLoading || !currentQuestion) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-lg">Загрузка вопросов...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6 max-w-4xl">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Свободная практика</h1>
          <p className="text-muted-foreground">
            Вопрос {currentQuestionIndex + 1} из {questions.length}
          </p>
        </div>
        <div className="text-right">
          <div className="text-lg font-semibold">
            Правильно: {stats.correctAnswers}/{stats.totalAnswered}
          </div>
          <div className="text-sm text-muted-foreground">
            Точность: {stats.accuracy}%
          </div>
        </div>
      </div>

      {/* Progress */}
      <Progress value={progress} className="w-full" />

      {/* Question Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg leading-relaxed">
            {currentQuestion.question_text}
          </CardTitle>
          {currentQuestion.explanation && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Lightbulb className="h-4 w-4" />
              Доступно объяснение после ответа
            </div>
          )}
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Options */}
          <RadioGroup
            value={currentQuestion.question_type === 'multiple' ? undefined : selectedOptions[0]}
            onValueChange={handleOptionSelect}
          >
            {currentQuestion.options.map((option) => (
              <div
                key={option.key}
                role="button"
                className={cn(
                  "flex items-center space-x-2 p-3 border-2 rounded-lg transition-colors cursor-pointer",
                  selectedOptions.includes(option.key)
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 hover:border-gray-300"
                )}
                onClick={() => handleOptionSelect(option.key)}
              >
                <RadioGroupItem
                  value={option.key}
                  id={`option-${option.key}`}
                  checked={selectedOptions.includes(option.key)}
                  className="flex-shrink-0"
                />
                <Label
                  htmlFor={`option-${option.key}`}
                  className="flex-1 cursor-pointer text-base"
                >
                  {option.text}
                </Label>
              </div>
            ))}
          </RadioGroup>

          {/* Submit Button */}
          {!showExplanation && (
            <div className="flex justify-end pt-4">
              <Button
                onClick={handleSubmitAnswer}
                disabled={selectedOptions.length === 0}
                size="lg"
              >
                Проверить ответ
              </Button>
            </div>
          )}

          {/* Feedback */}
          {showExplanation && currentFeedback && (
            <div className={cn(
              "p-4 rounded-lg border-2 mt-4",
              currentFeedback.is_correct
                ? "border-green-200 bg-green-50"
                : "border-red-200 bg-red-50"
            )}>
              <div className="flex items-center gap-3 mb-3">
                {currentFeedback.is_correct ? (
                  <>
                    <CheckCircle2 className="h-6 w-6 text-green-600" />
                    <span className="text-lg font-semibold text-green-800">
                      Правильно!
                    </span>
                  </>
                ) : (
                  <>
                    <XCircle className="h-6 w-6 text-red-600" />
                    <span className="text-lg font-semibold text-red-800">
                      Неправильно
                    </span>
                  </>
                )}
              </div>

              {!currentFeedback.is_correct && currentFeedback.correct_keys && (
                <div className="mb-3">
                  <p className="text-sm font-medium text-gray-700 mb-1">
                    Правильный ответ:
                  </p>
                  <div className="flex gap-2">
                    {currentFeedback.correct_keys.map((key) => (
                      <span
                        key={key}
                        className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm font-medium"
                      >
                        {key}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {currentFeedback.explanation && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">
                    Объяснение:
                  </p>
                  <p className="text-sm text-gray-600">
                    {currentFeedback.explanation}
                  </p>
                </div>
              )}

              <div className="flex justify-end pt-4">
                <Button onClick={handleNextQuestion} size="lg">
                  {currentQuestionIndex < questions.length - 1 ? 'Следующий вопрос' : 'Завершить практику'}
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Question Navigation */}
      {questions.length > 1 && (
        <Card>
          <CardContent className="p-4">
            <div className="flex gap-2 overflow-x-auto">
              {questions.map((_, index) => (
                <Button
                  key={index}
                  variant={index === currentQuestionIndex ? "default" : "outline"}
                  size="sm"
                  onClick={() => usePracticeStore.getState().setCurrentQuestion(index)}
                  className="flex-shrink-0"
                >
                  {index + 1}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}