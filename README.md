# AI Skills Collection

A curated collection of AI agent skills designed to enhance Claude's capabilities with specialized knowledge, workflows, and tool integrations. These skills transform Claude from a general-purpose assistant into a domain-specific expert. Made by Faiz Intifada (@faizntfd)

## What are Skills?

Skills are modular, self-contained packages that provide:
- **Specialized workflows** - Multi-step procedures for specific domains
- **Tool integrations** - Instructions for working with specific file formats or APIs  
- **Domain expertise** - Structured knowledge, schemas, and business logic
- **Bundled resources** - Scripts, references, and assets for complex tasks

## Available Skills

| Skill | Description | Category |
|-------|-------------|----------|
| [frontend-design](./skills/frontend-design) | Create distinctive, production-grade frontend interfaces with high design quality | Frontend |
| [frontend-ui-animator](./skills/frontend-ui-animator) | Implement purposeful UI animations for Next.js + Tailwind + React projects | Frontend |
| [frontend-ui-integration](./skills/frontend-ui-integration) | Extend user-facing workflows integrating with existing backend APIs | Frontend |
| [shadcn-management](./skills/shadcn-management) | Manage shadcn/ui components using MCP tools | Frontend |
| [rsc-data-optimizer](./skills/rsc-data-optimizer) | Optimize Next.js data fetching with React Server Components | Frontend |
| [backend-dev](./skills/backend-dev) | Comprehensive backend development from API design to deployment | Backend |
| [product-management](./skills/product-management) | PRDs, feature analysis, user research synthesis, and roadmap planning | Planning |
| [task-generator](./skills/task-generator) | Generate structured task lists from specs or requirements | Planning |
| [agents-md-generator](./skills/agents-md-generator) | Generate hierarchical AGENTS.md structures for codebases | Documentation |
| [browser](./skills/browser) | Chrome DevTools Protocol tools for browser automation and scraping | Automation |
| [skill-creator](./skills/skill-creator) | Guide for creating effective AI skills | Meta |
| [template-skill](./skills/template-skill) | Basic template for creating new skills | Meta |

## Skill Categories

### Frontend Development

#### `frontend-design`
Create distinctive, memorable frontend interfaces that avoid generic "AI slop" aesthetics. Features:
- Bold aesthetic direction and creative design thinking
- Typography, color, motion, and spatial composition guidelines
- Integration with shadcn/ui projects
- Production-grade, functional code output

#### `frontend-ui-animator`
Implement purposeful, performant UI animations. Includes:
- 20+ ready-to-use animation patterns (fade, slide, scale, clip-reveal, marquee)
- Scroll-triggered animations with `useScrollReveal` hook
- Tailwind config presets for keyframes and animations
- Accessibility-first with `prefers-reduced-motion` support
- Phased implementation workflow (Analyze → Plan → Implement → Verify)

#### `frontend-ui-integration`
Implement or extend user-facing workflows with existing backend APIs. Covers:
- React + TypeScript conventions
- Design system integration
- State management patterns
- Testing requirements (unit, integration, component tests)

#### `shadcn-management`
Manage shadcn/ui components via MCP tools:
- Search and discover components in registries
- View implementation details and examples
- Get installation commands
- Build complex UI features with multiple components

#### `rsc-data-optimizer`
Optimize slow client-side data fetching to instant server-side rendering:
- Convert useEffect + useState patterns to Server Components
- Parallel data fetching with Promise.all
- Hybrid SSR + client-side patterns
- Streaming with Suspense boundaries
- Caching strategies (static, revalidate, on-demand)

### Backend Development

#### `backend-dev`
End-to-end backend development workflow:
- Multi-expert system (Architect, Security Engineer, DevOps, Database Specialist)
- API design and database architecture
- Security-first implementation
- CI/CD and infrastructure automation
- Testing strategies (unit, integration, E2E, load testing)

### Planning & Documentation

#### `product-management`
Core product management activities:
- Writing and updating PRDs
- Feature request analysis (RICE, ICE frameworks)
- User research synthesis
- Roadmap planning
- Competitive analysis

#### `task-generator`
Generate structured task lists from specs or requirements:
- 2-phase workflow (parent tasks → sub-tasks)
- Markdown checklist format with relevant files
- Automatically triggered after ExitSpecMode
- Junior developer-friendly task descriptions

#### `agents-md-generator`
Generate hierarchical AGENTS.md structures optimized for AI coding agents:
- Lightweight root files with links to detailed sub-files
- Token-efficient JIT indexing
- Technology-specific templates (Design Systems, Database, API, Testing)

### Automation & Tools

#### `browser`
Minimal Chrome DevTools Protocol tools:
- Start Chrome with or without profile
- Navigate pages
- Execute JavaScript
- Take screenshots
- Interactive element picker

#### `skill-creator`
Guide for creating effective AI skills:
- Skill anatomy and structure
- Progressive disclosure patterns
- Best practices for SKILL.md writing
- Packaging and validation scripts

#### `template-skill`
Basic template for creating new skills:
- Minimal SKILL.md structure
- Ready to customize for new skill development

## Installation

### For Factory AI Users

Copy desired skill folders to your Factory skills directory:

```bash
# Copy a single skill
cp -r skills/frontend-ui-animator ~/.factory/skills/

# Or copy all skills
cp -r skills/* ~/.factory/skills/
```

### Manual Installation

1. Clone this repository
2. Copy the desired skill folder to your AI agent's skills directory
3. Ensure the skill's dependencies are available (check individual skill READMEs if present)

## Skill Structure

Each skill follows a consistent structure:

```
skill-name/
├── SKILL.md              # Main skill instructions (required)
├── references/           # Additional documentation loaded on-demand
│   └── *.md
├── scripts/              # Executable code (Python/Bash)
│   └── *.py
└── assets/               # Templates, images, boilerplate
    └── *
```

### SKILL.md Format

```yaml
---
name: skill-name
description: What the skill does and when to use it
---

# Skill Instructions

Markdown content with workflows, patterns, and guidelines.
```

## Usage Examples

### Frontend UI Animation

```
User: "Add animations to my landing page"

→ Skill analyzes pages and components
→ Creates animation audit table
→ Implements phased animations (hero → hover → scroll reveals)
→ Adds Tailwind config presets
→ Ensures accessibility compliance
```

### Backend API Development

```
User: "Create a REST API for user management"

→ Skill coordinates expert systems
→ Designs API contracts and database schema
→ Implements secure authentication
→ Sets up testing and CI/CD
→ Generates deployment documentation
```

### Product Requirements

```
User: "Write a PRD for a new search feature"

→ Skill gathers context and constraints
→ Structures problem statement and goals
→ Defines user stories and requirements
→ Documents technical considerations
→ Identifies risks and launch plan
```

## Contributing

Contributions are welcome! When adding new skills:

1. Follow the skill structure outlined above
2. Keep `SKILL.md` under 500 lines
3. Use `references/` for detailed documentation
4. Include concrete examples with actual file paths
5. Test the skill with real-world scenarios

## License

Individual skills may have their own licenses. Check each skill's directory for specific licensing information.

---

Built for [Factory AI](https://factory.ai) and compatible AI coding assistants.

Curated & Created by Faiz Intifada (@faizntfd)
