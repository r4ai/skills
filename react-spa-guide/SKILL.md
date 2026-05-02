---
name: react-spa-guide
description: Design and implementation guidelines for React SPA. Includes recommended tech stacks, design guidelines, implementation guidelines, and warnings about bad practices and best practices. Always read when implementing frontend solutions using React.
---

## Tech Stack

For technology selection, we recommend choosing from the following as our baseline guidelines.
However, feel free to make flexible adjustments based on specific project requirements.

- Framework: Vite+
- UI: React
- Component Library: Base UI or React Aria Components
- Styling: Tailwind CSS + Tailwind Merge + Tailwind Variants (if using shadcn/ui, follow their implementation)
- Design System: shadcn/ui or custom implementation
- Routing: TanStack Router
- Data Fetching: TanStack Query
- Testing: Vitest, Playwright, Storybook

Web frontend development evolves rapidly. Your current knowledge may already be outdated, so be sure to stay updated with the latest trends and follow best practices.

## Directory Structure

Organize directories with collocation in mind.

## Component Implementation Guide

- Keep components small. They should have a single responsibility.
- Separate logic from UI. Extract complex logic into custom hooks.
- Write Stories to verify behavior easily.

### Style

For shadcn/ui, follow the "shadcn" skill.

Otherwise:

- Use `twJoin` or `twMerge` for class name concatenation
- When class names are complex, use `tv`

### Design Guideline

- **Always utilize design tokens to ensure a consistent design**
  - If design tokens are unavailable, create them using shadcn/ui as a reference.
  - Keep dark mode compatibility in mind.
- **Accessibility**
  - Aim for WCAG 2.2 Level AA compliance.
  - Effectively leverage headless component libraries.
  - Avoid low-contrast color combinations.
  - Avoid excessively small font sizes.

### State Management

- Keep state minimal and localized. Use global state only when strictly necessary.
- Use Context to avoid prop drilling.

### Avoid premature optimization

- A straightforward implementation is best.
- Only apply optimizations using `useMemo`, `useCallback`, etc., when performance issues actually arise.
- Leverage the React Compiler effectively.

### useEffect

Stop overusing useEffect. If you aren't synchronizing with external systems, you probably don't need an Effect.

- If you can calculate something during render, you don’t need an Effect.
- To cache expensive calculations, add useMemo instead of useEffect.
- To reset the state of an entire component tree, pass a different key to it.
- To reset a particular bit of state in response to a prop change, set it during rendering.
- Code that runs because a component was displayed should be in Effects, the rest should be in events.
- If you need to update the state of several components, it’s better to do it during a single event.
- Whenever you try to synchronize state variables in different components, consider lifting state up.

For more details, see [you might not need an effect](./references/react.dev/you-might-not-need-an-effect.md).
