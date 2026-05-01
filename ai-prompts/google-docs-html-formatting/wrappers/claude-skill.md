---
name: google-docs-html-formatting
description: Apply Google Docs compatible HTML formatting to any HTML file so it can be pasted cleanly into a Google Doc. Trigger by saying "apply doc formatting".
---

When the user says "apply doc formatting" on an HTML file, apply the full style
below and replace the existing `<style>` block.

## FONT & PAGE
- Font: Calibri, Arial, sans-serif — 11pt
- Page: max-width 6.5in, margin 1in auto, padding 0
  (Google Docs Letter 8.5" × 11" Portrait = 8.5in total minus 1in left margin
  minus 1in right margin = 6.5in content width)

## HEADINGS
- h1: 24pt, color #0066cc, border-bottom 2px solid #0066cc, padding-bottom 6pt
- h2: 18pt, color #0066cc
- h3: 14pt, color #333
- h4: 12pt, color #333

## CODE BLOCKS
- Use `<pre><code>plain text</code></pre>` structure — no color spans inside
- pre: background #f5f5f5, border 1px solid #ddd, border-radius 4px,
       padding 12pt, font "Courier New" 9pt, line-height 1.6
- pre code: no extra background, no padding, no border (inherit from pre)
- inline code: background #f5f5f5, padding 2px 4px, border-radius 3px,
               font "Courier New" 9pt

## TABLES
- border-collapse: collapse, width 100%, margin 12pt 0, table-layout: fixed
- th and td: border 1px solid #ddd, padding 6pt, vertical-align top
- th: background #0066cc, color white, font-size 10pt
- td: word-break: break-word, overflow-wrap: break-word, font-size 9.5pt
- even rows: background #f9f9f9
- Dense tables (4+ columns): class="dense-table" — font-size 9pt, padding 5pt

## NOTE / CALLOUT BOXES
- All box types (.box, .box-info, .callout):
    border 1px solid #ddd, background #fafafa, padding 10pt 12pt,
    border-radius 6px, margin 12pt 0
- Warning (.box-warning): border-color #e6c84a, background #fffef0
- Danger  (.box-danger):  border-color #e0a0a0, background #fff8f8
- Success (.box-success): border-color #90cca0, background #f6fff8

## TAGS / CHIPS (.tag, .chip)
- background #eef6ff, color #004a99, border 1px solid #cfe6ff,
  border-radius 10px, font-size 9pt, padding 2px 6px

## DIVIDERS
- hr: border-top 1px solid #ddd, margin 18pt 0, no border on other sides

## FOOTER (.footer)
- border-top 1px solid #ddd, font-size 9pt, color #888,
  text-align center, margin-top 36pt, padding-top 10pt

## CRITICAL RULES FOR COPY-PASTE INTO GOOGLE DOCS
1. All code blocks must use `<pre><code>plain text</code></pre>`.
   Strip ALL `<span>` color tags inside `<pre>` blocks — keep text content only.
2. Tables must have explicit border on every th and td (not just border-bottom)
   so borders survive Google Docs paste.
3. No flexbox, no CSS grid, no box-shadow anywhere in content —
   these do not transfer on paste.
4. Meta/info rows must use `<p>` tags, not flex divs.
5. max-width must be 6.5in — never 8.5in.
   8.5in is the paper width; 6.5in is the usable content width.

## After applying
- Strip color `<span>` tags from all `<pre>` blocks (use a script if many blocks).
- Open in Chrome → Cmd+A → Cmd+C → paste into Google Docs.
