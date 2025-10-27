'use client';

import { createContext, useContext, useEffect, useRef } from 'react';
import { proctoringApi } from '@/lib/api/proctoring';
import { useProctoringStore } from '@/stores/proctoringStore';
import { AlertTriangle } from 'lucide-react';

interface ProctoringContextType {
  logEvent: (eventType: string, metadata?: any) => void;
  violations: number;
  isSuspicious: boolean;
}

const ProctoringContext = createContext<ProctoringContextType | null>(null);

interface ProctoringProviderProps {
  attemptId: string;
  enabled: boolean;
  children: React.ReactNode;
}

export function ProctoringProvider({ attemptId, enabled, children }: ProctoringProviderProps) {
  const { violations, isSuspicious, addViolation, reset } = useProctoringStore();
  const eventBatch = useRef<any[]>([]);
  const batchTimeout = useRef<NodeJS.Timeout>();

  const logEvent = async (eventType: string, metadata: any = {}) => {
    if (!enabled) return;

    const event = {
      event_type: eventType,
      proctoring_metadata: metadata,
      timestamp: new Date().toISOString(),
    };

    eventBatch.current.push(event);

    // Batch events and send every 30 seconds or when batch is large
    if (eventBatch.current.length >= 10) {
      await sendBatch();
    } else {
      // Reset timeout
      if (batchTimeout.current) {
        clearTimeout(batchTimeout.current);
      }
      batchTimeout.current = setTimeout(sendBatch, 30000);
    }

    // Check for violations
    if (['tab_switch', 'copy', 'paste', 'console_open'].includes(eventType)) {
      addViolation(eventType);
    }
  };

  const sendBatch = async () => {
    if (eventBatch.current.length === 0) return;

    try {
      await proctoringApi.logEvents(attemptId, {
        events: eventBatch.current,
      });
      eventBatch.current = [];
    } catch (error) {
      console.error('Failed to send proctoring events:', error);
      // Retry logic could be implemented here
    }
  };

  useEffect(() => {
    if (!enabled) return;

    const handleVisibilityChange = () => {
      if (document.hidden) {
        logEvent('tab_switch', {
          from_tab: 'exam',
          to_tab: 'unknown',
        });
      }
    };

    const handleCopy = (e: ClipboardEvent) => {
      e.preventDefault();
      logEvent('copy', {
        text_length: window.getSelection()?.toString().length || 0,
      });
    };

    const handlePaste = (e: ClipboardEvent) => {
      e.preventDefault();
      logEvent('paste', {
        text_length: e.clipboardData?.getData('text').length || 0,
      });
    };

    const handleContextMenu = (e: MouseEvent) => {
      e.preventDefault();
      logEvent('right_click');
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      // Detect F12 or Ctrl+Shift+I for developer tools
      if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && e.key === 'I')) {
        e.preventDefault();
        logEvent('console_open');
      }
    };

    const detectDevTools = () => {
      const widthThreshold = window.outerWidth - window.innerWidth > 160;
      const heightThreshold = window.outerHeight - window.innerHeight > 160;
      
      if (widthThreshold || heightThreshold) {
        logEvent('console_open');
      }
    };

    // Add event listeners
    document.addEventListener('visibilitychange', handleVisibilityChange);
    document.addEventListener('copy', handleCopy);
    document.addEventListener('paste', handlePaste);
    document.addEventListener('contextmenu', handleContextMenu);
    document.addEventListener('keydown', handleKeyDown);
    
    const devToolsInterval = setInterval(detectDevTools, 1000);

    // Fullscreen recommendation
    if (document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen().catch(() => {
        // User denied fullscreen, log the event
        logEvent('fullscreen_denied');
      });
    }

    // Prevent leaving the page
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      e.returnValue = 'Вы уверены, что хотите покинуть страницу? Прогресс экзамена может быть потерян.';
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      // Cleanup
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      document.removeEventListener('copy', handleCopy);
      document.removeEventListener('paste', handlePaste);
      document.removeEventListener('contextmenu', handleContextMenu);
      document.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('beforeunload', handleBeforeUnload);
      clearInterval(devToolsInterval);
      
      if (batchTimeout.current) {
        clearTimeout(batchTimeout.current);
      }
      
      // Send any remaining events
      sendBatch();
      
      // Exit fullscreen
      if (document.fullscreenElement) {
        document.exitFullscreen();
      }
    };
  }, [enabled, attemptId]);

  return (
    <ProctoringContext.Provider value={{ logEvent, violations, isSuspicious }}>
      {children}
      
      {/* Proctoring Alerts */}
      {violations > 0 && (
        <div className="fixed top-4 right-4 bg-yellow-100 border border-yellow-400 rounded-lg p-4 shadow-lg z-50">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-yellow-600" />
            <span className="font-medium text-yellow-800">
              Нарушений: {violations}
            </span>
          </div>
        </div>
      )}
    </ProctoringContext.Provider>
  );
}

export const useProctoring = () => {
  const context = useContext(ProctoringContext);
  if (!context) {
    throw new Error('useProctoring must be used within a ProctoringProvider');
  }
  return context;
};