## MODIFIED Requirements

### Requirement: Running phase indicator

The TUI SHALL track and expose the current run phase: `idle`, `running`, or `awaiting_approval`. Internally, the phase SHALL be represented by a `RunPhase` enumeration whose values match these strings for footer and `/status` display.

#### Scenario: Phase during tool execution

- **WHEN** the agent is executing tools for a user task
- **THEN** the run phase is `running` until the final assistant reply is shown

#### Scenario: Phase during approval

- **WHEN** the agent waits for user approval of a confirm-tier operation
- **THEN** the run phase is `awaiting_approval`

#### Scenario: Phase returns to idle after task

- **WHEN** an agent task completes or fails with an error shown in the conversation
- **THEN** the run phase is `idle`
