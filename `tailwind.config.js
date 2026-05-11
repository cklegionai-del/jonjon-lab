module.exports = {
  theme: {
    extend: {
      colors: {
        'color-1': '#ff0000',
        'color-2': '#00ff00',
        'color-3': '#0000ff',
        'color-4': '#ffff00',
        'color-5': '#00ffff',
      },
    },
  },
  plugins: [
    require('tailwindcss-dir')({
      default: 'ltr', // Default direction
      rtl: true, // Enable RTL support
    }),
  ],
}
