# Claude Code Output Styles

Output styles for Claude Code. Both keep Claude Code's built-in coding instructions and only change how Claude writes.

- [**Say no more**](output-styles/say-no-more.md): telegraphic responses, as if every word cost money. All technical substance stays; only fluff dies. Inspired by [caveman](https://github.com/JuliusBrussee/caveman).
- [**ASD-STE100**](output-styles/asd-ste100.md): responses in [ASD-STE100](https://www.asd-ste100.org/) Simplified Technical English.

## Installation

```bash
claude plugin marketplace add vinta/hal-9000
claude plugin install hal-output-styles@hal-9000
```

## Usage

Plugin output styles are namespaced by plugin name. Pick one in `/config` under **Output style**, or set it in a settings file:

```json
{
  "outputStyle": "hal-output-styles:Say no more"
}
```

```json
{
  "outputStyle": "hal-output-styles:ASD-STE100"
}
```

Restart Claude Code after installing so the styles show up in `/config`.
