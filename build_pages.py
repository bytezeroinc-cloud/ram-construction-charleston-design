#!/usr/bin/env python3
"""Assemble the RAM Charleston inner pages from the homepage's own parts.

Reads index.html for the SVG sprite, masthead, mobile menu, contact form and footer,
so the chrome stays one source, and writes about.html, faq.html, contact.html and the
four town pages. Run from the charleston folder:  python3 build_pages.py
"""
import re, html, pathlib

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

def relink(s):
    """Inner pages: homepage section anchors become index.html#…; the rest already point at pages."""
    s = s.replace('href="#top"', 'href="index.html"')
    for a in ('services', 'areas', 'work', 'process', 'coast', 'walk'):
        s = s.replace(f'href="#{a}"', f'href="index.html#{a}"')
    s = s.replace('href="#door"', 'href="contact.html"').replace('href="#faq"', 'href="faq.html"')
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

def breadcrumbs(items):
    """items: [(name, url), …]; the last is the page itself."""
    el = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]
    return '<script type="application/ld+json">' + html.escape(str(el).replace("'", '"'), quote=False).replace('&quot;', '"') + '</script>'

def jsonld(obj):
    import json
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
def arch_img(name, w1, w2, alt, ratio='3/3.6', sizes='(max-width:860px) 100vw, 44vw', pos=None, eager=False):
    st = f' style="object-position:{pos}"' if pos else ''
    ld = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<div class="arch" style="aspect-ratio:{ratio}"><img src="img/w/{name}-{w1}.webp" '
            f'srcset="img/w/{name}-{w2}.webp {w2}w, img/w/{name}-{w1}.webp {w1}w" sizes="{sizes}" '
            f'width="{w1}" {ld} alt="{alt}"{st}></div>')

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

def door(folio, eyebrow, h2, lede, qs=None, page_id='door', h_tag='h2', extra_left=''):
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
    rows = ''.join(f'<div class="ledger-item rv{" d"+str(i) if i else ""}"><span class="mk">{n}</span><h3>{t}</h3><p>{x}</p></div>' for i, (n, t, x) in enumerate(items))
    return f'<div class="ledger"><div class="wrap ledger-row">{rows}</div></div>'

def rail_lt(rows):
    """The survey rail on a light ground, every row open (town pages)."""
    out = []
    for i, (n, t, x, src) in enumerate(rows):
        out.append(f'''      <div class="rrow rv{" d"+str(min(i,3)) if i else ""}">
        <span class="rnum">{n}</span>
        <div class="rbody"><h3>{t}</h3><p>{x}</p><small>{src}</small></div>
      </div>''')
    return '<div class="rail-lt">\n' + '\n'.join(out) + '\n    </div>'

# ── content ──────────────────────────────────────────────────────────────────
SITE = 'https://ramconstructionsc.com'   # placeholder domain, swapped at launch
LEDE_DOOR = "Where it is, what you want it to become, and when. We'll come back to set a time to walk it with you."
BRAND = 'RAM Construction Charleston'
def url(f):
    """Route-style URL for schema: about.html -> /about (the app serves extensionless routes)."""
    return SITE + ('/' if f == 'index.html' else '/' + f[:-5])

TOWNS = {
 'mount-pleasant': dict(
   name='Mount Pleasant', county='Charleston County', file='mount-pleasant.html',
   hero=('mount-pleasant-live-oak-drive', 1600, 900, 'A shell drive under live oaks draped in Spanish moss, leading to a white custom home with a deep porch in Mount Pleasant'),
   second=('mount-pleasant-old-village-street', 1600, 800, 'A white two-storey home with stacked piazzas behind a brick wall on a live-oak street in the Old Village of Mount Pleasant'),
   third=('coast-house-between-live-oaks', 1600, 800, 'A white custom home sited between two grand live oaks, their limbs reaching over the roof'),
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
   hero=('isle-of-palms-elevated-beach-house', 1600, 900, 'An elevated beach house on white pilings behind grassy dunes on Isle of Palms'),
   second=('isle-of-palms-dune-boardwalk', 1600, 800, 'A wooden boardwalk over high dunes toward the Atlantic on Isle of Palms, a raised beach house at its edge'),
   third=('coast-salt-air-piazza-rail', 1600, 800, 'The corner of a white piazza rail with stainless fittings and a copper lantern, dunes and ocean haze beyond'),
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
   hero=('sullivans-island-island-cottage', 1600, 900, "A raised island cottage with a screened porch behind a picket fence on Sullivan's Island"),
   second=('sullivans-island-station-cottage', 1600, 800, "A white board-and-batten island cottage with a deep screened porch on a sandy lane on Sullivan's Island"),
   third=('coast-storm-shutters-squall', 1600, 800, 'An elevated white Lowcountry home with green Bahama shutters as a squall line crosses the marsh sky'),
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
   hero=('daniel-island-waterfront-home', 1600, 900, 'A new Lowcountry home with double porches on the marsh at sunset on Daniel Island'),
   second=('daniel-island-wando-waterfront', 1600, 800, 'A white Lowcountry home on a marsh-front lot on Daniel Island with a long private dock reaching the Wando River'),
   third=('tidal-creek-marsh-aerial-dusk', 2400, 1200, 'Aerial view of a tidal creek winding through spartina marsh with a private dock at dusk'),
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

def town_page(slug):
    t = TOWNS[slug]
    hero = arch_img(*t['hero'], ratio='3/3.6', eager=True)
    second = arch_img(*t['second'], ratio='4/5', pos=None)
    third = arch_img(*t['third'], ratio='4/3' if slug == 'daniel-island' else '4/5')
    others = [s for s in TOWN_ORDER if s != slug]
    other_links = ''.join(f'<li><a href="{TOWNS[o]["file"]}">{TOWNS[o]["name"]} <span>&rarr;</span></a></li>' for o in others)
    places = ''.join(f'<li class="rv{" d"+str(i%4) if i%4 else ""}"><span>{p}</span></li>' for i, p in enumerate(t['places']))
    intro_eb, intro_h2, intro_lede = t['intro']
    d = door('III', f'Begin a home in {t["name"]}', 'Tell us about <em>the lot.</em>', LEDE_DOOR, qs=t['qs'])
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
      <ul>{other_links}</ul>
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
                     {"@type": "ListItem", "position": 2, "name": "Where we build", "item": f'{SITE}/#areas'},
                     {"@type": "ListItem", "position": 3, "name": t['name'], "item": url(t["file"])}]}})
    title = f'Custom Home Builder in {t["name"]}, SC | {BRAND}'
    pre = f'<link rel="preload" as="image" href="img/w/{t["hero"][0]}-1600.webp">\n'
    return head(title, t['desc'], f'{SITE}/{t["file"]}', f'img/w/{t["hero"][0]}-1600.webp', pre) + chrome(t['file']) + body + tail(t['file'], ld)

# ── about ────────────────────────────────────────────────────────────────────
def about_page():
    hero = arch_img('porch-portrait-woman-golden-hour', 1600, 900, 'A woman on a Lowcountry piazza at golden hour, looking out over the marsh', ratio='3/3.6', eager=True)
    d = door('IV', 'Begin a home', 'Tell us about <em>the lot.</em>', LEDE_DOOR,
      qs=[('How is RAM Charleston related to RAM in Charlotte?', 'We are partners, not one company. RAM Construction Charleston holds its own South Carolina license and builds with its own Lowcountry team. RAM Construction in Charlotte, building there since 2004, shares the approach: a fixed bid and a 3D walk-through before construction.'),
          ('Who will I deal with?', 'One project manager from first sketch to final walk-through, with a site meeting every week and a written recap after each one.'),
          ('Is there a warranty?', 'Warranty terms are written into your RAM Construction Charleston contract and confirmed before you sign.')])
    body = f'''{phero('About RAM Charleston', 'Designed in the Lowcountry. <em>Built on the coast.</em>',
                 'RAM Construction Charleston is a South Carolina-licensed custom home builder. Design is in-house: our team draws with local Lowcountry architects who know each town’s boards, and every home is priced as a fixed bid and toured in 3D before it is built. We work in partnership with RAM Construction of Charlotte.',
                 hero, meta=['In-house design, local architects', 'SC-licensed residential builder', 'In partnership with RAM Charlotte'])}

{ledger([('i', 'Designed in-house', 'Our design team and local architects draw the plan; the price comes from the same table.'),
         ('ii', 'The budget comes early', 'Set before the plans are final, with the cost of every feature explained, so you decide what to keep with the number in front of you.'),
         ('iii', 'Walk it before we build', 'The lead designer builds the 3D model alongside the preliminary plans, checked by a structural engineer, so you tour the house months before construction.')])}

<!-- ═════ the RAM way ═════ -->
<section class="story">
  <div class="wrap story-grid">
    <div class="story-art rv">
      {arch_img('ram-two-storey-porches', 1600, 800, 'A home by RAM Construction of Charlotte with two storeys of deep porches', ratio='3/3.4')}
      <p class="cap">Partner home · RAM Construction, Charlotte</p>
    </div>
    <div class="story-copy">
      <span class="eyebrow rv"><i>I</i> The RAM way</span>
      <h2 class="h2 rv d1">We build your home <em>with you.</em></h2>
      <p class="rv d1">Most builders hand the drawing to someone else to price, and hand the price to someone else to build. We keep design in the house. Our design team listens to what matters to you and walks the lot to learn its layout and restrictions, local Lowcountry architects draw the plan with us, and the team that will build it prices it, so nothing is lost between the sketch and the site.</p>
      <p class="rv d2">Every plan is original, drawn for your lot by architects who work on this coast. The budget is established early, before the plans are finalised, with an up-front account of what each feature adds, so change orders are the exception rather than the business model. The drawings that go to the county are the drawings that get built.</p>
      <p class="rv d2">Because a house is hard to see on paper, the lead designer builds an immersive 3D model at the same time as the preliminary plans. You tour every room, fixture and finish before construction begins, and the model is approved by a structural engineer so the changes you make in it can be trusted.</p>
      <ul class="chips rv d3">
        <li>One project manager, first sketch to keys</li>
        <li>A site meeting every week, with a written recap</li>
        <li>Project scheduling you can see</li>
      </ul>
    </div>
  </div>
</section>

<!-- ═════ the partner in Charlotte ═════ -->
<section class="range on-dark">
  <div class="wrap">
{sec_head('II', 'Our partner in Charlotte', 'From SouthPark <em>to Dilworth.</em>', 'We work in partnership with <a href="https://www.ramconstructioninc.com">RAM Construction</a>, which has built custom homes in Charlotte since 2004: 6,000-square-foot modern homes in SouthPark, early-century Craftsman bungalows in Dilworth, and the renovations that keep an old street whole. Every photograph here is one of their finished homes.')}
    <div class="range-grid">
      <figure class="rv">{arch_img('ram-modern-home-balconies', 1600, 800, 'A modern RAM home with stacked balconies and a landscaped front', ratio='4/5')}<figcaption>Modern home · RAM Charlotte</figcaption></figure>
      <figure class="rv d1">{arch_img('ram-range-brass-kitchen', 1600, 800, 'Black and brass range beneath a white tile wall in a RAM kitchen', ratio='4/5')}<figcaption>Kitchen · RAM Charlotte</figcaption></figure>
      <figure class="rv d2">{arch_img('ram-screened-porch-wood-ceiling', 1600, 800, 'Screened porch with a vaulted wood ceiling and seating', ratio='4/5')}<figcaption>Screened porch · RAM Charlotte</figcaption></figure>
    </div>
    <div class="range-foot rv">
      <p>More of their work is in the <a href="index.html#work">homepage gallery</a>. Charleston's own homes will join it as each one is completed.</p>
    </div>
  </div>
</section>

<!-- ═════ the Charleston company ═════ -->
<section class="division">
  <div class="wrap division-grid">
    <div class="division-copy">
      <span class="eyebrow rv"><i>III</i> RAM Construction Charleston</span>
      <h2 class="h2 rv d1">Our own license, <em>our own ground.</em></h2>
      <p class="rv d1">RAM Construction Charleston is licensed as a residential builder in South Carolina, with its own team in the Lowcountry. The Lowcountry asks different questions of a house than Charlotte does: flood elevations, the state's beachfront lines, salt air, hurricane wind, and a review board in most towns. We answer them in the drawings, before the price is set.</p>
      <p class="rv d2">We build in four towns to begin with: Mount Pleasant, Isle of Palms, Sullivan's Island and Daniel Island. Each has a page of its own with the rules we design to.</p>
      <ul class="division-towns rv d2">
        <li><a href="mount-pleasant.html">Mount Pleasant <span>&rarr;</span></a></li>
        <li><a href="isle-of-palms.html">Isle of Palms <span>&rarr;</span></a></li>
        <li><a href="sullivans-island.html">Sullivan's Island <span>&rarr;</span></a></li>
        <li><a href="daniel-island.html">Daniel Island <span>&rarr;</span></a></li>
      </ul>
    </div>
    <div class="division-facts rv d1">
      <dl>
                <div><dt>Practice</dt><dd>Custom home builder, with in-house design through local Lowcountry architects</dd></div>
        <div><dt>Warranty</dt><dd>Terms written into your contract and confirmed before you sign</dd></div>
        <div><dt>South Carolina</dt><dd>Residential builder license · number listed at launch</dd></div>
        <div><dt>Charleston line</dt><dd><a href="tel:+18430000000">(843) 000-0000</a> · issued at launch</dd></div>
        <div><dt>Partner</dt><dd>RAM Construction, Charlotte, North Carolina</dd></div>
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
{d}
</main>
'''
    desc = 'RAM Construction Charleston is a South Carolina-licensed custom home builder with in-house design through local Lowcountry architects, a fixed bid and a 3D walk-through before construction, in partnership with RAM Construction of Charlotte.'
    ld = jsonld({"@context": "https://schema.org", "@type": "AboutPage", "name": f'About {BRAND}', "description": desc, "url": url("about.html"),
                 "mainEntity": {"@type": "GeneralContractor", "name": BRAND}})
    pre = '<link rel="preload" as="image" href="img/w/porch-portrait-woman-golden-hour-1600.webp">\n'
    return head('About RAM Construction Charleston | Custom Home Builder, SC', desc, f'{SITE}/about.html', 'img/w/porch-portrait-woman-golden-hour-1600.webp', pre) + chrome('about.html') + body + tail('about.html', ld)

# ── FAQ ──────────────────────────────────────────────────────────────────────
GROUPS = [
 ('lots', 'i', 'Lots and land', [
   ('Do I need to own a lot first?', 'No. We can evaluate lots you\'re considering and tell you what each one allows, including its flood zone and review rules, before you buy.'),
   ('Can you tell me what a lot allows before I buy it?', 'Yes. Lot evaluation is the first step of every RAM home: zoning and setbacks, the flood zone, the trees that are protected and which board, if any, reviews the design. You get it in writing, before you commit.'),
   ('How do I know which flood zone my lot is in?', 'We check your lot against the current flood maps during lot evaluation and explain what that zone means for the foundation and design.'),
   ('What about the trees on the lot?', 'In Mount Pleasant any tree of 16 inches and over on a residential lot is protected, and live oaks of 24 inches and over are historic trees. The other towns and review boards have rules of their own. We survey the canopy before we draw and site the house around the trees worth keeping.'),
 ]),
 ('price', 'ii', 'Design and price', [
   ('How is the price set?', 'After design, we issue a fixed bid with allowances listed line by line, so you know the number before you sign.'),
   ('Do you design in-house?', 'Yes. Design is in-house: our team draws with local Lowcountry architects who know each town\'s review boards, and the drawing is priced by the team that will build it. The drawings that go to the county are the drawings we build.'),
   ('When do we talk about budget?', 'Early, before the plans are final. We explain what each feature adds to the total as we design, so you decide what to keep with the number in front of you rather than after a bid comes back.'),
   ('What is the 3D walk-through?', 'Our lead designer builds an immersive 3D model alongside the preliminary plans, so you tour every room, fixture and finish before construction. The model is approved by a structural engineer, so the changes you make in it can be trusted.'),
   ('Can you build from my architect\'s plans?', 'Yes. We review third-party plans for constructability and coastal requirements before we bid. Most clients use our in-house design team and its local architects, because design and pricing stay together.'),
 ]),
 ('coast', 'iii', 'Building on the coast', [
   ('What does an elevated home involve?', 'The finished floor is set above the flood elevation from the maps and the town\'s rule; the foundation, venting or pilings are drawn for it; the ground level becomes parking and storage; and the porch goes where the breeze is. All of it is in the first sketch, not added at the end.'),
   ('Which towns have design review?', 'The Old Village of Mount Pleasant (Historic District Preservation Commission), Sullivan\'s Island (Design Review Board) and Daniel Island (Architectural Review Board) review new homes, and inside Wild Dunes on Isle of Palms the community\'s own board issues a permit. We prepare the drawings, elevations and 3D views each board asks to see, and present them.'),
   ('How do you build for hurricanes?', 'Impact-rated openings, a continuous load path and roof tie-downs are specified in the drawings for every coastal home, not added when the permit comes back.'),
   ('What about salt air?', 'Stainless fasteners, marine-grade finishes and siding chosen to last on the coast, specified by the team that builds the home.'),
   ('What are the beachfront lines on the islands?', 'The state\'s Bureau of Coastal Management sets a baseline along the primary dune and a setback line behind it. What may be built seaward of those lines is limited and permitted by the state. We locate both on the survey before we draw.'),
 ]),
 ('ram', 'iv', 'Working with RAM', [
   ('How is RAM Charleston related to RAM in Charlotte?', 'We are partners, not one company. RAM Construction Charleston holds its own South Carolina license and builds with its own Lowcountry team. RAM Construction in Charlotte, building there since 2004, shares the approach: a fixed bid and a 3D walk-through before construction.'),
   ('Who will I deal with?', 'One project manager from first sketch to final walk-through, with a site meeting every week and a written recap after each one.'),
   ('Is there a warranty?', 'Warranty terms are written into your RAM Construction Charleston contract and confirmed before you sign.'),
   ('Renovate or rebuild?', 'It depends on the structure, the flood elevation and what you want the home to become. We assess the house and give you an honest answer on both paths.'),
   ('Where can I see your work?', 'The homepage gallery shows finished homes by our partner, RAM Construction of Charlotte, photographed as built. Charleston\'s own homes will join it as each one is completed; the Lowcountry scenes on this site are illustrative renderings and are marked as such.'),
 ]),
]

def faq_page():
    hero = arch_img('open-living-room-stair-marsh-light', 1600, 900, 'A double-height open living room with tall windows to a screened porch, a white staircase and heart-pine floors', ratio='3/3.6', eager=True)
    index = ''.join(f'<li><a href="#{k}"><i>{n}</i> {t}</a></li>' for k, n, t, _ in GROUPS)
    d = door('V', 'Begin a home', 'Still a question? <em>Ask it here.</em>', "Tell us about the lot, or just what you are weighing up. We'll come back to you.")
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
    desc = 'Questions people ask before building a custom home in Charleston: lots and flood zones, how the fixed bid is set, the 3D walk-through, coastal design review, hurricanes and salt air, and how RAM Charleston works with its partner in Charlotte.'
    ld = jsonld({"@context": "https://schema.org", "@type": "WebPage", "name": f'Questions | {BRAND}', "description": desc, "url": url("faq.html")})
    pre = '<link rel="preload" as="image" href="img/w/open-living-room-stair-marsh-light-1600.webp">\n'
    return head('Questions Before You Build | RAM Construction Charleston', desc, f'{SITE}/faq.html', 'img/w/open-living-room-stair-marsh-light-1600.webp', pre) + chrome('faq.html') + body + tail('faq.html', ld)

# ── contact ──────────────────────────────────────────────────────────────────
def contact_page():
    extra = '''
      <dl class="cways">
        <div><dt>Write</dt><dd><a href="mailto:hello@ramconstructionsc.com">hello@ramconstructionsc.com</a></dd></div>
        <div><dt>Meet</dt><dd>On your lot, or one you are considering. We come to you across Mount Pleasant, the islands and Daniel Island.</dd></div>
        <div><dt>Then</dt><dd>A written note of what the lot allows, and a design meeting when you are ready.</dd></div>
      </dl>'''
    towns = ''.join(f'''      <a class="ctown rv{" d"+str(i) if i else ""}" href="{TOWNS[s]["file"]}">{arch_img(TOWNS[s]["hero"][0], 1600, 900, TOWNS[s]["hero"][3], ratio='3/3.4', sizes='(max-width:860px) 46vw, 22vw')}<span><small>{TOWNS[s]["county"].split(' ·')[0]}</small><b>{TOWNS[s]["name"]}</b></span></a>\n''' for i, s in enumerate(TOWN_ORDER))
    d = door('', 'Contact', 'Tell us about <em>the lot.</em>', LEDE_DOOR, page_id='contact', h_tag='h1', extra_left=extra).replace('<section class="door on-dark" id="contact">', '<section class="door door-page on-dark" id="contact">')
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
    desc = 'Contact RAM Construction Charleston about a custom home, coastal home or renovation in Mount Pleasant, Isle of Palms, Sullivan\'s Island or Daniel Island. We come back within one business day and meet you on the lot.'
    ld = jsonld({"@context": "https://schema.org", "@type": "ContactPage", "name": f'Contact {BRAND}', "description": desc, "url": url("contact.html"),
                 "mainEntity": {"@type": "GeneralContractor", "name": BRAND, "email": "hello@ramconstructionsc.com", "areaServed": ["Mount Pleasant, SC", "Isle of Palms, SC", "Sullivan's Island, SC", "Daniel Island, SC"]}})
    out = head('Contact RAM Construction Charleston | Begin a Home', desc, f'{SITE}/contact.html', 'img/w/daniel-island-waterfront-home-1200.webp') + chrome('contact.html') + body + tail('contact.html', ld)
    # the contact page's form is the page, not a reveal that waits
    return out.replace('<form class="form rv d2"', '<form class="form"', 1)

# ── write ────────────────────────────────────────────────────────────────────
pages = {'about.html': about_page(), 'faq.html': faq_page(), 'contact.html': contact_page()}
for s in TOWN_ORDER:
    pages[TOWNS[s]['file']] = town_page(s)
for f, s in pages.items():
    (ROOT / f).write_text(s)
    print(f, len(s))
