# Interview Guide

## 90-second explanation

I built a fail-closed trading research and paper-operations system. The goal was not to make a profitability claim; it was to make it difficult to fool myself or create an unsafe execution path.

On the research side, hypotheses, costs, inference, and rejection rules were frozen before evaluation. Two hypotheses failed and stayed failed. One produced a positive strategy-versus-cash result, but the registered anomaly comparison was negative, so I reported the primary claim as a failure. I also rejected a dataset that matched the reference within a cent on 99.94% of rows because two rows had impossible OHLC geometry and one breached a pre-frozen discrepancy limit.

On the operations side, credentials stayed local, paper endpoints were isolated, intent was written before mutation, ambiguous writes were never retried, and success required a reconciled clean account. The first 24-hour reliability run failed because the machine slept for three hours. I preserved that failure, added an awake lease, kept all nine thresholds unchanged, and the second run passed.

The main lesson is that a trustworthy system must make expensive negative decisions visible and reproducible, not merely produce a working order call.

## Likely questions

### Why is a negative result portfolio-worthy?

Because the work demonstrates research design, inference, data validation, operational safety, and judgment under selection pressure. A fabricated or overfit positive result would demonstrate less.

### Why did HYP-0001 fail if strategy versus cash was positive?

The primary question was whether turn-of-month days outperformed other eligible market days after cost. The cash comparison measured a different quantity and benefited from ordinary market drift during partial exposure. It was mandatory supporting output, not the registered decision rule.

### Why reject a dataset that was 99.94% clean?

The hard gates were frozen before inspection. Two impossible bars and a $0.20 discrepancy showed that excellent aggregate agreement could hide isolated defects. Relaxing the rule only because the dataset was needed would invalidate the admission process.

### What happens after an ambiguous order response?

The system does not retry. It records that manual reconciliation is required, checks the broker account through a read-only path, and does not permit another sequence until the persistent budget and reconciliation conditions allow it.

### What did the soak test discover?

The first run proved that observation count was insufficient: 1,440 observations accumulated despite a three-hour sleep gap. The second version added host-awake instrumentation while preserving the original thresholds. It then completed a real 24-hour window and passed.

### What is the biggest limitation?

There is no validated edge and no live deployment. Paper fills do not establish live execution quality, and one accepted 24-hour window does not establish long-term reliability.
