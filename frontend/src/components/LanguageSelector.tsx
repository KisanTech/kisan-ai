import React, { useState, useRef } from 'react';
import { View, Text, TouchableOpacity, Modal, Platform, Dimensions } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { SUPPORTED_LANGUAGES } from '../config/languages';

interface LanguageSelectorProps {
    currentLanguage: string;
    onLanguageChange: (languageId: string) => void;
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
    currentLanguage,
    onLanguageChange,
}) => {
    const [isVisible, setIsVisible] = useState(false);
    const [dropdownPosition, setDropdownPosition] = useState({ top: 0, right: 0 });
    const buttonRef = useRef<View>(null);
    const { width: windowWidth } = Dimensions.get('window');

    const measureButton = () => {
        buttonRef.current?.measure((
            _x: number,
            _y: number,
            width: number,
            height: number,
            pageX: number,
            pageY: number
        ) => {
            // Position dropdown below the button
            setDropdownPosition({
                top: pageY + height + 4, // 4px gap
                right: windowWidth - (pageX + width),
            });
            setIsVisible(true);
        });
    };

    return (
        <View>
            <TouchableOpacity
                ref={buttonRef}
                onPress={measureButton}
                className="w-10 h-10 rounded-full bg-background items-center justify-center"
                activeOpacity={0.7}
            >
                <MaterialCommunityIcons
                    name="translate"
                    size={24}
                    color="#121b0d"
                />
            </TouchableOpacity>

            <Modal
                visible={isVisible}
                transparent
                animationType="none"
                onRequestClose={() => setIsVisible(false)}
            >
                <TouchableOpacity
                    activeOpacity={1}
                    onPress={() => setIsVisible(false)}
                    className="flex-1"
                >
                    <View
                        className="absolute bg-card rounded-xl overflow-hidden shadow-lg border border-border"
                        style={{
                            minWidth: 200,
                            top: dropdownPosition.top,
                            right: dropdownPosition.right,
                            ...Platform.select({
                                ios: {
                                    shadowColor: '#000',
                                    shadowOffset: { width: 0, height: 2 },
                                    shadowOpacity: 0.25,
                                    shadowRadius: 4,
                                },
                                android: {
                                    elevation: 5,
                                }
                            })
                        }}
                    >
                        {SUPPORTED_LANGUAGES.map((item) => (
                            <TouchableOpacity
                                key={item.id}
                                className={`p-4 flex-row items-center justify-between ${item.id === currentLanguage ? 'bg-accent bg-opacity-20' : ''
                                    }`}
                                onPress={() => {
                                    onLanguageChange(item.id);
                                    setIsVisible(false);
                                }}
                            >
                                <View className="flex-row items-center">
                                    <Text className="text-foreground text-base">
                                        {item.name}
                                    </Text>
                                    <Text className="text-foreground opacity-60 text-base ml-2">
                                        ({item.nativeName})
                                    </Text>
                                </View>
                                {item.id === currentLanguage && (
                                    <MaterialCommunityIcons
                                        name="check"
                                        size={20}
                                        color="#22c55e"
                                    />
                                )}
                            </TouchableOpacity>
                        ))}
                    </View>
                </TouchableOpacity>
            </Modal>
        </View>
    );
}; 