# Component Patterns

Reference patterns for common landing page components. Use as starting points, adapt to match scraped design.

## Header/Navigation

```tsx
// Sticky header with mobile hamburger
export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <Logo className="size-8" />
          <span className="font-semibold">Brand</span>
        </Link>
        
        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-6">
          <Link href="#features">Features</Link>
          <Link href="#pricing">Pricing</Link>
          <Button>Get Started</Button>
        </nav>
        
        {/* Mobile hamburger */}
        <Sheet>
          <SheetTrigger asChild className="md:hidden">
            <Button variant="ghost" size="icon">
              <Menu className="size-5" />
            </Button>
          </SheetTrigger>
          <SheetContent>{/* Mobile nav items */}</SheetContent>
        </Sheet>
      </div>
    </header>
  )
}
```

## Hero Variants

### Centered Hero
```tsx
export function Hero() {
  return (
    <section className="py-20 md:py-32">
      <div className="container flex flex-col items-center text-center gap-6">
        <Badge>New Feature</Badge>
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight max-w-3xl">
          Headline goes here
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl">
          Subheadline description text
        </p>
        <div className="flex flex-col sm:flex-row gap-4">
          <Button size="lg">Primary CTA</Button>
          <Button size="lg" variant="outline">Secondary CTA</Button>
        </div>
      </div>
    </section>
  )
}
```

### Split Hero (Image + Content)
```tsx
export function Hero() {
  return (
    <section className="py-20">
      <div className="container grid lg:grid-cols-2 gap-12 items-center">
        <div className="flex flex-col gap-6">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
            Headline
          </h1>
          <p className="text-lg text-muted-foreground">Description</p>
          <div className="flex gap-4">
            <Button size="lg">CTA</Button>
          </div>
        </div>
        <div className="relative aspect-video lg:aspect-square">
          <Image src="/images/hero.jpg" alt="Hero" fill className="object-cover rounded-lg" />
        </div>
      </div>
    </section>
  )
}
```

## Features

### 3-Column Grid
```tsx
const features = [
  { icon: Zap, title: "Fast", description: "..." },
  { icon: Shield, title: "Secure", description: "..." },
  { icon: Sparkles, title: "Modern", description: "..." },
]

export function Features() {
  return (
    <section className="py-20 bg-muted/50">
      <div className="container">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold">Features</h2>
          <p className="text-muted-foreground mt-2">Why choose us</p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature) => (
            <Card key={feature.title}>
              <CardHeader>
                <feature.icon className="size-10 text-primary mb-2" />
                <CardTitle>{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
```

### Bento Grid
```tsx
export function Features() {
  return (
    <section className="py-20">
      <div className="container">
        <div className="grid md:grid-cols-3 gap-4">
          <Card className="md:col-span-2 md:row-span-2">{/* Large feature */}</Card>
          <Card>{/* Small feature 1 */}</Card>
          <Card>{/* Small feature 2 */}</Card>
        </div>
      </div>
    </section>
  )
}
```

## Testimonials

### Grid Layout
```tsx
const testimonials = [
  { name: "John", role: "CEO", content: "...", avatar: "/images/avatar-1.jpg" },
  // ...
]

export function Testimonials() {
  return (
    <section className="py-20">
      <div className="container">
        <h2 className="text-3xl font-bold text-center mb-12">What people say</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {testimonials.map((t) => (
            <Card key={t.name}>
              <CardContent className="pt-6">
                <p className="text-muted-foreground mb-4">"{t.content}"</p>
                <div className="flex items-center gap-3">
                  <Avatar>
                    <AvatarImage src={t.avatar} />
                    <AvatarFallback>{t.name[0]}</AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-medium">{t.name}</p>
                    <p className="text-sm text-muted-foreground">{t.role}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
```

## Pricing

```tsx
const plans = [
  { name: "Free", price: "$0", features: ["Feature 1", "Feature 2"] },
  { name: "Pro", price: "$29", features: ["Everything in Free", "Feature 3"], popular: true },
  { name: "Enterprise", price: "Custom", features: ["Everything in Pro", "Feature 4"] },
]

export function Pricing() {
  return (
    <section className="py-20">
      <div className="container">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold">Pricing</h2>
        </div>
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {plans.map((plan) => (
            <Card key={plan.name} className={cn(plan.popular && "border-primary shadow-lg")}>
              <CardHeader>
                {plan.popular && <Badge className="w-fit mb-2">Popular</Badge>}
                <CardTitle>{plan.name}</CardTitle>
                <div className="text-3xl font-bold">{plan.price}<span className="text-sm font-normal">/mo</span></div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-center gap-2">
                      <Check className="size-4 text-primary" />
                      {f}
                    </li>
                  ))}
                </ul>
                <Button className="w-full mt-6">{plan.popular ? "Get Started" : "Choose Plan"}</Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
```

## CTA Section

```tsx
export function CTA() {
  return (
    <section className="py-20 bg-primary text-primary-foreground">
      <div className="container text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to get started?</h2>
        <p className="text-primary-foreground/80 mb-8 max-w-xl mx-auto">
          Join thousands of users already using our platform.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button size="lg" variant="secondary">Get Started Free</Button>
          <Button size="lg" variant="outline" className="border-primary-foreground/20">
            Contact Sales
          </Button>
        </div>
      </div>
    </section>
  )
}
```

## Footer

```tsx
const footerLinks = {
  Product: ["Features", "Pricing", "Changelog"],
  Company: ["About", "Blog", "Careers"],
  Legal: ["Privacy", "Terms"],
}

export function Footer() {
  return (
    <footer className="border-t py-12">
      <div className="container">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div>
            <Logo className="size-8 mb-4" />
            <p className="text-sm text-muted-foreground">
              Brief company description.
            </p>
          </div>
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h4 className="font-medium mb-4">{category}</h4>
              <ul className="space-y-2">
                {links.map((link) => (
                  <li key={link}>
                    <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">
                      {link}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="border-t mt-12 pt-8 text-center text-sm text-muted-foreground">
          © {new Date().getFullYear()} Company. All rights reserved.
        </div>
      </div>
    </footer>
  )
}
```
