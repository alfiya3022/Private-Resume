/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: {
          DEFAULT: '#FAF8F5',
          card: '#FFFFFF',
          muted: '#F3EFE6',
          border: '#E2DCD2',
          darkborder: '#1A1A1A',
        },
        charcoal: {
          DEFAULT: '#1A1A1A',
          muted: '#52525B',
          light: '#71717A',
        },
        coral: {
          DEFAULT: '#E05A47',
          hover: '#CD4836',
          light: '#FDEEEB',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'monospace'],
      },
      boxShadow: {
        'brutal': '3px 3px 0px #1A1A1A',
        'brutal-sm': '2px 2px 0px #1A1A1A',
        'brutal-hover': '1px 1px 0px #1A1A1A',
      },
    },
  },
  plugins: [],
};
