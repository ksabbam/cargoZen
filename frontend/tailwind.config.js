/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // iOS system colors
        ios: {
          blue:    '#007AFF',
          green:   '#34C759',
          indigo:  '#5856D6',
          orange:  '#FF9500',
          pink:    '#FF2D55',
          purple:  '#AF52DE',
          red:     '#FF3B30',
          teal:    '#30B0C7',
          yellow:  '#FFCC00',
          gray:    '#8E8E93',
          gray2:   '#AEAEB2',
          gray3:   '#C7C7CC',
          gray4:   '#D1D1D6',
          gray5:   '#E5E5EA',
          gray6:   '#F2F2F7',
          bg:      '#F2F2F7',
          surface: '#FFFFFF',
        },
      },
      fontFamily: {
        sans: ['"Inter"', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'sans-serif'],
      },
      fontSize: {
        '2xs': ['10px', '14px'],
        xs:   ['12px', '16px'],
        sm:   ['13px', '18px'],
        base: ['15px', '22px'],
        lg:   ['17px', '24px'],
        xl:   ['20px', '26px'],
        '2xl':['24px', '30px'],
        '3xl':['28px', '34px'],
      },
      borderRadius: {
        none:  '0',
        sm:    '6px',
        DEFAULT:'8px',
        md:    '10px',
        lg:    '12px',
        xl:    '16px',
        '2xl': '20px',
        '3xl': '24px',
        full:  '9999px',
      },
      boxShadow: {
        xs:   '0 1px 2px rgba(0,0,0,0.04)',
        sm:   '0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)',
        DEFAULT:'0 2px 8px rgba(0,0,0,0.07), 0 0 1px rgba(0,0,0,0.05)',
        md:   '0 4px 16px rgba(0,0,0,0.08), 0 0 1px rgba(0,0,0,0.04)',
        lg:   '0 8px 30px rgba(0,0,0,0.10), 0 0 1px rgba(0,0,0,0.04)',
        xl:   '0 16px 50px rgba(0,0,0,0.14), 0 0 1px rgba(0,0,0,0.04)',
        'inner-sm': 'inset 0 1px 2px rgba(0,0,0,0.06)',
      },
      transitionTimingFunction: {
        'spring': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
        'ease-ios': 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
      },
    },
  },
  plugins: [],
}