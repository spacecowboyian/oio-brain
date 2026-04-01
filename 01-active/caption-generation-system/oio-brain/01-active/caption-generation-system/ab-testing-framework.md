# OIO Caption A/B Testing Framework

**Purpose:** Test AI-generated captions against manual captions and tune the system for optimal engagement and brand voice consistency.

---

## Overview

A/B testing compares AI-generated captions vs manually written captions (or different AI variations) to:
1. Validate AI caption quality and engagement performance
2. Identify which voice patterns drive higher engagement
3. Tune the generation system based on real performance data
4. Ensure AI captions match or exceed manual caption performance

---

## Testing Methodology

### Test Structure

**Cohort A:** AI-Generated Caption
**Cohort B:** Manual Caption (or Alternative AI Caption)

**Random Assignment:** Alternate post assignments to avoid bias
**Sample Size:** Minimum 20 posts per cohort for statistical significance
**Duration:** 4-6 weeks per test cycle

---

## Metrics Tracked

### Primary Metrics (Engagement)

#### 1. Engagement Rate
```
Engagement Rate = (Likes + Comments + Shares) / Reach × 100
```

**Target:** AI ≥ Manual engagement rate

#### 2. Reach
**Definition:** Total unique accounts who saw the post
**Platform:** Facebook Insights, Instagram Insights

#### 3. Click-Through Rate (for video posts)
```
CTR = Video Clicks / Post Impressions × 100
```

**Target:** AI ≥ Manual CTR (indicates effective video promo language)

---

### Secondary Metrics (Quality)

#### 4. Comment Sentiment
**Manual Review:** Categorize comments as positive, neutral, negative
**Target:** AI ≥ Manual positive sentiment ratio

#### 5. Brand Voice Consistency Score
**Manual Review:** Score each post using quality rubric (0-10)
**Target:** AI ≥ 7.0 average score

#### 6. First-Generation Approval Rate
```
Approval Rate = Captions Approved / Captions Generated × 100
```

**Target:** ≥90% approval rate

---

### Tertiary Metrics (Operational)

#### 7. Time to Publish
**Measure:** Time from video completion to social post published
**Target:** AI faster than manual process

#### 8. Revision Count
**Measure:** Number of edits needed before approval
**Target:** AI ≤1 revision on average

---

## Test Post Selection

### Inclusion Criteria

**Include posts that:**
- Have video content (consistent format)
- Are typical OIO content (not one-off experiments)
- Have comparable topics across A/B cohorts
- Are published at similar times (avoid timing bias)

**Exclude posts that:**
- Have unusual external factors (viral moment, news coverage)
- Are paid/boosted posts
- Are reposts or reshares
- Have drastically different content types in A vs B

---

## Test Design

### Scenario 1: AI vs Manual (Baseline Test)

**Purpose:** Validate AI can match manual caption performance

**Cohort A:** AI-generated captions (3 options, best selected)
**Cohort B:** Manually written captions by AI Copywriter/Social Media Manager

**Posts:** 20 video releases over 4 weeks
**Assignment:** Alternate A-B-A-B by publish date

**Success Criteria:**
- AI engagement rate ≥ 95% of manual engagement rate
- AI brand voice score ≥ 7.0/10
- AI approval rate ≥ 90%

---

### Scenario 2: AI Tone Bucket Variations

**Purpose:** Test which tone buckets drive higher engagement

**Cohort A:** Pit-Talk Casual tone captions
**Cohort B:** Story Promo tone captions

**Posts:** 20 similar video releases (build updates or race recaps)
**Assignment:** Alternate A-B-A-B

**Hypothesis:** Story Promo tone drives higher engagement for video releases

---

### Scenario 3: Caption Length Testing

**Purpose:** Validate optimal caption length

**Cohort A:** Short captions (<150 characters)
**Cohort B:** Medium captions (150-300 characters)
**Cohort C:** Long captions (>300 characters)

**Posts:** 30 video releases over 6 weeks
**Assignment:** Rotate A-B-C-A-B-C

**Hypothesis:** Medium-length captions (150-300 chars) drive highest engagement

---

### Scenario 4: Hashtag Count Testing

**Purpose:** Optimize hashtag strategy

**Cohort A:** Minimal hashtags (3-4 tags)
**Cohort B:** Standard hashtags (5-7 tags)
**Cohort C:** Heavy hashtags (8-10 tags)

**Posts:** 30 posts over 4 weeks
**Assignment:** Rotate A-B-C-A-B-C

**Hypothesis:** Standard hashtags (5-7) perform best for OIO

---

## Data Collection

### Post Metadata Template

```json
{
  "post_id": "facebook_12345",
  "date": "2026-03-30",
  "platform": "facebook",
  "cohort": "A",
  "caption_source": "AI",
  "video_title": "MR2 Engine Teardown",
  "cars": ["Goblin MR2"],
  "content_type": "Build Update",
  "tone_bucket": "Pit-Talk Casual",
  "character_count": 103,
  "hashtag_count": 4,
  "approval_status": "approved_no_edits",
  "time_to_generate": "2m 34s",
  "revision_count": 0
}
```

### Engagement Data Template

```json
{
  "post_id": "facebook_12345",
  "date_published": "2026-03-30T10:00:00Z",
  "date_measured": "2026-04-06T10:00:00Z",
  "days_elapsed": 7,
  "reach": 2450,
  "impressions": 3100,
  "likes": 187,
  "comments": 12,
  "shares": 8,
  "video_clicks": 342,
  "engagement_rate": 8.45,
  "ctr": 11.03
}
```

**Collection Schedule:**
- 24 hours after publish
- 7 days after publish
- 30 days after publish (final measurement)

---

## Analysis Process

### Step 1: Data Aggregation

Collect all post metadata and engagement data into spreadsheet or database.

**Tools:**
- Google Sheets
- CSV export
- Python analysis script (optional)

---

### Step 2: Statistical Comparison

Calculate average metrics per cohort:

```
Avg Engagement Rate A = Σ(Engagement Rate A) / Count A
Avg Engagement Rate B = Σ(Engagement Rate B) / Count B

Difference = ((Avg A - Avg B) / Avg B) × 100
```

**Statistical Significance:**
Use t-test or Mann-Whitney U test to validate results (p < 0.05)

---

### Step 3: Cohort Comparison

**Compare cohorts on:**
- Engagement rate (primary)
- Reach
- CTR
- Comment sentiment
- Brand voice score

**Visualize:**
- Bar charts for average metrics
- Line charts for performance over time
- Box plots for distribution comparison

---

### Step 4: Pattern Identification

**Look for:**
- Which tone buckets perform best
- Optimal character count range
- Hashtag count sweet spot
- Time of day/week patterns
- Content type preferences

**Segment by:**
- Platform (Facebook vs Instagram)
- Content type (Video Tease, Build Update, Event Recap)
- Car featured (Goblin MR2, Fitty Cent, etc.)

---

### Step 5: Tuning Recommendations

Based on test results, adjust:
- System prompt emphasis (tone bucket weights)
- Character count targets
- Hashtag strategy
- Opener/closer patterns
- Few-shot example selection

---

## Test Execution Checklist

### Pre-Test (Week 0)

- [ ] Define test hypothesis and success criteria
- [ ] Select post cohort (20-30 posts)
- [ ] Assign A/B cohorts randomly
- [ ] Prepare AI generation system
- [ ] Set up data collection spreadsheet
- [ ] Baseline manual caption performance (if not done)

---

### During Test (Weeks 1-6)

- [ ] Generate AI captions for cohort A posts
- [ ] Review and approve captions (track revisions)
- [ ] Publish posts on schedule
- [ ] Collect 24h, 7-day, 30-day metrics
- [ ] Monitor for external factors (viral moments, algorithm changes)
- [ ] Log any anomalies or issues

---

### Post-Test (Week 7)

- [ ] Finalize data collection
- [ ] Run statistical analysis
- [ ] Calculate significance (t-test or equivalent)
- [ ] Identify patterns and insights
- [ ] Document findings
- [ ] Make tuning recommendations
- [ ] Plan next test iteration

---

## Sample Test Results Format

### Test #1: AI vs Manual Baseline

**Duration:** 2026-03-15 to 2026-04-12 (4 weeks)
**Posts:** 20 video releases (10 AI, 10 Manual)
**Platform:** Facebook

#### Results

| Metric | AI (Cohort A) | Manual (Cohort B) | Difference | p-value |
|--------|---------------|-------------------|------------|---------|
| Engagement Rate | 8.32% | 8.15% | +2.1% | 0.73 |
| Reach | 2,340 | 2,280 | +2.6% | 0.68 |
| CTR | 11.2% | 10.9% | +2.8% | 0.64 |
| Positive Comments | 94% | 92% | +2.2% | - |
| Voice Score | 8.1/10 | 8.4/10 | -3.6% | - |

**Interpretation:**
- AI captions matched manual performance (no significant difference)
- Engagement rate slightly higher for AI (not statistically significant)
- Brand voice score slightly lower for AI but above quality gate (7.0)

**Conclusion:** AI captions are production-ready for video posts

**Next Steps:**
- Run tone bucket variation test (Test #2)
- Continue monitoring over longer period
- Tune AI to improve voice score closer to 8.5

---

## Test Cycle Cadence

### Initial Validation Phase (Months 1-2)
**Test #1:** AI vs Manual Baseline
**Test #2:** Tone Bucket Variations

**Goal:** Validate AI can match manual quality and identify best tone patterns

---

### Optimization Phase (Months 3-4)
**Test #3:** Caption Length Optimization
**Test #4:** Hashtag Count Optimization

**Goal:** Fine-tune parameters for maximum engagement

---

### Ongoing Monitoring (Month 5+)
**Test #5:** Seasonal content variations
**Test #6:** Platform-specific tuning (Facebook vs Instagram)
**Test #7:** New content types (Shorts, Reels)

**Goal:** Continuous improvement and adaptation

---

## Quality Gate Enforcement

Before deploying AI captions to production:

**Minimum Requirements:**
- [ ] Test #1 (AI vs Manual) shows no significant negative difference
- [ ] AI engagement rate ≥ 95% of manual baseline
- [ ] AI brand voice score ≥ 7.0/10 on average
- [ ] First-generation approval rate ≥ 90%
- [ ] No major negative feedback from team/community

**If requirements not met:**
- Tune system prompt and parameters
- Expand few-shot examples
- Re-run test with adjusted system
- Do not deploy until quality gate passed

---

## Reporting Template

### Monthly A/B Test Report

**Test Period:** [Start Date] to [End Date]
**Posts Tested:** [Count] ([Cohort A Count] AI, [Cohort B Count] Manual)

**Key Findings:**
1. [Primary insight]
2. [Secondary insight]
3. [Pattern observed]

**Metrics Summary:**
- Engagement Rate: AI [X%] vs Manual [Y%] ([+/- Z%])
- Reach: AI [X] vs Manual [Y] ([+/- Z%])
- Voice Score: AI [X/10] vs Manual [Y/10]
- Approval Rate: [X%]

**Recommendations:**
1. [Tuning recommendation]
2. [Process improvement]
3. [Next test focus]

**Attachments:**
- Detailed data CSV
- Visualization charts
- Sample caption comparisons

---

## Tools & Resources

### Data Collection
- Facebook Insights API
- Instagram Insights API
- Manual CSV export
- Google Sheets template

### Analysis
- Python + pandas (optional)
- Google Sheets pivot tables
- Statistical significance calculator

### Visualization
- Google Sheets charts
- Matplotlib/Seaborn (Python)
- Tableau/Looker (if available)

---

## Notes

- A/B testing should be ongoing, not one-time validation
- External factors (algorithm changes, viral moments) can skew results
- Minimum 20 posts per cohort for meaningful results
- Test one variable at a time for clear causation
- Document all test parameters and results for future reference
- Share results with Social Media Manager for alignment
