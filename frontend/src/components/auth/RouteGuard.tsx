'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';

interface RouteGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requireAdmin?: boolean;
}

export function RouteGuard({ 
  children, 
  requireAuth = true,
  requireAdmin = false 
}: RouteGuardProps) {
  const { isAuthenticated, user, isLoading } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;

    if (requireAuth && !isAuthenticated) {
      router.push('/login');
      return;
    }

    if (requireAuth && requireAdmin && user?.role !== 'admin') {
      router.push('/dashboard');
      return;
    }

    if (!requireAuth && isAuthenticated) {
      router.push('/dashboard');
      return;
    }
  }, [isAuthenticated, user, requireAuth, requireAdmin, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Загрузка...</div>
      </div>
    );
  }

  if (requireAuth && !isAuthenticated) {
    return null;
  }

  if (requireAuth && requireAdmin && user?.role !== 'admin') {
    return null;
  }

  return <>{children}</>;
}