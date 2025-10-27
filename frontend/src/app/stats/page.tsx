'use client';

import { useQuery } from '@tanstack/react-query';
import { statsApi } from '@/lib/api/stats';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { BookOpen, Target, TrendingUp, Award, Clock, CheckCircle2 } from 'lucide-react';
import { ExamResult } from '@/lib/api/types';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export default function StatsPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['user-stats'],
    queryFn: () => statsApi.getUserStats(),
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-gray-200 rounded animate-pulse"></div>
          ))}
        </div>
      </div>
    );
  }

  // Mock data for charts (in real app, use actual stats)
  const subjectData = [
    { subject: 'ТГО', correct: 85, total: 100, percentage: 85 },
    { subject: 'Английский', correct: 78, total: 100, percentage: 78 },
    { subject: 'Педагогика', correct: 92, total: 100, percentage: 92 },
    { subject: 'Психология', correct: 65, total: 100, percentage: 65 },
  ];

  const progressData = [
    { date: '1 Oct', score: 65 },
    { date: '8 Oct', score: 72 },
    { date: '15 Oct', score: 68 },
    { date: '22 Oct', score: 85 },
    { date: '29 Oct', score: 78 },
  ];

  const difficultyData = [
    { name: 'Легкие', value: 45 },
    { name: 'Средние', value: 35 },
    { name: 'Сложные', value: 20 },
  ];

  const statsCards = [
    {
      title: 'Пройдено практик',
      value: stats?.practice_attempts || 0,
      icon: BookOpen,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Сдано экзаменов',
      value: stats?.exam_attempts || 0,
      icon: Target,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Средний балл',
      value: `${stats?.average_score || 0}%`,
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Лучший результат',
      value: `${Math.round(stats?.average_score || 0)}%`,
      icon: Award,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Моя статистика</h1>
        <p className="text-gray-600 mt-2">
          Отслеживайте ваш прогресс в подготовке к экзаменам
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      {stat.title}
                    </p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {stat.value}
                    </p>
                  </div>
                  <div className={`p-3 rounded-full ${stat.bgColor}`}>
                    <Icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Progress Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Прогресс обучения</CardTitle>
            <CardDescription>
              Динамика ваших результатов за последний месяц
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={progressData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  stroke="#3B82F6" 
                  strokeWidth={2}
                  dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Subject Performance */}
        <Card>
          <CardHeader>
            <CardTitle>Результаты по предметам</CardTitle>
            <CardDescription>
              Процент правильных ответов по каждому предмету
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={subjectData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="subject" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="percentage" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Difficulty Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Сложность вопросов</CardTitle>
            <CardDescription>
              Распределение по уровням сложности
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={difficultyData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {difficultyData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Последние попытки</CardTitle>
            <CardDescription>
              Ваши недавние экзамены и практики
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
                {stats?.recent_attempts?.slice(0, 5).map((attempt: ExamResult, index: number) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-full ${
                      attempt.passed ? 'bg-green-100' : 'bg-red-100'
                    }`}>
                      {attempt.passed ? (
                        <CheckCircle2 className="h-5 w-5 text-green-600" />
                      ) : (
                        <Clock className="h-5 w-5 text-red-600" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium">
                        {attempt.mode === 'exam' ? 'Пробный экзамен' : 'Практика'}
                      </p>
                      <p className="text-sm text-gray-500">
                        {new Date(attempt.completed_at).toLocaleDateString('ru-RU')}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`text-lg font-bold ${
                      attempt.passed ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {attempt.score_percentage}%
                    </p>
                    <p className="text-sm text-gray-500">
                      {attempt.correct_answers}/{attempt.total_questions}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Study Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>Рекомендации для улучшения</CardTitle>
          <CardDescription>
            На основе вашей статистики
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="flex items-start gap-3 p-4 border rounded-lg">
              <Target className="h-6 w-6 text-blue-600 mt-0.5" />
              <div>
                <h4 className="font-medium">Слабые места</h4>
                <p className="text-sm text-gray-600 mt-1">
                  Сосредоточьтесь на предметах с результатом ниже 70%
                </p>
              </div>
            </div>
            
            <div className="flex items-start gap-3 p-4 border rounded-lg">
              <Clock className="h-6 w-6 text-orange-600 mt-0.5" />
              <div>
                <h4 className="font-medium">Тайм-менеджмент</h4>
                <p className="text-sm text-gray-600 mt-1">
                  Практикуйтесь с ограничением времени для экзаменов
                </p>
              </div>
            </div>
            
            <div className="flex items-start gap-3 p-4 border rounded-lg">
              <TrendingUp className="h-6 w-6 text-green-600 mt-0.5" />
              <div>
                <h4 className="font-medium">Регулярность</h4>
                <p className="text-sm text-gray-600 mt-1">
                  Занимайтесь ежедневно для стабильного прогресса
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}