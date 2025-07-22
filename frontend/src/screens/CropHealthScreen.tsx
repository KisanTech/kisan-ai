import React from 'react';
import { View, Text, SafeAreaView } from 'react-native';

export const CropHealthScreen: React.FC = () => {
    return (
        <SafeAreaView className="flex-1 bg-background font-sans">
            <View className="flex-1 justify-center items-center">
                <Text className="text-2xl font-bold text-foreground tracking-tighter">
                    Crop Health Diagnosis
                </Text>
            </View>
        </SafeAreaView>
    );
}; 