# Tech Stack Reference

## Next.js 16 App Router

### File Structure
```
app/
├── layout.tsx      # Root layout (required)
├── page.tsx        # Home page
├── globals.css     # Global styles
└── favicon.ico

components/
├── ui/             # Shadcn components
└── landing/        # Page-specific components

public/
└── images/         # Static assets

lib/
└── utils.ts        # cn() utility
```

### Root Layout Template
```tsx
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import "./globals.css"

export const metadata: Metadata = {
  title: "Site Title",
  description: "Site description from scraped meta tags",
  openGraph: {
    title: "Site Title",
    description: "Description",
    images: ["/images/og-image.jpg"],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={GeistSans.className}>
      <body className="min-h-screen bg-background antialiased">
        {children}
      </body>
    </html>
  )
}
```

### Page Template
```tsx
import { Header } from "@/components/landing/Header"
import { Hero } from "@/components/landing/Hero"
import { Features } from "@/components/landing/Features"
import { Footer } from "@/components/landing/Footer"

export default function Home() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <Features />
        {/* Other sections */}
      </main>
      <Footer />
    </>
  )
}
```

## Tailwind CSS v4

### globals.css Structure
```css
@import "tailwindcss";

:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --card: 0 0% 100%;
  --card-foreground: 222.2 84% 4.9%;
  --popover: 0 0% 100%;
  --popover-foreground: 222.2 84% 4.9%;
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
  --secondary: 210 40% 96.1%;
  --secondary-foreground: 222.2 47.4% 11.2%;
  --muted: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;
  --accent: 210 40% 96.1%;
  --accent-foreground: 222.2 47.4% 11.2%;
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 210 40% 98%;
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 4.9%;
  --radius: 0.5rem;
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  /* ... dark mode tokens */
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

### Responsive Breakpoints (Mobile First)
```
sm: 640px   - Small tablets
md: 768px   - Tablets
lg: 1024px  - Small laptops
xl: 1280px  - Desktops
2xl: 1536px - Large screens
```

### Common Patterns
```tsx
// Container with max-width
<div className="container mx-auto px-4">

// Responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

// Responsive text
<h1 className="text-3xl md:text-4xl lg:text-5xl">

// Responsive spacing
<section className="py-12 md:py-20 lg:py-32">

// Responsive visibility
<div className="hidden md:block">  // Hide on mobile
<div className="md:hidden">        // Show only on mobile
```

## Shadcn UI

### Required Components (Install as needed)
```bash
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add badge
npx shadcn@latest add avatar
npx shadcn@latest add sheet
npx shadcn@latest add accordion
npx shadcn@latest add input
```

### cn() Utility
```ts
// lib/utils.ts
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### Usage Pattern
```tsx
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

<Button className={cn("w-full", isActive && "bg-primary")}>
  Click me
</Button>
```

## Lucide React Icons

### Import Pattern
```tsx
import { Menu, X, ChevronRight, Check, Zap, Shield, Star } from "lucide-react"

// Usage
<Menu className="size-5" />
<Check className="size-4 text-primary" />
```

### Common Icons for Landing Pages
- Navigation: `Menu`, `X`, `ChevronDown`, `ChevronRight`
- Actions: `ArrowRight`, `ExternalLink`, `Download`
- Features: `Zap`, `Shield`, `Star`, `Sparkles`, `Rocket`
- Social: `Github`, `Twitter`, `Linkedin`
- Status: `Check`, `X`, `AlertCircle`, `Info`

## Image Handling

### Next.js Image Component
```tsx
import Image from "next/image"

// With fill (for responsive containers)
<div className="relative aspect-video">
  <Image 
    src="/images/hero.jpg" 
    alt="Description" 
    fill 
    className="object-cover"
    priority // for above-the-fold images
  />
</div>

// With fixed dimensions
<Image 
  src="/images/logo.png" 
  alt="Logo" 
  width={120} 
  height={40}
/>
```

### Unsplash Fallback URLs
```tsx
// Hero backgrounds (1920x1080)
"https://images.unsplash.com/photo-1557683316-973673baf926?w=1920&h=1080&fit=crop"

// Feature images (800x600)
"https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=600&fit=crop"

// Avatars (100x100)
"https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face"

// Abstract/patterns
"https://images.unsplash.com/photo-1557682250-33bd709cbe85?w=1200&h=800&fit=crop"
```

## SEO Metadata

### Extract from scrape and apply:
```tsx
export const metadata: Metadata = {
  title: "Page Title | Brand",
  description: "Meta description from scrape",
  keywords: ["keyword1", "keyword2"],
  authors: [{ name: "Author" }],
  openGraph: {
    title: "OG Title",
    description: "OG Description",
    url: "https://example.com",
    siteName: "Brand",
    images: [
      {
        url: "/images/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "OG Image Alt",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Twitter Title",
    description: "Twitter Description",
    images: ["/images/twitter-image.jpg"],
  },
}
```
