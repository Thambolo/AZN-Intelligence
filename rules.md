# Accessibility Rules

A concise, actionable checklist distilled from the provided guidance.

## Content

- [ ] Use plain language; avoid figures of speech, idioms, and complicated metaphors. Target about an 8th‑grade reading level. (WCAG 3.1.5)
- [ ] Ensure `button`, `a` (links), and `label` text is unique and descriptive; avoid vague phrases like “click here” or “read more.” (WCAG 1.3.1)
- [ ] Align text for readability: left-align for left‑to‑right languages and right‑align for right‑to‑left; avoid centered/justified long text. (WCAG 1.4.8)

## Global code

- [ ] Validate your HTML to ensure consistent behavior across browsers and assistive technology. (WCAG 4.1.1)
- [ ] Set the document language with a `lang` attribute on the `<html>` element (e.g., `<html lang="en">`). (WCAG 3.1.1)
- [ ] Provide a unique, descriptive `<title>` for every page/view. (WCAG 2.4.2)
- [ ] Do not disable viewport zoom; allow users to resize text. (WCAG 1.4.4)
- [ ] Use landmark elements to define regions (e.g., `header`, `nav`, `main`, `footer`, `aside`) for structure and quick navigation. (WCAG 4.1.2)
- [ ] Ensure a logical, linear content flow and focus order:
  - Remove `tabindex` values other than `0` and `-1`.
  - Do not add `tabindex` to inherently focusable elements (links, buttons).
  - Avoid adding `tabindex` to non-focusable elements unless absolutely necessary. (WCAG 2.4.3)
- [ ] Avoid using the `autofocus` attribute to prevent unexpected focus movement. (WCAG 2.4.3)
- [ ] Allow users to extend, adjust, or turn off session timeouts well before they expire. (WCAG 2.2.1)
- [ ] Do not rely on `title` attribute tooltips for important information. Acceptable use: labeling an `iframe` to describe its content. (WCAG 4.1.2)

## Keyboard

- [ ] Ensure interactive elements have a clearly visible focus style when navigated via keyboard, switch, voice control, or screen reader. (WCAG 2.4.7)
- [ ] Verify the keyboard focus order matches the visual layout and reading order; navigation should be predictable. (WCAG 1.3.2)
- [ ] Remove invisible/off‑screen focusable elements (e.g., inactive dropdown items, off‑canvas menus, hidden modals). (WCAG 2.4.3)

## Images

- [ ] All `img` elements include an appropriate `alt` attribute. (WCAG 1.1.1)
- [ ] Decorative images use a null/empty `alt` attribute (`alt=""`). (WCAG 1.1.1)
- [ ] Provide text alternatives for complex graphics (charts, graphs, maps): describe axes, labels, data points, and the overall message. (WCAG 1.1.1)
- [ ] If an image contains text, include that text in the `alt` description (e.g., a logo’s text). (WCAG 1.1.1)

## Headings

- [ ] Use heading elements to introduce content and build the document outline, not purely for visual styling. (WCAG 2.4.6)
- [ ] Use only one `<h1>` per page or view to state the page’s main purpose; do not use `<h1>` for site name across pages. (WCAG 2.4.6)
- [ ] Write headings in a logical sequence that reflects content depth (e.g., `h2` → `h3` → `h4`). (WCAG 2.4.6)
- [ ] Do not skip heading levels (e.g., avoid jumping from `h2` to `h4`); use CSS for visual styling instead. (WCAG 2.4.6)

## Lists

- [ ] Use semantic list elements (`ol`, `ul`, `dl`) for list content and related item groupings. (WCAG 1.3.1)

## Controls

- [ ] Use `<a>` for links and always include an `href` (including in SPAs). Avoid click-only anchors. (WCAG 1.3.1)
- [ ] Make links recognizable beyond color alone (e.g., underlines). (WCAG 1.4.1)
- [ ] Ensure all interactive controls have a visible `:focus` state. (WCAG 2.4.7)
- [ ] Use the `<button>` element for buttons; set `type="button"` when not submitting forms. (WCAG 1.3.1)
- [ ] Provide a “Skip to main content” link that becomes visible on focus. (WCAG 2.4.1)
- [ ] Identify links that open in a new tab/window with advance warning. (Technique G201)

## Tables

- [ ] Use `<table>` only for tabular data (rows/columns). (WCAG 1.3.1)
- [ ] Use `<th>` for headers with appropriate `scope` (e.g., `scope="col"`, `scope="row"`) when needed. (WCAG 4.1.1)
- [ ] Provide a descriptive `<caption>` for each data table. (WCAG 2.4.6)

## Forms

- [ ] Associate each input with a `<label>` using `for`/`id`. (WCAG 3.2.2)
- [ ] Group related inputs with `<fieldset>` and `<legend>` where appropriate. (WCAG 1.3.1)
- [ ] Use `autocomplete` on inputs when applicable (name, email, address, etc.). (WCAG 1.3.5)
- [ ] After submission, show a summary list of validation errors above the form; include links to fields. (WCAG 3.3.1)
- [ ] Programmatically associate inline error messages with inputs (e.g., `aria-describedby`). (WCAG 3.3.1)
- [ ] Don’t rely on color alone for error/warning/success states; add icons, text, or patterns. (WCAG 1.4.1)

## Media

- [ ] Do not autoplay audio/video. Provide user control. (WCAG 1.4.2)
- [ ] Use appropriate markup for media controls (e.g., range inputs for volume; pressed state for toggles). (WCAG 1.3.1)
- [ ] Ensure all media can be paused via UI and keyboard (Space when appropriate) without breaking page scroll. (WCAG 2.1.1)

## Video

- [ ] Provide captions for prerecorded video. (WCAG 1.2.2)
- [ ] Avoid seizure triggers; keep flashing below thresholds. (WCAG 2.3.1)

## Audio

- [ ] Provide transcripts for audio. (WCAG 1.1.1)

## Appearance

- [ ] Check content in specialized display modes (e.g., Windows High Contrast, inverted colors); ensure icons, borders, links, and form fields are still perceivable. (WCAG 1.4.1)
- [ ] Verify content remains readable at 200% text size; avoid overlap/clipping. (WCAG 1.4.4)
- [ ] Maintain clear proximity/spacing and support increased text spacing without loss of content or functionality (line height, paragraph, letter/word spacing). (WCAG 1.4.12)

## Animation

- [ ] Provide a way to pause/stop/hide moving, blinking, or auto-updating content (carousels, tickers). (WCAG 2.2.2)
- [ ] Respect “reduced motion” preferences; minimize motion (e.g., parallax, large transitions) and offer a user setting to disable non‑essential animations. (WCAG 2.3.3)
- [ ] Avoid flashing content; do not exceed three flashes per second or overall flash thresholds. (WCAG 2.3.1)

## Color contrast

- [ ] Text contrast meets AA: at least 4.5:1 for normal text and 3:1 for large text (≥18.66px regular or ≥14px bold). (WCAG 1.4.3)
- [ ] Non-text contrast (icons, graphical objects, component boundaries, focus indicators) is at least 3:1 against adjacent colors. (WCAG 1.4.11)
- [ ] Hover/focus/selected states and error/success colors preserve required contrast; don’t rely on color alone to convey meaning. (WCAG 1.4.3, 1.4.11, 1.4.1)

## Mobile and touch

- [ ] Touch targets are large enough: at least 24×24 CSS px (AA, WCAG 2.2) with adequate spacing; 44×44 is recommended when possible. (WCAG 2.5.8)
- [ ] Provide single‑pointer alternatives for multi‑point or path‑based gestures (e.g., offer a tap alternative to drag/slide). (WCAG 2.5.1)
- [ ] Do not trigger actions on pointer‑down; support cancellation/undo, or trigger on pointer‑up. (WCAG 2.5.2)
- [ ] Don’t lock orientation unless essential; support both portrait and landscape. (WCAG 1.3.4)
- [ ] Reflow without horizontal scrolling at 320 CSS px width; avoid pinned layouts. (WCAG 1.4.10)
- [ ] Content shown on hover/focus is dismissible, hoverable, and persistent; avoid hover‑only tooltips on touch. (WCAG 1.4.13)
