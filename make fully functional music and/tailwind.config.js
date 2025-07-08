/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary': {
          50: '#f0f5ff',
          100: '#e6eeff',
          500: '#4a6cf7',
          900: '#1a2b5f'
        },
        'dark': {
          50: '#1a1a1a',
          100: '#2c2c2c',
          500: '#3a3a3a',
          900: '#0a0a0a'
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
      animation: {
        'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
  darkMode: 'class'
}