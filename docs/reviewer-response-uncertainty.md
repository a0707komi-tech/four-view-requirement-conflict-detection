# Reviewer Response: Uncertainty and Abstention Reporting

**Reviewer comment.** The paper defines uncertainty as an abstention outcome but does not report when or why views abstain, limiting the practical usefulness of the uncertainty mechanism for identifying cases requiring human review. The paper also claims that uncertainty rates are reported separately, but they are absent from the results.

**Response.** We agree that the original results did not substantiate this claim. We revised the evaluation to report uncertainty at two levels. First, a view-level abstention is recorded whenever a Phase-1 view returns `uncertain` for a canonical candidate. Second, a final abstention is recorded when disagreement handling and arbitration still produce `uncertain`. We now report the denominator, count, and rate for both levels; the Phase-1 vote pattern; whether DA challenged the abstaining view; the final outcome after adjudication; and the stored reason and evidence for every abstention.

Across 6,911 final verdict rows, 169 were uncertain (2.45%). Because canonical aliases inherit their source pair's result, these rows correspond to 121 unique review units. Across 5,814 canonical candidates, at least one Phase-1 view abstained on 341 pairs (5.87%). The revised tables provide dataset-specific rates and view-specific abstention behavior.

We also made the operational policy explicit: every final `uncertain` verdict enters the human-review queue. Alias rows are collapsed to the canonical source pair so that the reported review workload is not inflated. We retained the legacy `needs_human_review` field only as provenance because older runs did not populate it consistently; it is no longer used to define the review queue in the report.

The replication package now includes the aggregate tables, per-dataset reports, exact uncertainty-source strings, Phase-1 reasoning records, and an offline generation script. This revision corrects the unsupported statement that uncertainty was already reported separately.
