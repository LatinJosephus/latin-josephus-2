# Narrative comparator correction

The first build3 comparison passed XIV's 160 adjoining intervals and XV's intervals through 124, then failed at XV.125 because the retained literal source chapter label `VII ` appeared at the end of the displayed interval. The independently recorded narrative scope excludes that literal label, while preserving its source bytes and display. The comparator initially stripped labels only at paragraph openings and required a correction to recognize the independently identified text-node prefix when an interval ends after it.

The corrected comparator removes that exact label from narrative comparison and leaves the built reader and source markup unchanged. A fresh run passed all 146 complete XV intervals in the contiguous checkpoint. This was a comparison failure, recorded and resolved; no source difference or additional browser error was waived. The literal label remains visible in the reader.
