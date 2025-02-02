import { useState, useCallback } from 'react';
import { useLogContext } from '@/context/LogContext';

export function useFileUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const { addLog } = useLogContext();

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      addLog(`Selected file: ${selectedFile.name}`, 'info');
      setProgress(0);
    }
  }, [addLog]);

  const uploadFile = useCallback(async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setProgress(25);
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      setProgress(75);

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      setProgress(100);
      addLog(`File uploaded successfully: ${file.name}`, 'success');
      return data;
    } catch (error) {
      setProgress(0);
      addLog(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
      throw error;
    }
  }, [file, addLog]);

  return {
    file,
    progress,
    handleFileChange,
    uploadFile,
  };
}
