export interface FormData {
  accountNumber?: string;
  client?: string;
  city?: string;
  additionalInfo?: Record<string, string | boolean>;
}

export interface LogEntry {
  timestamp: string;
  message: string;
  type: 'info' | 'error' | 'success';
}

export interface FileUploadState {
  file: File | null;
  progress: number;
}

export interface BusinessInfo {
  accountNumber: string;
  businessName: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  status: string;
}
