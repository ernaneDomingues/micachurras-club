/** @type {import('tailwindcss').Config} */
const defaultTheme = require('tailwindcss/defaultTheme');

module.exports = {
  content: [
    './mch_app/templates/**/*.html'
  ],
  theme: {
    extend: {
      // Fontes inspiradas na camiseta
      fontFamily: {
        'sans': ['Nunito', ...defaultTheme.fontFamily.sans],
        'display': ['Bungee', ...defaultTheme.fontFamily.sans],
      },
      // Paleta de cores inspirada na camiseta
      colors: {
        'mch-primary': '#00A0B0', // Azul-piscina principal
        'mch-accent': '#E84A5F',  // Vermelho/Laranja
        'mch-sun': '#FFC107',     // Amarelo Sol
        'mch-dark': '#073B4C',     // Azul escuro (gradiente)
      },
    },
  },
  plugins: [
    // Adiciona o plugin de formulários
    require('@tailwindcss/forms'),
  ],
}

