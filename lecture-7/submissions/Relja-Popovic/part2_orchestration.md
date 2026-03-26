# Part 2.1 – Orchestrated Design

## The Orchestrator

The orchestrator is a dedicated **PipelineOrchestrator** component. It is the only component that knows the full sequence of steps. All other components are passive services with no knowledge of each other.

## Sequence of Calls

1. Call **Validator** - on failure, return error to client immediately
2. Call **Extractor** - on failure, retry up to 3 times, then mark job failed
3. Call **Classifier** - on failure, retry once, then continue with `type = "unknown"`
4. Call **Storage** - on failure, retry up to 3 times, then mark job failed
5. Call **Notifier** - fire-and-forget; failures logged but do not fail the job

The orchestrator persists a checkpoint after each step so a restart can resume from the last successful point.

## Advantage

Centralised visibility - the full job state and retry history live in one place, making failures easy to debug and new steps easy to add.

## Disadvantage

Single point of failure - if the orchestrator goes down the entire pipeline stalls, regardless of whether the individual components are healthy.