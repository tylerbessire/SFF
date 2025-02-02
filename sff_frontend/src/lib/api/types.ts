export interface BusinessInfo {
  license_number: string;
  business_name: string;
  address: string;
  city: string;
  state: string;
  zip: string;
  status: string;
}

export interface FormState {
  accountNumber: string | undefined;
  client: string | undefined;
  city: string | undefined;
  additionalInfo?: Record<string, string | boolean>;
}

export interface FileUploadResponse {
  success: boolean;
  message: string;
  data?: any;
}

export interface LogMessage {
  timestamp: string;
  message: string;
  type: 'info' | 'error' | 'success';
}
