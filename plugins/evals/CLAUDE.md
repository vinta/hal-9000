# CLAUDE.md

Eval suites for this repo's plugins, run by `claude plugin eval`. Each case is a directory under `<plugin>/<skill>/`.

## Running

- Run suites from the repo root with this command, adding `--case <glob>` and `--runs <n>` to narrow it; a bare run does every case three times in both arms. Every run, including the old arm of an A/B run, keeps the Sonnet judge, and `--threshold 0` keeps gradient graders from failing the exit code:

  ```bash
  claude plugin eval . --eval-dir plugins/evals --judge-model sonnet --scaffold --allow-tools WebSearch WebFetch Edit --no-publish -j 4 --threshold 0
  ```
- `--case` takes one glob without braces, so give cases you run together a shared name prefix.
- To A/B a skill change, run the committed text as the old arm: `git archive HEAD skills | tar -x -C <dir>`, copy the case directories to the same path under `<dir>`, and run the same command from `<dir>` with `--trust-plugin`.
- Read each grader across the with and without arms, not the case score.

## Writing cases

- A prompt that names the skill under test makes the without-plugin arm measure the prompt, since that arm cannot load the skill. A case read across arms leaves the name out and checks the trigger with a `skill-fired` grader.
- A grader's expected verdict follows from the fixture alone. A verdict justified only by evidence the agent under test cannot see, such as another suite's results, fails in both arms and measures nothing.
- Plant fixture rules without gaps and that no editor would correct: every arm fills a gap with invented handling and corrects a rule that looks wrong, which hides the behaviour under test.
- An `llm` grader states its target by meaning and names the equivalent forms that pass, never only a literal sentence. Before trusting a new one, judge a real reply and an edited control whose verdict you know.
- A case's `description` carries the flags it needs, what each grader means, and, once measured, its baseline with run count and judge model.
