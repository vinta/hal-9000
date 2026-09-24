# Codex skill guidance

Reuse current guidance already fetched in the conversation; fetch missing guidance needed for the audit:

- For skill refactoring criteria: https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra
- For `gpt-6-astra` behavior: https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra#prompting-best-practices

Apply these checks within the requested scope:

- **Triggers:** Keep descriptions short and specific to the workflow. Check overlap or conflicts with other available skill descriptions; broad topic matches and repeated emphasis can load irrelevant skills, and long descriptions may be shortened.
- **Progressive disclosure:** For multiple workflows, keep the root a minimal router with explicit conditions for reading supporting files. Match required reading to the task.
- **Workflow:** Preserve constraints and completion criteria while removing prescribed steps, ordering, or review stops that do not serve correctness or an explicit user boundary. Continue authorized work through verification.
- **Model audience:** Judge defaults against the models that consume the skill. Preserve guidance needed by other supported models rather than assuming Astra's defaults apply to all of them.
