# CSS Layout Overhaul - 2026-06-17

## Objective
Transform hsst.hk website CSS layout from narrow, constrained containers to premium full-width design matching Apple/Tesla/LVMH visual standards.

## Changes Made (css/style-202605042143.css)

### A. `:root` CSS Variables
- `--max-width-xxl`: 1440px → **100%** (≥1920px full-width fluid)
- `--max-width-xl`: 1280px → **100%** (1440-1919px full-width fluid)
- `--max-width-lg`: 1120px → **100%** (1200-1439px full-width fluid)
- `--container-padding`: 24px → **48px**

### B. Section Padding
- `.section-padding`: 40px → **80px** vertical padding
- ≥1920px: **100px**, 1440-1919px: **90px**, 1200-1439px: **80px**
- Mobile: 768px → **40px**, 480px → **32px**, 375px → **24px**

### C. Inner Page White Card Removal
- `.inner-page .section-padding .container`: Removed background, border-radius, padding, box-shadow → transparent, 0, 0, none
- `.inner-page .section-padding`: background #F5F0EB → **transparent**
- `.inner-page .product-series-section > .container`: Same treatment
- `.inner-page .series-overview-section .container`: Same treatment
- `.inner-page .product-cat-section .container`: Same treatment
- `.inner-page .product-series-section` background → transparent
- `.inner-page .product-cat-section` background → transparent
- `.inner-page .series-overview-section` background → transparent

### D. Hero Region Full-Width
- `.hero-content` max-width: 1200px → **100%**
- `.hero-grid-video .container` max-width: 1200px → **100%**
- `.hero-grid-video .hero-content` max-width: 700px → **100%**

### E. Grid Component Expansion
- `.certificates-grid` max-width: 1200px → **100%**
- `.client-logos-grid`: 5 cols → **6 cols**, max-width 1000px → **100%**
- `.about-grid` gap: 60px → **80px** (120px at ≥1920px)
- `.why-choose-grid` gap: 32px → **40px** (48px at ≥1920px)
- `.scenarios-grid` gap: 24px → **32px** (40px at ≥1920px)
- `.footer-grid` max-width: 1400px → **100%**
- `.strength-grid` max-width: 1200px → **100%**
- `.team-grid` max-width: 1200px → **100%**
- `.csr-grid` max-width: 1200px → **100%**
- `.stats-row` max-width: 1200px → **100%**, width: 90% → **100%**

### F. Container Responsive Padding (was 0 on large screens)
- ≥1920px: **64px** left/right
- 1440-1919px: **48px** left/right
- 1200-1439px: **40px** left/right
- 768-1199px: **32px** left/right (new tablet breakpoint)
- <768px: **20px** left/right

### G. Section Description Width
- `.section-desc` max-width: 600px → **900px**
- About page section-descs: 800px → **100%**

### H. Enhancement Block Added (end of file)
- All section containers → max-width: 100%
- `.hero-video-grid` gap: 16px → **20px**
- `.why-card` padding: 40px 28px → **48px 32px**
- `.trust-item` padding enhanced, `.trust-number` larger
- `.categories-grid` gap: 20px → **24px**
- Section h2: clamp(2rem, 3.5vw, 3rem) with letter-spacing
- All major grids (products, news, projects, gallery, timeline, contact, tech-service, etc.) → max-width: 100%
- Large screen enhanced breathing room

## Verification
- ✅ All 12 key changes verified present in file
- ✅ CSS brace balance: 1676/1676 (no syntax errors)
- ✅ Total file: 184,519 bytes, 7,507 lines
- ✅ No HTML files modified
- ✅ Mobile responsive breakpoints preserved and enhanced
- ✅ Animations and interactions untouched

## Files Modified
- `css/style-202605042143.css` only
