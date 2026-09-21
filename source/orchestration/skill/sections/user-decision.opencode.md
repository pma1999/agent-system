In delegated-by-build mode, every required user interaction returns:

```text
STATUS: NEEDS_USER_DECISION
QUESTION: <exact decision or required action, why it blocks progress; never request secret values>
OPTIONS: <concrete options, or the secure setup action when a choice does not apply>
RECOMMENDATION: <one option/action and why>
BUNDLE: <path or None>
RESUME: Resume this orquestador task_id with the user's exact answer or setup confirmation;
verify the stated prerequisite without exposing secrets before continuing dependent work.
```
