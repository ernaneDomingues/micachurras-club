/** @type {import('tailwindcss').Config} */

// Vamos usar a paleta de cores da camiseta!
const colors = {
    'mch-primary': '#04a1af', // O azul-piscina principal
    'mch-accent': '#e14b4f',  // O vermelho/laranja
    'mch-sun': '#f7b031',     // O amarelo sol
    'mch-dark': '#1a2b47',    // O azul escuro do gradiente
    'mch-light': '#fdfdfd',   // Branco
  }
  
  
  module.exports = {
    content: [
      "./mch_app/templates/**/*.html", // Diz ao Tailwind para olhar nossos HTMLs
    ],
    theme: {
      extend: {
        colors: colors, // Adiciona nossas cores customizadas
        fontFamily: {
          // (Vamos adicionar as fontes do Google Fonts aqui depois)
          'font-sans': ['Nunito', 'sans-serif'],
          'font-display': ['Bungee', 'cursive'],
        }
      },
    },
    plugins: [],
  }
  