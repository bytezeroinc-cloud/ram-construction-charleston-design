# Pass 18 · Client feedback restructure (2026-10-22)

Source: the client's written review of the published comp (ten points + a six-section homepage brief). Design
direction unchanged: Fanlight II (arches as architecture, hairline rules, Cormorant + Jost, Black + Amber Red,
pills). What changes is the information architecture, the wording and the length. Backups: `index.pass17-partnership.html.bak`,
`build_pages.pass17.py.bak`, `css/*.pass17.css.bak`.

## Point by point

| # | Feedback | Done |
|---|---|---|
| 1 | Shorten the homepage | Six sections: hero · services · why RAM · featured projects · meet the team · contact. Ledger, 3D window, coast datum, four-column process, colonnade and homepage FAQ moved to pages (nothing deleted) |
| 2 | Repetition (in-house design, fixed bid, 3D) | Said once, in "Why choose RAM" (three ruled items on the band). Hero lede, services copy and process strip no longer restate them |
| 3 | Plainer headlines | H1 "Custom homes built for Lowcountry living." Section heads say what the section is; the serif italic carries the register |
| 4 | Reorganise services | Custom Homes · Renovations & Additions · Design & Preconstruction, each with its own page; coastal construction is a strip under the services and the Lowcountry page |
| 5 | Make it personal | "Meet the team" on the homepage and About, built around Greg: portrait arch and bio are PLACEHOLDERS until RAM supplies them (no fabrication) |
| 6 | Mobile readability, confusing stats | The "1 PM / 1 bid / 3D / 4" figures are gone; on phones the band photograph sits above the copy, which sits on solid black; longer type over photographs removed |
| 7 | Condense the process | One ruled strip of four steps under Why RAM, linking to `process.html` (full steps + the 3D walk-through window) |
| 8 | Move coastal detail | `lowcountry.html`: the five conditions, the four towns (colonnade) and the coast questions |
| 9 | Charlotte partnership | Framed as what it brings (a builder working since 2004, its design and 3D tools, the same fixed-bid process). "Charleston's own will join them" lines removed; captions and the footer provenance line stay truthful |
| 10 | Clearer CTAs | Header "Let's talk"; hero and form "Schedule a consultation"; contact H2 "Let's talk about your project"; project select includes renovations and design |

Also asked: more real project photography (all 16 Charlotte frames now sit in Featured projects + service pages), testimonials
and craftsmanship examples. Testimonials NOT built: none verified. Needs RAM's own public reviews, verbatim, with source.

## Page map after

index · custom-homes · renovations-additions · design-preconstruction · lowcountry · process · about · faq · contact · four towns

## Facts RAM owes before launch

Greg's full name, role, bio and portrait; team names/roles; any Charleston project photographs; testimonials with source;
843 number; SC license number; domain.

## Render and checks (2026-10-22)

| Page | 1440 height | 390 height | Notes |
|---|---|---|---|
| Homepage | 6,717 px (was 9,921) | 11,207 px | six sections; first phone screen at 360×740 holds photo, H1 and CTA (CTA bottom 693) |
| Lowcountry | 5,717 | 8,124 | five conditions on the rail, colonnade, coast questions |
| Process | 4,696 | 8,909 | four steps in full, the 3D window, price questions |
| Custom homes | 5,617 | 9,332 | seven stages, partner homes |
| Renovations & additions | 5,504 | 8,888 | four kinds of work |
| Design & preconstruction | 5,553 | 9,154 | six stages, renderings |
| About | 6,609 | — | team block with placeholders, partnership reframed |

No horizontal overflow at 390 or 360; header fits at 1200 and 1440; one H1 per page, no H1→H3 skips; every internal link
resolves; every image sized; no duplicate titles; mobile menu exercised at 360 (its CTA at 652–704 of 740).
Capture reports the seven off-screen slider frames as "broken": a lazy-load false positive (they load on scroll), same as pass 15.

## Score

| # | Dimension | /w | Note |
|---|---|---|---|
| 1 | Direction legible | 10/10 | Fanlight II reads from any crop |
| 2 | Signature device | 12/12 | arches: hero horn, arcade, piazza, portrait, form, footer fan |
| 3 | Composition | 10/12 | arch crosses the seam into the band; slider bleeds; the services strip is the one plain row |
| 4 | Image scale and spread | 9/12 | ↓ client-directed: homepage carries 17 frames instead of 25+, the rest moved to pages |
| 5 | Typography | 10/10 | |
| 6 | Depth / E-E-A-T | 8/10 | depth now one click away on three service pages, Lowcountry and Process |
| 7 | Conversion | 10/10 | phone in header, two consultation CTAs, towns in the door, JSON-LD |
| 8 | Template smell | 8/10 | the process strip and team facts list are conventional forms, dressed in the system |
| 9 | Truth | 8/8 | placeholders visibly bracketed; no testimonials until verified; captions unchanged |
| 10 | Mobile / technical | 6/6 | |
| | **Total** | **91** | pass 17 was 90; client-directed cuts are annotated, not scored down |

Three voices, one pass: the creative director wants a photograph behind the team block once the portrait exists (the
placeholder arch is honest but flat); the buyer asked "who is Greg?" and the page cannot answer until RAM does; the
ceiling brand's art director would drop the "Our specialty" strip into the arcade's portrait panel at 1440 to save a row.
None is a rubric failure; the first two are RAM's inputs.
