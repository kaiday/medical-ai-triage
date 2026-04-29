import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#e8f8f4',
          100: '#cff1ea',
          500: '#0e9487',
          700: '#07645d',
          800: '#05554f',
        },
        coral: {
          50: '#fff0ee',
          500: '#ff6b5f',
          600: '#f35d52',
        },
        clinic: {
          canvas: '#f7fbf8',
          card: '#ffffff',
          border: '#dde7e2',
          mint: '#cff8f5',
          green: '#eaf8ef',
          cyan: '#d6f7f7',
          pink: '#fbe7eb',
          orange: '#fadba8',
        },
        ink: {
          900: '#101828',
          700: '#27364a',
          500: '#536179',
          400: '#7a8699',
        },
      },
      boxShadow: {
        card: '0 18px 45px rgba(16, 24, 40, 0.06)',
        soft: '0 12px 28px rgba(6, 100, 94, 0.08)',
      },
      fontFamily: {
        sans: ['Inter', 'Manrope', 'Plus Jakarta Sans', 'Segoe UI', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config;
