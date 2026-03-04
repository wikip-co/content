# Copilot Instructions for wikip-co/content

## Repository Overview

This is a shared Markdown content repository for [wikip.co](https://wikip.co) and [anthonyrussano.com](https://anthonyrussano.com). It contains over 3,000 encyclopedic blog posts built with the Hexo static site generator. When Markdown files are pushed to `main`, GitHub Actions automatically triggers rebuilds of both sites.

All content is Markdown (`.md`). There are no source files to compile, no tests to run, and no package manifests to update. Every change is a content change.

## Directory Structure

Articles are organized into top-level topic categories. Each category may contain subdirectories for subtopics:

```
Bible Study/
Biology/
Child Development/
Current Events/
DevOps/
Finance/
History/
Natural Healing/
Real Estate Project/
```

Place new articles in the most specific matching subdirectory. Create new subdirectories when a topic doesn't fit an existing one.

## File Naming

- Use **lowercase kebab-case** for all file names: `turmeric.md`, `gut-microbiome.md`, `early-modern-europe.md`
- Use only letters, numbers, and hyphens — no spaces, underscores, or special characters
- File names should reflect the article title: `what-is-cesarean-birth.md` → title `What is Cesarean Birth?`

## Frontmatter (Required)

Every article **must** begin with a YAML frontmatter block:

```yaml
---
title: Article Title in Title Case
image: image-name
tags:
- Tag One
- Tag Two
---
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `title` | **Yes** | Title-case display name shown on the site |
| `tags` | **Yes** | List of relevant topic tags (one per line with `- ` prefix). Minimum 1 tag. |
| `image` | No | Image key used by the theme. Omit the file extension when referencing theme images (e.g., `image: turmeric`). Use the filename with extension for custom uploads (e.g., `image: funding.jpg`). |
| `encrypted` | No | Set to `true` to encrypt article content with the site password. |

**Tags must be meaningful and specific.** Use existing tags from similar articles for consistency (e.g., `Antioxidant`, `Antiinflammatory`, `Antimicrobial`, `Brain Health`, `Gut Health`, `AWS`, `Docker`).

## Article Structure by Category

### Natural Healing (Herbs, Spices, Vegetables, Fungi, Oils, etc.)

```markdown
---
title: [Common Name]
tags:
- [Relevant Health Properties]
---
**[Common Name]** ([Scientific name], [Other common names])

Brief introductory paragraph describing what the subject is.

## Composition

List of bioactive compounds and their known effects (optional, use for complex subjects).

## Healing Properties

### [Property Name]

Content about this healing property, with inline citations.[^1]

#### [Sub-property]

More specific content.[^1]

## Disease / Symptom Treatment

### [Condition Name]

Content about treatment of this condition.[^1]

## Synergistic Effects

### [Other Substance]

Description of synergistic interaction.[^1]

[^1]: **Title:** [Full Article Title](https://doi.org/...)
**Publication:** [Journal Name](https://journal-url.com/)
**Date:** Month Year
**Study Type:** Review
**Author(s):** Author One, Author Two
**Institutions:** Institution Name, City, Country
**Copy:** [archive](https://ipfs.io/ipfs/...), [archive-mirror](https://cloudflare-ipfs.com/ipfs/...)
```

### Biology / Child Development / Current Events

```markdown
---
title: Topic Title
image: image-name
tags:
- Tag One
---
Brief introductory paragraph or context.

## [Section Name]

- Bullet point fact with citation.[^1]
- Another fact.[^1]
  - Supporting detail.[^1]

### [Subsection Name]

Paragraph or bullet content.[^1]

[^1]: **Title:** [Full Article Title](https://doi.org/...)
**Publication:** [Journal Name](https://journal-url.com/)
**Date:** Month Year
**Study Type:** Review
**Author(s):** Author One, Author Two
**Institutions:** Institution Name, City, Country
**Copy:** [archive](https://ipfs.io/ipfs/...)
```

### History

```markdown
---
title: Topic Title
image: image-name
tags:
- Tag One
---
Introductory paragraph providing context and time period.

## Key Events and Developments

### [Region or Theme]

- **Event Name (Year):** Description of the event.

## Important Figures

- **Name (Birth–Death):** Brief description of significance.

## Societal and Cultural Developments

Paragraph describing broader developments.

[^1]: **Title:** [Source Title](https://url.com/)
**Publication:** [Publisher](https://publisher.com/)
**Archive:** [archive](https://ipfs.io/ipfs/...)
```

### Finance / Investing

```markdown
---
title: Topic Title
image: image-name
tags:
- Investing
- [Other Tags]
---
Introduction paragraph.

## [Section Heading]

Explanatory content in prose paragraphs or bullet lists.

### [Subsection]

Detailed content.[^1]

[^1]: [Source Title](https://url.com/)
```

### DevOps / Technology

```markdown
---
title: Service or Technology Name
image: image-key
tags:
- AWS
- [Other Tags]
---
Brief description of the technology or service.

## Overview

What it is and what it does.

## Key Features

- Feature one
- Feature two

## Use Cases

When and why to use it.

[^1]: **Title:** [Source Title](https://url.com/)
**Publication:** [Publisher](https://publisher.com/)
**Date:** Month Year
**Author(s):** Author Name
```

### Bible Study

```markdown
---
title: Term or Name
image: bible
tags:
---
Definition or meaning of the term.
```

## Citation & Reference Format

All factual claims **must** be cited with numbered footnotes. Place `[^N]` inline immediately after the claim and before any trailing punctuation (e.g., `...shown to reduce inflammation.[^1]`).

### Full Academic Reference (preferred for scientific articles)

```markdown
[^1]: **Title:** [Full Article Title](https://doi.org/10.xxxx/xxxxx)<br>
**Publication:** [Journal or Publisher Name](https://journal-url.com/)<br>
**Date:** Month Year<br>
**Study Type:** Review<br>
**Author(s):** Author One, Author Two, Author Three<br>
**Institutions:** Institution Name, City, Country; Another Institution, City, Country<br>
**Copy:** [archive](https://ipfs.io/ipfs/Qm...), [archive-mirror](https://cloudflare-ipfs.com/ipfs/Qm...)
```

### Minimal Reference (acceptable for non-scientific sources)

```markdown
[^1]: **Title:** [Source Title](https://url.com/)<br>
**Publication:** [Publisher](https://publisher.com/)<br>
**Date:** Date<br>
**Archive:** [archive](https://ipfs.io/ipfs/...)
```

### Simple URL Reference (for informal sources like YouTube)

```markdown
[^1]: [Video or Page Title](https://www.youtube.com/watch?v=...)
```

### Reference Field Guidelines

- **Title:** Full title of the article, book, or resource. Link to the canonical source (DOI preferred for academic papers).
- **Publication:** Name of the journal, publisher, or website. Link to the publication's homepage.
- **Date:** Month and year (e.g., `October 2020`, `June 2024`). Use `Last Reviewed: Month Day, Year` for updated pages.
- **Study Type:** One or more of: `Animal Study`, `Commentary`, `Human Study: In Vitro`, `Human Study: In Vivo`, `Human Study: In Silico`, `Human: Case Report`, `Meta Analysis`, `Review`, `Fungal Study`. Omit for non-scientific sources.
- **Author(s):** Full names of all authors, comma-separated.
- **Institutions:** Full institution names with city and country, semicolon-separated.
- **Copy / Archive:** Links to archived copies. Prefer IPFS archives (`https://ipfs.io/ipfs/Qm...`) with a cloudflare mirror (`https://cloudflare-ipfs.com/ipfs/Qm...`). Use Proton Drive or other hosts when IPFS is unavailable.

Use `<br>` to separate fields within a single footnote (not blank lines).

## Writing Style and Content Guidelines

### Tone and Voice
- Write in an **encyclopedic, neutral, factual tone**
- Avoid first-person pronouns and editorial opinions
- Use third-person and passive voice where appropriate
- Prefer concise, direct sentences over long complex ones

### Accuracy and Citations
- **Every factual claim must have a citation** (`[^N]`) immediately following the statement
- Do not add unsourced claims or speculation
- When a study type is uncertain, omit the `Study Type` field rather than guess
- Placeholder references (`[^N]: **Title:** []()`) are acceptable in draft articles but should be filled in before merging

### Formatting Rules
- Use `##` for top-level sections, `###` for subsections, `####` for sub-subsections
- Bold the article subject's name on first mention: `**Turmeric** (Curcuma longa)`
- Use bullet lists (`-`) for enumerating properties, effects, or items; use prose for explanatory content
- Do not use numbered lists except where order is meaningful (e.g., step-by-step processes)
- Include scientific names in parentheses after the common name on first mention
- Capitalize proper nouns, study types, and scientific classifications consistently

### Content Depth (Minimum Requirements)
- **New articles** must include at least: a frontmatter block with `title` and `tags`, a brief introductory paragraph or definition, and at least one cited claim
- **Natural Healing articles** should include the `## Healing Properties` section (even if partially empty) to establish the article structure for future expansion
- **Stub articles** (incomplete placeholder content) are acceptable but must have at minimum: correct frontmatter, the subject name in bold, and at least one reference stub `[^1]:` showing where citations will go
- **Complete articles** should have all key sections filled in with cited content

### Do Not
- Do not include personal opinions, commercial recommendations, or medical advice framing ("you should take X")
- It is okay to copy-paste text verbatim at times; but also okay to paraphrase and cite
- Do not leave broken links in `title` or `archive` fields (use empty parentheses `()` for placeholders)
- Do not use HTML except for `<br>` in references and `<iframe>` for embedded video

## Workflow

1. Add or edit `.md` files in the appropriate category directory
2. Ensure frontmatter is valid YAML and all required fields are present
3. All factual claims should have citation footnotes
4. Push to `main` — GitHub Actions will automatically trigger site rebuilds for both wikip.co and anthonyrussano.com

## Agent Tooling

When asked to review a research URL and generate importable markdown, run the local scraper tool in this repository:

```bash
cd .github/agent-tools/web-scraper
uv run main.py "<URL>" "<output_file.md>"
```

If `uv` is unavailable, use:

```bash
cd .github/agent-tools/web-scraper
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py "<URL>" "<output_file.md>"
```

Use the generated markdown as source material when updating the target article in this repository.
