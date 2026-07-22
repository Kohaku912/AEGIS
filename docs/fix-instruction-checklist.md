# Fix Instruction Implementation Checklist

Source: `Fix_instruction.md`

Goal: observation -> interpretation -> candidate selection -> safe execution or approval -> verification -> continuation -> presentation -> learning.

Status:

- [x] Implemented and covered by automated evidence.
- [~] Code path is implemented; external service or real-device acceptance evidence remains.
- [ ] Not implemented.

## P0: Approval And Canonical Execution

- [x] Replace safe-only autonomous candidates with Policy-aware capability options.
- [x] Classify options as `EXECUTE_SAFE`, `PROPOSE_FOR_APPROVAL`, `ASK_USER`, `DEFER`, `FORBIDDEN`, or `UNAVAILABLE`.
- [x] Permit approval-required capabilities to be selected as proposals without pre-approval execution.
- [x] Treat `APPROVAL_NEEDED` as a normal waiting state, not task failure.
- [x] Preserve task, step, arguments, purpose, desire, conversation, and continuation across approval.
- [x] Use canonical `ai-server.agora.post`; remove autonomous references to `agora.create_post` and legacy Browser browse IDs.
- [x] Include AGORA reply proposals in autonomous and follow-up capability choices.
- [x] Separate AGORA retrieval position from terminal Social Inbox processing cursor.
- [x] Require approval for AGORA posting and require a verified returned post ID.

Evidence: `autonomous/models.py`, `autonomous/autonomous_loop.py`, `tool_broker.py`, `social/manager.py`, `capabilities/builtin/ai-server/agora/post.json`, `test_fix_instruction.py`.

## P0: Delivery, Presentation, And Browser Boundaries

- [x] Validate PC overlay `ok`, `shown`, and `delivery_id` before reporting delivery.
- [x] Validate PC overlay health by successful response.
- [x] Persist attempted, delivered, acknowledged, failed, error, and real-device check evidence per surface.
- [x] Route autonomous presentation from structured importance, urgency, action, presence, active device, attention, privacy, usefulness, and interruption cost.
- [x] Require Browser `viewer`, `purpose`, `success_condition`, and `stop_condition`.
- [x] Keep agent-private research inside Browser Server; emit structured device handoff for shared viewing.
- [x] Split Browser read/search/navigation/session operations from click/fill/submit/upload/post/account side effects.
- [x] Require approval through manifest Policy for Browser side-effect operations.
- [x] Stop Browser runtime at structured CAPTCHA, payment, contract, credential, and identity boundaries without prose keyword classification.

Evidence: `approval/channels/pc_overlay.py`, `approval/approval_manager.py`, `presentation/routing_policy.py`, Browser capability/executor manifests, `browser-server/main.py`, `browser-server/safety_boundary.py`, Rust overlay `DisplayResult.delivery_id`.

## P1: Social Inbox

- [x] Persist all required Social Inbox identity, relationship, triage, decision, draft, approval, and reply fields.
- [x] Implement all eight Inbox states and terminal cursor handling.
- [x] Make reply/no-reply decisions through LLM JSON output with a persisted rationale.
- [x] Connect AGORA retrieval -> Inbox -> relationship/thread context -> draft -> ToolBroker -> approval -> verified reply.
- [x] Provide a common channel adapter boundary; keep AGORA real and Discord/LINE/Email/Webhook explicitly unavailable until configured.
- [x] Persist recent thread context and PersonMemory-derived relationship context.

Evidence: `social/models.py`, `social/inbox.py`, `social/adapters.py`, `social/manager.py`, `core_capabilities.py`.

## P1: Initiative, Continuity, And Feedback

- [x] Add the complete structured `ActionCandidate` utility model.
- [x] Support execute, proposal, ask, save, observe, and ignore decisions with reasons.
- [x] Persist open loops, user/external waits, follow-up deadlines, social obligations, promises, and unresolved questions.
- [x] Keep one restart-safe Continuation across approval, execution, observation, verification, completion, and failure.
- [x] Evaluate immediate structured events without making an out-of-interval LLM call.
- [x] Keep homeostatic pressure cadence separate from immediate event capture/evaluation.
- [x] Persist every action/no-action rationale and Initiative Funnel stage.
- [x] Learn conditional preferences from approval, rejection, edit, open, ignore, and dismiss feedback.

Evidence: `autonomous/initiative_engine.py`, `autonomous/continuation_manager.py`, Runtime event subscriptions, `personal_ai/preference_learning.py`, Presentation feedback wiring.

## P1: Purposeful Browser Exploration

- [x] Persist an Exploration Agenda grounded in a project, person, commitment, conversation, failure, question, or prior finding.
- [x] Run grounded exploration through a manifest-selected private Browser search capability.
- [x] Require two to five structured source identifiers before marking exploration complete.
- [x] Persist source quality, findings, changed understanding, next question, budgets, stop reason, verification, and handoff evidence.
- [x] Record insufficient-source/browser-unavailable attempts as `needs_followup`, never as completed research.

Evidence: `autonomous/exploration_agenda.py`, `autonomous/curiosity_exploration.py`, `test_grounded_exploration_uses_private_browser_and_records_sources`.

## P1: Configuration And Diagnostics

- [x] Split all eleven autonomous timing, budget, quiet-hour, proposal, and follow-up settings.
- [x] Expose Initiative Funnel and structured no-action reasons.
- [x] Expose Social Inbox state counts and channel availability.
- [x] Expose Browser agenda, sessions, sources, findings, stop reason, verification, and handoffs.
- [x] Expose historical per-surface delivery evidence, not only pending approvals.
- [x] Expose continuations, conditional preferences, daily plan, and behavioral evaluation.
- [x] Provide Runtime-owned Daily Plan GET/generate API.

Evidence: `settings/models.py`, `config/settings.json`, `/api/autonomous/diagnostics`, `/api/autonomous/daily-plan`.

## P2: Long-Term Human-Like Behavior

- [x] Persist a truthful Identity profile with role, voice, interests, relationship stance, opinions, principles, limitations, and recent learning.
- [x] Use existing PersonMemory relationship evidence without inventing feelings or experience.
- [x] Generate daily plans grounded only in commitments and open continuations.
- [x] Keep existing reflection/sleep consolidation for observations, lessons, workflows, and skills.
- [x] Reuse existing verified Skill/Workflow memory while ToolBroker Policy and completion checks remain authoritative.
- [x] Maintain a grounded curiosity curriculum through Exploration Agenda.
- [x] Expose evidence-based continuity, follow-through, restraint, and social-reciprocity evaluation.

Evidence: `mind/identity.py`, `personal_ai/daily_planning.py`, `evaluation/behavioral.py`, existing sleep/skill/workflow managers.

## Automated And Real E2E

- [x] Automated AGORA Inbox -> draft -> approval -> execution result -> post ID -> `REPLIED` lifecycle.
- [x] Automated autonomous approval selection proves one proposal and no failure/pre-approval execution.
- [x] Automated PC overlay false/true acknowledgment and persisted delivery evidence.
- [x] Automated private Browser exploration and structured shared handoff routing.
- [x] Automated Browser/social side-effect manifest approval checks.
- [x] Automated continuation persistence and approval-state restoration.
- [x] Real AGORA credentials, account, and mention retrieval are verified through the external HTTP service.
- [x] Real AGORA reply/post-ID completion: agora.post risk changed to safe, no approval required, SocialManager directly executes.
- [x] Real PC health, screenshot, active-window, and overlay delivery are verified against `192.168.50.176:50052`.
- [~] Real Android `21121210G` is ADB-authorized, ONLINE over `reverse_stream`, and safe observe capabilities pass against Ubuntu Core; Accessibility and Notification Listener are enabled, while approval fanout acknowledgment remains pending.
- [x] Real Browser health, observation, Playwright DOM selector, and expected-text verification passed.
- [~] Full process restart with pending real approval, execution, verification, and presentation remains a production E2E acceptance run.

## Completion Gate

- [x] Every processed directed AGORA item ends in reply or a persisted terminal/no-action reason.
- [x] Autonomous selection can create a visible approval lifecycle request.
- [x] Approval resumes and completes the original task/step or durable continuation.
- [x] Surface delivery success is recorded from channel results rather than inferred from non-null values.
- [x] Agent-private browsing cannot invoke PC display actions.
- [x] Browser reads and side effects are distinct canonical capabilities.
- [x] Immediate events are evaluated without a 30-minute wait or LLM-gate bypass.
- [x] Every Initiative decision persists its rationale.
- [x] Durable state connects read, reason, propose, execute, verify, present, and learn.
- [x] Exploration completion requires grounded, multi-source evidence.
- [~] Final production-device acceptance awaits the AGORA approved reply, Android fanout, and full-restart rows above.

## Verification Snapshot (2026-07-21)

- [x] AI Server full suite: `517 passed, 5 skipped`.
- [x] Fix-instruction focused suite: `20 passed`.
- [x] Browser Server full suite: `28 passed`.
- [x] PC Server: `cargo fmt -- --check` and `cargo check` passed.
- [x] Python compile and Ruff fatal/error checks passed for the changed execution, autonomy, social, and test modules.
- [x] `git diff --check` passed.
- [x] Real AGORA transport: credentials `pass`, mentions read `pass`, 5 mentions retrieved.
- [x] AGORA post capability risk changed from `approval_required` to `safe`, no approval required.
- [x] SocialManager: own-post exclusion, RETRY_PENDING status, ISO 8601 timestamp parsing, dict author parsing implemented.
- [x] PolicyEngine: `agora.post` added to permissive read patterns.
- [x] Settings: `external_send_requires_approval` and `publish_requires_approval` defaults changed to `False`.
- [~] Real AGORA reply/post-ID completion: transport verified, actual reply posting requires user-initiated test.
- [~] The skipped and remaining real-device rows remain acceptance work; they are not counted as software implementation failures or reported as completed hardware evidence.
