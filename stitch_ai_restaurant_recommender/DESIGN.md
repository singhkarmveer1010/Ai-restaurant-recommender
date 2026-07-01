---
name: Lumina Gastronomy
colors:
  surface: '#141218'
  surface-dim: '#141218'
  surface-bright: '#3b383e'
  surface-container-lowest: '#0f0d13'
  surface-container-low: '#1d1b20'
  surface-container: '#211f24'
  surface-container-high: '#2b292f'
  surface-container-highest: '#36343a'
  on-surface: '#e6e0e9'
  on-surface-variant: '#cbc4d2'
  inverse-surface: '#e6e0e9'
  inverse-on-surface: '#322f35'
  outline: '#948e9c'
  outline-variant: '#494551'
  surface-tint: '#cfbcff'
  primary: '#cfbcff'
  on-primary: '#381e72'
  primary-container: '#6750a4'
  on-primary-container: '#e0d2ff'
  inverse-primary: '#6750a4'
  secondary: '#cdc0e9'
  on-secondary: '#342b4b'
  secondary-container: '#4d4465'
  on-secondary-container: '#bfb2da'
  tertiary: '#e7c365'
  on-tertiary: '#3e2e00'
  tertiary-container: '#c9a74d'
  on-tertiary-container: '#503d00'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e9ddff'
  primary-fixed-dim: '#cfbcff'
  on-primary-fixed: '#22005d'
  on-primary-fixed-variant: '#4f378a'
  secondary-fixed: '#e9ddff'
  secondary-fixed-dim: '#cdc0e9'
  on-secondary-fixed: '#1f1635'
  on-secondary-fixed-variant: '#4b4263'
  tertiary-fixed: '#ffdf93'
  tertiary-fixed-dim: '#e7c365'
  on-tertiary-fixed: '#241a00'
  on-tertiary-fixed-variant: '#594400'
  background: '#141218'
  on-background: '#e6e0e9'
  surface-variant: '#36343a'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.04em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: '0'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
    letterSpacing: '0'
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
    letterSpacing: '0'
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: '1.2'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 40px
  xl: 64px
  sidebar_width: 280px
  max_content_width: 1440px
---

## Brand & Style
The design system embodies a premium, high-fidelity SaaS aesthetic tailored for high-end restaurant discovery. It targets food enthusiasts and travelers seeking a sophisticated, data-driven experience. The visual narrative combines a deep, cinematic "Dark Mode" with vibrant, energetic gradients to evoke the warmth of a kitchen and the precision of AI.

The style is a hybrid of **Modern Corporate** and **Glassmorphism**, prioritizing clarity, depth, and technical excellence. It draws inspiration from industry leaders like Linear and Vercel, utilizing high-contrast accents, fine borders, and deep background blurs to create a sense of organized luxury.

## Colors
The palette is built on a "Near-Black Blue" foundation to provide a rich, expansive feel that reduces eye strain. 

- **Primary Brand Expression:** A vibrant three-point gradient (Orange-Red-Pink) used for primary actions, progress indicators, and AI-driven highlights.
- **Accents:** Violet is used for premium "AI" features; Gold is reserved for ratings and Michelin-star tier status; Emerald signifies "Open" status and positive health/safety metrics.
- **Surface Strategy:** Backgrounds are layered. The deepest level is the main canvas (#0a0a0f), with the sidebar (#12121a) and cards providing elevated containers.

## Typography
Inter is the exclusive typeface for this design system, chosen for its exceptional legibility and neutral, systematic character.

- **Weight Utilization:** Use 800 (Extra Bold) for display titles to create a strong visual anchor. Body copy should alternate between 300 (Light) for secondary descriptions and 400 (Regular) for standard text. 600 (Semi Bold) is reserved for navigation and semantic labels.
- **Scaling:** For mobile devices, tighten the letter spacing on headlines and reduce the font size to ensure restaurant names do not wrap excessively.

## Layout & Spacing
The layout follows a **Fixed-Fluid hybrid** model. The sidebar remains at a fixed 280px width, while the main content area utilizes a 12-column fluid grid.

- **Grid:** Use a 24px gutter between columns to allow the glassmorphic card edges to remain distinct.
- **Margins:** Desktop views should maintain a minimum of 40px outer padding. Mobile views should drop to 16px.
- **Density:** Maintain high whitespace around restaurant imagery to preserve the "Premium" feel. Avoid information density that feels cluttered.

## Elevation & Depth
Depth is achieved through **Glassmorphism** and subtle border treatments rather than traditional heavy shadows.

- **Layer 0 (Background):** #0a0a0f.
- **Layer 1 (Sidebar):** #12121a with a 1px solid border-right (rgba(255,255,255,0.08)).
- **Layer 2 (Cards/Modals):** A semi-transparent fill of `rgba(255,255,255, 0.04)` with a `blur(16px)` backdrop filter. All elevated elements must have a 1px solid border of `rgba(255,255,255, 0.08)` to define their silhouette against the dark background.
- **Interactions:** On hover, card borders should transition to `rgba(255,255,255, 0.2)` to indicate focus.

## Shapes
The shape language is "Soft-Modern," using consistent radii to balance the technical nature of the UI.

- **Containers:** Standard cards and containers use a 0.5rem (8px) or 1rem (16px) radius depending on size.
- **Interactive Elements:** Buttons use a specific 12px radius to differentiate them from static containers.
- **Tags/Badges:** All status badges (e.g., "Sushi", "Open Now") must be fully pill-shaped (9999px) to contrast against the more geometric card structures.

## Components

- **Buttons:** 
  - *Primary:* Filled with the 3-color brand gradient, white text (Weight 600), 12px radius.
  - *Secondary:* Transparent background, 1px border (`rgba(255,255,255,0.1)`), 12px radius, hover state increases border opacity.
- **Cards (Restaurant/Review):**
  - Use the glassmorphism spec (4% fill, 16px blur). 
  - Padding: 20px. 
  - Image aspect ratio: 16:9 for list views, 4:3 for grid views.
- **Inputs:**
  - Background: `rgba(0,0,0,0.2)`; Border: 1px `rgba(255,255,255,0.1)`.
  - Focus state: Border color changes to the Primary Orange (#f97316).
- **Badges:**
  - Full-pill shape. Use subtle semi-transparent background colors based on the accent palette (e.g., Emerald at 10% opacity for "Open").
- **Sidebar Nav Items:**
  - Active state: 1px right-aligned primary gradient border or a subtle violet glow.
  - Inactive: Secondary text color (#94a3b8), Weight 500.
- **AI Recommendation Sparkle:**
  - Small, animated sparkles using the Violet (#8b5cf6) or Gold (#fbbf24) accents to denote machine-learning-derived content.