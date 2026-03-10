## Prompt Examples

  ---                                                                                                                                                                                                                    
  Minimal — let the agent decide everything:                                                                                                                                                                             
  Work through the research backlog and publish new findings to the content repo.                                                                                                                                        
  Use the agent-workflow tools. Prioritize open-access articles with score >= 18.                                                                                                                                        
  Create a PR when done.                                                                                                                                                                                                 

  ---
  Topic-directed — you pick the theme:
  Use the agent-workflow backlog command to find unprocessed open-access articles
  related to quercetin or resveratrol, scrape the best candidates with
  --match-existing, add the findings to the relevant existing articles, and open a PR.

  ---
  Category-directed — you pick where content goes:
  Pull the top 10 unprocessed selected articles from the backlog
  (--open-access --min-score 18). For each one, use prepare --match-existing
  to find where it fits in the repo. If it matches an existing article with
  score >= 40, add the findings as a new section with a footnote.
  If there's no good match, create a new stub under the appropriate
  Natural Healing category. Validate and open a PR.

  ---
  Fully autonomous with guardrails:
  Use ./agent-workflow backlog --open-access --min-score 19 --limit 10 to surface
  candidates. Skip any that are about animal husbandry, agriculture, or non-human
  health topics. For each remaining article, run prepare --match-existing and:
    - If matches returns a repo article with score >= 50: add the key findings
      as bullet points with a footnote to that article.
    - If no strong match: create a new stub under the closest Natural Healing
      subcategory using --create-new.
  Run validate before committing. Put all changes in a single PR.

  ---
  The key things worth including in any variation:

  - --open-access --min-score 18 — keeps quality high and ensures the scraper gets full text
  - --match-existing on prepare — without it the agent may miss existing articles
  - "validate and open a PR" — gives the agent a clear stopping condition
  - Any topic/category constraints you care about for that session

I need you to integrate new research into an existing article in this repository.

**How to  Integrate the findings:**
- Incorporate all relevant findings from the research article into the existing article
- Every new sentence or bullet point added must include an inline citation reference (e.g., [1], [2]) tied to this source
- Do not remove or alter existing citations or content — only add to it

**Add the citation:**
Append the full citation for this research article to the bottom of the article under a `## References` section (or add to the existing references list if one already exists). Use this citation format:
[Author(s). Title. Journal/Platform. Year. DOI/URL]

**Update keywords:**
Review the `keywords` section of the article and add any new relevant keywords introduced by this research. Do not remove existing keywords.

Confirm each step as you complete it.
