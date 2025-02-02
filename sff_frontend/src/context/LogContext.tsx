import { createContext, useContext, ReactNode } from 'react';
import { useLog } from '@/hooks/useLog';
import type { LogEntry } from '@/types';

interface LogContextType {
  logs: LogEntry[];
  addLog: (message: string, type?: LogEntry['type']) => void;
}

const LogContext = createContext<LogContextType | undefined>(undefined);

export function LogProvider({ children }: { children: ReactNode }) {
  const logHook = useLog();
  return <LogContext.Provider value={logHook}>{children}</LogContext.Provider>;
}

export function useLogContext() {
  const context = useContext(LogContext);
  if (!context) {
    throw new Error('useLogContext must be used within a LogProvider');
  }
  return context;
}
