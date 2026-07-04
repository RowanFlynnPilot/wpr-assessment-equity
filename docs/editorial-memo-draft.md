# MEMO — Assessment equity study: data use & publication policy

**To:** Editor, Wausau Pilot & Review
**From:** Rowan
**Re:** New analytical use of raw RETR data; sign-off requested on three points
**Status:** DRAFT — not yet sent

## What this project is

A sales ratio study asking whether cheaper homes in Marathon County are assessed
at a higher fraction of their market value than expensive homes — meaning
lower-priced homeowners would be paying proportionally more property tax than
they should, and higher-priced owners less. This is a standard, court-tested
method (the same family of analysis behind published investigations in Chicago,
Detroit, and Philadelphia, and a University of Chicago national study). The
statistics involved are the ones assessors themselves are professionally
evaluated against, so findings are defensible against pushback.

## What's new versus the property transactions column

The transactions column publishes individual sales under the policy you signed
off in June (genuine sales, $1,000 floor, full street address, no mailing
addresses, no parcel numbers, community-level mapping).

This study is different in both directions:

1. **It uses MORE of the raw data internally.** The analysis needs fields we
   deliberately discard from the public feed — parcel numbers (to match each
   sale to its assessment), the buyer/seller relationship field (to keep only
   arm's-length sales), and fee-exemption codes. The raw file stays on our
   machines, is never committed to any repository, and is deleted per run —
   the same handling as today.

2. **It publishes LESS.** Every output of this pipeline is aggregate-only:
   statistics by municipality and by price bracket. No names, no addresses, no
   parcel numbers, no individual properties appear in anything it produces.

## Sign-off requested

1. **Approve the internal use of parcel numbers and relationship fields** from
   raw RETR data for this analysis, under the handling described above.
2. **Confirm aggregate-only output** as the pipeline's hard rule. (Built in
   already; this makes it policy.)
3. **Illustrative properties in any eventual story** — the Chicago reporting
   named specific over-assessed and under-assessed homes, which is powerful but
   is a judgment call about naming private homeowners' tax situations. This is
   entirely an editorial decision, entirely yours, and nothing in the pipeline
   assumes either answer. Flagging it now so it isn't decided by default later.

## Timing

The 2025 study runs as soon as the state publishes the 2025 assessment roll in
the statewide parcel dataset (the "V12" release, scheduled June 30, 2026 —
imminent). First deliverable is an internal findings memo, not a story: if
Marathon County assessments turn out to be equitable, that is a small story or
none, and we will not manufacture one.
