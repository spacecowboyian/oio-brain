#!/usr/bin/env python3
"""
OIO Racing - Social Posts Analyzer

Reads all social media posts from OIO Brain/data/social-posts/
and generates two brain documents:

  OIO Brain/01 - Brand/Social-Post-Voice.md
    → Marketing voice and tone as demonstrated by real published posts.
      Includes tone patterns, post-type taxonomy, real example posts,
      hashtag strategy, and cadence observations.

  OIO Brain/02 - Content/Car-and-Driver-Story-Arcs.md
    → Chronological story arcs for each car and driver as told through
      social posts. Updated whenever new posts are ingested.

Usage:
  python scripts/analyze_social_posts.py

This script is called automatically by fetch-social-posts.yml after
new posts are committed.  It is safe to run at any time — it always
regenerates the docs from the full corpus.
"""

import os
import re
from collections import defaultdict
from datetime import datetime, date

# ---------------------------------------------------------------------------
# Paths (relative to repo root)
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOCIAL_DIR = os.path.join(REPO_ROOT, "OIO Brain", "data", "social-posts")
BRAND_DIR  = os.path.join(REPO_ROOT, "OIO Brain", "01 - Brand")
CONTENT_DIR = os.path.join(REPO_ROOT, "OIO Brain", "02 - Content")

VOICE_DOC  = os.path.join(BRAND_DIR, "Social-Post-Voice.md")
ARCS_DOC   = os.path.join(CONTENT_DIR, "Car-and-Driver-Story-Arcs.md")

TODAY = date.today().isoformat()

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
    "Corolla (Domination)": [
        r"domination.*corolla", r"corolla.*dominat",
    ],
}

DRIVER_PATTERNS = {
    "Ian": [
        r"\bIan\b", r"\bIan's\b", r"\bIan here\b",
    ],
    "Ryan": [
        r"\bRyan\b", r"\bRyan's\b",
    ],
    "Richard": [
        r"\bRichard\b",
    ],
    "Hudson": [
        r"\bHudson\b",
    ],
    "Miles": [
        r"\bMiles\b",
    ],
    "Keegan": [
        r"\bKeegan\b",
    ],
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
    "punchy_short": [],  # detected by word count < 10
    "hashtag_heavy": [],  # detected by hashtag count >= 3
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

        # Strip frontmatter
        if raw.startswith("---"):
            end = raw.find("---", 3)
            fm = raw[3:end]
            body = raw[end + 3:].strip()
            # Extract date from frontmatter
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

        # Punchy: fewer than 12 words and no hashtags or <=2 hashtags
        word_count = len(self.text.split())
        if word_count < 12:
            self.tone_tags.append("punchy_short")

        # Hashtag-heavy
        if len(self.hashtags) >= 3:
            self.tone_tags.append("hashtag_heavy")

        for tone, patterns in TONE_MARKERS.items():
            if tone in ("punchy_short", "hashtag_heavy"):
                continue
            if any(re.search(p, text_lower) for p in patterns):
                if tone not in self.tone_tags:
                    self.tone_tags.append(tone)


# ---------------------------------------------------------------------------
# Load all posts
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
                    p = Post(os.path.join(folder, fname))
                    posts.append(p)
                except Exception as e:
                    print(f"  Warning: could not parse {fname}: {e}")
    posts.sort(key=lambda p: p.date or date.min)
    return posts


# ---------------------------------------------------------------------------
# Aggregate helpers
# ---------------------------------------------------------------------------
def count_occurrences(posts: list[Post], attr: str) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for p in posts:
        for val in getattr(p, attr):
            counts[val] += 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def count_hashtags(posts: list[Post]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for p in posts:
        for tag in p.hashtags:
            counts[tag] += 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def posts_for_car(posts: list[Post], car: str) -> list[Post]:
    return [p for p in posts if car in p.car_mentions]


def posts_for_driver(posts: list[Post], driver: str) -> list[Post]:
    return [p for p in posts if driver in p.driver_mentions]


def posts_for_type(posts: list[Post], ptype: str) -> list[Post]:
    return [p for p in posts if ptype in p.post_types]


def excerpt(text: str, max_len: int = 120) -> str:
    text = text.replace("\n", " ").strip()
    return text if len(text) <= max_len else text[:max_len].rstrip() + "…"


def post_line(p: Post) -> str:
    return f"- **{p.date_str}** — {excerpt(p.text)}"


# ---------------------------------------------------------------------------
# Generate Social-Post-Voice.md
# ---------------------------------------------------------------------------
def generate_voice_doc(posts: list[Post]) -> str:
    total = len(posts)
    fb_posts = [p for p in posts if p.platform == "facebook"]
    ig_posts = [p for p in posts if p.platform == "instagram"]

    type_counts = count_occurrences(posts, "post_types")
    tone_counts = count_occurrences(posts, "tone_tags")
    hashtag_counts = count_hashtags(posts)
    top_hashtags = list(hashtag_counts.items())[:25]

    # Pick representative examples per type
    def examples(ptype: str, n: int = 3) -> list[Post]:
        return posts_for_type(posts, ptype)[:n]

    punchy = [p for p in posts if "punchy_short" in p.tone_tags]
    absurdist = [p for p in posts if "absurdist_humor" in p.tone_tags]
    storytelling = [p for p in posts if "storytelling" in p.tone_tags]
    community = [p for p in posts if "community_voice" in p.tone_tags]

    # Date range
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
        "video_tease": "Link in the comments. Hook + one-line tease. Pull, don't push.",
        "build_update": "Progress checkpoint. Photo + caption. Shows the work without over-explaining.",
        "event_recap": "Race day results. Names, cars, outcomes. Tone: celebratory or rueful.",
        "event_hype": "Pre-race hype. Sets expectations up or down. Often includes trash talk.",
        "trash_talk": "Playful smack talk between Ian, Ryan, and the audience. Never mean.",
        "farewell_milestone": "Departure of cars or places. Respectful, brief, sometimes funny.",
        "community_celebration": "Highlights an achievement. Always about someone else, not OIO.",
        "acquisition": "A car arrived. Usually understated. Let the car do the talking.",
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

    def section(heading: str, example_posts: list[Post], note: str = "") -> list[str]:
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
# Generate Car-and-Driver-Story-Arcs.md
# ---------------------------------------------------------------------------
def generate_arcs_doc(posts: list[Post]) -> str:
    total = len(posts)
    dated = [p for p in posts if p.date]
    first_date = min(p.date for p in dated).isoformat() if dated else "unknown"
    last_date  = max(p.date for p in dated).isoformat() if dated else "unknown"

    def car_section(car: str, note: str, arc_bullets: list[str]) -> list[str]:
        car_posts = posts_for_car(posts, car)
        out = [
            f"### {car}",
            "",
            f"*{note}*",
            "",
            f"**Social post mentions:** {len(car_posts)} posts",
            "",
        ]
        if arc_bullets:
            out.append("**Story arc from social posts:**")
            out.append("")
            for b in arc_bullets:
                out.append(f"- {b}")
            out.append("")
        if car_posts:
            out.append("**Recent posts:**")
            out.append("")
            for p in car_posts[-5:]:
                out.append(post_line(p))
            out.append("")
        return out

    def driver_section(driver: str, note: str, arc_bullets: list[str]) -> list[str]:
        driver_posts = posts_for_driver(posts, driver)
        out = [
            f"### {driver}",
            "",
            f"*{note}*",
            "",
            f"**Social post mentions:** {len(driver_posts)} posts",
            "",
        ]
        if arc_bullets:
            out.append("**Story arc from social posts:**")
            out.append("")
            for b in arc_bullets:
                out.append(f"- {b}")
            out.append("")
        if driver_posts:
            out.append("**Recent posts:**")
            out.append("")
            for p in driver_posts[-4:]:
                out.append(post_line(p))
            out.append("")
        return out

    # Derive arc bullets from post chronology
    def arc_for_goblin(car_posts: list[Post]) -> list[str]:
        arc = []
        if any("revival" in p.text.lower() or "bring back to life" in p.text.lower() for p in car_posts):
            arc.append("**Revival arc begins** — Goblin pulled from storage, brought back before the hard freeze (Nov 2025)")
        if any("new tires" in p.text.lower() or "new meat" in p.text.lower() for p in car_posts):
            arc.append("**New rubber** — fresh tires arrive ahead of race season (Mar 2026)")
        if any("quick rack" in p.text.lower() or "steering rack" in p.text.lower() or "making hay" in p.text.lower() for p in car_posts):
            arc.append("**Suspension work** — quick rack and other prep toward race season (Feb–Mar 2026)")
        if any("is ready" in p.text.lower() or "bonesaw" in p.text.lower() for p in car_posts):
            arc.append("**Race-ready declaration** — 'BONESAW… er.. the Goblin is READY!' pre-event hype (Mar 22, 2026)")
        if any("cylinder four" in p.text.lower() or "cylinder 4" in p.text.lower() or "tear it down" in p.text.lower() for p in car_posts):
            arc.append("**Engine failure** — cylinder 4 confirmed dead post-event; announced publicly (Mar 28, 2026)")
        if not arc:
            arc.append("Arc data pending — insufficient keywords matched. Check car posts for details.")
        return arc

    def arc_for_mgb(car_posts: list[Post]) -> list[str]:
        arc = []
        if any("mystery" in p.text.lower() for p in car_posts):
            arc.append("**Mystery acquisition** — 'The mystery18rg is coming apart' — teardown and assessment begins (Dec 2025)")
        if any("getting ready" in p.text.lower() or "racing this weekend" in p.text.lower() for p in car_posts):
            arc.append("**Race debut** — Ryan gets the MGBGT ready for its first event (Dec 2025)")
        if any("better and better" in p.text.lower() for p in car_posts):
            arc.append("**Growing confidence** — 'This thing just gets better and better' (Dec 2025)")
        if any("strip" in p.text.lower() or "paint" in p.text.lower() or "bodywork" in p.text.lower() for p in car_posts):
            arc.append("**Full bodywork campaign** — stripped to bare metal, patch panel work, sanding season (Feb–Mar 2026)")
        if any("inches ever closer" in p.text.lower() for p in car_posts):
            arc.append("**Race season approaching** — 'MGBGTS inches ever closer' — late-build-season milestone (Mar 2026)")
        if not arc:
            arc.append("Arc data pending — insufficient keywords matched. Check car posts for details.")
        return arc

    def arc_for_fit(car_posts: list[Post]) -> list[str]:
        arc = []
        if any("fit.?off" in p.text.lower() or "fit off" in p.text.lower() for p in car_posts):
            arc.append("**Fit-Off series** — Honda Fits compete head-to-head in rally and autocross (Nov–Dec 2025)")
        if any("christmas" in p.text.lower() or "sway bar" in p.text.lower() for p in car_posts):
            arc.append("**Christmas gift** — rear sway bar gifted, Fitty Cent continuously upgraded (Dec 2025)")
        if any("new tires" in p.text.lower() or "dws06" in p.text.lower() or "continental" in p.text.lower() for p in car_posts):
            arc.append("**New Continental DWS06 tires** — Fitty Cent geared up for summer duty (Mar 2026)")
        if any("hudson" in p.text.lower() for p in car_posts):
            arc.append("**Hudson behind the wheel** — 15-year-old Hudson fastest novice at KCRX E1 2026 (Mar 2026)")
        if not arc:
            arc.append("Arc data pending — insufficient keywords matched. Check car posts for details.")
        return arc

    def arc_for_dale(car_posts: list[Post]) -> list[str]:
        arc = []
        if any("followed us home" in p.text.lower() for p in car_posts):
            arc.append("**New Celica acquired** — 'Another 1st Generation Celica followed us home' (Dec 2025)")
        if any("gary rod" in p.text.lower() or "fabrication" in p.text.lower() for p in car_posts):
            arc.append("**Sent to Gary Rod and Chassis** — Dale loaded for fabrication work ahead of race season (Feb 2026)")
        if not arc:
            arc.append("Arc data pending — insufficient keywords matched. Check car posts for details.")
        return arc

    goblin_posts = posts_for_car(posts, "Goblin (MR2)")
    mgb_posts    = posts_for_car(posts, "MGB GT")
    fit_posts    = posts_for_car(posts, "Honda Fit / Fitty Cent")
    dale_posts   = posts_for_car(posts, "Dale (Celica)")

    lines = [
        "---",
        "title: Car and Driver Story Arcs",
        "type: reference",
        "status: active",
        "owner: Ian Jennings",
        f"updated: {TODAY}",
        "tags: [story, arc, cars, drivers, narrative, social, auto-generated]",
        "source_of_truth: false",
        "summary: Chronological story arcs for OIO cars and drivers as told through social media posts.",
        "  Updated automatically whenever new social posts are ingested.",
        "  Do not hand-edit — regenerated by scripts/analyze_social_posts.py.",
        "---",
        "",
        "# Car and Driver Story Arcs",
        "",
        "> Story arcs extracted from published social posts. These reflect what has been",
        "> communicated publicly about each car and driver — the narrative the audience",
        "> has already been shown.",
        ">",
        f"> Auto-generated {TODAY} from {total} posts",
        f"> covering {first_date} → {last_date}.",
        "> Do not hand-edit — regenerated on every social post ingestion run.",
        "",
        "---",
        "",
        "## Car Story Arcs",
        "",
        "Each car's arc is the story the audience has already been told through social posts.",
        "Use these to maintain continuity in new posts and video scripts.",
        "",
    ]

    lines += car_section(
        "Goblin (MR2)",
        "Ian's 1985 AW11 MR2 rallycross car. The heart of the OIO universe.",
        arc_for_goblin(goblin_posts),
    )

    lines += car_section(
        "MGB GT",
        "Ryan's 1973 MGB GT with Toyota 4A-C engine. The congregation's most dramatic build arc.",
        arc_for_mgb(mgb_posts),
    )

    lines += car_section(
        "Honda Fit / Fitty Cent",
        "Ian's GE8 Honda Fit. Double-duty daily driver, autocross, and rallycross car. Also Hudson's ride.",
        arc_for_fit(fit_posts),
    )

    lines += car_section(
        "Dale (Celica)",
        "Ian's 1972 Toyota Celica. Named Dale. Long-term time-attack and Lake Garnett goal.",
        arc_for_dale(dale_posts),
    )

    lines += car_section(
        "Richard's ST205",
        "Richard's Celica GT-Four ST205. Revealed at a Church of Combustion event. Not a museum piece.",
        [
            "**Prophecy fulfilled** — Richard arrives with the ST205 at a Church of Combustion event,",
            "  revealed as a living legend dropped straight into the dirt to be tested (Dec 2025)",
        ],
    )

    lines += car_section(
        "Starlet",
        "Richard's Toyota Starlet — future 4A-GE swap project.",
        [
            "**Future build teased** — 'Future Richard is calling. Time to get that 4age in the Starlet.' (Mar 2026)",
        ],
    )

    lines += [
        "---",
        "",
        "## Driver Story Arcs",
        "",
    ]

    lines += driver_section(
        "Ian",
        "Founder, driver, perpetual underdog. His cars always break at the worst time.",
        [
            "**Goblin revival** — Off-season, Ian brings the Goblin back from cold storage",
            "**Pre-race hype meets reality** — declares the Goblin ready; engine fails post-event",
            "**Smack talk backfires** — challenges Ryan/Larry's Miata, posts trash talk, Goblin dies anyway",
            "**Dale at Gary Rod and Chassis** — sends Dale for fabrication, building toward Lake Garnett",
        ],
    )

    lines += driver_section(
        "Ryan",
        "Co-conspirator. Building the MGB GT through a full winter bodywork campaign.",
        [
            "**MGBGT buildout** — Winter 2025–26 bodywork campaign: strip, patch, sand, paint",
            "**Trash talk initiator** — leads the Miata-vs-MR2 smack talk series against Ian",
        ],
    )

    lines += driver_section(
        "Hudson",
        "Ian's 15-year-old son. First official race results in 2026.",
        [
            "**Breakout** — Fastest novice run all day at KCRX E1 2026, faster than most non-novice (Mar 2026)",
        ],
    )

    lines += driver_section(
        "Richard",
        "ST205 Celica owner. Surprise reveals are his style.",
        [
            "**ST205 reveal** — Appears at a Church of Combustion event with the ST205; crowd goes silent",
            "**Starlet 4A-GE** — telegraphing the next build in social posts (Mar 2026)",
        ],
    )

    lines += driver_section(
        "Miles",
        "Co-driver of the MR2. Multi-season KC RallyCross competitor.",
        [],
    )

    lines += [
        "---",
        "",
        "## Continuity Notes for Writers",
        "",
        "When writing new social posts or scripts, check this document to ensure story continuity:",
        "",
        "- **The Goblin is currently down.** Posts should acknowledge the rebuild arc, not assume it runs.",
        "- **The MGB GT is in late-stage bodywork.** Race season is approaching for Ryan's car.",
        "- **Hudson is now established as a real competitor.** Reference his KCRX E1 result when relevant.",
        "- **Dale is at Gary Rod and Chassis.** Fabrication is underway. Return ETA is TBD.",
        "- **The ST205 has been revealed.** Richard's car is no longer a mystery — it's been driven in the dirt.",
        "- **Fitty Cent has fresh Continental tires.** Ready for summer.",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("OIO Social Posts Analyzer")
    print(f"  Repo root: {REPO_ROOT}")
    print(f"  Social dir: {SOCIAL_DIR}")

    posts = load_posts()
    print(f"  Loaded {len(posts)} posts")

    if not posts:
        print("  No posts found — skipping doc generation.")
        return

    print(f"\n  Generating {VOICE_DOC} ...")
    voice_content = generate_voice_doc(posts)
    os.makedirs(BRAND_DIR, exist_ok=True)
    with open(VOICE_DOC, "w", encoding="utf-8") as f:
        f.write(voice_content + "\n")
    print("  Done.")

    print(f"\n  Generating {ARCS_DOC} ...")
    arcs_content = generate_arcs_doc(posts)
    os.makedirs(CONTENT_DIR, exist_ok=True)
    with open(ARCS_DOC, "w", encoding="utf-8") as f:
        f.write(arcs_content + "\n")
    print("  Done.")

    print("\nAnalysis complete.")
    print(f"  → {VOICE_DOC}")
    print(f"  → {ARCS_DOC}")


if __name__ == "__main__":
    main()
