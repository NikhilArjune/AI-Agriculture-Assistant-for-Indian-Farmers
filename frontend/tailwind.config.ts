import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f0fdf4",
          100: "#dcfce7",
          500: "#22c55e",
          600: "#16a34a",
          700: "#15803d",
          900: "#14532d",
        },
        earth: {
          100: "#fef3c7",
          500: "#d97706",
          700: "#b45309",
        },
      },
      fontFamily: {
        sans: ["Noto Sans", "Segoe UI", "Roboto", "sans-serif"],
        devanagari: ["Noto Sans Devanagari", "Noto Sans", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
