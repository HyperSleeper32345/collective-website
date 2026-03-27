# CLAUDE.md - Collective Website Build Brief

This is the single source of truth for the Collective website. Read this entire file before writing any code.

---

## 1. PROJECT CONTEXT

**Client:** David Collins, trustee for David Collins Family Trust, trading as Collective.
**What Collective is:** A revenue operating system company based in Australia. Not a traditional marketing agency.
**Primary brand line:** Make revenue measurable.
**Category positioning:** Collective is a revenue operating system company that helps high-value businesses build a measurable growth model across demand generation, lead capture, qualification, pipeline performance, and operating system visibility.

**Infrastructure (already complete):**
- Domain: wearecollective.com.au (registered at GoDaddy)
- Hosting: Cloudflare Pages (free tier), live at collective-website-1lc.pages.dev
- GitHub: HyperSleeper32345/collective-website
- Auto-deployments: enabled (every push to GitHub triggers a Cloudflare Pages deploy)

---

## 2. TECH CONSTRAINTS

- Static HTML/CSS/JS only. No frameworks. No build tools. No Node.js. No package.json.
- Must deploy cleanly to Cloudflare Pages (static file hosting).
- All pages as .html files in the root directory.
- CSS in a single styles.css file.
- JS in a single main.js file (for interactions like mobile menu, smooth scroll, dark mode transitions).
- Use modern CSS features: CSS custom properties (variables), Container Queries (@container), clamp() for fluid typography. All are well-supported in modern browsers.
- Google Fonts loaded via link tags for now (Playfair Display + Inter).
- Note: The heading font will eventually be upgraded to Canela by Commercial Type (self-hosted .woff2 files in a /fonts folder). The CSS should be structured so this is a single-variable swap when ready.
- No CMS integration yet. All content is hardcoded. Sanity CMS will be added later.

---

## 3. VISUAL IDENTITY AND AESTHETIC

### Core Concept
Collective's visual identity is built on a central metaphor: **Collective reveals the invisible structure of growth.** A butterfly represents organic growth. A scanning/X-ray effect represents measurement and insight. The brand becomes: seeing the system inside growth.

### Hero Animation Concept (homepage)
- Black background.
- A butterfly appears. At first it looks natural and organic. Soft white or very pale blue. Wings slowly moving.
- A subtle horizontal scan line passes across the butterfly. Where the scan touches, wing veins glow, geometric grid overlays appear, structural patterns become visible.
- For a moment the butterfly looks partly like a scientific model, network geometry, or data structure. But still recognisable as a butterfly.
- The structure fades. The butterfly becomes organic again. Loop repeats slowly.
- Motion must be slow and subtle. If the animation is too obvious it will feel gimmicky. Think: calm, elegant, slightly mysterious. The viewer should notice it after a few seconds, not instantly.

**Important: The butterfly animation is aspirational. For the initial build, create a CSS/SVG-based interpretation that captures the essence of this concept. A simplified geometric butterfly with subtle scanning line animation and glowing vein effects using CSS animations and SVG. Do not attempt photorealistic butterfly imagery. The aesthetic should feel like scientific imaging, not nature illustration.**

### Visual Mood
Somewhere between:
- Scientific imaging
- Fashion editorial minimalism
- Natural history museum displays

NOT: tech startup. NOT cyberpunk. NOT crypto. NOT wellness/spirituality.
The mood should feel intelligent and quiet.

### Design Direction
- Black as the dominant background colour, especially for hero sections and the homepage.
- Clean and minimal. Generous whitespace on content sections.
- Let typography and spacing do the heavy lifting.
- Subtle hover animations on buttons and links.
- Smooth scroll between sections.
- No stock photography placeholders. Use solid colour blocks or subtle CSS patterns where images would go, with a comment marking each as IMAGE PLACEHOLDER.

---

## 4. COLOUR SYSTEM

Define all colours as CSS custom properties in :root. The palette is extremely restrained.

### Light Mode (default for content sections)
- --color-bg-primary: #FFFFFF (white backgrounds for content pages)
- --color-bg-secondary: #F5F5F7 (alternating sections, subtle lift)
- --color-bg-dark: #0A0A0F (black backgrounds for hero sections, homepage, footer)
- --color-text-heading: #0A0A0F (heading text on light backgrounds)
- --color-text-body: #6B7280 (body paragraph text)
- --color-text-light: #FFFFFF (text on dark backgrounds)
- --color-text-muted: rgba(255, 255, 255, 0.55) (subheadings on dark backgrounds)
- --color-accent: #5FA8FF (Collective Blue, soft scientific blue. Buttons, links, CTAs, hover states, scanning glow effects)
- --color-accent-hover: #4A93E8 (slightly darker blue for hover states)
- --color-border: rgba(0, 0, 0, 0.08) (subtle borders on light backgrounds)
- --color-border-dark: rgba(255, 255, 255, 0.1) (subtle borders on dark backgrounds)

### Dark Mode
Override variables inside @media (prefers-color-scheme: dark).
- --color-bg-primary: #0A0A0F (near-black primary background)
- --color-bg-secondary: #12121A (slightly lighter surface for sections)
- --color-bg-dark: #0A0A0F (stays the same)
- --color-text-heading: #FFFFFF
- --color-text-body: #9CA3AF (lighter slate for readability)
- --color-text-light: #FFFFFF
- --color-accent: #5FA8FF (stays the same, works in both modes)
- --color-border: rgba(255, 255, 255, 0.08)
- Image placeholders should also adapt (slightly lighter blocks in dark mode so they are visible).
- All interactive elements (buttons, form fields, hover states) must look polished in both modes.
- Do NOT add a manual toggle. Just respect the system preference via the media query.

---

## 5. TYPOGRAPHY

### Heading Font: Playfair Display (Google Fonts)
- Weights: 400, 500, 600, 700
- Use for: hero headlines, page titles, section headings, the word "Collective" in the nav
- This is the launch font. It will be upgraded to Canela by Commercial Type in a future update. Structure CSS so the swap is a single variable change.

### Body Font: Inter (Google Fonts)
- Weights: 400, 500
- Use for: body text, subheadlines, navigation links, buttons, form elements, captions, eyebrow text

### Eyebrow Text (small uppercase labels above headlines)
- Font: Inter
- Size: 12px
- Weight: 500
- Letter-spacing: 0.12em
- Text-transform: uppercase
- Colour: muted (rgba white on dark, rgba black on light)

### Fluid Typography
Use clamp() for heading sizes so text scales smoothly:
- Hero headline: clamp(36px, 5vw, 64px)
- Page title: clamp(28px, 4vw, 48px)
- Section heading: clamp(24px, 3vw, 36px)
- Body: 16px base, line-height 1.65

---

## 6. BRAND VOICE RULES

These rules apply to ALL placeholder copy and any text written for the site.

### The voice should feel:
- Precise, calm, commercially credible
- Systems-oriented, premium, structured
- Confident without hype

### The voice should NOT feel:
- Generic agency-like or "full-service agency"
- Overly consulting, trend-heavy, inflated
- Overly technical for the sake of sounding smart
- Loud or theatrical

### HARD RULES (non-negotiable):
1. **NEVER use the em dash character.** Not in copy. Not in code comments. Not anywhere on the site. Use commas, full stops, colons, or restructure the sentence instead. This is a zero-tolerance rule.
2. **NEVER use the phrase "No fluff" or "no fluff."** This phrase is permanently banned from all Collective output.
3. Never use: "game-changing", "cutting-edge", "bespoke solutions", "full-service agency", "unlock growth", "supercharge", "revolutionary", "next-level", "transformation-driven".
4. Preferred language: measurable, system, operating model, revenue, visibility, diagnose, optimise, pipeline, qualification, clarity, commercial, performance, trust, velocity.
5. Prefer clarity over cleverness. Write as if every sentence must justify its existence.
6. Short paragraphs. Clean sequencing. Minimal adjectives. Strong nouns and verbs.

---

## 7. RESPONSIVE AND ADAPTIVE REQUIREMENTS

This site must be USER-FIRST. It needs to look great however someone views it: phone, tablet, laptop, ultrawide monitor, split-screen window, or anything in between.

- Use CSS Container Queries (@container) for all component-level layout decisions (card grids, service blocks, contact form layout, etc.). Wrap each major content section in a container query container so components respond to their available space, not just the viewport width.
- Use standard @media queries only for page-level layout concerns (navigation behaviour, overall page margins, base font sizing).
- Navigation collapses to hamburger menu on narrow viewports.
- All grids should fluidly adapt from single column to multi-column based on available container space.
- Minimum touch target size 44px on all interactive elements.
- Use fluid typography with clamp() so text scales smoothly across screen sizes.
- The site should look intentional and polished at any width from 320px to 2560px.

---

## 8. SITE ARCHITECTURE

### Main Navigation
Home | System | Services (dropdown) | Collective OS | About | Insights | Contact

### Services Dropdown
- Pitcher
- Catcher
- Closer

### Header CTA: Book a Strategy Call
### Footer CTA: Book a Strategy Call

### Page Order (10 pages total):
1. Home (index.html)
2. System (system.html)
3. Services (services.html)
4. Pitcher (pitcher.html)
5. Catcher (catcher.html)
6. Closer (closer.html)
7. Collective OS (collective-os.html)
8. About (about.html)
9. Insights (insights.html)
10. Contact (contact.html)

---

## 9. CTA SYSTEM

### Primary CTAs
- Book a Strategy Call
- Book a Revenue OS Diagnostic
- Talk to Collective

### Secondary CTAs
- Explore the System
- View Services
- Explore Collective OS
- About Collective
- Read the Thinking
- Send an Enquiry

### Page-Level Primary CTA Mapping
| Page | Primary CTA |
|------|-------------|
| Home | Book a Strategy Call |
| System | Book a Strategy Call |
| Services | Book a Strategy Call |
| Pitcher | Talk to Collective |
| Catcher | Book a Strategy Call |
| Closer | Talk to Collective |
| Collective OS | Book a Revenue OS Diagnostic |
| About | Book a Strategy Call |
| Insights | Book a Strategy Call |
| Contact | Send an Enquiry / Book a Strategy Call |

### Supporting line (use sparingly below primary CTAs):
"Collective works with a limited number of clients at a time to ensure the system is implemented properly."

---

## 10. COMPLETE PAGE COPY

All copy below is approved. Use it exactly as written. Do not add em dashes. Do not add "no fluff". Do not add hype language.

### 10.1 HOMEPAGE (index.html)

**Hero Section:**
- Eyebrow: Collective
- Headline: Make revenue measurable.
- Subheadline: Collective helps high-value businesses turn marketing, lead capture, and sales into one measurable revenue system, so you can see what is working, what is slowing growth, and what to do next.
- Primary CTA: Book a Strategy Call
- Secondary CTA: Explore the System
- Support line: Built for high-value, longer-cycle growth.

**Section 1 - Problem:**
- Heading: Most businesses don't have a lead problem. They have a systems problem.
- Body: More campaigns do not automatically create better outcomes. In most businesses, growth is fragmented. Marketing reports activity. Sales reports outcomes. Leadership is left trying to interpret disconnected signals. That creates predictable problems: inconsistent lead quality, unclear attribution, slow decision-making, weak handoffs, and revenue that feels harder to control than it should. Collective fixes that by turning growth into a measurable operating system.

**Section 2 - System:**
- Heading: One system for every revenue moment.
- Body: Collective is built around four connected layers: Pitcher generates demand. Catcher captures and qualifies it. Closer builds the trust that improves it. Collective OS makes the whole system visible. Instead of isolated tactics, you get a connected model that creates demand, converts it, and measures performance from first touch to closed revenue.
- CTA: Explore the System

**Section 3 - Method:**
- Heading: Growth works better when it is measured properly.
- Body: Collective Revenue OS is the method behind the system. It treats marketing and sales as one measurable continuum and runs on a simple loop: Measure. Diagnose. Optimise. That means less guesswork, fewer random fixes, and faster visibility into where performance is actually breaking.

**Section 4 - Layer Clarity:**
- Heading: Measure the right layer. Fix the right problem.
- Body: One of the biggest causes of wasted spend is misdiagnosis. Collective separates: channel health, conversion performance, and commercial outcomes, so teams can identify the real constraint before changing the wrong thing. A channel should be measured by whether it is doing the job it exists to do.
- CTA: Read the Thinking

**Section 5 - Services:**
- Heading: Services built as system components.
- Pitcher: Lead Generation. Create demand on purpose.
- Catcher: Lead Capture. Respond faster. Book more. Waste nothing.
- Closer: Demand Generation. Be known before you're needed.
- CTA: View Services

**Section 6 - Collective OS:**
- Heading: The operating layer behind measurable revenue.
- Body: Collective OS connects marketing, lead capture, qualification, reporting, and sales visibility into one environment. Without better system visibility, growth stays fragile. With it, growth becomes clearer, faster to diagnose, and easier to govern.
- CTA: Explore Collective OS

**Section 7 - Fit:**
- Heading: Built for businesses where better measurement changes real decisions.
- Body: Collective works best with businesses operating in high-value, longer-cycle environments where timing, trust, and pipeline quality matter. That includes: property development, investment and advisory, high-ticket B2C, and complex B2B services. These are markets where growth cannot be managed well through vanity metrics or disconnected reporting.

**Section 8 - Philosophy:**
- Heading: We believe revenue should behave like a system.
- Body: Collective was built on a simple belief: growth should be measurable, diagnosable, and commercially accountable. That is why we do not position Collective as a traditional agency. We build systems that help leadership understand how revenue is actually being created, and where it is being lost.
- CTA: About Collective

**Final CTA Block:**
- Heading: If revenue matters, measurement matters.
- Body: Collective helps businesses build a measurable revenue system so leadership can make clearer decisions, teams can focus on the right constraints, and growth becomes more predictable.
- Primary CTA: Book a Strategy Call
- Secondary CTA: Send an Enquiry

### 10.2 SYSTEM PAGE (system.html)

**Hero:**
- Eyebrow: The Collective System
- Headline: One system for every revenue moment.
- Subheadline: Collective connects demand generation, lead capture, sales intelligence, and operating system visibility into one measurable revenue model.
- Primary CTA: Book a Strategy Call
- Secondary CTA: View Services

**Core Sections:**
- What the system is: Not an agency stack. A revenue system.
- The four layers: Pitcher, Catcher, Closer, Collective OS.
- The logic behind the system: Growth is easier to improve when the system is visible.
- How diagnosis works: Diagnose before you react. Execution, content, messaging, strategy.
- Why the system matters: Revenue quality depends on more than lead volume.
- What clients actually get: Visibility, control, cleaner diagnosis, stronger coordination.
- CTA: Book a Strategy Call

### 10.3 SERVICES PAGE (services.html)

**Hero:**
- Eyebrow: Services
- Headline: Services built around measurable revenue.
- Subheadline: Collective's services are structured as connected system components designed to improve demand, capture, conversion, and revenue visibility.
- Primary CTA: Book a Strategy Call
- Secondary CTA: Explore the System

**Core Sections:**
- How services are structured: Each service solves a different part of the revenue system.
- Pitcher: Lead Generation
- Catcher: Lead Capture
- Closer: Demand Generation
- Collective OS: Operating System
- How to start: Start with the constraint, not the assumption.

### 10.4 PITCHER PAGE (pitcher.html)

**Hero:**
- Eyebrow: Pitcher
- Headline: Create demand on purpose.
- Subheadline: Pitcher is Collective's lead generation suite, built to turn targeting, messaging, and paid acquisition into qualified pipeline.
- Primary CTA: Talk to Collective
- Secondary CTA: View the System

**Core Sections:**
- What Pitcher does: Lead generation with clearer commercial intent.
- What's included: Paid acquisition, lead pages, tracking, attribution, testing.
- What we measure: CTR, CVR, CPL, qualified opportunity flow, early pipeline signals.
- Where Pitcher fits: When demand is the real constraint.
- CTA: Talk to Collective

### 10.5 CATCHER PAGE (catcher.html)

**Hero:**
- Eyebrow: Catcher
- Headline: Respond faster. Book more. Waste nothing.
- Subheadline: Catcher is Collective's lead capture suite, designed to improve response speed, qualification, booking, and follow-up across the moments where revenue is most often lost.
- Primary CTA: Book a Strategy Call
- Secondary CTA: View the System

**Core Sections:**
- What Catcher does: Lead capture is where good demand often gets wasted.
- What's included: Response workflows, qualification logic, booking systems, enrichment, follow-up.
- What we measure: Speed-to-first-touch, contact rate, booking rate, show rate, qualified meeting rate, LQR.
- Why it matters: A slower handoff creates a weaker pipeline.
- Best fit: When the business already has demand but leaks value after enquiry.
- CTA: Book a Strategy Call

### 10.6 CLOSER PAGE (closer.html)

**Hero:**
- Eyebrow: Closer
- Headline: Be known before you're needed.
- Subheadline: Closer is Collective's demand generation suite, built to increase trust, authority, and familiarity before the sales conversation begins.
- Primary CTA: Talk to Collective
- Secondary CTA: View the System

**Core Sections:**
- What Closer does: Trust changes conversion.
- What's included: Founder knowledge capture, messaging, narrative, SEO, FAQ content, proof assets.
- What it improves: Trust, familiarity, authority, content-assisted conversion, sales cycle efficiency.
- Why it matters: Not all conversion problems start at the point of capture.
- Best fit: Trust-sensitive, higher-value categories.
- CTA: Talk to Collective

### 10.7 COLLECTIVE OS PAGE (collective-os.html)

**Hero:**
- Eyebrow: Collective OS
- Headline: One operating system for every revenue moment.
- Subheadline: Collective OS is the system layer that connects marketing, lead capture, qualification, automation, reporting, and sales visibility into one measurable environment.
- Primary CTA: Book a Revenue OS Diagnostic
- Secondary CTA: Explore the System

**Core Sections:**
- What it is: The command layer behind measurable revenue.
- What it connects: CRM, workflows, source tracking, enrichment, dashboards, governance.
- Why it matters: Without system visibility, growth stays fragile.
- Core modules: Unified CRM, Automation Hub, Data and Enrichment, Dashboards, Governance.
- What it changes: Reporting becomes a decision-making system.
- CTA: Book a Revenue OS Diagnostic

### 10.8 ABOUT PAGE (about.html)

**Hero:**
- Eyebrow: About Collective
- Headline: We are not a marketing agency. We are a revenue operating system company.
- Subheadline: Collective helps businesses turn growth into a measurable system by aligning marketing, lead capture, sales performance, and operating system visibility.
- Primary CTA: Book a Strategy Call
- Secondary CTA: Explore the System

**Core Sections:**
- What we believe: Revenue should behave like a system.
- Why Collective exists: Built for businesses that need more than activity and reporting.
- What makes the company different: We optimise the system, not just the channel.
- Who we work best with: High-value, longer-cycle growth businesses.
- Founder philosophy: Clarity compounds.
- CTA: Book a Strategy Call

### 10.9 INSIGHTS PAGE (insights.html)

**Hero:**
- Eyebrow: Insights
- Headline: Thinking for businesses that want clearer revenue decisions.
- Subheadline: Frameworks, papers, and practical ideas on measurable growth, pipeline performance, and revenue system design.
- Primary CTA: Read the Thinking
- Secondary CTA: Book a Strategy Call

**Core Sections:**
- What this page is: Not content for content's sake.
- Content categories: Revenue Systems, Channel Health, Pipeline Velocity, Sales and Marketing Alignment, Demand Generation and Trust.
- Featured article intros (placeholders for now, will be populated via Sanity CMS later):
  - Collective Revenue OS
  - The Channel Health Framework
  - Pipeline Velocity and Better Revenue Decisions
  - The Collective System
- CTA: Book a Strategy Call

### 10.10 CONTACT PAGE (contact.html)

**Hero:**
- Eyebrow: Contact
- Headline: Let's make revenue measurable.
- Subheadline: If you want better visibility, stronger pipeline performance, and a clearer revenue system, start the conversation here.
- Primary CTA: Book a Strategy Call
- Secondary CTA: Send an Enquiry

**Core Sections:**
- Intro: Start with the real question.
- What to share: Business model, sales cycle, lead generation model, current constraints, visibility gaps.
- Contact paths: Strategy Call, Direct Enquiry.
- Contact form: Name, Email, Phone (optional), Message, Submit button. Form does not need to be functional yet, just the HTML/CSS.
- Closing line: Better systems start with better visibility.

---

## 11. SHARED COMPONENTS

### Navigation Bar
- Logo text "Collective" in Playfair Display 700, left-aligned
- Nav links right-aligned: Home, System, Services (dropdown with Pitcher, Catcher, Closer), Collective OS, About, Insights, Contact
- Header CTA button: "Book a Strategy Call" in accent colour
- Collapses to hamburger menu on narrow viewports
- On dark backgrounds: white text. On light backgrounds: dark text. Should adapt automatically.

### Footer
- "Collective" logo text
- "Make revenue measurable." tagline
- Support line: A revenue operating system for high-value growth.
- Footer nav links: Home, System, Services, Collective OS, About, Insights, Contact
- Footer CTA: Book a Strategy Call
- Copyright: © 2026 David Collins Family Trust trading as Collective
- Email: hello@wearecollective.com.au
- Dark background (#0A0A0F)

### Page Structure Pattern
Each major page should follow this pattern:
1. What it is
2. Why it matters
3. How it works
4. Who it is for / where it fits
5. CTA

---

## 12. IMPLEMENTATION RULES

### Layout Rules
- Headline should carry the emotional and category weight.
- Subheadline should explain clearly.
- Keep paragraphs short.
- Use cards for system and service sections.
- Do not overload the hero with proof clutter.
- Use whitespace generously.

### Messaging Rules
- Always position Collective as a revenue operating system company.
- Never drift into "full-service agency" language.
- Keep AI as a quiet supporting layer, not the lead promise.
- Keep "measurement", "visibility", "pipeline", and "system" as recurring anchors.
- Prefer clarity over cleverness.

### Technical Rules
- Do NOT use any build tools, bundlers, or package managers.
- Do NOT install any npm packages.
- Do NOT create a package.json.
- Every page shares the same nav and footer (copy the HTML, no templating system at this stage).
- Use semantic HTML5 elements (header, nav, main, section, footer).
- Include proper meta tags and page titles on every page.
- Make sure all internal links work correctly between pages.

---

## 13. FILE STRUCTURE

```
collective-website/
├── index.html
├── system.html
├── services.html
├── pitcher.html
├── catcher.html
├── closer.html
├── collective-os.html
├── about.html
├── insights.html
├── contact.html
├── styles.css
├── main.js
├── CLAUDE.md
└── README.md
```

---

## 14. BUILD ORDER

1. styles.css (complete colour system, typography, layout utilities, dark mode, container queries)
2. main.js (mobile menu, smooth scroll, any interaction logic)
3. index.html (homepage, most complex page, sets the pattern)
4. Shared nav and footer pattern established from homepage
5. system.html
6. services.html
7. pitcher.html, catcher.html, closer.html
8. collective-os.html
9. about.html
10. insights.html
11. contact.html
12. README.md (update with project description)

Build all pages. Start with styles.css and main.js, then build each page in order.
