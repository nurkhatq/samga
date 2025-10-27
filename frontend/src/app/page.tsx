import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-6 py-16">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Connect AITU
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Платформа подготовки к экзаменам в магистратуру Казахстана. 
            Практикуйтесь и сдавайте пробные экзамены с системой прокторинга.
          </p>
          <div className="space-x-4">
            <Link href="/login">
              <Button size="lg">Войти</Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="outline" size="lg">
                Начать подготовку
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}