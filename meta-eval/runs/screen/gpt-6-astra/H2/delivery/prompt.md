You are designing scoring criteria that other people will use to judge
engineering proposals. Your criteria will be applied later, by someone else,
to proposals you have not seen. Write them so that application is mechanical.

DOMAIN: proposals to reduce CI test flakiness (tests that pass and fail on the
same code). You must score each proposal for NOVELTY and USEFULNESS combined
into ONE overall score on a 0-3 scale (3 = best).

Four calibration proposals from this domain are in the workspace files
CAL-A.txt, CAL-B.txt, CAL-C.txt, CAL-D.txt. Read them. They are examples of
the kind of text your criteria must handle; you are NOT told how good any of
them is.

DELIVERABLE: create exactly one file named criteria.md in the workspace root
containing ALL of the following sections, in this order, with these exact
headings:

## Checks
A numbered list of checks. Each check has: an id (C1, C2, ...), a yes/no
question that can be answered from a proposal's text alone (quote the exact
evidence rule: what words/content count as YES and what counts as NO), and
the points awarded for YES (an integer >= 0). A competent reader must be able
to answer every check YES or NO for any proposal without inventing new rules.

## Score mapping
How the sum of points maps to the 0-3 overall score. Give explicit numeric
ranges for 0, 1, 2, and 3 that cover every possible total with no gaps or
overlaps.

## Worked examples
Apply your checks to each of CAL-A, CAL-B, CAL-C, CAL-D. For each: every
check's YES/NO, the total, and the mapped 0-3 score.

## Failure modes
At least three bullet points: ways a proposal could obtain a high score under
your checks without actually being novel or useful, and how your checks do or
do not guard against each.

Rules: do not modify the CAL-*.txt files. Create no other deliverable files.
Your final message must state that criteria.md is written and give the 0-3
score you assigned to each calibration proposal.
