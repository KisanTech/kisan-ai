export interface Language {
    id: string;
    name: string;
    nativeName: string;
    icon?: string; // Optional flag icon
}

export const SUPPORTED_LANGUAGES: Language[] = [
    {
        id: 'en',
        name: 'English',
        nativeName: 'English',
    },
    {
        id: 'kn',
        name: 'Kannada',
        nativeName: 'ಕನ್ನಡ',
    },
    {
        id: 'hi',
        name: 'Hindi',
        nativeName: 'हिंदी',
    },
    {
        id: 'od',
        name: 'Odia',
        nativeName: 'ଓଡ଼ିଆ',
    },
]; 