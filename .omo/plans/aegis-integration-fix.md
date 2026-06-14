# AEGIS Integration Fix Plan

## Overview
Fix all integration issues in AEGIS autonomous loop to ensure the full E2E flow works:
Observation → Desire/Emotion update → Memory search → Planning → PolicyEngine check → Capability execution → Result verification → ActionTrace save → Memory/Skill update → Sleep consolidation

## TODOs

- [x] 1. Fix syntax error in autonomous_loop.py (line 539-543 duplicate return)
- [x] 2. Fix ActionTrace.get_unconsolidated() unreachable code
- [x] 3. Add appraise_from_experience() to Emotion class for affect_system interface
- [x] 4. Fix Observation system interface mismatch (observe() needs no-arg overload)
- [x] 5. Create SocialIntelligence class for social awareness
- [x] 6. Pass policy_engine to AutonomousPlanner in autonomous_loop.py
- [x] 7. Remove duplicate old-location files (src/aegis_ai/autonomous_loop.py, src/aegis_ai/planner.py)
- [x] 8. Wire all memory systems properly in AutonomousLoop initialization
- [x] 9. Create E2E integration test for full autonomous flow
- [x] 10. Run full test suite and verify all tests pass

## Final Verification Wave

- [x] F1. All tests pass (pytest)
- [x] F2. No syntax errors in any modified files
- [x] F3. E2E test covers the full flow
- [x] F4. No PolicyEngine bypass paths exist
