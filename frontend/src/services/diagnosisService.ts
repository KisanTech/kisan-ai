
// Use the new backend URL
const API_BASE_URL = 'https://kisan-ai-api-v2-556613941388.us-central1.run.app';

// Diagnosis API Endpoints
const DIAGNOSIS_ENDPOINTS = {
  CROP_DIAGNOSE: '/api/v1/crop-diagnosis/analyze-upload',
  TRANSLATE: '/api/v1/translation/translate',
} as const;

// Types for diagnosis service
export interface DiagnosisRequest {
  imageUri: string; // Local image URI
  description?: string; // Optional description
}

export interface DiagnosisResponse {
  success: boolean;
  image_url: string;
  description: string;
  uploaded_filename: string;
  crop_identification: any | null;
  disease_analysis: any | null;
  treatment_recommendations: any | null;
  prevention_measures: any | null;
  follow_up: any | null;
  crop_health_diagnosis: any | null;
  treatment_recommendation: any | null;
  prevention_notes: any | null;
  disclaimer: string | null;
  raw_agent_response: string;
  error: string | null;
}

// Interface for the parsed agent response
// Interface for translation API response
export interface TranslationResponse {
  translated_text: string;
  detected_language: string;
  source_language: string;
  target_language: string;
  original_text: string;
}

export interface ParsedAgentResponse {
  crop_identification?: {
    crop_name?: string;
    variety_hints?: string;
    growth_stage?: string;
    confidence_percentage?: number;
  };
  disease_analysis?: {
    disease_detected?: boolean;
    primary_diagnosis?: {
      disease_name?: string;
      scientific_name?: string;
      confidence_percentage?: number;
      severity_level?: string;
      affected_area_percentage?: number;
    };
    differential_diagnosis?: string[];
    symptoms_observed?: string[];
  };
  treatment_recommendations?: {
    immediate_action?: {
      steps?: string[];
      urgency?: string;
    };
    organic_treatment?: {
      primary_recommendation?: string;
      application_method?: string;
      frequency?: string;
      local_availability?: string;
    };
    chemical_treatment?: {
      primary_recommendation?: string;
      dosage?: string;
      application_method?: string;
      frequency?: string;
      precautions?: string;
      indian_brands?: string[];
    };
    cost_analysis?: {
      organic_cost_per_acre?: string;
      chemical_cost_per_acre?: string;
      recommendation?: string;
    };
  };
  prevention_measures?: {
    cultural_practices?: string[];
    resistant_varieties?: string[];
    seasonal_timing?: string;
  };
  follow_up?: {
    monitoring_schedule?: string;
    success_indicators?: string[];
    escalation_triggers?: string[];
    lab_testing_needed?: boolean;
  };
  disclaimer?: string;
}

// Diagnosis Service Class
class DiagnosisService {
  /**
   * Translate text to target language
   */
  async translateText(text: string, targetLanguage: string): Promise<string> {
    try {
      if (!text || !text.trim()) {
        return text;
      }

      // Construct full URL
      const url = `${API_BASE_URL}${DIAGNOSIS_ENDPOINTS.TRANSLATE}`;

      // Send request using fetch
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          target_language: targetLanguage,
        }),
      });

      if (!response.ok) {
        console.error(`Translation API error! status: ${response.status}`);
        return text; // Return original text if translation fails
      }

      const data: TranslationResponse = await response.json();
      return data.translated_text || text;
    } catch (error) {
      console.error('Translation error:', error);
      return text; // Return original text if translation fails
    }
  }

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
      const url = `${API_BASE_URL}${DIAGNOSIS_ENDPOINTS.CROP_DIAGNOSE}`;

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
      console.log('API Response Headers:', headers);
      console.log('API Response Status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.log('API Error Response:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, response: ${errorText}`);
      }

      const data = await response.json();
      console.log('API Success Response:', JSON.stringify(data, null, 2));
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
