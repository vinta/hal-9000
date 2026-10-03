export type GrammarCheck = { status: 'checking' | 'done' | 'submitted'; lines: string[] }

declare module 'claude-code' {
  interface PluginState {
    'hal-grammar-check': { check: GrammarCheck | null }
  }
}
