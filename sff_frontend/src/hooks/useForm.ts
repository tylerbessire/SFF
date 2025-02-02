import { useState, useCallback } from 'react';

export interface FormDataBase {
  additionalInfo?: Record<string, any>;
  [key: string]: any;
}

export function useForm<T extends FormDataBase = FormDataBase>(initialState: T = {} as T) {
  const [formData, setFormData] = useState<T>(initialState);

  const handleChange = useCallback((field: keyof T) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (field === 'additionalInfo') {
      setFormData(prev => ({
        ...prev,
        additionalInfo: {
          ...(prev.additionalInfo || {}),
          [e.target.name]: e.target.value
        }
      } as T));
    } else {
      setFormData(prev => ({ ...prev, [field]: e.target.value } as T));
    }
  }, []);

  const handleAdditionalInfoChange = useCallback((field: string) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      additionalInfo: {
        ...(prev.additionalInfo || {}),
        [field]: e.target.value
      }
    } as T));
  }, []);

  const handleCheckboxChange = useCallback((field: string) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      additionalInfo: {
        ...(prev.additionalInfo || {}),
        [field]: e.target.checked
      }
    } as T));
  }, []);

  const resetForm = useCallback(() => setFormData(initialState), [initialState]);

  return {
    formData,
    handleChange,
    handleAdditionalInfoChange,
    handleCheckboxChange,
    resetForm,
    setFormData
  };
}
