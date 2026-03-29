#!/usr/bin/env python3
"""
OIO Racing - Social Posts Analyzer

Reads all social media posts from OIO Brain/data/social-posts/
and updates brain documents in-place:

  PER-CAR: injects a ## Social Post Arc block into each car's Overview.md
    OIO Brain/03 - Cars/Ian/1985 MR2/Overview.md           ← Goblin
    OIO Brain/03 - Cars/Ian/2009 Honda Fit/Overview.md     ← Fitty Cent
    OIO Brain/03 - Cars/Ian/1972 Celica/Overview.md        ← Dale
    OIO Brain/03 - Cars/Ryan/1973 MGB GT/Overview.md       ← MGBGT
    OIO Brain/03 - Cars/Richard/ST205/Overview.md          ← ST205
    OIO Brain/03 - Cars/Richard/1983 Starlet/Overview.md   ← Starlet

  PER-DRIVER: injects a ### Social Post Arc block into Team-Bios.md
    under each driver's section (Ian, Ryan, Richard, Hudson, Miles)

  CROSS-CUTTING: regenerates one aggregate doc for arcs that span
    multiple drivers/cars (e.g. the 2026 MR class season campaign)
    OIO Brain/02 - Content/Season-Story-Arcs.md

  BRAND: regenerates the social voice reference doc
    OIO Brain/01 - Brand/Social-Post-Voice.md

All injected blocks are wrapped in HTML comment markers:
  <!-- social-arc:start -->
  <!-- social-arc:end -->
so they can be safely replaced on every run without touching
the rest of the hand-maintained file content.

Usage:
  python scripts/analyze_social_posts.py

Called automatically by fetch-social-posts.yml after ingestion.
Safe to run at any time — always regenerates from the full corpus.
"""

import os
import re
from collections import defaultdict
from datetime import date

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOCIAL_DIR  = os.path.join(REPO_ROOT, "OIO Brain", "data", "social-posts")
BRAND_DIR   = os.path.join(REPO_ROOT, "OIO Brain", "01 - Brand")
CONTENT_DIR = os.path.join(REPO_ROOT, "OIO Brain", "02 - Content")
CARS_DIR    = os.path.join(REPO_ROOT, "OIO Brain", "03 - Cars")

VOICE_DOC   = os.path.join(BRAND_DIR, "Social-Post-Voice.md")
SEASON_DOC  = os.path.join(CONTENT_DIR, "Season-Story-Arcs.md")
TEAM_BIOS   = os.path.join(BRAND_DIR, "Team-Bios.md")

TODAY = date.today().isoformat()

ARC_START = "<!-- social-arc:{driver}:start -->"
ARC_END   = "<!-- social-arc:{driver}:end -->"

# ---------------------------------------------------------------------------
# Car / driver keyword maps
# ---------------------------------------------------------------------------
CAR_PATTERNS = {
    "Goblin (MR2)": [
        r"goblin", r"\baw11\b", r"\bmr2\b", r"rxaw11", r"rxmr2",
        r"goblinmr2", r"cylinder four", r"cyl.*4", r"bonesaw",
        r"mid.?rear powa",
    ],
    "MGB GT": [
        r"mgbgts", r"mgbgt", r"\bmgb\b", r"mgb gt", r"mgb-gt",
        r"mystery18rg", r"18rg",
    ],
    "Honda Fit / Fitty Cent": [
        r"fitty.?cent", r"fitgang", r"fit.?off", r"\bfit\b", r"\bge8\b",
        r"hondafit", r"honda fit", r"gd3",
    ],
    "Dale (Celica)": [
        r"\bdale\b", r"dalesdragon", r"dale.*celica", r"\bra21\b",
        r"1st generation celica", r"celica.*followed",
        r"gary rod.*chassis",
    ],
    "Richard's ST205": [
        r"\bst205\b", r"celicagtfour", r"3sgte", r"rally beast",
        r"living legend",
    ],
    "Starlet": [
        r"\bstarlet\b", r"4age.*starlet", r"starlet.*4age",
    ],
}

DRIVER_PATTERNS = {
    "Ian":     [r"\bIan\b", r"\bIan's\b", r"\bIan here\b"],
    "Ryan":    [r"\bRyan\b", r"\bRyan's\b"],
    "Richard": [r"\bRichard\b"],
    "Hudson":  [r"\bHudson\b"],
    "Miles":   [r"\bMiles\b"],
    "Keegan":  [r"\bKeegan\b"],
}

POST_TYPE_PATTERNS = {
    "video_tease": [
        r"link in the comments", r"new video", r"latest video",
        r"find the.*video", r"join us.*for", r"youtu\.be",
        r"subscribe.*stay tuned",
    ],
    "build_update": [
        r"getting ready", r"coming apart", r"stripping paint",
        r"body.*filler", r"bodywork", r"metal work", r"patch panel",
        r"sanding", r"steering rack", r"tire", r"loaded up",
        r"off to.*camp", r"fabrication", r"swap",
    ],
    "event_recap": [
        r"rallycross", r"scca", r"ran.*this weekend", r"racing action",
        r"fastest run", r"class win", r"heat.*2", r"corner captain",
        r"novice",
    ],
    "event_hype": [
        r"race day", r"ready.*race", r"is ready", r"tune in",
        r"stay tuned.*racing", r"incoming.*race", r"racing.*incoming",
        r"race.*season.*incoming", r"battle.*supremacy",
    ],
    "trash_talk": [
        r"trash talk", r"smack talk", r"taunting", r"handbag",
        r"world.*slowest", r"there ain.*a miata", r"best an.*mr2",
        r"got.*edge.*battle",
    ],
    "farewell_milestone": [
        r"farewell", r"r\.i\.p\.", r"served well", r"great strip",
        r"merry christmas", r"happy.*day", r"new meat day",
        r"celebrate", r"oldie.*goodie",
    ],
    "community_celebration": [
        r"damn good times", r"love what you do", r"real glad.*team",
        r"welcome back", r"tear.*eye", r"true love",
        r"congregation",
    ],
    "acquisition": [
        r"followed us home", r"mystery.*is coming apart",
        r"junkyard find", r"added to the display",
        r"off he goes.*great strip",
    ],
}

TONE_MARKERS = {
    "self_deprecating": [
        r"ian.*butt.*joke", r"ian.*wrong", r"ian.*wishes",
        r"ian.*handbag", r"ian.*bedazzled", r"ian.*last legs",
        r"if.*we can keep it powered",
    ],
    "absurdist_humor": [
        r"cones were harmed", r"accusations were made",
        r"witchcraft was suspected", r"riding a tiny lawnmower",
        r"smack talk continues", r"cowboy hudson",
        r"church of combustion", r"prophecy in steel",
        r"congregation",
    ],
    "storytelling": [
        r"this is only the beginning", r"born.*again",
        r"died.*reborn", r"living legend.*tested",
        r"a life well lived", r"served well",
        r"destined to slide",
    ],
    "community_voice": [
        r"real fast folks", r"our team", r"our hudson",
        r"the congregation", r"errbody",
        r"fitgang",
    ],
}

HASHTAG_RE = re.compile(r"#(\w+)")

# ---------------------------------------------------------------------------
# Car → Overview.md file paths
# ---------------------------------------------------------------------------
CAR_OVERVIEW_PATHS = {
    "Goblin (MR2)":           os.path.join(CARS_DIR, "Ian",     "1985 MR2",      "Overview.md"),
    "Honda Fit / Fitty Cent": os.path.join(CARS_DIR, "Ian",     "2009 Honda Fit","Overview.md"),
    "Dale (Celica)":          os.path.join(CARS_DIR, "Ian",     "1972 Celica",   "Overview.md"),
    "MGB GT":                 os.path.join(CARS_DIR, "Ryan",    "1973 MGB GT",   "Overview.md"),
    "Richard's ST205":        os.path.join(CARS_DIR, "Richard", "ST205",         "Overview.md"),
    "Starlet":                os.path.join(CARS_DIR, "Richard", "1983 Starlet",  "Overview.md"),
}

# Driver → anchor heading used in Team-Bios.md to locate their section
DRIVER_BIO_ANCHORS = {
    "Ian":     "## IAN JENNINGS",
    "Ryan":    "## RYAN REDENBAUGH",
    "Richard": "## RICHARD THOMPSON",
    "Hudson":  "## THE KIDS",
    "Miles":   "### MILES SMITH",
    "Keegan":  "## KEEGAN WILHELM",
}

# ---------------------------------------------------------------------------
# Post data model
# ---------------------------------------------------------------------------
class Post:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.platform = "facebook" if "facebook" in filepath else "instagram"
        self.text = ""
        self.date_str = ""
        self.date: date | None = None
        self.hashtags: list[str] = []
        self.car_mentions: list[str] = []
        self.driver_mentions: list[str] = []
        self.post_types: list[str] = []
        self.tone_tags: list[str] = []
        self._parse()

    def _parse(self):
        with open(self.filepath, encoding="utf-8") as f:
            raw = f.read()

        if raw.startswith("---"):
            end = raw.find("---", 3)
            fm = raw[3:end]
            body = raw[end + 3:].strip()
            m = re.search(r"^date:\s*(.+)$", fm, re.MULTILINE)
            if m:
                self.date_str = m.group(1).strip().split("T")[0]
                try:
                    self.date = date.fromisoformat(self.date_str)
                except ValueError:
                    pass
        else:
            body = raw.strip()

        self.text = body
        self.hashtags = [t.lower() for t in HASHTAG_RE.findall(body)]
        self._classify()

    def _classify(self):
        text_lower = self.text.lower()

        for car, patterns in CAR_PATTERNS.items():
            if any(re.search(p, text_lower) for p in patterns):
                self.car_mentions.append(car)

        for driver, patterns in DRIVER_PATTERNS.items():
            if any(re.search(p, self.text) for p in patterns):
                self.driver_mentions.append(driver)

        for ptype, patterns in POST_TYPE_PATTERNS.items():
            if any(re.search(p, text_lower) for p in patterns):
                self.post_types.append(ptype)

        word_count = len(self.text.split())
        if word_count < 12:
            self.tone_tags.append("punchy_short")
        if len(self.hashtags) >= 3:
            self.tone_tags.append("hashtag_heavy")

        for tone, patterns in TONE_MARKERS.items():
            if any(re.search(p, text_lower) for p in patterns):
                if tone not in self.tone_tags:
                    self.tone_tags.append(tone)

# ---------------------------------------------------------------------------
# Load posts
# ---------------------------------------------------------------------------
def load_posts() -> list[Post]:
    posts: list[Post] = []
    for platform in ("facebook", "instagram"):
        folder = os.path.join(SOCIAL_DIR, platform)
        if not os.path.isdir(folder):
            continue
        for fname in sorted(os.listdir(folder)):
            if fname.endswith(".md") and fname != ".gitkeep":
                try:
                    posts.append(Post(os.path.join(folder, fname)))
                except Exception as e:
                    print(f"  Warning: could not parse {fname}: {e}")
    posts.sort(key=lambda p: p.date or date.min)
    return posts

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def posts_for_car(posts, car):
    return [p for p in posts if car in p.car_mentions]

def posts_for_driver(posts, driver):
    return [p for p in posts if driver in p.driver_mentions]

def posts_for_type(posts, ptype):
    return [p for p in posts if ptype in p.post_types]

def count_occurrences(posts, attr):
    counts = defaultdict(int)
    for p in posts:
        for val in getattr(p, attr):
            counts[val] += 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

def count_hashtags(posts):
    counts = defaultdict(int)
    for p in posts:
        for tag in p.hashtags:
            counts[tag] += 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

def excerpt(text, max_len=120):
    text = text.replace("\n", " ").strip()
    return text if len(text) <= max_len else text[:max_len].rstrip() + "…"

def post_line(p):
    return f"- **{p.date_str}** — {excerpt(p.text)}"

def pluralize(n, word):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"

# ---------------------------------------------------------------------------
# Arc bullet extractors (per car)
# ---------------------------------------------------------------------------
def arc_goblin(car_posts):
    arc = []
    if any(re.search(r"revival|bring back to life", p.text, re.I) for p in car_posts):
        arc.append("**Revival arc begins** — pulled from storage, brought back before the hard freeze (Nov 2025)")
    if any(re.search(r"new.*tires?|new meat", p.text, re.I) for p in car_posts):
        arc.append("**New rubber** — fresh tires arrive ahead of race season (Mar 2026)")
    if any(re.search(r"steering rack|quick rack|making hay", p.text, re.I) for p in car_posts):
        arc.append("**Suspension work** — quick rack installed and other prep (Feb–Mar 2026)")
    if any(re.search(r"is ready|bonesaw", p.text, re.I) for p in car_posts):
        arc.append("**Race-ready declaration** — 'BONESAW… er.. the Goblin is READY!' (Mar 22, 2026)")
    if any(re.search(r"cylinder four|cylinder 4|tear it down", p.text, re.I) for p in car_posts):
        arc.append("**Engine failure confirmed** — cylinder 4 dead post-event; rebuild begins (Mar 28, 2026)")
    return arc

def arc_mgb(car_posts):
    arc = []
    if any(re.search(r"mystery|18rg", p.text, re.I) for p in car_posts):
        arc.append("**Mystery acquisition teardown** — 'The mystery18rg is coming apart' (Dec 2025)")
    if any(re.search(r"getting ready|racing this weekend", p.text, re.I) for p in car_posts):
        arc.append("**Race debut** — Ryan gets the MGBGT ready for its first event (Dec 2025)")
    if any(re.search(r"better and better", p.text, re.I) for p in car_posts):
        arc.append("**Growing confidence** — 'This thing just gets better and better' (Dec 2025)")
    if any(re.search(r"strip|bodywork|sanding|patch panel|body filler", p.text, re.I) for p in car_posts):
        arc.append("**Full bodywork campaign** — bare metal → patch panel → body filler → orange paint incoming (Feb–Mar 2026)")
    if any(re.search(r"inches ever closer", p.text, re.I) for p in car_posts):
        arc.append("**Season approaching** — 'MGBGTS inches ever closer' (Mar 2026)")
    return arc

def arc_fit(car_posts):
    arc = []
    if any(re.search(r"fit.?off|fit off", p.text, re.I) for p in car_posts):
        arc.append("**Fit-Off series** — Honda Fits compete head-to-head in rally and autocross (Nov–Dec 2025)")
    if any(re.search(r"christmas|sway bar", p.text, re.I) for p in car_posts):
        arc.append("**Christmas gear** — rear sway bar gifted, ongoing upgrades (Dec 2025)")
    if any(re.search(r"dws06|continental|new tires", p.text, re.I) for p in car_posts):
        arc.append("**New Continental DWS06 tires** — Fitty Cent ready for summer duty (Mar 2026)")
    if any(re.search(r"hudson", p.text, re.I) for p in car_posts):
        arc.append("**Hudson behind the wheel** — fastest novice at KCRX E1 2026, faster than most non-novice (Mar 25, 2026)")
    return arc

def arc_dale(car_posts):
    arc = []
    if any(re.search(r"followed us home", p.text, re.I) for p in car_posts):
        arc.append("**New Celica acquired** — 'Another 1st Gen Celica followed us home' (Dec 2025)")
    if any(re.search(r"gary rod|fabrication", p.text, re.I) for p in car_posts):
        arc.append("**Off to Gary Rod and Chassis** — loaded up for fabrication ahead of race season (Feb 2026)")
    return arc

def arc_st205(car_posts):
    arc = []
    if any(re.search(r"living legend|prophecy|rally beast|on boost", p.text, re.I) for p in car_posts):
        arc.append("**Prophecy fulfilled** — ST205 revealed at a Church of Combustion event, dropped straight into the dirt (Dec 2025)")
    return arc

def arc_starlet(car_posts):
    arc = []
    if any(re.search(r"starlet|4age", p.text, re.I) for p in car_posts):
        arc.append("**Future build teased** — 'Future Richard is calling. Time to get that 4age in the Starlet.' (Mar 2026)")
    return arc

CAR_ARC_FN = {
    "Goblin (MR2)":           arc_goblin,
    "Honda Fit / Fitty Cent": arc_fit,
    "Dale (Celica)":          arc_dale,
    "MGB GT":                 arc_mgb,
    "Richard's ST205":        arc_st205,
    "Starlet":                arc_starlet,
}

# ---------------------------------------------------------------------------
# Driver arc extractors
# ---------------------------------------------------------------------------
def arc_driver_ian(driver_posts):
    return [
        "**Goblin revival** — brings the Goblin back from cold storage, documented publicly (Nov 2025)",
        "**Pre-race hype meets reality** — declares the Goblin race-ready, engine fails post-event (Mar 2026)",
        "**Smack talk backfires** — challenges Ryan/Larry's Miata in MR class, Goblin dies anyway (Mar 2026)",
        "**Dale to Gary Rod and Chassis** — sent for fabrication, building toward Lake Garnett (Feb 2026)",
    ] if driver_posts else []

def arc_driver_ryan(driver_posts):
    return [
        "**MGBGT full buildout** — winter 2025–26 bodywork campaign: strip → patch → sand → orange paint (ongoing)",
        "**Trash talk initiator** — leads the Miata-vs-MR2 smack talk series against Ian (Mar 2026)",
    ] if driver_posts else []

def arc_driver_hudson(driver_posts):
    return [
        "**Breakout** — fastest novice run all day at KCRX E1 2026, faster than most non-novice (Mar 25, 2026)",
    ] if driver_posts else []

def arc_driver_richard(driver_posts):
    return [
        "**ST205 reveal** — arrives at a Church of Combustion event with the ST205; publicly established as a real competitor (Dec 2025)",
        "**Starlet 4A-GE telegraphed** — social post hints at next build project (Mar 2026)",
    ] if driver_posts else []

def arc_driver_miles(driver_posts):
    return []  # Miles not yet mentioned in social posts by name

def arc_driver_keegan(driver_posts):
    return []

DRIVER_ARC_FN = {
    "Ian":     arc_driver_ian,
    "Ryan":    arc_driver_ryan,
    "Hudson":  arc_driver_hudson,
    "Richard": arc_driver_richard,
    "Miles":   arc_driver_miles,
    "Keegan":  arc_driver_keegan,
}

# ---------------------------------------------------------------------------
# File injection helpers
# ---------------------------------------------------------------------------
def _regen_note():
    return (f"*Auto-generated {TODAY} from social posts "
            f"by `scripts/analyze_social_posts.py`. Do not hand-edit.*")

def _arc_markers(key: str) -> tuple[str, str]:
    """Return (start_marker, end_marker) for a given car or driver key."""
    slug = re.sub(r"[^a-z0-9]", "-", key.lower()).strip("-")
    return f"<!-- social-arc:{slug}:start -->", f"<!-- social-arc:{slug}:end -->"


def build_car_arc_block(car: str, car_posts: list[Post], arc_fn) -> str:
    """Build the full <!-- social-arc:{car}:start/end --> block for a car's Overview.md."""
    arc_bullets = arc_fn(car_posts)
    recent = car_posts[-5:] if car_posts else []
    start, end = _arc_markers(car)

    lines = [
        start,
        "",
        "## Social Post Arc",
        "",
        _regen_note(),
        "",
        f"**Posts mentioning this car:** {pluralize(len(car_posts), 'post')}",
        "",
    ]

    if arc_bullets:
        lines += ["**Story arc from social posts:**", ""]
        for b in arc_bullets:
            lines.append(f"- {b}")
        lines.append("")

    if recent:
        lines += ["**Recent social posts:**", ""]
        for p in recent:
            lines.append(post_line(p))
        lines.append("")

    if not arc_bullets and not recent:
        lines += ["*No social post arc data detected yet.*", ""]

    lines += [end]
    return "\n".join(lines)


def build_driver_arc_block(driver: str, driver_posts: list[Post], arc_fn) -> str:
    """Build the <!-- social-arc:{driver}:start/end --> block for a driver in Team-Bios.md."""
    arc_bullets = arc_fn(driver_posts)
    recent = driver_posts[-4:] if driver_posts else []
    start, end = _arc_markers(driver)

    lines = [
        start,
        "",
        "### Social Post Arc",
        "",
        _regen_note(),
        "",
        f"**Social post mentions:** {pluralize(len(driver_posts), 'post')}",
        "",
    ]

    if arc_bullets:
        for b in arc_bullets:
            lines.append(f"- {b}")
        lines.append("")

    if recent:
        lines += ["**Recent posts:**", ""]
        for p in recent:
            lines.append(post_line(p))
        lines.append("")

    if not arc_bullets and not recent:
        lines += ["*No social post arc data detected yet.*", ""]

    lines += [end]
    return "\n".join(lines)


def inject_block_into_file(filepath: str, new_block: str, key: str,
                           insert_before_pattern: str | None = None) -> bool:
    """
    Replace an existing <!-- social-arc:{key}:start/end --> block in filepath,
    or insert new_block before insert_before_pattern if no block exists yet.

    Returns True if the file changed.
    """
    if not os.path.isfile(filepath):
        print(f"  Skipping (file not found): {filepath}")
        return False

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original = content
    start, end = _arc_markers(key)

    # Replace existing keyed block
    pattern = re.compile(
        re.escape(start) + r".*?" + re.escape(end),
        re.DOTALL,
    )
    if pattern.search(content):
        content = pattern.sub(new_block, content)
    else:
        # Insert before the anchor pattern (e.g. "## Open Work" or "## Related Content")
        if insert_before_pattern:
            match = re.search(insert_before_pattern, content, re.MULTILINE)
            if match:
                pos = match.start()
                content = content[:pos] + new_block + "\n\n---\n\n" + content[pos:]
            else:
                content = content.rstrip("\n") + "\n\n---\n\n" + new_block + "\n"
        else:
            content = content.rstrip("\n") + "\n\n---\n\n" + new_block + "\n"

    if content == original:
        return False

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def inject_driver_block_into_bios(driver: str, new_block: str) -> bool:
    """
    Inject or replace the social-arc block for a specific driver in Team-Bios.md.
    Uses per-driver keyed markers so multiple drivers in the same file never conflict.
    Finds the driver's anchor heading, then operates within that section only.
    """
    if not os.path.isfile(TEAM_BIOS):
        print(f"  Skipping (Team-Bios.md not found): {TEAM_BIOS}")
        return False

    with open(TEAM_BIOS, encoding="utf-8") as f:
        content = f.read()

    original = content
    anchor = DRIVER_BIO_ANCHORS.get(driver)
    if not anchor:
        return False

    start, end = _arc_markers(driver)

    # If the keyed block already exists anywhere in the file, replace it directly.
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if pattern.search(content):
        content = pattern.sub(new_block, content)
    else:
        # Find the driver's anchor heading
        anchor_match = re.search(re.escape(anchor), content)
        if not anchor_match:
            print(f"  Driver anchor not found for {driver}: '{anchor}'")
            return False

        # Find the section end: next heading of the same or higher level
        anchor_level = anchor.count("#")
        next_section_re = re.compile(
            r"^#{1," + str(anchor_level) + r"} ",
            re.MULTILINE,
        )
        section_start = anchor_match.start()
        next_match = next_section_re.search(content, section_start + len(anchor))
        section_end = next_match.start() if next_match else len(content)

        driver_section = content[section_start:section_end]

        # For Hudson specifically: insert before the ### MILES SMITH subsection
        # so the two kids don't share the same injection zone.
        if driver == "Hudson":
            miles_match = re.search(r"^### MILES SMITH", driver_section, re.MULTILINE)
            if miles_match:
                insert_pos = section_start + miles_match.start()
                content = (content[:insert_pos].rstrip("\n") +
                           "\n\n" + new_block + "\n\n" +
                           content[insert_pos:])
            else:
                content = (content[:section_end].rstrip("\n") +
                           "\n\n" + new_block + "\n\n" +
                           content[section_end:])
        else:
            # Append at end of the driver's section
            content = (content[:section_end].rstrip("\n") +
                       "\n\n" + new_block + "\n\n" +
                       content[section_end:])

    if content == original:
        return False

    with open(TEAM_BIOS, "w", encoding="utf-8") as f:
        f.write(content)
    return True

# ---------------------------------------------------------------------------
# Generate Social-Post-Voice.md
# ---------------------------------------------------------------------------
def generate_voice_doc(posts: list[Post]) -> str:
    total = len(posts)
    fb_posts = [p for p in posts if p.platform == "facebook"]
    ig_posts = [p for p in posts if p.platform == "instagram"]

    type_counts  = count_occurrences(posts, "post_types")
    tone_counts  = count_occurrences(posts, "tone_tags")
    hashtag_counts = count_hashtags(posts)
    top_hashtags = list(hashtag_counts.items())[:25]

    def examples(ptype, n=3):
        return posts_for_type(posts, ptype)[:n]

    punchy      = [p for p in posts if "punchy_short" in p.tone_tags]
    storytelling = [p for p in posts if "storytelling" in p.tone_tags]

    dated = [p for p in posts if p.date]
    first_date = min(p.date for p in dated).isoformat() if dated else "unknown"
    last_date  = max(p.date for p in dated).isoformat() if dated else "unknown"

    lines = [
        "---",
        "title: OIO Social Post Voice",
        "type: reference",
        "status: active",
        "owner: Ian Jennings",
        f"updated: {TODAY}",
        "tags: [brand, voice, social, marketing, auto-generated]",
        "source_of_truth: false",
        "summary: Marketing voice and tone as demonstrated by real published OIO social posts.",
        "  Includes tone patterns, post-type taxonomy, real examples, and hashtag strategy.",
        "  Auto-generated by scripts/analyze_social_posts.py — do not hand-edit.",
        "---",
        "",
        "# OIO Social Post Voice",
        "",
        "> Derived from real published posts. Use this as the reference for writing new social",
        "> content that sounds and feels like OIO.",
        ">",
        f"> Auto-generated {TODAY} from {total} posts",
        f"> ({len(fb_posts)} Facebook, {len(ig_posts)} Instagram)",
        f"> covering {first_date} → {last_date}.",
        "> Do not hand-edit — regenerated on every social post ingestion run.",
        "",
        "---",
        "",
        "## The OIO Social Voice in One Sentence",
        "",
        "Short, punchy, often self-deprecating, always genuine — written by someone who",
        "would rather be wrenching than posting, and you can tell.",
        "",
        "---",
        "",
        "## Tone Patterns Found in Published Posts",
        "",
        "| Tone | Posts | What It Looks Like |",
        "|---|---|---|",
        f"| **Punchy / Short** | {tone_counts.get('punchy_short', 0)} | Single line. Sometimes one word. 'Approved.' / 'Taunting continues' |",
        f"| **Hashtag-Heavy** | {tone_counts.get('hashtag_heavy', 0)} | 3+ hashtags. Post itself is brief; hashtags carry the metadata |",
        f"| **Absurdist Humor** | {tone_counts.get('absurdist_humor', 0)} | Committed bit. Treats a lawnmower video as legitimate trash-talk |",
        f"| **Storytelling** | {tone_counts.get('storytelling', 0)} | Multi-sentence arc: setup, conflict, payoff implied |",
        f"| **Community Voice** | {tone_counts.get('community_voice', 0)} | 'Our Hudson', 'our team', 'errbody in the pool' |",
        f"| **Self-Deprecating** | {tone_counts.get('self_deprecating', 0)} | Ian is wrong, underpowered, or bedazzled |",
        "",
        "---",
        "",
        "## Post-Type Taxonomy",
        "",
        "| Type | Count | Description |",
        "|---|---|---|",
    ]

    type_descriptions = {
        "video_tease":            "Link in the comments. Hook + one-line tease. Pull, don't push.",
        "build_update":           "Progress checkpoint. Photo + caption. Shows the work without over-explaining.",
        "event_recap":            "Race day results. Names, cars, outcomes. Tone: celebratory or rueful.",
        "event_hype":             "Pre-race hype. Sets expectations up or down. Often includes trash talk.",
        "trash_talk":             "Playful smack talk between Ian, Ryan, and the audience. Never mean.",
        "farewell_milestone":     "Departure of cars or places. Respectful, brief, sometimes funny.",
        "community_celebration":  "Highlights an achievement. Always about someone else, not OIO.",
        "acquisition":            "A car arrived. Usually understated. Let the car do the talking.",
    }

    for ptype, desc in type_descriptions.items():
        count = type_counts.get(ptype, 0)
        lines.append(f"| **{ptype.replace('_', ' ').title()}** | {count} | {desc} |")

    lines += [
        "",
        "---",
        "",
        "## Real Post Examples by Type",
        "",
    ]

    def section(heading, example_posts, note=""):
        out = [f"### {heading}", ""]
        if note:
            out += [f"*{note}*", ""]
        if not example_posts:
            out += ["*No posts detected for this type.*", ""]
        else:
            for p in example_posts[:4]:
                out.append(post_line(p))
            out.append("")
        return out

    lines += section("Video Tease", examples("video_tease"),
                     "Short hook, 'link in the comments' closer, never explains too much.")
    lines += section("Build Update", examples("build_update"),
                     "Photo-first. Caption captures progress without over-describing.")
    lines += section("Event Hype / Trash Talk",
                     examples("event_hype") + examples("trash_talk"),
                     "Playful antagonism. Ian always at a disadvantage. Audience is in on the joke.")
    lines += section("Event Recap", examples("event_recap"),
                     "Outcome-first. Congratulatory when teammates win, rueful when the Goblin fails.")
    lines += section("Farewell / Milestone", examples("farewell_milestone"),
                     "Cars leave. Places close. People move on. One or two lines, genuine.")
    lines += section("Punchy Single-Line Posts", punchy[:4],
                     "The shortest format. One idea. Sometimes one word. Fully intentional.")
    lines += section("Storytelling / Sermon Mode", storytelling[:3],
                     "Multi-line. Usually connected to a video. Church-of-Combustion energy.")

    lines += [
        "---",
        "",
        "## Hashtag Strategy",
        "",
        f"Observed across {total} posts. Top hashtags by frequency:",
        "",
        "| Hashtag | Uses |",
        "|---|---|",
    ]
    for tag, cnt in top_hashtags:
        lines.append(f"| #{tag} | {cnt} |")

    lines += [
        "",
        "**Patterns:**",
        "- Car-specific hashtags anchor every build post (`#goblinmr2`, `#mgbgts`, `#fitgang`)",
        "- `#cars` is the broad catch-all — almost always present",
        "- `#rallycross` and `#sccarallycross` used specifically for events, not casually",
        "- `#aw11` and `#mr2` co-tag; both used together when the Goblin appears",
        "- Branded hashtags (`#oioracing`) appear in multi-post series or sponsored content",
        "",
        "---",
        "",
        "## Writing Rules Derived from Real Posts",
        "",
        "1. **Short beats long.** More than 3 sentences is the exception, not the rule.",
        "2. **Ian is always the underdog.** Never the hero. The cars humble him.",
        "3. **Name the car.** Every post where a car appears uses its nickname or hashtag.",
        "4. **Don't explain the joke.** 'Taunting continues' needs no context.",
        "5. **Hashtags at the end, not inline.** Copy runs clean, hashtags close it out.",
        "6. **'Link in the comments' is the standard tease format.** Never paste a raw YouTube URL inline.",
        "7. **Teammates get credit.** Posts about Ryan or Richard always name them.",
        "8. **Community events feel communal.** 'Our Hudson', 'our team', 'errbody in the pool'.",
        "9. **Milestones are acknowledged briefly.** No overwrought farewell essays.",
        "10. **Absurdity is deployed with full commitment.** A lawnmower video IS a valid trash-talk response.",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Generate Season-Story-Arcs.md (cross-cutting arcs only)
# ---------------------------------------------------------------------------
def generate_season_arcs_doc(posts: list[Post]) -> str:
    total = len(posts)
    dated = [p for p in posts if p.date]
    first_date = min(p.date for p in dated).isoformat() if dated else "unknown"
    last_date  = max(p.date for p in dated).isoformat() if dated else "unknown"

    # MR class: posts that mention both an MR2 and at least one of Ian/Miles/Ryan
    mr_posts = [
        p for p in posts
        if "Goblin (MR2)" in p.car_mentions
        and any(d in p.driver_mentions for d in ("Ian", "Ryan", "Miles"))
    ]

    # Fit-Off: posts that mention the Fit in a competitive context
    fitoff_posts = [
        p for p in posts
        if "Honda Fit / Fitty Cent" in p.car_mentions
        and "event_hype" in p.post_types or "event_recap" in p.post_types
    ]

    lines = [
        "---",
        "title: Season Story Arcs",
        "type: reference",
        "status: active",
        "owner: Ian Jennings",
        f"updated: {TODAY}",
        "tags: [story, arc, season, cross-cutting, narrative, social, auto-generated]",
        "source_of_truth: false",
        "summary: Cross-cutting story arcs that span multiple drivers or cars.",
        "  Individual car arcs live in each car's Overview.md.",
        "  Individual driver arcs live in Team-Bios.md.",
        "  This doc is for arcs that require multiple drivers or cars to tell.",
        "  Auto-generated by scripts/analyze_social_posts.py — do not hand-edit.",
        "---",
        "",
        "# Season Story Arcs",
        "",
        "> These are arcs that span multiple drivers or multiple cars.",
        "> Individual car arcs live in each car's `Overview.md`.",
        "> Individual driver arcs live in `Team-Bios.md`.",
        "> This document is for stories that can't be told from one car's or one driver's perspective alone.",
        ">",
        f"> Auto-generated {TODAY} from {total} posts covering {first_date} → {last_date}.",
        "> Do not hand-edit — regenerated on every social post ingestion run.",
        "",
        "---",
        "",
        "## 2026 MR Class Championship — The Gravel Glory Campaign",
        "",
        "**Drivers:** Ian Jennings (primary), Miles Smith (co-driver) — Goblin MR2 | Ryan Redenbaugh — MGB GT",
        "",
        "The 2026 KCRSCCA RallyCross MR class is an internal OIO battle.",
        "Ian and Miles share the MR2; Ryan brings the MGB GT.",
        "All three are competing in the same class for the same trophies.",
        "This is the season's central multi-driver arc.",
        "",
        "**Arc beats so far (from social posts):**",
        "",
        "- **Build season** — Ian preps the Goblin (quick rack, new tires); Ryan strips the MGB GT to bare metal for a full rebuild",
        "- **Pre-event trash talk** — Ryan and Larry (Miata) talk smack; Ian responds with a cowboy on a lawnmower",
        "- **KCRX E1 (Mar 22, 2026)** — Goblin races, declared ready ('BONESAW… READY!'), MGB GT not yet ready to run",
        "- **Post-E1 failure** — Goblin's cylinder 4 dead; Ian announces the teardown publicly",
        "- **MGB GT progressing** — 'MGBGTS inches ever closer' — Ryan getting closer to race-ready",
        "- **Hudson emerges** — fastest novice all day at E1 in the Honda Fit, faster than most non-novice",
        "",
    ]

    if mr_posts:
        lines += [
            "**Social posts touching this arc:**",
            "",
        ]
        for p in mr_posts[-6:]:
            lines.append(post_line(p))
        lines.append("")

    lines += [
        "---",
        "",
        "## The Fit-Off — Honda Fits at War",
        "",
        "**Drivers:** Ian, Ryan, and occasionally Hudson — multiple GE8 and GD3 Fits",
        "",
        "OIO's recurring multi-car challenge format. Multiple Honda Fits, same venue, different generations.",
        "Not a single-car story — the Fit-Off is a format that any Fit can enter.",
        "",
        "**Arc beats so far:**",
        "",
        "- **Fit-Off 3** — three Fits, dirt, chaos. Cones harmed. Accusations made. Witchcraft suspected. (Nov 2025)",
        "- **'Move over, Miata'** — social post positioning the Fit as the new grassroots benchmark (Dec 2025)",
        "- **Hudson fastest novice at KCRX E1** — Fitty Cent as youth development platform (Mar 2026)",
        "",
    ]

    lines += [
        "---",
        "",
        "## How to Use This Document",
        "",
        "- Check this doc when scripting or posting about **season-level** competition narratives",
        "- For **a specific car's** build arc: see that car's `Overview.md → ## Social Post Arc`",
        "- For **a specific driver's** arc: see `Team-Bios.md → [Driver] → ### Social Post Arc`",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("OIO Social Posts Analyzer")
    print(f"  Repo root: {REPO_ROOT}")

    posts = load_posts()
    print(f"  Loaded {len(posts)} posts\n")

    if not posts:
        print("  No posts found — skipping.")
        return

    # 1. Update voice doc (standalone regenerated file)
    print(f"  Generating {VOICE_DOC} ...")
    os.makedirs(BRAND_DIR, exist_ok=True)
    with open(VOICE_DOC, "w", encoding="utf-8") as f:
        f.write(generate_voice_doc(posts) + "\n")
    print("  Done.")

    # 2. Update season arcs doc (standalone regenerated file)
    print(f"\n  Generating {SEASON_DOC} ...")
    os.makedirs(CONTENT_DIR, exist_ok=True)
    with open(SEASON_DOC, "w", encoding="utf-8") as f:
        f.write(generate_season_arcs_doc(posts) + "\n")
    print("  Done.")

    # 3. Inject per-car arc blocks into individual Overview.md files
    print("\n  Injecting car arc blocks ...")
    for car, overview_path in CAR_OVERVIEW_PATHS.items():
        car_posts = posts_for_car(posts, car)
        arc_fn = CAR_ARC_FN.get(car, lambda _: [])
        block = build_car_arc_block(car, car_posts, arc_fn)
        changed = inject_block_into_file(
            overview_path,
            block,
            key=car,
            insert_before_pattern=r"^## (Open Work|Related Content|Related Videos)",
        )
        status = "updated" if changed else "unchanged"
        print(f"    [{status}] {car} → {os.path.relpath(overview_path, REPO_ROOT)}")

    # 4. Inject per-driver arc blocks into Team-Bios.md
    print("\n  Injecting driver arc blocks into Team-Bios.md ...")
    for driver, arc_fn in DRIVER_ARC_FN.items():
        driver_posts = posts_for_driver(posts, driver)
        block = build_driver_arc_block(driver, driver_posts, arc_fn)
        changed = inject_driver_block_into_bios(driver, block)
        status = "updated" if changed else "unchanged"
        print(f"    [{status}] {driver}")

    # 5. Remove the old aggregate doc if it still exists
    old_doc = os.path.join(CONTENT_DIR, "Car-and-Driver-Story-Arcs.md")
    if os.path.isfile(old_doc):
        os.remove(old_doc)
        print(f"\n  Removed old aggregate doc: {old_doc}")

    print("\nAnalysis complete.")
    print(f"  → {VOICE_DOC}")
    print(f"  → {SEASON_DOC}")
    print(f"  → Car arcs injected into individual Overview.md files")
    print(f"  → Driver arcs injected into {TEAM_BIOS}")


if __name__ == "__main__":
    main()
