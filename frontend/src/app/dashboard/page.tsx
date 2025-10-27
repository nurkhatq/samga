'use client';

import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { majorsApi } from '@/lib/api/majors';
import { Major } from '@/lib/api/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { BookOpen, FileText, BarChart3, Users } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const [recentMajors, setRecentMajors] = useState<Major[]>([]);

  const { data: majorsData, isLoading } = useQuery({
    queryKey: ['majors'],
    queryFn: () => majorsApi.getMajors({ active_only: true, limit: 6 }),
  });

  useEffect(() => {
    if (majorsData?.majors) {
      setRecentMajors(majorsData.majors.slice(0, 3));
    }
  }, [majorsData]);

  const stats = [
    { label: 'Пройдено практик', value: '12', icon: BookOpen, color: 'text-blue-600' },
    { label: 'Сдано экзаменов', value: '3', icon: FileText, color: 'text-green-600' },
    { label: 'Средний балл', value: '78%', icon: BarChart3, color: 'text-purple-600' },
    { label: 'Рейтинг', value: '#45', icon: Users, color: 'text-orange-600' },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Добро пожаловать!
        </h1>
        <p className="text-gray-600 mt-2">
          Продолжайте подготовку к экзаменам в магистратуру
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      {stat.label}
                    </p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {stat.value}
                    </p>
                  </div>
                  <Icon className={`h-8 w-8 ${stat.color}`} />
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Majors */}
        <Card>
          <CardHeader>
            <CardTitle>Популярные специальности</CardTitle>
            <CardDescription>
              Начните подготовку по выбранной специальности
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {isLoading ? (
              <div className="text-center py-4">Загрузка...</div>
            ) : (
              recentMajors.map((major) => (
                <div
                  key={major.code}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div>
                    <h3 className="font-medium text-gray-900">
                      {major.title_ru || major.title_kk}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {major.categories.length} предметов
                    </p>
                  </div>
                  <Link href={`/practice?major=${major.code}`}>
                    <Button variant="outline" size="sm">
                      Начать
                    </Button>
                  </Link>
                </div>
              ))
            )}
            <Link href="/practice">
              <Button variant="ghost" className="w-full">
                Все специальности →
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Quick Links */}
        <Card>
          <CardHeader>
            <CardTitle>Быстрый доступ</CardTitle>
            <CardDescription>
              Перейдите к нужному разделу
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link href="/practice">
              <Button variant="outline" className="w-full justify-start h-12">
                <BookOpen className="h-5 w-5 mr-3" />
                <div className="text-left">
                  <div className="font-medium">Свободная практика</div>
                  <div className="text-sm text-gray-500">Тренируйтесь без ограничений</div>
                </div>
              </Button>
            </Link>
            
            <Link href="/exam">
              <Button variant="outline" className="w-full justify-start h-12">
                <FileText className="h-5 w-5 mr-3" />
                <div className="text-left">
                  <div className="font-medium">Пробный экзамен</div>
                  <div className="text-sm text-gray-500">Проверьте свои знания</div>
                </div>
              </Button>
            </Link>
            
            <Link href="/stats">
              <Button variant="outline" className="w-full justify-start h-12">
                <BarChart3 className="h-5 w-5 mr-3" />
                <div className="text-left">
                  <div className="font-medium">Моя статистика</div>
                  <div className="text-sm text-gray-500">Отслеживайте прогресс</div>
                </div>
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}