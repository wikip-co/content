# Natural Healing Content Style Guide

**Version:** 2.0  
**Purpose:** Standardized format for all articles in the Natural Healing encyclopedia.

---

## 1. Frontmatter (YAML)

Every file must begin with this exact structure:

```yaml
---
title: Exact Article Title
tags:
- Primary Property
- Secondary Benefit
- Condition or Symptom
- Another Keyword
---
```

**Rules:**
- `title` must be a string (not a YAML list).
- `tags` must be a bulleted list.
- Tags should reflect healing properties, mechanisms, and conditions treated.

---

## 2. Opening / Lead Section

- Start with a single short definition using bold:
  - `**Term Name** (Scientific Name if relevant) is ...`
- Limit to 1–2 sentences.
- Do **not** expand into paragraphs here.

---

## 3. Core Content Rule: Bullet Points + Citations

### Primary Format (Strictly Preferred)

- Use **bullet points** as the default content structure under every heading.
- Each bullet point must be **as close to verbatim** as possible from the source material.
- **Every bullet point requires a citation**.

**Example:**

```markdown
### Anti-Inflammatory

- Chrysin is a flavonoid compound found naturally in honey and has anti-Hyperuricemic effects.[^1]
- Honey binding inhibitors of Covid19 scored a binding affinity better than lopinavir.[^2]
- Three active compounds from honey showed superior binding to the virus compared to the protease drug lopinavir.[^2]
```

### When Paragraphs Are Allowed

- Use a short paragraph **only** when a concept requires brief explanation to support the bullets that follow.
- Goal: Minimize prose. Bullet points should carry the factual weight of the article.

---

## 4. Standard Section Order

### 1. `## Composition` (when applicable)
- Use for articles with notable bioactive compounds, phytochemicals, polysaccharides, etc.
- Structure with nested bullets.
- Every specific finding or effect must be cited.

### 2. `## Healing Properties`
- This is the primary section (present in nearly all articles).
- Create one `### Heading` per major property.
- Content under each heading should be bullet points with citations.
- Use deeper nesting when needed:
  - `### Antimicrobial`
    - `#### Antiviral`
    - `#### Antibacterial`

### 3. `## Disease / Symptom Treatment`
- Create one `### Condition Name` per disease or symptom.
- Use bullet points with citations.
- Nest subtypes when relevant (e.g., `#### Breast Cancer`).

### Optional Sections (use only when relevant)
- `## Synergistic Effects`
- `## Adverse Effects` (note correct spelling)
- `## Preparation`
- `## Biological Activity`

---

## 5. Citation Format

Place all references at the bottom of the file using footnote style.

**Preferred detailed template:**

```markdown
[^1]: **Title:** [Full Paper Title](https://doi.org/...)
**Publication:** [Journal or Site Name](url)
**Date:** YYYY
**Study Type:** Human Study / Animal Study / Review / Meta Analysis / In Vitro
**Author(s):** 
**Institution(s):** 
**Abstract:** 
**Copy:** [archive](https://ipfs.io/ipfs/...), [archive-mirror](https://cloudflare-ipfs.com/ipfs/...)
```

**Rules:**
- Attach `[^n]` at the end of **every** bullet point.
- Preserve original scientific phrasing as closely as possible.
- Include IPFS archive links when available.

---

## 6. General Principles

- **Bullet-first approach**: Default to bullets. Only use paragraphs for necessary context.
- **Verbatim priority**: Keep source sentences as close to the original wording as possible.
- **One idea per bullet**.
- **Consistency**: Align headings and tags with existing articles in the repository.
- **Spelling & Typos**: Use correct spelling (e.g., “Osteoporosis”, “Adverse Effects”).

---

This guide ensures a consistent, scannable, research-oriented format across the entire Natural Healing collection.