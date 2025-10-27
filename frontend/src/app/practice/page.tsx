'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { majorsApi } from '@/lib/api/majors';
import { subjectsApi } from '@/lib/api/subjects';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Search, BookOpen, Clock, Target } from 'lucide-react';
import Link from 'next/link';

export default function PracticePage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMajor, setSelectedMajor] = useState<string>('');

  const { data: majorsData } = useQuery({
    queryKey: ['majors'],
    queryFn: () => majorsApi.getMajors({ active_only: true }),
  });

  const { data: subjectsData } = useQuery({
    queryKey: ['subjects', selectedMajor],
    queryFn: () => subjectsApi.getSubjects({
      major_code: selectedMajor || undefined,
      active_only: true,
    }),
  });

  const filteredMajors = majorsData?.majors.filter(major =>
    major.title_ru?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    major.title_kk.toLowerCase().includes(searchTerm.toLowerCase()) ||
    major.code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getSubjectStats = (subjectCode: string) => {
    // Mock stats - в реальном приложении брать из API
    return {
      progress: Math.floor(Math.random() * 100),
      correctAnswers: Math.floor(Math.random() * 50),
      totalQuestions: 100,
    };
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Свободная практика</h1>
        <p className="text-gray-600 mt-2">
          Выберите специальность и предмет для тренировки
        </p>
      </div>

      {/* Search and Filter */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Поиск специальности..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <select
              value={selectedMajor}
              onChange={(e) => setSelectedMajor(e.target.value)}
              className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Все специальности</option>
              {majorsData?.majors.map((major) => (
                <option key={major.code} value={major.code}>
                  {major.title_ru || major.title_kk}
                </option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Majors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredMajors?.map((major) => (
          <Card key={major.code} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="text-lg">{major.title_ru || major.title_kk}</CardTitle>
              <CardDescription>
                Код: {major.code} • {major.magistracy_type === 'profile' ? 'Профильная' : 'Научно-педагогическая'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-medium text-sm text-gray-900 mb-2">Профильные предметы:</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  {major.categories.slice(0, 3).map((category, index) => (
                    <li key={index}>• {category}</li>
                  ))}
                  {major.categories.length > 3 && (
                    <li className="text-blue-600">+{major.categories.length - 3} еще</li>
                  )}
                </ul>
              </div>
              
              <div className="flex gap-2">
                <Link href={`/practice/major/${major.code}`} className="flex-1">
                  <Button className="w-full">Выбрать предмет</Button>
                </Link>
                <Link href={`/exam/start?major=${major.code}`}>
                  <Button variant="outline">Экзамен</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Subjects List (if major selected) */}
      {selectedMajor && subjectsData && (
        <Card>
          <CardHeader>
            <CardTitle>Предметы выбранной специальности</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {subjectsData.subjects.map((subject) => {
                const stats = getSubjectStats(subject.code);
                
                return (
                  <div
                    key={subject.code}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">
                        {subject.title_ru || subject.title_kk}
                      </h3>
                      <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                        <div className="flex items-center gap-1">
                          <BookOpen className="h-4 w-4" />
                          {subject.questions_count} вопросов
                        </div>
                        <div className="flex items-center gap-1">
                          <Target className="h-4 w-4" />
                          Прогресс: {stats.progress}%
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          {stats.correctAnswers}/{stats.totalQuestions}
                        </div>
                      </div>
                    </div>
                    
                    <Link href={`/practice/subject/${subject.code}`}>
                      <Button>Начать практику</Button>
                    </Link>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}