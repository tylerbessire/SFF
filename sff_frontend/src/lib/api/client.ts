import { FileUploadResponse, BusinessInfo, FormState } from './types';

// Mock API implementation for development
export async function uploadFiles(
  _inputFile: File,
  _templateFile: File,
  _outputPath: string
): Promise<FileUploadResponse> {
  await new Promise(resolve => setTimeout(resolve, 1000));
  return {
    success: true,
    message: 'Files processed successfully',
    data: [{
      accountNumber: '12345',
      client: 'Mock Business',
      city: 'Mock City'
    }]
  };
}

export async function submitManualEntry(formData: FormState) {
  await new Promise(resolve => setTimeout(resolve, 500));
  const response = {
    success: true,
    data: formData
  };
  console.log('Mock API Response:', response);
  return response;
}

export async function scrapeBusiness(
  businessName: string,
  city: string
): Promise<{ results: BusinessInfo[] }> {
  await new Promise(resolve => setTimeout(resolve, 1000));
  return {
    results: [{
      license_number: '12345',
      business_name: businessName,
      address: '123 Main St',
      city: city,
      state: 'CA',
      zip: '95814',
      status: 'Active'
    }]
  };
}

export async function generatePDF(
  templatePath: string,
  data: Record<string, any>
): Promise<Blob> {
  await new Promise(resolve => setTimeout(resolve, 1500));
  const content = `Mock PDF for ${data.client || 'Unknown'}\nTemplate: ${templatePath}\nData: ${JSON.stringify(data, null, 2)}`;
  return new Blob([content], { type: 'application/pdf' });
}
