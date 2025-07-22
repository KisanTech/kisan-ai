/// <reference types="nativewind/types" />

// Extend React Native components with className prop
import 'react-native';

declare module 'react-native' {
    interface ViewProps {
        className?: string;
    }

    interface TextProps {
        className?: string;
    }

    interface ScrollViewProps {
        className?: string;
    }

    interface ImageProps {
        className?: string;
    }

    interface TouchableOpacityProps {
        className?: string;
    }

    interface SafeAreaViewProps {
        className?: string;
    }
} 