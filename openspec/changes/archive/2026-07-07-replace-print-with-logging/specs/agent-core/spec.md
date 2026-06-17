## ADDED Requirements

### Requirement: Agent progress logging

When no step callback is registered, the agent SHALL emit step progress (`thinking`, tool names) through the operational logger at INFO level instead of `print`.

#### Scenario: Headless agent run logs steps

- **WHEN** `Agent.run` executes without `on_step`
- **THEN** each step summary is logged at INFO under the agent module logger

#### Scenario: Interactive run avoids duplicate logs

- **WHEN** `Agent.run` executes with `on_step` provided
- **THEN** step summaries are not also logged at INFO by the agent
