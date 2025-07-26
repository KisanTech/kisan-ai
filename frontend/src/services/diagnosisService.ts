import { DIAGNOSIS_API_BASE_URL } from './baseApiService';

// Diagnosis API Endpoints
const DIAGNOSIS_ENDPOINTS = {
  CROP_DIAGNOSE: '/crop/diagnose',
} as const;

// Types for diagnosis service
export interface DiagnosisRequest {
  imageUri: string; // Local image URI
  description?: string; // Optional description
}

export interface DiagnosisResponse {
  status: string;
  message: string;
  image_metadata: {
    filename: string;
    content_type: string;
    size_kb: number;
    description?: string;
  };
  diagnosis: {
    disease_name: string;
    confidence: number;
    severity: string;
    affected_area: string;
  };
  treatment: {
    immediate_action: string;
    recommended_fungicide: string;
    application_frequency: string;
  };
  local_suppliers: Array<{
    name: string;
    distance: string;
  }>;
}

// Diagnosis Service Class
class DiagnosisService {
  /**
   * Diagnose crop disease using FormData
   */
  async diagnoseCrop(request: DiagnosisRequest): Promise<DiagnosisResponse> {
    try {
      // Create FormData with React Native compatible approach
      const formData = new FormData();

      // For React Native, we can append the file directly using the URI
      formData.append('image', {
        uri: request.imageUri,
        type: 'image/jpeg',
        name: 'crop_image.jpg',
      } as any);

      if (request.description) {
        formData.append('description', request.description);
      }

      // Construct full URL
      const url = `${DIAGNOSIS_API_BASE_URL}${DIAGNOSIS_ENDPOINTS.CROP_DIAGNOSE}`;

      // @ts-ignore - FormData._parts is React Native specific
      if (formData._parts) {
        // @ts-ignore
        formData._parts.forEach((part, index) => {
          console.log(`  ${index}:`, part);
        });
      }

      // Send request using fetch to properly handle FormData
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        // Don't set Content-Type - let React Native set it with proper boundary
      });

      // Log response headers
      const headers: Record<string, string> = {};
      response.headers.forEach((value, key) => {
        headers[key] = value;
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, response: ${errorText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      throw error;
    }
  }
}

// Create and export the diagnosis service instance
export const diagnosisService = new DiagnosisService();

// Export the class for creating new instances if needed
export { DiagnosisService };

// Default export
export default diagnosisService;
