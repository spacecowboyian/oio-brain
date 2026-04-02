# OIO Caption Quality Criteria & Tuning Guide

**Purpose:** Define quality standards and tuning parameters for AI-generated OIO Racing captions to achieve >90% first-generation approval rate.

---

## Quality Assessment Rubric

### Score Range: 0-10 (7+ passes quality gate)

### Core Criteria (Must-Pass)

#### 1. Voice Authenticity (Weight: 3.0)
**Question:** Does this sound like someone from OIO actually said it?

**10 points:** Unmistakably OIO voice — could be quoted from Ian, Ryan, or Richard
**7-9 points:** Clearly OIO style with minor adjustments needed
**4-6 points:** Generic car enthusiast voice, lacks OIO specificity
**1-3 points:** Corporate/marketing voice, polished brand language
**0 points:** Completely wrong tone (fake-hype, dealership, influencer)

**Red Flags:**
- "We're excited to announce"
- "Check out our latest content"
- "Don't forget to like and subscribe"
- Generic motivational language
- Overpolished, no rough edges

**Green Flags:**
- Car nicknames used naturally (Goblin, Fitty Cent, Dale's Dragon)
- Mechanic's voice (broke, fixed, tore down, swapped)
- Self-aware humor (slowest drag race, questionable choices)
- Specific event/car/person references
- Grassroots language (junkyard, budget, dirt, chaos)

---

#### 2. Specificity vs Generic (Weight: 2.5)
**Question:** Could this caption belong to any random car page?

**10 points:** Deeply specific — names cars, chassis codes, events, people, failures
**7-9 points:** Good specifics with 1-2 generic elements
**4-6 points:** Mix of specific and generic, could use more detail
**1-3 points:** Mostly generic with minimal OIO identity
**0 points:** Could be posted by any car account

**Specificity Markers:**
- Car names/nicknames
- Chassis codes (AW11, GD3, RA21, ST205)
- Event names (KCRSCCA, LGGPR, Solo Nats)
- Driver names (Ian, Ryan, Richard, Keegan)
- Technical details (4AGE, 18RG, 3SGTE)
- Location references (Kansas City, Lincoln NE, Riverside MO)

---

#### 3. Tone Bucket Match (Weight: 2.0)
**Question:** Does the tone match the content type?

**Tone Bucket Guidelines:**
- **Pit-Talk Casual:** Quick updates, shop moments, simple reactions (1-3 sentences)
- **Story Promo:** Video releases, big reveals, race recaps (dramatic, 2-4 vivid lines)
- **Enthusiast Opinion:** Hot takes, platform comparisons, tribal humor (punchy, quotable)
- **Car Mythology:** Builds, revivals, farewell posts (car as character, emotional arc)

**10 points:** Perfect tone for content type
**7-9 points:** Mostly appropriate with minor adjustments
**4-6 points:** Mismatched tone (too casual for big moment, too dramatic for small update)
**0-3 points:** Completely wrong tone bucket

---

#### 4. Structure & Pacing (Weight: 1.5)
**Question:** Does the caption flow naturally and use OIO patterns?

**Strong Structures:**
- **Quick Hit:** 1 strong line + 1 follow-up + tags
- **Video Promo:** Link mention → premise tease → 2-4 lines → closer + tags
- **Car Mythology:** Car as character → challenge → consequence hint
- **One-Liner:** Single impactful statement + tags (when earned)

**10 points:** Perfect structure, strong opener/closer, natural pacing
**7-9 points:** Good structure with minor flow issues
**4-6 points:** Awkward pacing, weak opener/closer, too long or too short
**0-3 points:** No clear structure, rambling or choppy

**Red Flags:**
- Run-on sentences that lose momentum
- Overexplanation (saying too much)
- Weak opener ("Here's a video")
- No rhythm in multi-line posts

**Green Flags:**
- Strong OIO openers (Video link in comments, This thing..., Another one followed us home)
- Short punchy lines with breaks
- Strong closers (Let's jump in, This was only the beginning, Church adjourned)
- Intentional pacing (periods for dramatic breaks)

---

#### 5. Hashtag Quality (Weight: 1.0)
**Question:** Are hashtags relevant, appropriate, and not overloaded?

**10 points:** Perfect tag selection (3-7 relevant tags, car/event specific)
**7-9 points:** Good tags with 1-2 generic additions
**4-6 points:** Too many tags or missing key tags
**0-3 points:** Generic tag spam or no tags when needed

**Hashtag Rules:**
- Use 3-7 tags (not 15+)
- Include car-specific tags when applicable
- Include event tags when applicable
- Avoid generic fluff (#cars is OK, #passion is not)
- Match historical OIO tag patterns

**Top OIO Tags by Usage:**
#cars #fitgang #mgbgts #rallycross #mr2 #hondafit #sccarallycross #goblinmr2 #aw11 #dalesdragon #ra21 #toyota

---

## Secondary Criteria (Fine-Tuning)

#### 6. Character Count Target
**Optimal:** <300 characters (high engagement)
**Acceptable:** 300-500 characters
**Too Long:** >500 characters (needs editing)

**Platform Limits:**
- Instagram: 2,200 max
- Facebook: 63,206 max

---

#### 7. Humor Quality (If Present)
**Good Humor:**
- Self-deprecating (Ian losing to Miatas)
- Earned from truth (world's slowest drag race)
- Insider jokes (Fit > Miata)
- Mechanical absurdity (cylinder four is done)

**Bad Humor:**
- Forced jokes
- Meme spam
- Overused formats
- Try-hard cringe

---

#### 8. Emotional Investment
**Good Investment:**
- Cars treated as characters
- Genuine sentiment (farewells, milestones)
- Underdog celebration
- Earned drama (championship race pressure)

**Bad Investment:**
- Fake sentiment
- Overblown drama
- Marketing hype
- Manufactured urgency

---

## Tuning Parameters

### System Prompt Adjustments

#### Temperature Settings
- **Default:** 0.7 (balanced creativity/consistency)
- **Increase to 0.8-0.9:** For more creative/experimental captions
- **Decrease to 0.5-0.6:** For stricter brand voice adherence

#### Few-Shot Example Weights
**Increase emphasis on:**
- Pit-Talk Casual examples → Generate shorter captions
- Story Promo examples → Generate more dramatic captions
- Enthusiast Opinion examples → Generate more opinionated captions

#### Tone Bucket Overrides
Force specific tone by explicitly stating in prompt:
- "Generate only Pit-Talk Casual captions (1-3 sentences max)"
- "Use Story Promo tone with strong closer"
- "Enthusiast Opinion tone, punchy and quotable"

---

## Quality Gate Thresholds

### Pass: Score ≥ 7.0/10
**Action:** Approve for use (may need minor hashtag/length tweaks)

### Review: Score 5.0-6.9/10
**Action:** Needs editing — identify specific issues and regenerate or hand-edit

### Fail: Score < 5.0/10
**Action:** Regenerate with adjusted parameters or write manually

---

## Common Failure Patterns & Fixes

### Problem: Too Generic
**Symptoms:** Could belong to any car page, no OIO specifics
**Fix:** Add explicit details in prompt (car names, event specifics, driver names)

### Problem: Too Polished
**Symptoms:** Sounds like marketing copy, fake-hype language
**Fix:** Increase Pit-Talk Casual example weight, lower temperature, emphasize "grassroots voice"

### Problem: Wrong Tone
**Symptoms:** Casual tone for big moment, dramatic tone for small update
**Fix:** Explicitly state content type and expected tone bucket in prompt

### Problem: Too Long
**Symptoms:** Caption exceeds 500 characters
**Fix:** Add length constraint to prompt ("Keep under 300 characters")

### Problem: Weak Opener/Closer
**Symptoms:** Generic start/end, no impact
**Fix:** Emphasize strong opener/closer examples, explicitly request them

### Problem: Bad Hashtags
**Symptoms:** Too many tags, generic tags, missing car/event tags
**Fix:** Provide specific car/event context in prompt, reference hashtag guide

---

## Manual Review Checklist

Use this checklist before approving AI-generated captions:

- [ ] Sounds like OIO voice (not generic brand)
- [ ] Includes specific details (car/event/person names)
- [ ] Appropriate tone for content type
- [ ] Strong opener (or intentionally minimal)
- [ ] Natural pacing and structure
- [ ] Character count reasonable (<500, ideally <300)
- [ ] Hashtags relevant and not overloaded (3-7 tags)
- [ ] No marketing language ("excited to announce", "check out")
- [ ] No fake-hype or forced humor
- [ ] Car nickname used if applicable
- [ ] Could NOT belong to any random car page

---

## Success Metrics

### Target: >90% First-Generation Approval Rate

**Tracking:**
- Total captions generated
- Approved without edits
- Approved with minor edits (hashtags/length only)
- Needs regeneration (tone/voice issues)
- Manual write required (AI failed)

**Formula:**
```
Approval Rate = (Approved + Minor Edits) / Total Generated × 100
```

### Quality Monitoring

**Weekly Review:**
- Calculate approval rate
- Identify common failure patterns
- Adjust system prompt or parameters
- Update few-shot examples if needed

**Monthly Review:**
- Compare AI-generated vs manual caption engagement metrics
- Update quality criteria based on performance data
- Refine hashtag strategy based on tag performance

---

## Tuning Workflow

1. **Generate Test Batch** (20 captions)
2. **Score Each Caption** using rubric
3. **Calculate Average Score**
4. **Identify Patterns** in low-scoring captions
5. **Adjust Parameters** (temperature, examples, constraints)
6. **Regenerate Failed Captions**
7. **Compare Scores** before/after tuning
8. **Document Changes** and results

**Iterate until:** Average score ≥ 7.5 and approval rate ≥ 90%

---

## Example Scoring

### Caption A (Score: 9.2/10)
```
The goblin speaketh… cylinder four is done. Time to tear it down.
#goblinMR2 #RXMR2 #rallycross #aw11
```

**Breakdown:**
- Voice Authenticity: 10/10 (perfect OIO voice, mechanical language)
- Specificity: 9/10 (car nickname, specific problem, chassis code)
- Tone Match: 9/10 (Pit-Talk Casual, perfect for build update)
- Structure: 9/10 (strong character voice opener, natural pacing)
- Hashtags: 9/10 (4 relevant tags, car-specific)

**Result:** PASS — Approve for use

---

### Caption B (Score: 4.8/10)
```
We're excited to share this amazing rallycross content with our community! Check out how our team pushed the limits and showed what grassroots racing is all about. Don't forget to follow for more exciting updates from the track! 🔥🏁 #rallycross #racing #grassroots #carsofinstagram #motorsports #racing life #trackday #performance #community
```

**Breakdown:**
- Voice Authenticity: 1/10 (corporate/marketing voice, fake-hype)
- Specificity: 2/10 (no car names, no specifics, generic)
- Tone Match: 4/10 (too polished for any OIO content)
- Structure: 5/10 (rambling, weak CTA)
- Hashtags: 3/10 (too many generic tags, tag spam)

**Result:** FAIL — Regenerate with stricter voice parameters

---

## Notes

- Quality criteria should evolve based on actual performance data
- Weight adjustments may be needed after A/B testing results
- This rubric applies to both AI-generated and manually written captions
- When in doubt, refer to historical high-performing posts in few-shot examples
