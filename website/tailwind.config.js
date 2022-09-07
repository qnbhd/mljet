/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "super": "#1CF1CC",
        "prim": "#9733f5",
        "super-hover": "#C97BFF",
        "chick": "#DF38FA"
      }
    },
  },
  plugins: []
}