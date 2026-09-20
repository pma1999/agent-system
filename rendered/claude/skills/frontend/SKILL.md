---
name: frontend
description: Use when the task builds or reshapes any user-facing surface - landing page, website, app screen, dashboard, admin tool, component, prototype, demo, or game UI. Sets the visual and UX bar: mode (extend or redesign), art direction, tokens and theming including dark mode, composition, dense product surfaces, states, accessibility, motion, and the checks the result must pass.
---

# Frontend skill

Use this skill when the quality of the work depends on art direction, hierarchy, restraint, tokens, states, and motion rather than component count.

Goal: ship interfaces that feel deliberate, premium, and current, and that hold up when someone actually uses them - at 375px, in dark mode, with a keyboard, with an empty list, with a failed request.

## 0. Declare the mode first

Before any decision about layout or color, state which of these you are in. They lead to different work, and getting this wrong is the most expensive mistake in the skill.

- **Extend** - a design language, token set, or component library already exists. **This is the default for work inside a real product.** Conform to it: reuse its tokens, its components, its spacing scale, its motion. Raise quality *within* it. Do not introduce a second visual language, a second button, or a second way to show an error. Fix inconsistency only where this work touches it; log the rest as follow-up.
- **Redesign** - the user asked to improve or redesign. Design from scratch. Do not inherit the current visual and interaction decisions by default; keep only what survives review. Define the new direction and the migration path for surfaces outside this scope.
- **Greenfield** - nothing exists yet. Design from scratch the best UI/UX for this product and audience.

In Extend mode, most of the sections below are constraints you inherit rather than choices you make. Read the existing tokens and components **before** writing anything, and say in one line what you found.

## 1. Working model

Before building, write three things:

- **visual thesis**: one sentence describing mood, material, and energy
- **content plan**: what each section is for, in order
- **interaction thesis**: 2-3 motion ideas that change the feel of the surface

Each section gets one job, one dominant visual idea, and one primary takeaway or action.

"Clean", "modern", and "professional" are not a direction. If a reference exists - mockup, existing screen, brand kit, a competitor the user named - prefer it over prose. If nothing is decided and no reference exists, pick one and justify it in a line. Do not ship options.

## 2. Tokens and theming

Every visual decision is a token, not a literal. Define them once and use them everywhere; a hardcoded hex or a magic pixel value in a component is a defect.

- **Color**: surface, raised surface, border, text primary/secondary/disabled, accent, and one semantic set (success, warning, danger, info). One accent by default. Define them as variables, not as values scattered through the markup.
- **Type**: a scale with a named role per step (display, title, body, caption), one or two typefaces maximum, line-height and measure set deliberately. Body text stays comfortable to read: roughly 60-75 characters per line.
- **Space**: one scale, used for everything. Do not mix `12px` here and `0.8rem` there.
- **Radius and elevation**: a small set of steps. Elevation means something (this thing floats above that one), it is not decoration.
- **State**: hover, active, focus-visible, disabled, selected, loading. Define these once per interactive element type. Focus-visible is not optional and is never `outline: none` without a replacement.

**Dark mode is a first-class requirement, not an appendix.** If the product has a dark theme, or the platform default suggests one, design both from the start: pick token values per theme rather than filtering or inverting, check contrast in both, and make sure imagery, shadows, and borders still read. Shadows carry almost no weight on a dark surface - use border and surface-level contrast instead. Respect the system preference, and if you offer a toggle, persist it and avoid a flash of the wrong theme on load.

## 3. Composition

- Start with composition, not components.
- Use whitespace, alignment, scale, cropping, and contrast before adding chrome.
- Default to cardless layouts. Use sections, columns, dividers, lists, and media blocks instead.
- One dominant idea per section.
- If a panel can become plain layout without losing meaning, remove the card treatment.

## 4. Landing and marketing pages

Default sequence:

1. **Hero**: brand or product, promise, CTA, and one dominant visual
2. **Support**: one concrete feature, offer, or proof point
3. **Detail**: atmosphere, workflow, product depth, or story
4. **Final CTA**: convert, start, visit, or contact

Hero rules:

- One composition only. Full-bleed image or dominant visual plane.
- Canonical full-bleed rule: on branded landing pages the hero runs edge-to-edge with no inherited page gutters, framed container, or shared max-width; constrain only the inner text/action column.
- Brand first, headline second, body third, CTA fourth. Make the brand or product name the loudest text.
- No hero cards, stat strips, logo clouds, pill soup, or floating dashboards by default.
- Headlines around 2-3 lines on desktop, readable in one glance on mobile.
- Keep the text column narrow and anchored to a calm area of the image, with strong contrast and clear tap targets.

If the first viewport still works after removing the image, the image is too weak. If the brand disappears after hiding the nav, the hierarchy is too weak.

**Viewport budget.** A sticky or fixed header counts against the hero: header plus hero content must fit the initial viewport at common desktop and mobile sizes. With `100vh`/`100svh` heroes, subtract persistent chrome (`calc(100svh - header-height)`) or overlay the header instead of stacking it in flow.

## 5. Product surfaces: apps, dashboards, admin tools

Default to Linear-style restraint: calm surface hierarchy, strong typography and spacing, few colors, dense but readable information, minimal chrome. Cards only when the card is the interaction.

Organize around a primary workspace, navigation, secondary context or inspector, and one clear accent for action or state.

Avoid: dashboard-card mosaics, thick borders on every region, decorative gradients behind routine product UI, multiple competing accent colors, ornamental icons that do not improve scanning.

### Tables and lists

- Decide the row's job first: scanning, comparing, or acting. That decides density, alignment, and what is truncated.
- Numbers right-aligned and tabular; text left-aligned; one visual weight for the column that carries the row's identity.
- Sticky header when the list scrolls past it. Row actions revealed on hover *and* reachable by keyboard - hover-only is not an affordance.
- Decide truncation deliberately: what truncates, what wraps, what gets a tooltip. Never let a long value silently break the layout.
- State how many rows are expected and choose pagination, infinite scroll, or virtualization against that number, not by habit.
- Sorting, filtering and selection survive a reload if the user would expect them to; put them in the URL when they are shareable state.

### Forms

- Group by meaning, one column by default, labels above fields. Placeholder text is not a label.
- Validate on blur and on submit, not on every keystroke; show the error next to the field, in words that say what to do.
- Never clear what the user typed. Keep the input on failure, keep scroll position, focus the first error.
- Disable submit only when you can say why; prefer an enabled button with clear validation over a dead one.
- Destructive actions confirm, and the confirmation names exactly what will be destroyed.

### The state matrix

Every surface that loads data has all of these, and each one is designed, not defaulted:

first-run · empty · loading (skeleton matching the final layout, not a spinner in a void) · partial · success · error with a retry that actually retries · permission-denied · offline, where relevant.

**No dead ends.** Every error and empty state offers the next action. An empty state is an opportunity to explain what goes here and how to put something there.

## 6. Data visualization

When the surface shows charts:

- Pick the chart for the question, not for the variety. Most product questions are a bar, a line, or a number.
- One categorical palette, colorblind-safe, defined as tokens and checked in both themes. Never encode meaning by color alone - pair it with label, shape, or position.
- Label axes and units. Start bar axes at zero. Say what the time range is and when the data was last refreshed.
- Direct-label the series when there are few; use a legend only when there are many.
- Tooltips give the precise value the chart cannot; they are not where the meaning lives.
- Charts get the same state matrix as everything else: loading, empty, error, and "not enough data to be meaningful".

## 7. Imagery

Imagery must do narrative work.

- Use at least one strong, real-looking image for brands, venues, editorial pages, and lifestyle products.
- Prefer in-situ photography over abstract gradients or fake 3D objects.
- Choose or crop images with a stable tonal area for text.
- Do not use images with embedded signage, logos, or typographic clutter fighting the UI, and do not generate images with built-in UI frames, splits, cards, or panels.
- If multiple moments are needed, use multiple images, not one collage.
- Every image has dimensions or an aspect ratio reserved before it loads, and meaningful alt text - or an empty alt when it is decoration.

The first viewport needs a real visual anchor. Decorative texture is not enough.

## 8. Copy

- Write in product language, not design commentary. Never let prompt language or design commentary reach the UI.
- Let the headline carry the meaning; supporting copy is usually one short sentence.
- Cut repetition between sections. Give every section one responsibility: explain, prove, deepen, or convert.

If deleting 30 percent of the copy improves the page, keep deleting.

**Utility copy for product UI.** On a dashboard, app surface, admin tool, or operational workspace, default to utility copy over marketing copy.

- Prioritize orientation, status, and action over promise, mood, or brand voice.
- Start with the working surface itself: KPIs, charts, filters, tables, status, or task context. No hero section unless the user asks for one.
- Headings say what the area is or what the user can do there: "Selected KPIs", "Plan status", "Top segments", "Last sync".
- Avoid aspirational hero lines, metaphors, campaign language, and executive-summary banners on product surfaces.
- Supporting text explains scope, behavior, freshness, or decision value in one sentence.
- If a sentence could appear in a homepage hero or an ad, rewrite it until it sounds like product UI.
- Litmus: if an operator scans only headings, labels, and numbers, can they understand the page immediately?

## 9. Motion

Use motion to create presence and hierarchy, not noise. Ship at least 2-3 intentional motions for visually led work:

- one entrance sequence in the hero
- one scroll-linked, sticky, or depth effect
- one hover, reveal, or layout transition that sharpens affordance

Prefer Framer Motion when available for section reveals, shared layout transitions, scroll-linked opacity/translate/scale, sticky storytelling, narrative carousels, and menu/drawer/modal presence.

Motion rules: noticeable in a quick recording, smooth on mobile, fast and restrained, consistent across the surface, removed if ornamental only. **Honor `prefers-reduced-motion`**: replace movement with a cut or a fade, never just slow it down.

## 10. Non-negotiables

These are not stylistic. A surface that fails one of these is not finished:

- Keyboard-operable end to end, with a visible focus indicator and a sane focus order. Modals trap focus and return it on close.
- Semantic structure: one `h1`, headings in order, landmarks, real buttons for actions and real links for navigation.
- Accessible names on every control, including icon-only ones.
- Text contrast meets WCAG AA (4.5:1 body, 3:1 large text), and interactive borders and focus rings meet 3:1 - in **every** theme.
- Touch targets at least 44x44 CSS pixels with spacing between them.
- Responsive behavior defined at named breakpoints, with no horizontal page scroll and no clipped content at 320px.
- No cumulative layout shift: reserve space for images, embeds, fonts, and anything that arrives late.
- `prefers-reduced-motion` respected.
- Forms keep user input on error and label their errors.

## 11. Performance

Budget initial payload and interaction latency, then decide what is server-rendered, streamed, code-split, lazy-loaded, virtualized, or optimistically updated - where it materially changes the experience, not everywhere. Images are sized, modern-format, and lazy below the fold. Fonts are subset and loaded so text is never invisible.

## 12. Hard rules

- No cards by default. No hero cards by default.
- No boxed or center-column hero when the brief calls for full bleed.
- No more than one dominant idea per section.
- No section should need many tiny UI devices to explain itself.
- No headline should overpower the brand on branded pages.
- No filler copy.
- No split-screen hero unless text sits on a calm, unified side.
- No more than two typefaces without a clear reason.
- No more than one accent color unless the product already has a strong system.
- No new component when an existing one fits. If you do introduce one, define its API, variants, and states so parallel work cannot diverge.
- No hardcoded color, spacing, or radius value where a token exists.

## 13. Reject these failures

- Generic SaaS card grid as the first impression
- Beautiful image with weak brand presence
- Strong headline with no clear action
- Busy imagery behind text
- Sections that repeat the same mood statement
- Carousel with no narrative purpose
- App UI made of stacked cards instead of layout
- A second visual language introduced inside a product that already had one
- A surface with only a happy path: no empty, no loading, no error
- Dark mode that was never opened

## 14. Checks before you call it done

Two lists. The first is judgement. The second is verifiable, and someone else will verify it - bring the surface up in a browser and look, at each breakpoint and in each theme.

**Judgement**

- Is the brand or product unmistakable in the first screen?
- Is there one strong visual anchor?
- Can the surface be understood by scanning headlines and labels only?
- Does each section have one job?
- Are cards actually necessary?
- Does motion improve hierarchy or atmosphere?
- Would it still feel premium with every decorative shadow removed?

**Verifiable**

- Every color, space, and radius comes from a token; grep the diff for stray hex values and magic pixels.
- Contrast measured on every text-on-surface pair used, in every theme, meets AA.
- Tab through the whole primary flow: focus is always visible, order matches the visual order, nothing is reachable only by mouse.
- Every interactive element has an accessible name.
- Rendered at the narrow, medium, and wide breakpoints: no horizontal scroll, no clipped or overlapping text, no broken table.
- Every state in the matrix has been seen, not assumed - including error and empty.
- Reduced-motion on: nothing moves that should not.
- Nothing shifts after load.
- Console is clean.
