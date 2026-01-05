/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fff8f0',
          500: '#c87b2f',
          600: '#8e4d12',
          700: '#6b3a0e',
          900: '#3d2207',
        },
        dark: {
          50: '#f5f5f5',
          100: '#d0d0d0',
          700: '#1a1a1a',
          800: '#0a0a0a',
          900: '#000000',
        },
      },
    },
  },
  plugins: [],
}
