# HTML Generation: McKinsey Style Report

## Design Principles

- Sharp corners (NO border-radius)
- Muted corporate colors (navy #003d5c, gray #f8f9fa)
- Ultra-compact layout
- Info-first structure
- 14px base font, compact spacing
- No decorative gradients or colors
- NO EMOJIS in final HTML

---

## Generation Steps

### Step 1: Read McKinsey Template
Load template from: `./templates/mckinsey_report_template.html`

### Step 2: Extract Key Metrics
Extract 3-4 key quantitative findings for dashboard display at top.

### Step 3: Convert MD to HTML

Generate the HTML inline (no external converter ships). Read the markdown report
and the McKinsey template, then map each markdown construct to the template's HTML.
Split the output into two parts for the template placeholders:
- **Part A ({{CONTENT}}):** All sections except Bibliography
- **Part B ({{BIBLIOGRAPHY}}):** Bibliography section only

**Conversion mapping:**
- Headers: `##` -> `<div class="section"><h2 class="section-title">`
- Headers: `###` -> `<h3 class="subsection-title">`
- Lists: Markdown bullets -> `<ul><li>` with nesting
- Tables: Markdown tables -> `<table>` with thead/tbody
- Paragraphs: Text wrapped in `<p>` tags
- Bold/italic: `**text**` -> `<strong>`, `*text*` -> `<em>`
- Citations: [N] preserved for tooltip conversion

### Step 4: Add Citation Tooltips (Optional)

Attribution Gradients - wrap each [N] citation:
```html
<span class="citation">[N]
  <span class="citation-tooltip">
    <div class="tooltip-title">[Source Title]</div>
    <div class="tooltip-source">[Author/Publisher]</div>
    <div class="tooltip-claim">
      <div class="tooltip-claim-label">Supports Claim:</div>
      [Extract sentence with this citation]
    </div>
  </span>
</span>
```
NOTE: This step is optional for speed. Basic [N] citations are sufficient.

### Step 5: Replace Template Placeholders

| Placeholder | Content |
|-------------|---------|
| {{TITLE}} | Report title (from first ## heading) |
| {{DATE}} | Generation date (YYYY-MM-DD) |
| {{SOURCE_COUNT}} | Number of unique sources |
| {{METRICS_DASHBOARD}} | Metrics HTML from step 2 |
| {{CONTENT}} | HTML from Part A |
| {{BIBLIOGRAPHY}} | HTML from Part B |

### Step 6: Verify HTML

Manual check (no verify script ships):
- Every `## ` section from the markdown appears in the HTML
- `{{SOURCE_COUNT}}` in the dashboard matches the bibliography entry count
- No unfilled `{{PLACEHOLDER}}` tokens remain
- Tables render as `<table>`, not raw `|` pipes
- Fix any failure and re-render before opening

### Step 7: Open in Browser
```bash
open [html_path]
```

---

## PDF Generation

**Preflight:** PDF is optional. Check for a renderer first:
```bash
command -v weasyprint || python3 -c "import weasyprint" 2>/dev/null || echo "no-weasyprint"
```
If no renderer and the `generating-pdf` skill is unavailable, deliver the markdown
and HTML as the primary artifacts and note in the final message that PDF was
skipped (missing renderer). Do NOT fail the run over a missing PDF.

**Option A: WeasyPrint Direct (Preferred)**

1. Create print-optimized HTML following `./reference/weasyprint_guidelines.md`
2. Critical CSS:
   - `page-break-inside: avoid` on tables, boxes
   - `page-break-after: avoid` on headings
   - `orphans: 3; widows: 3` on paragraphs
   - Use `display: table` not Flexbox/Grid
   - Font sizes in pt (10pt body, 8pt citations)
3. Generate: `weasyprint [html_path] [pdf_path]`
4. Open: `open [pdf_path]`

**Option B: generating-pdf Skill**

Use Task tool with general-purpose agent, invoke generating-pdf skill.
