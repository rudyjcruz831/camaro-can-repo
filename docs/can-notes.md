# CAN Bus Findings

Raw notes from `candump`/`cansend` sessions. Keep this messy and dated — it's a lab
notebook, not a polished doc. Clean findings graduate into `architecture.md` once confirmed.

## How to capture

```bash
# Listen only, no transmitting - always start here
candump can0

# Narrow down: toggle lock/unlock via key fob or door switch while dumping,
# save output to compare before/after
candump can0 > lock_test_$(date +%s).log
```

## Findings log

### YYYY-MM-DD

- Candidate arbitration ID: `0x___`
- Data bytes observed on lock: `__ __ __ __ __ __ __ __`
- Data bytes observed on unlock: `__ __ __ __ __ __ __ __`
- Confirmed by replay? y/n
- Notes:

<!-- Add a new dated section each session -->
