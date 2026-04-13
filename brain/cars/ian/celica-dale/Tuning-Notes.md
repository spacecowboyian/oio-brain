# Dale — Tuning Notes

> Comprehensive ignition timing, carburetion, and drivability tuning history

*Last updated: April 2026*

---

## Current Running State

As of October 26, 2024, Dale's most recent tuning configuration:

| Parameter | Setting |
|---|---|
| **Total Timing** | 32 degrees BTDC |
| **Accelerator Pump Position** | Middle (standard) |
| **Peak Power RPM** | ~5800 RPM (18R-GU characteristic) |
| **Running Behavior** | Pulls strong, slight hesitation on tip-in, some tailpipe backfires on decel |
| **AFR at 6000 RPM** | Low 13s |

---

## Ignition Timing Development

### Initial Timing Changes (October 22, 2024)

**What Ian Did:**
- Dialed in more advance on the distributor
- Method: Turning it counterclockwise

**Effect Observed:**
- ✅ Engine had more power at higher RPMs
- ✅ AFR readings in low 13s around 6000 RPM
- ❌ Bogged on throttle tip-in below 4000 RPM

**Interpretation:**
This is a critical tuning data point showing the tradeoff between top-end power feel and lower-RPM drivability. Adding timing helped top-end but hurt throttle response at lower RPMs.

### Current Timing Setup (October 26, 2024)

**Total Advance:** 32 degrees BTDC

**Running Characteristics:**
- ✅ Car pulls strong
- ⚠️ Slight hesitation on tip-in
- ⚠️ Some backfires from the tailpipe on deceleration

**Peak Power Understanding:**
Ian concluded the 18R-GU makes peak power around 5800 RPM, which explains why power tapers above that point.

---

## Carburetion & Fueling

Dale runs Mikuni PHH sidedraft carburetors (likely dual 40PHH setup based on context).

### Accelerator Pump Tuning

#### Accelerator Pump Shaft Position Behavior

Ian documented the Mikuni PHH accelerator pump shaft behavior:

| Position | Setting | Effect |
|---|---|---|
| Top hole | Rich | More fuel on throttle tip-in |
| Middle hole | Standard | Balanced fueling |
| Bottom hole | Lean | Less fuel on throttle tip-in |

**Critical Note:** The bottom hole in the accelerator pump shaft leans it out.

### Tuning Evolution

#### October 22, 2024 — Initial Adjustment

**What Changed:**
After adding ignition advance, Ian suspected accelerator pump adjustment might help with the bog issue.

**After Initial Adjustment:**
- Less bog on tip-in
- AFR went lean initially
- Then dipped rich
- Then leveled out around 13 AFR during a low-RPM pull
- Above 3500 RPM, the car pulled hard from tip-in to 6500 RPM

#### October 26, 2024 — Return to Middle Position

**What Changed:**
Ian moved the accelerator pumps back to the middle position.

**Result:**
- ✅ Seemed to clear up the lean bog condition on tip-in
- ❌ But some bog remained after tip-in
- 💡 Ian suspected jets may need to be adjusted
- ⏰ Viewed jet changes as a longer-term fix because he did not have jets on hand

**Interpretation:**
This is a classic partial tune: timing and accelerator pump settings improved the car, but the underlying fuel curve likely still needs refinement through jetting changes.

---

## Known Weak Spots / Open Tuning Questions

### Mechanical Issues

| Issue | Status | Notes |
|---|---|---|
| Carb jetting optimization | Open | Suspected to need attention for full drivability |
| Full elimination of tip-in bog | Partial | Improved but not fully resolved |
| Decel backfire source/acceptability | Open | Present but may be acceptable |
| Timing chain tick | Concern | Possible slack in timing system |
| Thermostat behavior | Concern | May be stuck open |

### Tuning Areas for Future Work

1. **Jetting** — Longer-term tuning area to refine fuel curve
2. **Accelerator Pump Fine-Tuning** — May need custom positioning or spring changes
3. **Timing Chain Inspection** — Address tick/slack concern
4. **Thermostat Replacement** — Verify proper operation for consistent tuning

---

## Tuning Philosophy & Approach

### Ian's Methodology

Ian's approach to Dale's tuning has been:
1. **Incremental changes** — One variable at a time when possible
2. **Data-driven** — Uses AFR gauge to verify changes
3. **Real-world testing** — Evaluates drivability on the road and at events
4. **Documented** — Records settings and observations for future reference

### Tradeoffs Identified

**Top-End vs. Low-End:**
- More timing advance = better high-RPM power, worse tip-in response
- Leaner accelerator pump = less bog potential, but requires proper jetting backup

**Perfection vs. Usability:**
- Car is currently very usable for competition
- Further refinement would improve drivability but requires parts and time
- Ian has prioritized getting Dale to events over achieving perfect tune

---

## Future Tuning Plans

### Short-Term
- Monitor timing chain condition
- Verify thermostat operation
- Continue to refine accelerator pump settings as needed

### Long-Term (With Higher-Compression 18RG)
- Complete jetting optimization
- Revisit total timing for new compression ratio
- Potentially upgrade to programmable ignition for better control
- Consider dyno tuning session for baseline optimization

---

## Related Documentation

→ [Build History](Build-History.md) — 18RG swap details and engine development
→ [Maintenance Log](Maintenance-Log.md) — Oil changes after tuning sessions
→ [Setup Notes](Setup-Notes.md) — How tuning integrates with overall setup

---

## Key Takeaway

Dale's tuning is at a "good enough to compete" stage but not yet fully optimized. The current setup represents careful iteration on timing and accelerator pump settings, with jetting recognized as the next major step for drivability refinement.

The tuning story is valuable content material because it shows the real-world process of sorting a carbureted vintage engine — not a clean dyno session, but incremental improvement through testing and observation.
