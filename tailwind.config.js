/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Neo Brutalism UI Library colors - 仿照图片配色
        brutal: {
          yellow: '#FEF445',      // 明亮柠檬黄 (和图片一致)
          pink: '#FF69B4',        // 活泼粉色 (和图片一致)  
          cyan: '#7FFFD4',        // 薄荷青色 (和图片背景一致)
          green: '#98FB98',       // 浅绿色（恢复原色）
          orange: '#FFB347',      // 温暖橙色
          red: '#FF6B6B',         // 珊瑚红色
          blue: '#87CEEB',        // 天空蓝色
          purple: '#DDA0DD',      // 淡紫色 (和图片一致)
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      // Neo Brutalism UI Library shadows - 仿照图片风格
      boxShadow: {
        'brutal': '6px 6px 0px 0px #2563EB',        // 蓝色阴影 (和图片一致)
        'brutal-sm': '3px 3px 0px 0px #2563EB',     // 小蓝色阴影
        'brutal-lg': '9px 9px 0px 0px #2563EB',     // 大蓝色阴影
        'brutal-yellow': '6px 6px 0px 0px #2563EB, 0px 0px 0px 3px #FEF445',
        'brutal-pink': '6px 6px 0px 0px #2563EB, 0px 0px 0px 3px #FF69B4',
        'brutal-cyan': '6px 6px 0px 0px #2563EB, 0px 0px 0px 3px #7FFFD4',
        'brutal-green': '6px 6px 0px 0px #2563EB, 0px 0px 0px 3px #98FB98',
      },
    },
  },
  plugins: [require("@tailwindcss/forms"), require("@tailwindcss/typography")],
}