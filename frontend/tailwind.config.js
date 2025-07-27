/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './App.{js,jsx,ts,tsx}',
    './src/**/*.{js,jsx,ts,tsx}',
    './components/**/*.{js,jsx,ts,tsx}',
    './screens/**/*.{js,jsx,ts,tsx}',
  ],
  presets: [require('nativewind/preset')],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Lexend', 'Noto Sans', 'sans-serif'],
      },
      letterSpacing: {
        tighter: '-0.015em',
      },
      colors: {
        // Standard color naming with Project Kisan design colors
        primary: '#19BA49', // Bright green for primary buttons
        secondary: '#669a4c', // Medium olive green for active states
        background: '#f9fcf8', // Soft off-white green-tinted
        foreground: '#121b0d', // Very dark green text
        card: '#ffffff', // Pure white for cards
        border: '#d7e7cf', // Pale green borders
        muted: '#ebf3e7', // Very light green for separators
        accent: '#d7e7cf', // Pale green accents
        cardBackground: '#d7e6cf', // Soft off-white green-tinted
      },
    },
  },
  plugins: [],
};
