'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { majorsApi } from '@/lib/api/majors';
import { examApi } from '@/lib/api/exam';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Alert, AlertDescription } from '@/components/ui/Alert';
import { Clock, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

export default function ExamStartPage() {
  const [selectedMajor, setSelectedMajor] = useState<string>('');
  const [isStarting, setIsStarting] = useState(false);
  const router = useRouter();

  const { data: majorsData, isLoading } = useQuery({
    queryKey: ['majors'],
    queryFn: () => majorsApi.getMajors({ active_only: true }),
  });

  const selectedMajorData = majorsData?.majors.find(m => m.code === selectedMajor);

  const handleStartExam = async () => {
    if (!selectedMajor) return;

    setIsStarting(true);
    try {
      const exam = await examApi.startExam({ major_code: selectedMajor });
      router.push(`/exam/${exam.attempt_id}`);
    } catch (error: any) {
      console.error('Failed to start exam:', error);
      setIsStarting(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Начать пробный экзамен</h1>
        <p className="text-gray-600 mt-2">
          Выберите специальность для прохождения пробного экзамена
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Major Selection */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Выбор специальности</CardTitle>
              <CardDescription>
                Выберите специальность для экзамена
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-8">Загрузка специальностей...</div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {majorsData?.majors.map((major) => (
                    <div
                      key={major.code}
                      className={`
                        border-2 rounded-lg p-4 cursor-pointer transition-all
                        ${selectedMajor === major.code
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                        }
                      `}
                      onClick={() => setSelectedMajor(major.code)}
                    >
                      <h3 className="font-semibold text-gray-900">
                        {major.title_ru || major.title_kk}
                      </h3>
                      <p className="text-sm text-gray-500 mt-1">
                        Код: {major.code}
                      </p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs px-2 py-1 bg-gray-100 rounded">
                          {major.magistracy_type === 'profile' ? 'Профильная' : 'Научно-педагогическая'}
                        </span>
                        <span className="text-xs text-gray-500">
                          {major.categories.length} предметов
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Exam Rules */}
          <Card>
            <CardHeader>
              <CardTitle>Правила экзамена</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start gap-3">
                <Clock className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <h4 className="font-medium">Ограничение по времени</h4>
                  <p className="text-sm text-gray-600">
                    Экзамен длится 180 минут. Таймер нельзя остановить.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <XCircle className="h-5 w-5 text-red-600 mt-0.5" />
                <div>
                  <h4 className="font-medium">Запрещенные действия</h4>
                  <p className="text-sm text-gray-600">
                    Нельзя возвращаться к предыдущим вопросам, копировать текст или переключать вкладки.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-orange-600 mt-0.5" />
                <div>
                  <h4 className="font-medium">Система прокторинга</h4>
                  <p className="text-sm text-gray-600">
                    Все действия отслеживаются. Нарушения могут привести к аннулированию результатов.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                <div>
                  <h4 className="font-medium">Результаты</h4>
                  <p className="text-sm text-gray-600">
                    Результаты будут доступны сразу после завершения экзамена.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Exam Summary */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Информация об экзамене</CardTitle>
            </CardHeader>
            <CardContent>
              {selectedMajorData ? (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-lg">
                      {selectedMajorData.title_ru || selectedMajorData.title_kk}
                    </h3>
                    <p className="text-sm text-gray-500">Код: {selectedMajorData.code}</p>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Тип магистратуры:</span>
                      <span className="font-medium">
                        {selectedMajorData.magistracy_type === 'profile' ? 'Профильная' : 'Научно-педагогическая'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Время:</span>
                      <span className="font-medium">180 минут</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Вопросов:</span>
                      <span className="font-medium">~130 вопросов</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Проходной балл:</span>
                      <span className="font-medium">70%</span>
                    </div>
                  </div>

                  <Button
                    onClick={handleStartExam}
                    disabled={isStarting}
                    className="w-full"
                    size="lg"
                  >
                    {isStarting ? 'Запуск экзамена...' : 'Начать экзамен'}
                  </Button>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  Выберите специальность для просмотра информации
                </div>
              )}
            </CardContent>
          </Card>

          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Убедитесь, что у вас есть 3 часа непрерывного времени и стабильное интернет-соединение.
            </AlertDescription>
          </Alert>
        </div>
      </div>
    </div>
  );
}