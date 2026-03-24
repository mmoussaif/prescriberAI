# Product Brief: AI-Powered Practice Onboarding

We will replace our manual onboarding process with an AI-guided self-serve experience, reducing practice activation from 2–3 CS calls to a single sub-20-minute session for 80% of incoming practices. This is the single highest-leverage investment available right now. PrescriberPoint serves 500K+ HCPs monthly across drug lookup, prior authorization, sample ordering, and coverage tools—but every new practice still requires a CS rep to walk them through configuration manually. That model breaks at scale. If we double practice acquisition, we must either double CS headcount or break the linear relationship between new signups and onboarding labor. AI breaks that relationship.

## 1. The Onboarding Experience from the Practice’s Perspective

The experience is a single, continuous AI-guided conversation that takes a practice from first login to completing a real workflow on the platform. The practice admin never navigates a settings page or waits for a CS callback. The AI drives the sequence, asks questions in clinical language, pre-fills answers where possible, and escalates to a human only when confidence is low.

### Phase 1: Identity & Context (2 min)

The AI requests the practice NPI number to pull name, address, taxonomy, and provider rosters from the NPPES registry for confirmation. This replaces intake forms and immediately demonstrates system competence.

### Phase 2: Configuration (4 min)

The AI configures the account based on specialty. It pre-selects relevant drug categories, PA rules, sample preferences, and coverage tool defaults. It asks targeted questions only when specialty is ambiguous, such as whether the practice sees patients under 18, and explains each default setting.

### Phase 3: Data Import (3 min)

The AI parses medication lists from CSVs, spreadsheets, or photos. It maps medications to our 35K+ drug database for review. If no data exists, the AI seeds the account with specialty-appropriate defaults.

### Phase 4: Guided First Workflow (5 min)

The AI walks the practice through a real task, such as a sample PA submission, using a simulated patient. This step converts setup into active usage.

### Phase 5: Handoff (1 min)

The AI summarizes the configuration, provides dashboard links, and offers continued AI support or a scheduled 15-minute call with a specialist. The AI persists as an in-app assistant to create continuity.

### Human intervention

CS reps will handle multi-location setups, non-standard EMR integrations, and low-confidence data imports. The AI never guesses when stakes are high. It surfaces uncertainty, explains the gap, and hands off with full context to the human representative.

## 2. The Three Hardest Problems

### Earning trust in the first 30 seconds

We demonstrate competence through action. The NPI lookup serves as the primary trust signal. When the AI correctly identifies the practice, the admin gains confidence in the system. Every subsequent action follows a pattern: act, show work, and confirm. The AI uses clinical language such as “prior authorization” instead of “approval workflow” to establish domain fluency.

### Handling complex practice configurations

The AI will not attempt to solve every edge case. It tracks its own assumption count and escalates when thresholds are met. This escalation uses a quality-assurance framing. Every hand-off feeds a learning loop where CS tags missing data to train future iterations and systematically shrink the long tail of manual work.

### Measuring success through activation

We define success as a practice completing a real workflow within 48 hours of setup. We will instrument the funnel from onboarding start through the first real PA or sample order. We will track configuration accuracy by comparing AI settings against actual practice needs.

### Current prototype (demo)

The current engineering prototype validates Phase 1 and 2 mechanics, including NPI lookup, conversational configuration, and escalation paths, within a demo environment. This prototype de-risks the agent and UX patterns before the two-week ship plan. This plan represents the minimum viable scope for extracting live learning from real practices.

## 3. What We Ship in the First Two Weeks

We ship Phase 1 and Phase 2 only: NPI-powered identity and AI-guided configuration for single-specialty, single-location practices. No data import. No guided first workflow. No multi-location support.

This scope is optimal for three reasons. First, it tests the core hypothesis that an AI agent can correctly configure an account through conversation without a human in the loop. If the AI cannot reliably set up a family medicine practice, downstream features are irrelevant. Second, it provides immediate measurement. We will deploy alongside the manual process and compare AI output to CS rep actions to get a live accuracy signal. Third, it utilizes existing infrastructure. The NPI registry is a public API, and the conversation runs on our established AI framework.

### Strategic scope

NPI lookup alone is insufficient to replace a CS workflow. Configuration is where the AI makes critical decisions regarding drug categories and PA rules. We have excluded data import and guided workflows from the initial two-week launch to avoid untested infrastructure pipelines and maintain focus on core decision-making logic.
