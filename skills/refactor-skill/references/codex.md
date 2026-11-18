# Codex skill guidance

Reuse current guidance already fetched in the conversation; fetch missing guidance needed for the audit:

- Read the selected GPT model's prompting best practices. For `astra`, use the current Astra model in [OpenAI's latest-model guide](https://developers.openai.com/api/docs/guides/latest-model.md).
- Find and read current OpenAI guidance on refactoring skills and prompts that applies to the selected model.

Apply these checks within the requested scope:

- **Triggers:** Keep descriptions short and specific to the workflow. Check overlap or conflicts with other available skill descriptions; broad topic matches and repeated emphasis can load irrelevant skills, and long descriptions may be shortened.
- **Progressive disclosure:** For multiple workflows, keep the root a minimal router with explicit conditions for reading supporting files. Match required reading to the task.
- **Workflow:** Preserve constraints and completion criteria while removing prescribed steps, ordering, or review stops that do not serve correctness or an explicit user boundary. Continue authorized work through verification.
- **Model audience:** Judge defaults against each model that uses the skill. Keep guidance any supported model still needs.
