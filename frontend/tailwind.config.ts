import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./hooks/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["'Space Grotesk'", "'Segoe UI'", "sans-serif"],
        mono: ["'IBM Plex Mono'", "'Fira Code'", "monospace"],
      },
      boxShadow: {
        glow: "0 12px 36px rgba(2, 132, 199, 0.28)",
      },
    },
  },
  plugins: [],
};

export default config;
