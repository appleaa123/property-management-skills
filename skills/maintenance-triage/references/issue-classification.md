# Issue Classification Guide

## Keyword → issue_type Mapping

| Keywords / Visual Cues                                          | issue_type               | vendor trade_type | Emergency?           |
| --------------------------------------------------------------- | ------------------------ | ----------------- | -------------------- |
| flood, burst pipe, water pouring, wet ceiling, water everywhere | water damage             | plumber           | YES                  |
| gas smell, gas leak                                             | —                        | —                 | YES (call 911 first) |
| no heat, furnace out, furnace broken, cold, no hot water        | HVAC                     | HVAC              | YES (Oct–Apr)        |
| sparks, electrical burning smell, outlet not working, breaker   | electrical damage        | electrician       | YES (sparks/smell)   |
| fire                                                            | —                        | —                 | YES (call 911 first) |
| washer, dryer, dishwasher, fridge, stove, oven, microwave       | appliance                | appliance         | No                   |
| roof leak, shingles, attic wet                                  | roof                     | roofer            | No                   |
| AC not working, AC broken                                       | HVAC                     | HVAC              | No                   |
| driveway slope, yard flooding, water pooling near foundation    | Improper Surface Grading | general           | No                   |
| general repair, door, window, lock, paint, drywall, flooring    | maintenance              | general           | No                   |

## Emergency Decision Tree

```
Is keyword present?
├── "flood" / "burst pipe" / "water everywhere" → YES, water emergency
├── "gas smell" / "gas leak" → YES, call 911 first, then manager
├── "no heat" + month is Oct–Apr → YES, HVAC emergency
├── "sparks" / "electrical burning" → YES, electrical emergency
└── else → Standard triage workflow
```

## Visual Analysis Cues (Photo/Video)

When analyzing attachment images:

- Visible water on floor/ceiling → water damage
- Blackened outlets or burn marks → electrical damage
- Appliance with visible damage, no power → appliance
- Missing/damaged shingles, wet insulation → roof
- Pooled water near foundation → Improper Surface Grading
- General wear, broken fixtures → maintenance

## Classification Priority

When multiple issues are present, classify by highest severity:

1. Emergency (any) — override all else
2. water damage
3. electrical damage
4. HVAC
5. appliance / roof
6. maintenance / Improper Surface Grading
