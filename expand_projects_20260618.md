# Expand 11 Short Project Pages (ZH + EN)

**Date:** 2026-06-18  
**Task:** Expand 11 short project subpages from 6 sections to 11 sections each, for both Chinese and English versions (22 files total).

## What Was Done

### Problem
11 project subpages (airport, bank, convention, education, government, mall, metro, museum, office, stadium, villa) only had 6 sections. The "good" pages (hotel, commercial, medical, residential, resort) had 11 sections.

### Solution
Used a Python script (`expand_projects.py`) to programmatically generate and insert 5 new sections into each page:

1. **施工過程 / Construction Process** — gallery-grid with 3 construction photos
2. **安裝細節 / Installation Details** — gallery-grid with 4 detail photos
3. **相關產品 / Related Products** — stone-grid with 3 stone cards linking to product pages
4. **技術亮點與解決方案 / Technical Highlights & Solutions** — tech-list with 3 project-specific challenge/solution items
5. **打造您的頂級項目 / Build Your Premium Project** — CTA section with formspree form + "探索更多案例 / Explore More Projects" section

### Key Details
- Each section has unique, project-specific content (not copy-paste from hotel)
- Chinese pages use Traditional Chinese
- English pages use English
- Form IDs are unique per page (e.g., airportFormZh, airportFormEn, bankFormZh, bankFormEn)
- Form hidden _subject field includes the project name
- Old simple CTA replaced with full CTA (with form) + More section
- Old lightbox with onclick handlers replaced with new event-listener-based lightbox
- Form CSS (.hsst-form) added to all pages that didn't have it
- All pages verified: 11 sections, balanced tags, single lightbox, form present

### Files Modified (22 total)
- `projects/{airport,bank,convention,education,government,mall,metro,museum,office,stadium,villa}.html`
- `en/projects/{airport,bank,convention,education,government,mall,metro,museum,office,stadium,villa}.html`

### Commit
`cbedb1a` — pushed to main branch on GitHub
