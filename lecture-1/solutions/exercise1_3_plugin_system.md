# Exercise 1.3 — Plugin System for Text Processing

Summary
- Built a small plugin framework with three plugin types:
  - `FormatterPlugin` — normalizes/structures text
  - `TransformerPlugin` — transforms text (translate, encrypt, etc.)
  - `AnalyzerPlugin` — computes metrics about text

Implemented plugins
- Formatters: `PlainTextFormatter`, `MarkdownFormatter`
- Transformers: `UppercaseTransformer`, `CaesarCipherTransformer`
- Analyzers: `WordCountAnalyzer`, `ReadabilityAnalyzer`

Design notes
- `TextProcessor` composes any combination of plugins. New plugins implement the appropriate abstract base class and can be added without modifying existing code.
- Plugins are executed in stages: formatting -> transformation -> analysis. This keeps responsibilities clear.

Extension
- To add a new plugin, create a class implementing the required interface and pass it to `TextProcessor`.

Usage
- Run: `python solutions/exercise1_3_plugin_system.py`

Architecture diagram (ASCII):

  [Input Text] -> [Formatter Plugins]* -> [Transformer Plugins]* -> [Analyzer Plugins]* -> [Results]
