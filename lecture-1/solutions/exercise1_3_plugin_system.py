from __future__ import annotations
import abc
from typing import List, Protocol


class FormatterPlugin(abc.ABC):
    @abc.abstractmethod
    def format(self, text: str) -> str:
        pass


class AnalyzerPlugin(abc.ABC):
    @abc.abstractmethod
    def analyze(self, text: str) -> dict:
        pass


class TransformerPlugin(abc.ABC):
    @abc.abstractmethod
    def transform(self, text: str) -> str:
        pass


class PlainTextFormatter(FormatterPlugin):
    def format(self, text: str) -> str:
        return text.strip()


class MarkdownFormatter(FormatterPlugin):
    def format(self, text: str) -> str:
        # naive: wrap paragraphs
        return "\n\n".join(p.strip() for p in text.split("\n\n"))


class WordCountAnalyzer(AnalyzerPlugin):
    def analyze(self, text: str) -> dict:
        words = [w for w in text.split() if w]
        return {"word_count": len(words)}


class ReadabilityAnalyzer(AnalyzerPlugin):
    def analyze(self, text: str) -> dict:
        sentences = [s for s in text.split('.') if s.strip()]
        words = [w for w in text.split() if w]
        avg_words_per_sentence = len(words) / max(1, len(sentences))
        return {"avg_words_per_sentence": avg_words_per_sentence}


class UppercaseTransformer(TransformerPlugin):
    def transform(self, text: str) -> str:
        return text.upper()


class CaesarCipherTransformer(TransformerPlugin):
    def __init__(self, shift: int = 3):
        self.shift = shift

    def transform(self, text: str) -> str:
        def shift_char(c: str) -> str:
            if 'a' <= c <= 'z':
                return chr((ord(c) - ord('a') + self.shift) % 26 + ord('a'))
            if 'A' <= c <= 'Z':
                return chr((ord(c) - ord('A') + self.shift) % 26 + ord('A'))
            return c
        return ''.join(shift_char(c) for c in text)


class TextProcessor:
    def __init__(self, formatters: List[FormatterPlugin] | None = None,
                 analyzers: List[AnalyzerPlugin] | None = None,
                 transformers: List[TransformerPlugin] | None = None):
        self.formatters = formatters or []
        self.analyzers = analyzers or []
        self.transformers = transformers or []

    def process(self, text: str) -> dict:
        # Formatting stage
        for f in self.formatters:
            text = f.format(text)

        # Transformation stage
        for t in self.transformers:
            text = t.transform(text)

        # Analysis stage (collect results)
        results = {}
        for a in self.analyzers:
            results.update(a.analyze(text))

        return {"text": text, "analysis": results}


def _demo():
    text = "Hello world. This is a sample document."

    processor = TextProcessor(
        formatters=[PlainTextFormatter()],
        analyzers=[WordCountAnalyzer(), ReadabilityAnalyzer()],
        transformers=[UppercaseTransformer()]
    )

    out = processor.process(text)
    assert out["analysis"]["word_count"] == 7

    # Show plugin extensibility: add Caesar cipher transformer
    processor2 = TextProcessor(
        formatters=[PlainTextFormatter()],
        analyzers=[WordCountAnalyzer()],
        transformers=[CaesarCipherTransformer(1)]
    )
    out2 = processor2.process("abc XYZ")
    assert out2["text"].startswith("bcd")


if __name__ == "__main__":
    _demo()
    print("Exercise 1.3 demo passed")
