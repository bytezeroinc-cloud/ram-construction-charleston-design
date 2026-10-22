#!/usr/bin/env python3
"""Assemble the RAM Charleston inner pages from the homepage's own parts.

Reads index.html for the SVG sprite, masthead, mobile menu, contact form and footer,
so the chrome stays one source, and writes:
  about.html, faq.html, contact.html, the four town pages,
  custom-homes.html, renovations-additions.html, design-preconstruction.html,
  lowcountry.html, process.html
Run from the charleston folder:  python3 build_pages.py
"""
import re, html, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
home = (ROOT / 'index.html').read_text()

# ── shared parts lifted from the homepage ────────────────────────────────────
def between(s, a, b, inclusive=True):
    i = s.index(a); j = s.index(b, i) + (len(b) if inclusive else 0)
    return s[i:j]

SPRITE = next(l for l in home.split('\n') if l.startswith('<svg width="0" height="0"'))
HEADER = between(home, '<!-- ═════ masthead ═════ -->', '</header>')
MNAV   = between(home, '<div class="mnav" id="mnav"', '\n<main', inclusive=False).rstrip()
FOOTER = between(home, '<!-- ═════ colophon ═════ -->', '</footer>')
FORM   = re.search(r'<form class="form rv d2".*?</form>', home, re.S).group(0)
FONTS  = between(home, '<link rel="preconnect" href="https://fonts.googleapis.com">', 'display=swap" rel="stylesheet">')
HOWTO  = between(home, '<div class="howto on-dark">', '\n  </div>\n</section>', inclusive=False) + '\n  </div>'

# image widths available in img/w, so every <img> gets a real srcset
W = {}
for f in (ROOT / 'img' / 'w').iterdir():
    m = re.match(r'(.+)-(\d+)\.webp$', f.name)
    if m: W.setdefault(m[1], []).append(int(m[2]))
for k in W: W[k].sort()

def relink(s):
    """Inner pages: homepage section anchors become index.html#…; the CTA anchors become the contact page."""
    s = s.replace('href="#top"', 'href="index.html"')
    for a in ('services', 'why', 'projects', 'team'):
        s = s.replace(f'href="#{a}"', f'href="index.html#{a}"')
    s = s.replace('href="#contact"', 'href="contact.html"').replace('href="#door"', 'href="contact.html"')
    return s

def mark_current(s, current):
    return s.replace(f'href="{current}">', f'href="{current}" aria-current="page">')

def head(title, desc, canonical, og_image, extra=''):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:image" content="{og_image}">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="img/brand/ram-logo--bw.svg">
{FONTS}
<link rel="stylesheet" href="css/charleston.css">
<link rel="stylesheet" href="css/pages.css">
{extra}<script>document.documentElement.classList.add('js')</script>
</head>
<body class="inner">
{SPRITE}

'''

def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'

def tail(current, ld):
    return f'''
{relink(FOOTER)}
{ld}
<script src="js/site.js"></script>
</body>
</html>
'''

def chrome(current):
    return mark_current(relink(HEADER), current) + '\n\n' + mark_current(relink(MNAV), current) + '\n\n<main id="top">\n'

# ── components ───────────────────────────────────────────────────────────────
def pic(name, alt, ratio='3/3.6', sizes='(max-width:860px) 100vw, 44vw', pos=None, eager=False, cls='arch'):
    ws = W[name]; w1 = ws[-1]
    st = f' style="object-position:{pos}"' if pos else ''
    ld = 'fetchpriority="high"' if eager else 'loading="lazy"'
    srcset = ', '.join(f'img/w/{name}-{w}.webp {w}w' for w in ws)
    return (f'<div class="{cls}" style="aspect-ratio:{ratio}"><img src="img/w/{name}-{w1}.webp" '
            f'srcset="{srcset}" sizes="{sizes}" width="{w1}" {ld} alt="{alt}"{st}></div>')

def arch_img(name, w1, w2, alt, ratio='3/3.6', sizes='(max-width:860px) 100vw, 44vw', pos=None, eager=False):
    return pic(name, alt, ratio, sizes, pos, eager)

def phero(eyebrow, h1, lede, art, meta=None, folio=None):
    fol = f'<i aria-hidden="true">{folio}</i> ' if folio else ''
    m = ''
    if meta:
        m = '<ul class="phero-meta rv d2">' + ''.join(f'<li>{x}</li>' for x in meta) + '</ul>'
    return f'''
<!-- ═════ page hero ═════ -->
<section class="phero on-dark">
  <div class="wrap">
    <div class="phero-copy">
      <h1 class="hx rv"><span class="eyebrow">{fol}{eyebrow}</span><span class="sr-only">. </span><span class="display">{h1}</span></h1>
      <p class="lede rv d1">{lede}</p>
      {m}
    </div>
    <div class="phero-art rv d1">{art}</div>
  </div>
</section>
'''

def faq_items(qs, first_open=True):
    out = []
    for i, (q, a) in enumerate(qs):
        op = ' open' if (i == 0 and first_open) else ''
        out.append(f'<details{op}><summary>{q}</summary><div class="ans">{a}</div></details>')
    return '\n'.join(out)

LEDE_DOOR = "A new home, a renovation or a lot you're considering. Tell us where it is and what you have in mind, and we'll set a time to meet you there."

def door(folio, eyebrow='Schedule a consultation', h2="Let's talk about <em>your project.</em>", lede=LEDE_DOOR, qs=None, page_id='door', h_tag='h2', extra_left=''):
    faq = ''
    if qs:
        faq = f'''
      <div class="faq" id="faq">
        <p class="faq-lab">Questions <i>/</i> before you call</p>
        <div class="faq-list rv d1">
{faq_items(qs)}
        </div>
        <a class="more" href="faq.html">More questions <span>&rarr;</span></a>
      </div>'''
    return f'''
<!-- ═════ the door ═════ -->
<section class="door on-dark" id="{page_id}">
  <div class="door-bg"><img src="img/w/daniel-island-waterfront-home-1200.webp" width="1200" height="1607" loading="lazy" alt=""></div>
  <div class="wrap door-grid">
    <div class="rv">
      <{h_tag} class="hx"><span class="eyebrow">{('<i aria-hidden="true">'+folio+'</i> ') if folio else ''}{eyebrow}</span><span class="sr-only">. </span><span class="h2">{h2}</span></{h_tag}>
      <p class="lede">{lede}</p>
      <div class="phone"><small>Charleston line</small><a href="tel:+18430000000">(843) 000-0000</a><span>843 number issued at launch · Mon to Fri, 8am to 6pm</span></div>{extra_left}{faq}
    </div>
    {FORM}
  </div>
</section>
'''

def sec_head(folio, eyebrow, h2, lede=None):
    l = f'<p class="lede rv d1">{lede}</p>' if lede else ''
    return f'''    <div class="sec-head">
      <h2 class="hx rv"><span class="eyebrow"><i aria-hidden="true">{folio}</i> {eyebrow}</span><span class="sr-only">. </span><span class="h2">{h2}</span></h2>
      {l}
    </div>'''

def ledger(items):
    rows = ''.join(f'<div class="ledger-item rv{" d"+str(i) if i else ""}"><span class="mk">{n}</span><p class="lt">{t}</p><p>{x}</p></div>' for i, (n, t, x) in enumerate(items))
    return f'<div class="ledger"><div class="wrap ledger-row">{rows}</div></div>'

def rail_lt(rows):
    """The survey rail on a light ground, every row open. Rows are (n, title, text) or (n, title, text, source)."""
    out = []
    for i, r in enumerate(rows):
        n, t, x = r[:3]; src = f'<small>{r[3]}</small>' if len(r) > 3 and r[3] else ''
        out.append(f'''      <div class="rrow rv{" d"+str(min(i,3)) if i else ""}">
        <span class="rnum">{n}</span>
        <div class="rbody"><h3>{t}</h3><p>{x}</p>{src}</div>
      </div>''')
    return '<div class="rail-lt">\n' + '\n'.join(out) + '\n    </div>'

def range_grid(folio, eyebrow, h2, lede, figs, foot=None):
    """Three arch photographs on black: finished homes by the partner."""
    f = ''.join(f'<figure class="rv{" d"+str(i) if i else ""}">{pic(n, alt, ratio="4/5", sizes="(max-width:860px) 100vw, 30vw")}<figcaption>{cap}</figcaption></figure>' for i, (n, alt, cap) in enumerate(figs))
    ft = f'<div class="range-foot rv"><p>{foot}</p></div>' if foot else ''
    return f'''
<!-- ═════ finished homes ═════ -->
<section class="range on-dark">
  <div class="wrap">
{sec_head(folio, eyebrow, h2, lede)}
    <div class="range-grid">{f}</div>
    {ft}
  </div>
</section>
'''

def team_block(folio, h2, lede, long=False):
    """Meet the team. Greg's portrait and bio are placeholders until RAM supplies them: nothing invented."""
    more = ''
    if long:
        more = '''
      <!-- PLACEHOLDER COPY · the Charleston team: names, roles and one line each, from RAM -->
      <p class="story-p"><span class="ph">[The Charleston team: names and roles, one line each. Project manager, site superintendent, design lead.]</span></p>'''
    return f'''
<!-- ═════ meet the team ═════ -->
<section class="team" id="team">
  <div class="wrap team-grid">
    <figure class="team-art rv">
      <div class="arch ph-port" role="img" aria-label="Portrait of Greg, to be photographed"><svg viewBox="190 128 528 488" aria-hidden="true"><use href="#glyphdef"/></svg><span>Portrait<br>to come</span></div>
      <figcaption class="cap">Greg · RAM Construction Charleston</figcaption>
    </figure>
    <div class="team-copy rv d1">
      <h2 class="hx"><span class="eyebrow"><i aria-hidden="true">{folio}</i> Meet the team</span><span class="sr-only">. </span><span class="h2">{h2}</span></h2>
      <p class="lede">{lede}</p>
      <!-- PLACEHOLDER COPY · replace with Greg's name, role and background before launch -->
      <p class="team-bio"><b>Greg</b> <span class="ph">[full name and role]</span> leads RAM Construction Charleston. <span class="ph">[Two or three sentences on his background: years building, where he trained, what brought him to the Lowcountry, the kind of homes he likes to build.]</span></p>{more}
      <dl class="team-facts">
        <div><dt>Your project manager</dt><dd>One person from the first sketch to the final walk-through, with a site meeting every week and a written recap after each one.</dd></div>
        <div><dt>Our design team</dt><dd>In-house, drawing with local Lowcountry architects who know each town's review boards.</dd></div>
        <div><dt>Our partner</dt><dd>RAM Construction of Charlotte, building custom homes since 2004, whose experience and resources stand behind every Charleston project.</dd></div>
      </dl>
    </div>
  </div>
</section>
'''

# ── content ──────────────────────────────────────────────────────────────────
SITE = 'https://ramconstructionsc.com'   # placeholder domain, swapped at launch
BRAND = 'RAM Construction Charleston'
def url(f):
    """Route-style URL for schema: about.html -> /about (the app serves extensionless routes)."""
    return SITE + ('/' if f == 'index.html' else '/' + f[:-5])

PARTNER_FIGS = [
    ('ram-modern-home-balconies', 'A modern RAM home with stacked balconies and a landscaped front', 'Modern home · RAM Charlotte'),
    ('ram-range-brass-kitchen', 'Black and brass range beneath a white tile wall in a RAM kitchen', 'Kitchen · RAM Charlotte'),
    ('ram-screened-porch-wood-ceiling', 'Screened porch with a vaulted wood ceiling and seating', 'Screened porch · RAM Charlotte'),
]
PARTNER_LEDE = 'Finished homes by our partner, RAM Construction of Charlotte, photographed as built: the standard of finish every RAM Charleston home is held to.'

Q = {  # one source for every question that appears on more than one page
 'lot': ('Do I need to own a lot first?', "No. We can evaluate lots you're considering and tell you what each one allows, including its flood zone and review rules, before you buy."),
 'price': ('How is the price set?', 'After design, we issue a fixed bid with allowances listed line by line, so you know the number before you sign.'),
 'flood': ('How do I know which flood zone my lot is in?', 'We check your lot against the current flood maps during lot evaluation and explain what that zone means for the foundation and design.'),
 'plans': ("Can you build from my architect's plans?", 'Yes. We review third-party plans for constructability and coastal requirements before we bid. Most clients use our in-house design team and its local architects, because design and pricing stay together.'),
 'reno': ('Renovate or rebuild?', 'It depends on the structure, the flood elevation and what you want the home to become. We assess the house and give you an honest answer on both paths.'),
 'partner': ('How is RAM Charleston related to RAM in Charlotte?', 'We are partners, not one company. RAM Construction Charleston holds its own South Carolina license and builds with its own Lowcountry team. RAM Construction of Charlotte, building custom homes there since 2004, brings its experience, its design and 3D modelling tools and the same fixed-bid process to every Charleston project.'),
 'who': ('Who will I be working with?', 'Greg and the Charleston team, introduced on our About page. You have one project manager from first sketch to final walk-through, with a site meeting every week and a written recap after each one.'),
 'warranty': ('Is there a warranty?', 'Warranty terms are written into your RAM Construction Charleston contract and confirmed before you sign.'),
 'budget': ('When do we talk about budget?', 'Early, before the plans are final. We explain what each feature adds to the total as we design, so you decide what to keep with the number in front of you rather than after a bid comes back.'),
 '3d': ('What is the 3D walk-through?', 'Our lead designer builds an immersive 3D model alongside the preliminary plans, so you tour every room, fixture and finish before construction. The model is approved by a structural engineer, so the changes you make in it can be trusted.'),
 'inhouse': ('Do you design in-house?', "Yes. Design is in-house: our team draws with local Lowcountry architects who know each town's review boards, and the drawing is priced by the team that will build it. The drawings that go to the county are the drawings we build."),
 'elevated': ('What does an elevated home involve?', "The finished floor is set above the flood elevation from the maps and the town's rule; the foundation, venting or pilings are drawn for it; the ground level becomes parking and storage; and the porch goes where the breeze is. All of it is in the first sketch, not added at the end."),
 'boards': ('Which towns have design review?', "The Old Village of Mount Pleasant (Historic District Preservation Commission), Sullivan's Island (Design Review Board) and Daniel Island (Architectural Review Board) review new homes, and inside Wild Dunes on Isle of Palms the community's own board issues a permit. We prepare the drawings, elevations and 3D views each board asks to see, and present them."),
 'wind': ('How do you build for hurricanes?', 'Impact-rated openings, a continuous load path and roof tie-downs are specified in the drawings for every coastal home, not added when the permit comes back.'),
 'salt': ('What about salt air?', 'Stainless fasteners, marine-grade finishes and siding chosen to last on the coast, specified by the team that builds the home.'),
 'lines': ('What are the beachfront lines on the islands?', "The state's Bureau of Coastal Management sets a baseline along the primary dune and a setback line behind it. What may be built seaward of those lines is limited and permitted by the state. We locate both on the survey before we draw."),
 'trees': ('What about the trees on the lot?', 'In Mount Pleasant any tree of 16 inches and over on a residential lot is protected, and live oaks of 24 inches and over are historic trees. The other towns and review boards have rules of their own. We survey the canopy before we draw and site the house around the trees worth keeping.'),
 'work': ('Where can I see your work?', "Featured projects on the homepage and the service pages show finished homes by our partner, RAM Construction of Charlotte, photographed as built. They set the standard every RAM Charleston home is held to. The Lowcountry scenes on this site are illustrative renderings and are marked as such."),
 'renos': ('Do you take on renovations and additions?', 'Yes. Whole-home remodels, additions and the renovation of older homes, including houses under historic or design review, with the same fixed bid and 3D walk-through as a new home.'),
}

TOWNS = {
 'mount-pleasant': dict(
   name='Mount Pleasant', county='Charleston County', file='mount-pleasant.html',
   hero=('mount-pleasant-live-oak-drive', 'A shell drive under live oaks draped in Spanish moss, leading to a white custom home with a deep porch in Mount Pleasant'),
   second=('mount-pleasant-old-village-street', 'A white two-storey home with stacked piazzas behind a brick wall on a live-oak street in the Old Village of Mount Pleasant'),
   third=('coast-house-between-live-oaks', 'A white custom home sited between two grand live oaks, their limbs reaching over the roof'),
   h1='Mount Pleasant, <em>drawn around the oaks.</em>',
   lede='Marsh-front lots off Shem Creek and the Wando, the Old Village behind its brick walls, and the grand trees that came before any of it. We read the lot, the trees and the flood map before the first line.',
   meta=['Old Village Historic District', 'Tree protection ordinance', 'Creek and harbour flood zones'],
   intro=('What the town asks', 'Four rules, <em>read before we draw.</em>',
          'Mount Pleasant is the largest of the four towns and the most varied: a historic village, marsh-front creeks and new neighbourhoods inland. Each brings its own paperwork, and each is handled in the drawings.'),
   rows=[
     ('01', 'Grand trees', 'Any tree of 16 inches and over on a residential lot is protected and needs the town\'s approval before removal; live oaks of 24 inches and over are historic trees and call for an arborist\'s report. We survey the canopy first and site the house around it, then keep a barricaded protection zone, one foot of radius for every inch of trunk, clear through construction.', 'Town of Mount Pleasant zoning code, §156.702 and §156.705'),
     ('02', 'The Old Village', 'Inside the Old Village Historic District the Historic District Preservation Commission reviews new construction, additions, exterior changes, walls, driveways and docks. A meeting with town staff comes before the application, and the commission reads the drawings against its published guidelines. We prepare that set.', 'Old Village Historic District guidelines, Town of Mount Pleasant'),
     ('03', 'Flood elevation', 'Much of the Old Village and the creek-front lots lie inside flood zones. The zone and the lot\'s elevation set the finished floor, the foundation and the venting before the plan begins, not after.', 'Town of Mount Pleasant, flood zone guidance in the Old Village guidelines'),
     ('04', 'Wind and salt', 'The harbour wind reaches every street. Impact-rated openings, a continuous load path and roof tie-downs are specified in the drawings; fasteners and finishes are chosen for the salt.', 'RAM Construction Charleston, standard for every coastal home'),
   ],
   places=['Old Village', "I'On", 'Hobcaw Creek', 'Snee Farm', 'Park West', 'Carolina Park', 'Dunes West', 'Rivertowne', 'Belle Hall'],
   places_lede='From the Old Village to the neighbourhoods off Highway 17 and 41, each with its own architectural review or none at all. Tell us the street and we will tell you the rules.',
   ram=[('i', 'The canopy on the plan', 'Every protected tree on the survey before the first sketch, and a house shaped around the ones worth keeping.'),
        ('ii', 'The commission\'s set', 'Drawings, elevations and 3D views prepared for the Old Village review, presented by us.'),
        ('iii', 'One fixed bid', 'Priced by the team that will build it, with allowances listed line by line.')],
   qs=[('Can you save the oaks on my lot?', 'Usually the question is which ones. We survey every protected tree, tell you which are historic, and draw the house around the ones worth keeping. Where a removal is unavoidable we handle the town\'s permit and mitigation.'),
       ('Do you handle the Old Village review?', 'Yes. We meet town staff first, prepare the drawings, elevations and views the Historic District Preservation Commission asks for, and present them.'),
       ('Is my lot in a flood zone?', 'We check it against the current flood maps during lot evaluation and explain what the zone means for the finished floor and the foundation before you commit to a plan.')],
   desc='Custom home builder in Mount Pleasant, SC. RAM Construction Charleston designs and builds around the town\'s grand trees, the Old Village historic review and the flood maps, with a fixed bid and a 3D walk-through before construction.',
 ),
 'isle-of-palms': dict(
   name='Isle of Palms', county='Charleston County', file='isle-of-palms.html',
   hero=('isle-of-palms-elevated-beach-house', 'An elevated beach house on white pilings behind grassy dunes on Isle of Palms'),
   second=('isle-of-palms-dune-boardwalk', 'A wooden boardwalk over high dunes toward the Atlantic on Isle of Palms, a raised beach house at its edge'),
   third=('coast-salt-air-piazza-rail', 'The corner of a white piazza rail with stainless fittings and a copper lantern, dunes and ocean haze beyond'),
   h1='Isle of Palms, <em>raised above the dune line.</em>',
   lede='Front-beach lots, the Intracoastal side and Wild Dunes behind its gates. Every home here stands on pilings, faces the wind, and answers to the state\'s beachfront lines before the city\'s permit.',
   meta=['State beachfront baseline and setback', 'Wild Dunes Architectural Review Board', 'Pile foundations, salt-rated finishes'],
   intro=('What the island asks', 'A barrier island <em>has its own lines.</em>',
          'The Isle of Palms is built out; most new homes replace an older one on the same lot. That lot carries lines the state drew, rules the city wrote and, inside Wild Dunes, a review board of its own.'),
   rows=[
     ('01', 'The beachfront lines', 'The state\'s Bureau of Coastal Management sets a baseline along the crest of the primary dune and a setback line behind it. What may be built or rebuilt seaward of those lines is limited and permitted by the state, not the city. We locate both lines on the survey before we draw.', 'S.C. Code §48-39-280; SCDES Bureau of Coastal Management jurisdictional lines, 2018'),
     ('02', 'Wild Dunes', 'Inside the gates every exterior work needs a Wild Dunes Community Association building permit. Its Architectural Review Board meets twice a month and asks for a sealed tree and topographic survey showing every tree of six inches and over, the drainage and the critical line.', 'Wild Dunes Community Association, architectural review standards'),
     ('03', 'Pilings and flood', 'Oceanfront and marsh lots carry the island\'s flood elevations. The home rises on pilings with parking and storage beneath and the living floors above; the porch goes where the breeze is, on the ocean side, screened from the salt.', 'FEMA flood maps for Charleston County; City of Isle of Palms building department'),
     ('04', 'Water on the lot', 'New hardscaping must be pervious, and any work that disturbs 625 square feet or more needs a drainage plan. Both are drawn with the house, not added when the permit comes back.', 'City of Isle of Palms zoning, 2020 building guidance'),
   ],
   places=['Wild Dunes', 'Front Beach, Ocean Boulevard', 'Forest Trail', 'Waterway Boulevard', 'Palm Boulevard', 'The Breach Inlet end'],
   places_lede='Oceanfront, second row or on the Intracoastal Waterway, each address changes the flood elevation, the wind exposure and who reviews the drawings.',
   ram=[('i', 'The lines on the survey', 'Baseline, setback line and critical line located before the first sketch, so the plan fits the buildable ground.'),
        ('ii', 'Built for the salt', 'Stainless fasteners, marine-grade finishes and siding chosen to last on the island.'),
        ('iii', 'Walk it before we build', 'An immersive 3D tour of the raised plan, porch to parking, before a piling is driven.')],
   qs=[('Can I rebuild on my oceanfront lot?', 'Usually yes, within the state\'s beachfront lines and the city\'s zoning. We locate the lines on your survey during lot evaluation and tell you what the ground allows before you plan.'),
       ('Do you work inside Wild Dunes?', 'Yes. We prepare the survey, drawings and materials the Wild Dunes Architectural Review Board asks for and take the design through its review before the city permit.'),
       ('How high will the house sit?', 'That comes from the flood map and the lot\'s elevation. We set the finished floor, the pilings and the parking level from the first sketch and show you the result in 3D.')],
   desc='Custom home builder on Isle of Palms, SC. RAM Construction Charleston designs and builds elevated beach homes to the state beachfront lines, Wild Dunes review and the flood maps, with a fixed bid and a 3D walk-through.',
 ),
 'sullivans-island': dict(
   name="Sullivan's Island", county='Charleston County', file='sullivans-island.html',
   hero=('sullivans-island-island-cottage', "A raised island cottage with a screened porch behind a picket fence on Sullivan's Island"),
   second=('sullivans-island-station-cottage', "A white board-and-batten island cottage with a deep screened porch on a sandy lane on Sullivan's Island"),
   third=('coast-storm-shutters-squall', 'An elevated white Lowcountry home with green Bahama shutters as a squall line crosses the marsh sky'),
   h1="Sullivan's Island, <em>to the island's measure.</em>",
   lede='A small island with firm ideas about size. The Design Review Board reads every new home, the zoning caps the footprint against the lot, and the historic cottages set the tone for what comes next.',
   meta=['Design Review Board', 'House size capped by lot area', 'Historic island cottages'],
   intro=('What the island asks', 'Smaller by rule, <em>better by design.</em>',
          "Sullivan's Island protects its scale in writing. That is a constraint for some builders and a brief for us: the best houses here are the ones drawn to the island's measure from the start."),
   rows=[
     ('01', 'The Design Review Board', 'Seven members appointed by council review and approve the design of every new home and renovation on the island, meeting once a month. Foundation height, orientation and the street façade are design standards the board reads; we bring the drawings and the 3D views that answer them.', "Town of Sullivan's Island, Design Review Board"),
     ('02', 'Size against the lot', 'Zoning caps the principal building\'s footprint at 15 percent of the lot on lots of 15,000 square feet and more, with a higher share on small lots, and caps the square footage by formula. The board may allow a modest increase where it makes the house sit better among its neighbours.', "Town of Sullivan's Island zoning ordinance, §21-25 to §21-27 and §21-52"),
     ('03', 'The historic cottages', 'Older houses are classed as Traditional Island Resources and Landmarks, and changes to them are reviewed against their character. A renovation here begins with what the house already is.', "Town of Sullivan's Island, Design Review Board application guidance"),
     ('04', 'Harbour on one side, ocean on the other', 'Every lot carries a flood elevation and a wind design; the state\'s beachfront lines run along the ocean side. We draw the foundation height as the board reads it and specify the openings and tie-downs for the wind.', 'FEMA flood maps for Charleston County; SCDES beachfront jurisdictional lines'),
   ],
   places=['The Stations, 9 through 32', 'Middle Street', 'Atlantic Avenue', "I'On Avenue", 'The Breach Inlet end', 'The Fort Moultrie end'],
   places_lede='Addresses run by station number along one long island. The ocean side, the back beach and the harbour end each carry their own lines and views.',
   ram=[('i', 'Drawn to the cap', 'Footprint and square footage worked out against the lot before the plan, so nothing is designed twice.'),
        ('ii', 'The board\'s set', 'Elevations, foundation height and views prepared for the Design Review Board and presented by us.'),
        ('iii', 'One fixed bid', 'Priced by the team that will build it, allowances listed line by line.')],
   qs=[('How big a house can I build?', 'It depends on the lot area. We work the footprint and square footage caps for your lot during evaluation and design to them from the start, so the board sees a house that already fits.'),
       ('Do you present to the Design Review Board?', 'Yes. We prepare the drawings, elevations and 3D views the board asks for and present the design at its monthly meeting.'),
       ('Can you renovate a historic cottage?', 'Yes. We assess what the house is, what the review allows and what the flood elevation asks, and give you an honest answer on renovating or rebuilding.')],
   desc="Custom home builder on Sullivan's Island, SC. RAM Construction Charleston designs to the island's Design Review Board and its size caps, with a fixed bid and a 3D walk-through before construction.",
 ),
 'daniel-island': dict(
   name='Daniel Island', county='Berkeley County · City of Charleston', file='daniel-island.html',
   hero=('daniel-island-waterfront-home', 'A new Lowcountry home with double porches on the marsh at sunset on Daniel Island'),
   second=('daniel-island-wando-waterfront', 'A white Lowcountry home on a marsh-front lot on Daniel Island with a long private dock reaching the Wando River'),
   third=('tidal-creek-marsh-aerial-dusk', 'Aerial view of a tidal creek winding through spartina marsh with a private dock at dusk'),
   h1='Daniel Island, <em>to the plan of the place.</em>',
   lede='A master-planned island on the Wando with review guidelines for every neighbourhood and a board that reads each new home before the city does. We design inside those guidelines and make them look easy.',
   meta=['Architectural Review Board', 'Neighbourhood design guidelines', 'Wando and creek-front lots'],
   intro=('What the island asks', 'A plan for the island, <em>a plan for the house.</em>',
          'Daniel Island was drawn as a whole before its first house. The guidelines that came with it decide roof pitch, foundation, size and where the house sits on its lot. Knowing them first is most of the work.'),
   rows=[
     ('01', 'The Architectural Review Board', 'The Daniel Island Architectural Review Board reviews every new home and every exterior change before the City of Charleston issues a permit. Each association has its own guidelines: the Community Association, Daniel Island Park, the Town Center, Captain\'s Island and the Retreat.', 'Daniel Island Property Owners\' Association, ARB and design guidelines'),
     ('02', 'The rules of the house', 'Pitched roofs between 8:12 and 12:12, foundation walls that enclose a crawl space rather than a slab at grade, minimum and maximum home sizes, and a build-to line that most of the front of the house must meet. We draw to them from the first sketch.', 'Daniel Island Community Association design guidelines'),
     ('03', 'Daniel Island Park', 'In the Park the home must be designed by a registered architect and the landscape by a landscape architect registered in South Carolina; garages step back or turn to the side, and a house that overpowers its setting is not approved. Our in-house design team works with local registered architects and landscape architects to carry both.', 'Daniel Island Park residential planning guide'),
     ('04', 'The water\'s edge', 'Marsh-front lots on the Wando and along Ralston and Beresford creeks carry a visual buffer of planting at the water and a flood elevation from the county maps. The dock, the buffer and the finished floor are drawn with the house.', 'Daniel Island Park planning guide; FEMA flood maps for Berkeley County'),
   ],
   places=['Daniel Island Park', 'Smythe Park', 'Center Park', "Codner's Ferry Park", 'Etiwan Park', 'Barfield Park', 'Ralston Creek', 'Beresford Creek', "Captain's Island"],
   places_lede='Park by park the guidelines shift a little: lot widths, build-to lines, the size of the house the street expects. We keep the current set for each one.',
   ram=[('i', 'Architect and builder, one table', 'The local registered architect the Park requires works with our design team, at the same table as the builder who prices the drawing.'),
        ('ii', 'The board\'s set', 'Conceptual and final submittals, landscape plan included, prepared and presented by us.'),
        ('iii', 'Walk it before we build', 'An immersive 3D tour of every room and finish before the first inspection.')],
   qs=[('Do you take the design through the ARB?', 'Yes. We prepare the conceptual and final submittals for the Daniel Island Architectural Review Board, including the landscape plan where the guidelines require one, and present them.'),
       ('Can you design for Daniel Island Park?', 'Yes. Our in-house design is drawn with local registered architects, as the Park requires, and we work with a South Carolina-registered landscape architect on the site plan.'),
       ('What about a dock on the Wando?', 'Docks are reviewed by the board and permitted by the state. We design the dock, the water\'s-edge buffer and the house together so nothing is left to the end.')],
   desc='Custom home builder on Daniel Island, SC. RAM Construction Charleston designs to the Daniel Island Architectural Review Board and each park\'s guidelines, with a fixed bid and a 3D walk-through before construction.',
 ),
}
TOWN_ORDER = ['mount-pleasant', 'isle-of-palms', 'sullivans-island', 'daniel-island']

def colonnade(folio, lede, with_marquee=True):
    """The four towns as the staggered colonnade (homepage device, now on the Lowcountry page)."""
    cards = {
      'mount-pleasant': ('Marsh-front lots, Old Village cottages and grand protected trees.', 'Building in Mount Pleasant'),
      'isle-of-palms': ('Elevated beach homes built for wind, water and salt.', 'Building on Isle of Palms'),
      'sullivans-island': ('Island homes that fit a small, historic town and its design review.', "Building on Sullivan's"),
      'daniel-island': ("Custom homes drawn inside the community's architectural guidelines.", 'Building on Daniel Island'),
    }
    out = ''
    for i, s in enumerate(TOWN_ORDER):
        t = TOWNS[s]; p, more = cards[s]
        out += f'''      <a class="area{" is-open" if i == 0 else ""} rv{" d"+str(i) if i else ""}" href="{t["file"]}">{pic(t["hero"][0], t["hero"][1], ratio="3/4", sizes="(max-width:860px) 46vw, 30vw")}<div class="area-meta"><small>{t["county"].split(" ·")[0]}</small><h3>{t["name"]}</h3><p>{p}</p><span class="more">{more} <span>&rarr;</span></span></div></a>\n'''
    marquee = '''  <div class="marquee" aria-hidden="true"><div class="marquee-track">
    <span>Mount Pleasant</span><span>Isle of Palms</span><span>Sullivan's Island</span><span>Daniel Island</span><span>Charleston</span>
    <span>Mount Pleasant</span><span>Isle of Palms</span><span>Sullivan's Island</span><span>Daniel Island</span><span>Charleston</span>
  </div></div>''' if with_marquee else ''
    return f'''
<!-- ═════ where we build · the colonnade ═════ -->
<section class="areas on-dark" id="areas">
  <svg class="watermark" viewBox="190 128 528 488" aria-hidden="true"><use href="#glyphdef"/></svg>
  <div class="wrap">
{sec_head(folio, 'Where we build · Charleston', 'Four towns, <em>four sets of rules.</em>', lede)}
    <div class="colonnade acc" id="acc">
{out}    </div>
  </div>
{marquee}
</section>
'''

# ── towns ────────────────────────────────────────────────────────────────────
def town_page(slug):
    t = TOWNS[slug]
    hero = pic(*t['hero'], ratio='3/3.6', eager=True)
    second = pic(*t['second'], ratio='4/5')
    third = pic(*t['third'], ratio='4/3' if slug == 'daniel-island' else '4/5')
    others = [s for s in TOWN_ORDER if s != slug]
    other_links = ''.join(f'<li><a href="{TOWNS[o]["file"]}">{TOWNS[o]["name"]} <span>&rarr;</span></a></li>' for o in others)
    places = ''.join(f'<li class="rv{" d"+str(i%4) if i%4 else ""}"><span>{p}</span></li>' for i, p in enumerate(t['places']))
    intro_eb, intro_h2, intro_lede = t['intro']
    d = door('III', 'Schedule a consultation', f'Let\'s talk about <em>your {t["name"]} project.</em>', LEDE_DOOR, qs=t['qs'])
    body = f'''{phero(f'Where we build · {t["county"]}', t['h1'], t['lede'], hero, meta=t['meta'])}

<!-- ═════ the conditions ═════ -->
<section class="tconds">
  <div class="wrap">
{sec_head('I', intro_eb, intro_h2, intro_lede)}
    <div class="tconds-grid">
      {rail_lt(t['rows'])}
      <div class="tconds-art rv d1">
        {second}
        {third}
      </div>
    </div>
  </div>
</section>

<!-- ═════ what RAM does here ═════ -->
{ledger(t['ram'])}

<!-- ═════ the places ═════ -->
<section class="tplaces on-dark">
  <div class="wrap">
{sec_head('II', 'Where we draw', f'<em>{t["name"]}</em>, street by street.', t['places_lede'])}
    <ul class="places">{places}</ul>
    <div class="tother rv">
      <p class="datum-lab">Also on the coast</p>
      <ul>{other_links}<li><a href="lowcountry.html">Building in the Lowcountry <span>&rarr;</span></a></li></ul>
    </div>
  </div>
</section>
{d}
</main>
'''
    ld = jsonld({"@context": "https://schema.org", "@type": "WebPage", "name": f'Custom Homes in {t["name"]}, SC',
                 "description": t['desc'], "url": url(t["file"]),
                 "about": {"@type": "Service", "serviceType": "Custom home building", "provider": {"@type": "GeneralContractor", "name": BRAND},
                           "areaServed": {"@type": "Place", "name": f'{t["name"]}, SC'}},
                 "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
                     {"@type": "ListItem", "position": 1, "name": "Home", "item": f'{SITE}/'},
                     {"@type": "ListItem", "position": 2, "name": "Building in the Lowcountry", "item": url('lowcountry.html')},
                     {"@type": "ListItem", "position": 3, "name": t['name'], "item": url(t["file"])}]}})
    title = f'Custom Home Builder in {t["name"]}, SC | {BRAND}'
    pre = f'<link rel="preload" as="image" href="img/w/{t["hero"][0]}-{W[t["hero"][0]][-1]}.webp">\n'
    return head(title, t['desc'], f'{SITE}/{t["file"]}', f'img/w/{t["hero"][0]}-{W[t["hero"][0]][-1]}.webp', pre) + chrome(t['file']) + body + tail(t['file'], ld)

# ── services ─────────────────────────────────────────────────────────────────
SERVICES = {
 'custom-homes': dict(
   file='custom-homes.html', name='Custom Homes', svc='Custom home building',
   title=f'Custom Homes in Charleston, SC | {BRAND}',
   desc="Custom home builder in Charleston, SC. RAM Construction Charleston designs and builds new homes in Mount Pleasant, Isle of Palms, Sullivan's Island and Daniel Island: lot evaluation first, in-house design with local architects, one fixed bid and a 3D walk-through before construction.",
   hero=('hero-lowcountry-portrait', 'A white Lowcountry custom home with double piazzas on the edge of a golden marsh at sunset'),
   h1='A new home, <em>designed for your lot.</em>',
   lede="Ground-up custom homes in Mount Pleasant, Isle of Palms, Sullivan's Island and Daniel Island. We evaluate the lot first, design with you and our local architects, price it as one fixed bid and let you walk the house in 3D before we build it.",
   meta=['Lot evaluation first', 'Original design, in-house', 'One fixed bid before you sign'],
   ledger=[('i', 'The lot comes first', 'Zoning and setbacks, the flood zone, protected trees and which board reviews the design, in writing before you commit to a plan or a purchase.'),
           ('ii', 'Drawn for your ground', 'Every plan is original, drawn by our design team with local Lowcountry architects for your lot, your trees and your light.'),
           ('iii', 'One fixed price', 'The team that will build it prices the drawing, with every allowance listed line by line.')],
   intro=('What a custom home includes', 'From the first site walk <em>to the keys.</em>',
          'Seven stages, in the order they happen. The depth of each is on our process page; this is what you can expect from a RAM Charleston custom home.'),
   rows=[('01', 'Lot evaluation', 'We walk the lot, at low tide if it touches the marsh, and check it against the zoning, the flood maps, the tree ordinance and any review board. You get the findings in writing.'),
         ('02', 'Design with local architects', 'Our design team and Lowcountry architects draw the plan, the elevations and the materials with you over the table. The design answers the lot and the town from the first sketch.'),
         ('03', 'A budget before the plans are final', 'We explain what each feature adds as we design, so you decide what to keep with the number in front of you.'),
         ('04', 'The 3D walk-through', 'Tour every room, fixture and finish in an immersive model, checked by a structural engineer, and change what you want to change before construction.'),
         ('05', 'The fixed bid', 'Priced by the team that will build it. Allowances listed line by line; you know the number before you sign.'),
         ('06', 'Permits and review boards', 'We prepare and present the drawings, elevations and views each town or board asks to see, then pull the permits.'),
         ('07', 'The build', 'A dedicated RAM Charleston team, one project manager, a site meeting every week and a written recap after each one, through to the final walk-through.')],
   art=[('ram-two-storey-porches', 'A home by RAM Construction of Charlotte with two storeys of deep porches'), ('ram-coffered-living-room', 'Finished living room by RAM Construction of Charlotte with a coffered ceiling and fireplace')],
   figs=[('ram-two-storey-porches', 'A RAM custom home with two storeys of deep covered porches', 'Custom home · RAM Charlotte'),
         ('ram-kitchen-island-lanterns', 'RAM kitchen with a marble island and iron lanterns', 'Kitchen · RAM Charlotte'),
         ('ram-pool-terrace', 'Long pool and stone terrace behind a RAM home', 'Pool terrace · RAM Charlotte')],
   qs=['lot', 'price', 'plans'],
 ),
 'renovations-additions': dict(
   file='renovations-additions.html', name='Renovations & Additions', svc='Home renovation and additions',
   title=f'Home Renovations & Additions in Charleston, SC | {BRAND}',
   desc="Renovations and additions in Charleston, SC. RAM Construction Charleston remodels and extends homes in Mount Pleasant, the islands and Daniel Island, including houses under historic or design review, with a fixed bid and a 3D walk-through.",
   hero=('ram-craftsman-porte-cochere', 'A craftsman home by RAM Construction of Charlotte with a screened porch and stone porte-cochere'),
   h1='Renovations and additions <em>that keep what you love.</em>',
   lede="The right lot and the wrong layout, a cottage that needs one more room, a house that has to come up above the flood line. We remodel and extend homes across the four towns with the same fixed bid and 3D walk-through as a new home.",
   meta=['Whole-home remodels', 'Additions', 'Historic and review-board renovations'],
   ledger=[('i', 'Renovate or rebuild', 'We assess the structure, the flood elevation and what you want the house to become, and give you an honest answer on both paths.'),
           ('ii', 'Review boards handled', "The Old Village, Sullivan's Island and Daniel Island review exterior changes. We prepare the drawings each board asks for and present them."),
           ('iii', 'Priced before you sign', 'A fixed bid with allowances listed line by line, after the design is settled and toured in 3D.')],
   intro=('What we take on', 'Four kinds of work, <em>one way of working.</em>',
          'A renovation starts with what the house already is. We measure it, draw the change with you and our local architects, and show you the result in 3D before anyone picks up a tool.'),
   rows=[('01', 'Whole-home remodels', 'New plan, new kitchen, new baths, new systems inside the shell you have. Drawn as one design so the house reads as one house when it is done.'),
         ('02', 'Additions', 'A room, a wing, a second storey or a porch, designed to the house and to the lot, with the setbacks, the trees and the flood elevation checked first.'),
         ('03', 'Historic and review-board renovations', "Older houses in the Old Village and on Sullivan's Island are reviewed against their character. We begin with what the house is, prepare the board's set and present it."),
         ('04', 'Renovate-or-rebuild assessment', 'When the question is whether the house is worth keeping, we assess the structure, the flood elevation and the cost of each path and give you a straight answer.')],
   art=[('ram-craftsman-porte-cochere', 'A craftsman home by RAM Construction of Charlotte with a stone porte-cochere'), ('ram-brass-bridge-faucet', 'A brass bridge faucet over a farmhouse sink in a RAM kitchen')],
   figs=[('ram-coffered-living-room', 'Finished RAM living room with a coffered ceiling and fireplace', 'Living room · RAM Charlotte'),
         ('ram-brass-tub-filler', 'Brass floor-mounted tub filler beside plantation shutters', 'Primary bath · RAM Charlotte'),
         ('ram-outdoor-fireplace-porch', 'Covered porch with a stone outdoor fireplace and wood ceiling', 'Porch · RAM Charlotte')],
   qs=['reno', 'boards', 'price'],
 ),
 'design-preconstruction': dict(
   file='design-preconstruction.html', name='Design & Preconstruction', svc='Home design and preconstruction',
   title=f'Home Design & Preconstruction in Charleston, SC | {BRAND}',
   desc="Home design and preconstruction in Charleston, SC. RAM Construction Charleston's in-house design team draws with local Lowcountry architects, sets the budget before the plans are final and builds the 3D model you walk through before construction.",
   hero=('drafting-table-lowcountry-drawings', 'Architectural drawings of a Lowcountry home with a basswood model on a walnut drafting table'),
   h1='Designed in-house, <em>with local architects.</em>',
   lede="Our design team draws your home with Lowcountry architects who know each town's review boards, sets the budget alongside the design, and builds the 3D model you walk through before a board is cut. Design and pricing stay at one table.",
   meta=['Local Lowcountry architects', 'Budget before the plans are final', '3D model, engineer-checked'],
   ledger=[('i', 'Local architects', "Architects who work on this coast and know what each board asks to see, drawing with our design team at the same table as the builder."),
           ('ii', 'The budget comes early', 'Set before the plans are final, with the cost of every feature explained, so change orders are the exception rather than the business model.'),
           ('iii', 'The model you can trust', 'The lead designer builds the 3D model alongside the preliminary plans, and a structural engineer approves it, so what you change in the model is what gets built.')],
   intro=('What preconstruction covers', 'Everything that happens <em>before the first nail.</em>',
          'The expensive mistakes in a custom home are made on paper. Preconstruction is where we make sure they are not made at all.'),
   rows=[('01', 'Lot evaluation and feasibility', 'What the lot allows: zoning, setbacks, the flood zone, the trees and the board, in writing before you commit.'),
         ('02', 'Schematic design', 'Plans, elevations and materials drawn with you and our local architects, answering the lot and the town from the first sketch.'),
         ('03', 'Budget alongside the design', 'What each feature adds, explained as it is drawn, so the design and the number arrive together.'),
         ('04', 'The 3D walk-through', 'Every room, fixture and finish in an immersive model, approved by a structural engineer, toured and changed before construction.'),
         ('05', 'Review-board and permit drawings', 'The set each town or board asks for, prepared and presented by us, then the permit drawings that follow.'),
         ('06', 'Plans from elsewhere', "Bringing your own architect's plans? We review them for constructability and coastal requirements before we bid.")],
   art=[('ram-3d-rendering-modern', 'A 3D rendering by RAM of a modern three-storey home with a motor court'), ('ram-3d-rendering-hillside', 'A 3D rendering by RAM of a hillside home')],
   figs=[('ram-3d-rendering-modern', 'A 3D rendering of a modern three-storey home', '3D rendering · RAM Charlotte'),
         ('ram-modern-home-balconies', 'A modern RAM home with stacked balconies and a landscaped front terrace', 'As built · RAM Charlotte'),
         ('ram-range-brass-kitchen', 'Black and brass range beneath a white tile wall in a RAM kitchen', 'Kitchen · RAM Charlotte')],
   qs=['inhouse', '3d', 'plans'],
 ),
}
SERVICE_ORDER = ['custom-homes', 'renovations-additions', 'design-preconstruction']

def service_page(slug):
    s = SERVICES[slug]
    hero = pic(*s['hero'], ratio='3/3.6', eager=True)
    others = ''.join(f'<li><a href="{SERVICES[o]["file"]}">{SERVICES[o]["name"]} <span>&rarr;</span></a></li>' for o in SERVICE_ORDER if o != slug)
    intro_eb, intro_h2, intro_lede = s['intro']
    art = ''.join(pic(n, alt, ratio='4/5' if i == 0 else '4/3') for i, (n, alt) in enumerate(s['art']))
    d = door('III', qs=[Q[k] for k in s['qs']])
    body = f'''{phero('Services · Charleston, SC', s['h1'], s['lede'], hero, meta=s['meta'])}

{ledger(s['ledger'])}

<!-- ═════ what it includes ═════ -->
<section class="tconds">
  <div class="wrap">
{sec_head('I', intro_eb, intro_h2, intro_lede)}
    <div class="tconds-grid">
      {rail_lt(s['rows'])}
      <div class="tconds-art rv d1">
        {art}
      </div>
    </div>
    <div class="tother tother-lt rv">
      <p class="datum-lab">Also from RAM Charleston</p>
      <ul>{others}<li><a href="lowcountry.html">Building in the Lowcountry <span>&rarr;</span></a></li></ul>
    </div>
  </div>
</section>
{range_grid('II', 'Finished homes', 'The standard <em>we build to.</em>', PARTNER_LEDE, s['figs'], foot='More finished homes are in the <a href="index.html#projects">featured projects</a> on the homepage.')}
{d}
</main>
'''
    ld = jsonld({"@context": "https://schema.org", "@type": "WebPage", "name": s['title'].split(' | ')[0], "description": s['desc'], "url": url(s['file']),
                 "about": {"@type": "Service", "serviceType": s['svc'], "provider": {"@type": "GeneralContractor", "name": BRAND},
                           "areaServed": [{"@type": "Place", "name": f'{TOWNS[t]["name"]}, SC'} for t in TOWN_ORDER]},
                 "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
                     {"@type": "ListItem", "position": 1, "name": "Home", "item": f'{SITE}/'},
                     {"@type": "ListItem", "position": 2, "name": "Services", "item": f'{SITE}/#services'},
                     {"@type": "ListItem", "position": 3, "name": s['name'].replace('&amp;', '&'), "item": url(s['file'])}]}})
    og = f'img/w/{s["hero"][0]}-{W[s["hero"][0]][-1]}.webp'
    pre = f'<link rel="preload" as="image" href="{og}">\n'
    return head(s['title'], s['desc'], f'{SITE}/{s["file"]}', og, pre) + chrome(s['file']) + body + tail(s['file'], ld)

# ── building in the Lowcountry ───────────────────────────────────────────────
COAST = [
 ('01', 'Flood elevation', 'We check the lot against the current flood maps first, then set the finished floor, the foundation and the venting from the first sketch. On the islands the home rises on pilings, with parking and storage beneath and the living floors above.', 'Marsh lots · the islands'),
 ('02', 'Hurricane wind', 'Impact-rated openings, a continuous load path and roof tie-downs are specified in the drawings for every coastal home, not added when the permit comes back.', 'Every coastal home'),
 ('03', 'Salt air', 'Stainless fasteners, marine-grade finishes and siding chosen to last on the coast, specified by the team that builds the home.', "Isle of Palms · Sullivan's Island"),
 ('04', 'Grand trees', 'We survey the canopy before we draw and site the house around the oaks worth keeping. In Mount Pleasant any tree of 16 inches and over is protected, and live oaks of 24 inches and over are historic trees.', 'Mount Pleasant'),
 ('05', 'Design review', "The Old Village, Sullivan's Island and Daniel Island review new homes, and Wild Dunes issues its own permit. We prepare the drawings, elevations and 3D views each board asks to see, and present them.", "Old Village · Sullivan's · Daniel Island · Wild Dunes"),
]

def lowcountry_page():
    hero = pic('coast-storm-shutters-squall', 'An elevated white Lowcountry home with green Bahama shutters as a squall line crosses the marsh sky', ratio='3/3.6', eager=True)
    d = door('IV', qs=[Q['elevated'], Q['flood'], Q['lines']])
    body = f'''{phero('Building on the coast', 'Building in <em>the Lowcountry.</em>',
                 'A marsh lot asks five things of a house: flood elevation, hurricane wind, salt air, grand trees and design review. We answer each one in the drawings, before the price is set, so nothing is discovered at the end.',
                 hero, meta=['Flood maps read first', 'Wind-rated envelope', 'Salt-air materials', 'Review boards presented'])}

<!-- ═════ the five conditions ═════ -->
<section class="tconds">
  <div class="wrap">
{sec_head('I', 'What the lot asks', 'Handled in the drawings, <em>not at the end.</em>', 'Five conditions every coastal home answers. Each town adds rules of its own; those are on the town pages below.')}
    <div class="tconds-grid">
      {rail_lt(COAST)}
      <div class="tconds-art rv d1">
        {pic('coast-house-between-live-oaks', 'A white custom home sited between two grand live oaks, their limbs reaching over the roof', ratio='4/5')}
        {pic('coast-salt-air-piazza-rail', 'The corner of a white piazza rail with stainless fittings and a copper lantern, dunes and ocean haze beyond', ratio='4/5')}
      </div>
    </div>
  </div>
</section>

{ledger([('i', 'Read before we draw', 'Flood zone, beachfront lines, tree survey and the board that reviews the design, all on the survey before the first sketch.'),
         ('ii', 'Built for the coast', 'Pilings, impact-rated openings, tie-downs and salt-rated materials specified by the team that builds the home.'),
         ('iii', 'Presented for you', "Each board's set of drawings, elevations and 3D views prepared and presented by us.")])}
{colonnade('II', 'Protected oaks, design review boards, flood maps and salt air. Each town has a page of its own with the rules we design to.')}
{d}
</main>
'''
    desc = "Building a custom home on the Charleston coast: flood elevation, hurricane wind, salt air, grand trees and design review, handled in the drawings by RAM Construction Charleston before the price is set. Mount Pleasant, Isle of Palms, Sullivan's Island and Daniel Island."
    ld = jsonld({"@context": "https://schema.org", "@type": "WebPage", "name": 'Building in the Lowcountry', "description": desc, "url": url('lowcountry.html')})
    og = f'img/w/coast-storm-shutters-squall-{W["coast-storm-shutters-squall"][-1]}.webp'
    return head(f'Building on the Charleston Coast | {BRAND}', desc, f'{SITE}/lowcountry.html', og, f'<link rel="preload" as="image" href="{og}">\n') + chrome('lowcountry.html') + body + tail('lowcountry.html', ld)

# ── the process ──────────────────────────────────────────────────────────────
def process_page():
    hero = pic('great-room-marsh-view-golden-hour', 'A great room with tall windows open to a golden marsh at sunset', ratio='3/3.6', eager=True)
    d = door('IV', qs=[Q['price'], Q['budget'], Q['3d']])
    body = f'''{phero('How we build', 'From the lot <em>to the keys.</em>',
                 'Four steps, one project manager, a site meeting every week and a written recap after each one. Here is what happens, in the order it happens.',
                 hero, meta=['Design', 'Fixed bid', '3D walk-through', 'Build'])}

<!-- ═════ the four steps ═════ -->
<section class="process on-dark" id="steps">
  <div class="wrap">
{sec_head('I', 'The four steps', 'What happens, <em>in order.</em>', 'Each step ends with something you can hold: a drawing, a number, a model you have walked through, a set of keys.')}
    <div class="steps">
      <div class="stepc rv"><span class="num">i</span><h3>Design</h3><p>We walk the lot and read what it allows. Then our design team and local Lowcountry architects draw the plans, elevations and materials with you over the table, and the budget takes shape beside the drawing so you decide what to keep with the number in front of you.</p><figure>{pic('ram-3d-rendering-modern', 'RAM 3D design rendering of a modern home', ratio='4/3', cls='stepfig')}<figcaption>The drawing · 3D rendering</figcaption></figure></div>
      <div class="stepc rv d1"><span class="num">ii</span><h3>Fixed bid</h3><p>The team that will build it prices the drawing. Every allowance is listed line by line and the bid is fixed before you sign, so change orders are the exception rather than the business model.</p><figure>{pic('ram-kitchen-island-lanterns', 'RAM kitchen with a marble island and iron lanterns', ratio='4/3', cls='stepfig')}<figcaption>The allowances · partner home, Charlotte</figcaption></figure></div>
      <div class="stepc rv d2"><span class="num">iii</span><h3>Walk-through</h3><p>Our lead designer builds an immersive 3D model alongside the preliminary plans, approved by a structural engineer. You tour every room, fixture and finish and change what you want to change on the model, not on site.</p><figure>{pic('ram-coffered-living-room', 'Finished RAM living room with a coffered ceiling and fireplace', ratio='4/3', cls='stepfig')}<figcaption>A finished room · partner home, Charlotte</figcaption></figure></div>
      <div class="stepc rv d3"><span class="num">iv</span><h3>Build</h3><p>A dedicated RAM Charleston team builds the home you approved. One project manager from first sketch to final walk-through, a site meeting every week, a written recap after each one, and a schedule you can see.</p><figure>{pic('ram-stone-fireplace-pavilion', 'Stone fireplace in a RAM outdoor pavilion with a wood ceiling', ratio='4/3', cls='stepfig')}<figcaption>Delivered · partner home, Charlotte</figcaption></figure></div>
    </div>
  </div>
</section>

<!-- ═════ the window · a walk-through in four beats ═════ -->
<section class="window on-dark" id="walk">
  <div class="wrap window-grid">
    <div class="rv">
      <h2 class="hx"><span class="eyebrow"><i aria-hidden="true">II</i> 3D home walk-through</span><span class="sr-only">. </span><span class="h2">Stand in the room <em>before it exists.</em></span></h2>
      <p class="lede">RAM's immersive 3D plans let you walk every room of the proposed design before it exists: the view from the kitchen, the evening sun on the porch floor, every fixture and finish. You review the home before we build it, and change what you want to change on the model, not on site.</p>
      <ol class="beats" aria-hidden="true"><li>The marsh</li><li>The house</li><li>The door</li><li>The room</li></ol>
    </div>
    <figure class="pane rv d1">
      <div class="pane-arch" role="img" aria-label="A walk-through drawn in four beats: the marsh, the house across the creek, its front door, and a sitting room open to the porch and the same marsh">
        <div class="beat b-marsh"><img src="img/w/tidal-creek-marsh-aerial-dusk-2400.webp" width="2400" height="1340" loading="lazy" alt=""></div>
        <div class="beat b-house"><img src="img/w/hero-lowcountry-custom-home-marsh-golden-hour-2400.webp" width="2400" height="1340" loading="lazy" alt=""></div>
        <div class="beat b-room"><img src="img/w/great-room-marsh-view-golden-hour-2400.webp" width="2400" height="1340" loading="lazy" alt=""></div>
        <div class="doors" aria-hidden="true"><span class="dl"></span><span class="dr"></span></div>
        <div class="dip" aria-hidden="true"></div>
        <!-- when the rendered walk-through clip exists, set data-src and it replaces the drawn sequence -->
        <video class="pane-video" muted loop playsinline preload="none" poster="img/w/great-room-marsh-view-golden-hour-1200.webp"></video>
      </div>
    </figure>
  </div>
</section>

{ledger([('i', 'The budget comes early', 'Set before the plans are final, with the cost of every feature explained, so you decide what to keep with the number in front of you.'),
         ('ii', 'One project manager', 'From first sketch to the keys, with a site meeting every week and a written recap after each one.'),
         ('iii', 'The drawings we build', 'The drawings that go to the county are the drawings that get built. Nothing is lost between the plan and the site.')])}
{d}
</main>
'''
    desc = 'How RAM Construction Charleston builds a custom home: design with local architects and a budget set early, one fixed bid with allowances listed, a 3D walk-through approved by a structural engineer, then the build with one project manager and a site meeting every week.'
    ld = jsonld({"@context": "https://schema.org", "@type": "WebPage", "name": f'Our Process | {BRAND}', "description": desc, "url": url('process.html')})
    og = 'img/w/great-room-marsh-view-golden-hour-2400.webp'
    return head(f'How We Build: Our Process | {BRAND}', desc, f'{SITE}/process.html', og, f'<link rel="preload" as="image" href="{og}">\n') + chrome('process.html') + body + tail('process.html', ld)

# ── about ────────────────────────────────────────────────────────────────────
TEAM_H2 = "The people <em>you'll build with.</em>"
TEAM_LEDE = 'A home is the largest thing most people will ever build, and you should know who is building it.'

def about_page():
    TEAM = team_block('I', TEAM_H2, TEAM_LEDE, long=True)
    hero = pic('porch-portrait-woman-golden-hour', 'A woman on a Lowcountry piazza at golden hour, looking out over the marsh', ratio='3/3.6', eager=True)
    d = door('V', qs=[Q['partner'], Q['who'], Q['warranty']])
    body = f'''{phero('About RAM Charleston', 'Designed in the Lowcountry. <em>Built on the coast.</em>',
                 'RAM Construction Charleston is a South Carolina-licensed custom home builder. Our design team draws with local Lowcountry architects, every home is priced as one fixed bid and toured in 3D before it is built, and the experience of our partner, RAM Construction of Charlotte, stands behind every project.',
                 hero, meta=['In-house design, local architects', 'SC-licensed residential builder', 'In partnership with RAM Charlotte'])}
{TEAM}

<!-- ═════ the RAM way ═════ -->
<section class="story on-dark story-dk">
  <div class="wrap story-grid">
    <div class="story-art rv">
      {pic('ram-two-storey-porches', 'A home by RAM Construction of Charlotte with two storeys of deep porches', ratio='3/3.4')}
      <p class="cap">Partner home · RAM Construction, Charlotte</p>
    </div>
    <div class="story-copy">
      <span class="eyebrow rv"><i>II</i> How we work</span>
      <h2 class="h2 rv d1">We build your home <em>with you.</em></h2>
      <p class="rv d1">Most builders hand the drawing to someone else to price, and hand the price to someone else to build. We keep design in the house. Our design team listens to what matters to you and walks the lot to learn its layout and restrictions, local Lowcountry architects draw the plan with us, and the team that will build it prices it, so nothing is lost between the sketch and the site.</p>
      <p class="rv d2">The budget is established early, before the plans are finalised, with an up-front account of what each feature adds, so change orders are the exception rather than the business model. Because a house is hard to see on paper, the lead designer builds an immersive 3D model at the same time as the preliminary plans, approved by a structural engineer, and you tour every room, fixture and finish before construction begins.</p>
      <a class="more rv d2" href="process.html">Our process, step by step <span>&rarr;</span></a>
    </div>
  </div>
</section>

<!-- ═════ the partner in Charlotte ═════ -->
<section class="division">
  <div class="wrap division-grid">
    <div class="division-copy">
      <span class="eyebrow rv"><i>III</i> Our partner in Charlotte</span>
      <h2 class="h2 rv d1">What the partnership <em>brings to Charleston.</em></h2>
      <p class="rv d1">We work in partnership with <a href="https://www.ramconstructioninc.com">RAM Construction</a> of Charlotte, which has built custom homes there since 2004: 6,000-square-foot modern homes in SouthPark, early-century Craftsman bungalows in Dilworth, and the renovations that keep an old street whole. It is a regular on the Dilworth Home Tour.</p>
      <p class="rv d2">Charleston draws on that experience directly: the design and 3D modelling tools, the fixed-bid process with every allowance listed, the weekly site meeting and written recap, and the standard of finish in the photographs across this site. RAM Construction Charleston holds its own South Carolina license and builds with its own Lowcountry team.</p>
      <ul class="division-towns rv d2">
        <li><a href="mount-pleasant.html">Mount Pleasant <span>&rarr;</span></a></li>
        <li><a href="isle-of-palms.html">Isle of Palms <span>&rarr;</span></a></li>
        <li><a href="sullivans-island.html">Sullivan's Island <span>&rarr;</span></a></li>
        <li><a href="daniel-island.html">Daniel Island <span>&rarr;</span></a></li>
      </ul>
    </div>
    <div class="division-facts rv d1">
      <dl>
        <div><dt>Practice</dt><dd>Custom homes, renovations and additions, design and preconstruction, with in-house design through local Lowcountry architects</dd></div>
        <div><dt>Warranty</dt><dd>Terms written into your contract and confirmed before you sign</dd></div>
        <div><dt>South Carolina</dt><dd>Residential builder license · number listed at launch</dd></div>
        <div><dt>Charleston line</dt><dd><a href="tel:+18430000000">(843) 000-0000</a> · issued at launch</dd></div>
        <div><dt>Partner</dt><dd>RAM Construction, Charlotte, North Carolina, building custom homes since 2004</dd></div>
      </dl>
    </div>
  </div>
  <div class="wrap creds-row rv" aria-label="Credentials">
    <p>The marks our partner, <em>RAM Construction of Charlotte,</em> builds under.</p>
    <ul class="plates">
      <li><img src="img/cred/bbb.png" alt="BBB Accredited Business" loading="lazy" width="120" height="120"></li>
      <li><img src="img/cred/nahb.png" alt="Member, National Association of Home Builders" loading="lazy" width="120" height="120"></li>
      <li><img src="img/cred/qbw.png" alt="Quality Builders Warranty" loading="lazy" width="200" height="60"></li>
      <li><img src="img/cred/ica-x12.png" alt="ICA X12" loading="lazy" width="120" height="120"></li>
      <li><img src="img/cred/lumion.png" alt="Lumion 3D rendering" loading="lazy" width="120" height="120"></li>
    </ul>
  </div>
</section>
{range_grid('IV', 'Finished homes', 'The standard <em>we build to.</em>', PARTNER_LEDE, PARTNER_FIGS, foot='More finished homes are in the <a href="index.html#projects">featured projects</a> on the homepage.')}
{d}
</main>
'''
    desc = 'About RAM Construction Charleston: a South Carolina-licensed custom home builder with in-house design through local Lowcountry architects, a fixed bid and a 3D walk-through before construction, in partnership with RAM Construction of Charlotte. Meet Greg and the Charleston team.'
    ld = jsonld({"@context": "https://schema.org", "@type": "AboutPage", "name": f'About {BRAND}', "description": desc, "url": url("about.html"),
                 "mainEntity": {"@type": "GeneralContractor", "name": BRAND}})
    og = f'img/w/porch-portrait-woman-golden-hour-{W["porch-portrait-woman-golden-hour"][-1]}.webp'
    return head('About RAM Construction Charleston | Meet the Team', desc, f'{SITE}/about.html', og, f'<link rel="preload" as="image" href="{og}">\n') + chrome('about.html') + body + tail('about.html', ld)

# ── FAQ ──────────────────────────────────────────────────────────────────────
GROUPS = [
 ('lots', 'i', 'Lots and land', [Q['lot'],
   ('Can you tell me what a lot allows before I buy it?', 'Yes. Lot evaluation is the first step of every RAM home: zoning and setbacks, the flood zone, the trees that are protected and which board, if any, reviews the design. You get it in writing, before you commit.'),
   Q['flood'], Q['trees']]),
 ('price', 'ii', 'Design and price', [Q['price'], Q['inhouse'], Q['budget'], Q['3d'], Q['plans']]),
 ('coast', 'iii', 'Building on the coast', [Q['elevated'], Q['boards'], Q['wind'], Q['salt'], Q['lines']]),
 ('ram', 'iv', 'Working with RAM', [Q['who'], Q['partner'], Q['renos'], Q['warranty'], Q['reno'], Q['work']]),
]

def faq_page():
    hero = pic('open-living-room-stair-marsh-light', 'A double-height open living room with tall windows to a screened porch, a white staircase and heart-pine floors', ratio='3/3.6', eager=True)
    index = ''.join(f'<li><a href="#{k}"><i>{n}</i> {t}</a></li>' for k, n, t, _ in GROUPS)
    d = door('V', 'Schedule a consultation', 'Still a question? <em>Ask it here.</em>', "Tell us about the project, or just what you are weighing up. We'll come back to you.")
    groups = ''
    for k, n, t, qs in GROUPS:
        groups += f'''
    <section class="qa faq" id="{k}">
      <h2 class="qa-h rv"><i>{n}</i> {t}</h2>
      <div class="rv d1">
{faq_items(qs, first_open=(k == 'lots'))}
      </div>
    </section>'''
    body = f'''{phero('Questions', 'Before you <em>call us.</em>',
                 'What people ask before their first meeting, answered the way we would answer them at the table. If yours is not here, the Charleston line is at the foot of the page.',
                 hero, meta=['Lots and land', 'Design and price', 'Building on the coast', 'Working with RAM'])}

<!-- ═════ the questions ═════ -->
<section class="qwrap">
  <div class="wrap qgrid">
    <aside class="qindex rv">
      <p class="datum-lab">On this page</p>
      <ul>{index}</ul>
    </aside>
    <div class="qgroups">{groups}
    </div>
  </div>
</section>
{d}
</main>
'''
    desc = 'Questions people ask before building or renovating a home in Charleston: lots and flood zones, how the fixed bid is set, the 3D walk-through, coastal design review, hurricanes and salt air, and how RAM Charleston works with its partner in Charlotte.'
    ld = jsonld({"@context": "https://schema.org", "@type": "WebPage", "name": f'Questions | {BRAND}', "description": desc, "url": url("faq.html")})
    og = f'img/w/open-living-room-stair-marsh-light-{W["open-living-room-stair-marsh-light"][-1]}.webp'
    return head('Questions Before You Build | RAM Construction Charleston', desc, f'{SITE}/faq.html', og, f'<link rel="preload" as="image" href="{og}">\n') + chrome('faq.html') + body + tail('faq.html', ld)

# ── contact ──────────────────────────────────────────────────────────────────
def contact_page():
    extra = '''
      <dl class="cways">
        <div><dt>Write</dt><dd><a href="mailto:hello@ramconstructionsc.com">hello@ramconstructionsc.com</a></dd></div>
        <div><dt>Meet</dt><dd>On your lot, at the house you want to change, or at a lot you are considering. We come to you across Mount Pleasant, the islands and Daniel Island.</dd></div>
        <div><dt>Then</dt><dd>A written note of what the lot or the house allows, and a design meeting when you are ready.</dd></div>
      </dl>'''
    towns = ''.join(f'''      <a class="ctown rv{" d"+str(i) if i else ""}" href="{TOWNS[s]["file"]}">{pic(TOWNS[s]["hero"][0], TOWNS[s]["hero"][1], ratio='3/3.4', sizes='(max-width:860px) 46vw, 22vw')}<span><small>{TOWNS[s]["county"].split(' ·')[0]}</small><b>{TOWNS[s]["name"]}</b></span></a>\n''' for i, s in enumerate(TOWN_ORDER))
    d = door('', 'Contact', "Let's talk about <em>your project.</em>", LEDE_DOOR, page_id='contact', h_tag='h1', extra_left=extra).replace('<section class="door on-dark" id="contact">', '<section class="door door-page on-dark" id="contact">')
    body = f'''{d}

<!-- ═════ the towns ═════ -->
<section class="ctowns">
  <div class="wrap">
{sec_head('I', 'Where we build', 'Four towns, <em>one line to call.</em>', 'Each town has a page of its own with the rules we design to. Tell us which one and we will bring the right set of drawings to the first meeting.')}
    <div class="ctown-grid">
{towns}    </div>
  </div>
</section>
</main>
'''
    desc = "Schedule a consultation with RAM Construction Charleston about a custom home, renovation or addition in Mount Pleasant, Isle of Palms, Sullivan's Island or Daniel Island. We meet you on the lot."
    ld = jsonld({"@context": "https://schema.org", "@type": "ContactPage", "name": f'Contact {BRAND}', "description": desc, "url": url("contact.html"),
                 "mainEntity": {"@type": "GeneralContractor", "name": BRAND, "email": "hello@ramconstructionsc.com", "areaServed": ["Mount Pleasant, SC", "Isle of Palms, SC", "Sullivan's Island, SC", "Daniel Island, SC"]}})
    out = head('Contact RAM Construction Charleston | Schedule a Consultation', desc, f'{SITE}/contact.html', 'img/w/daniel-island-waterfront-home-1200.webp') + chrome('contact.html') + body + tail('contact.html', ld)
    # the contact page's form is the page, not a reveal that waits
    return out.replace('<form class="form rv d2"', '<form class="form"', 1)

# ── write ────────────────────────────────────────────────────────────────────
pages = {'about.html': about_page(), 'faq.html': faq_page(), 'contact.html': contact_page(),
         'lowcountry.html': lowcountry_page(), 'process.html': process_page()}
for s in SERVICE_ORDER:
    pages[SERVICES[s]['file']] = service_page(s)
for s in TOWN_ORDER:
    pages[TOWNS[s]['file']] = town_page(s)
for f, s in pages.items():
    (ROOT / f).write_text(s)
    print(f, len(s))
