import { useState, useCallback } from 'react';
import type { LogEntry } from '@/types';

export function useLog() {
  const [logs, setLogs] = useState<LogEntry[]>([]);

  const addLog = useCallback((message: string, type: LogEntry['type'] = 'info') => {
    const newLog: LogEntry = {
      timestamp: new Date().toISOString(),
      message,
      type,
    };
    setLogs(prev => [...prev, newLog]);
  }, []);

  return { logs, addLog };
}
