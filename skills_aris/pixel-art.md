# Pixel Art

SVG pixel art illustrations for READMEs, docs, and slides.

## Design Principles

7px pixel grid, no gaps. Characters 8-10×8-12 pixels. Use transform groups for positioning and reuse. 3-5 colors per character.

## Color Palette

Skin: light with blush/shadow variant. Eyes: dark. Hair: brown/black/blonde/red. Clothes: project brand color. Keep palette simple and consistent.

## Scene Composition

Chat dialogue: characters on sides, bubbles alternating with tails toward speaker, arrows between. Single character: centered with label. Keep viewBox tight — match content + padding.

## Bubble and Arrow Mechanics

Bubble: rect + tail polygon pointing toward speaker + junction cover rect. Vertical spacing 38-44px. Arrow: marker with orient="auto" — direction follows line order. Text width: measure before setting bubble dimensions (monospace ≈7.8px/char, emoji ≈14px). Keep character and bubble zones separated ≥10px.
