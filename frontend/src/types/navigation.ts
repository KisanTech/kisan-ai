// Navigation parameter types for type-safe navigation
export type RootStackParamList = {
  Home: undefined;
  CropHealth: undefined;
  DiagnosisResult: {
    diagnosis: any; // We'll replace 'any' with proper type when needed
    imageUri: string;
  };
  MarketPrices: undefined;
  GovernmentSchemes: undefined;
};
