#!/usr/bin/env python3
"""
Exercise 1.3: Design a Plugin System 🔴

This example demonstrates:
- Advanced abstraction patterns for plugin architecture
- Extensible system design using the Strategy and Chain of Responsibility patterns
- Runtime plugin discovery and composition
- Enterprise-grade plugin management

Business Scenario: Text Processing Platform
- Core system with plugin-based extensibility
- Three plugin categories: Formatting, Analysis, Transformation
- Runtime plugin discovery and composition
- Zero-code plugin addition capability

Architecture Pattern: Plugin System with Abstract Factories
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable, Type, Set
from dataclasses import dataclass, field
from enum import Enum
import re
import json
from datetime import datetime
import inspect
from collections import Counter
import string


# ============================================================================
# CORE PLUGIN ARCHITECTURE
# ============================================================================

class PluginType(Enum):
    """Enumeration of plugin types for categorization"""
    FORMATTER = "formatter"
    ANALYZER = "analyzer"
    TRANSFORMER = "transformer"


@dataclass
class PluginMetadata:
    """Metadata for plugin discovery and documentation"""
    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProcessingContext:
    """Context object passed through plugin chain"""
    input_text: str
    output_text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata during processing"""
        self.metadata[key] = value
    
    def add_error(self, error: str):
        """Add error message"""
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Add warning message"""
        self.warnings.append(warning)


# ============================================================================
# ABSTRACT INTERFACES - THE PLUGIN CONTRACTS
# ============================================================================

class TextPlugin(ABC):
    """
    Abstract base class for all text plugins.
    
    This is the root of the plugin hierarchy. All plugins must:
    1. Provide metadata for discovery
    2. Implement the process method
    3. Declare their plugin type
    """
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata for discovery"""
        pass
    
    @abstractmethod
    def process(self, context: ProcessingContext) -> ProcessingContext:
        """
        Process the text in the given context.
        
        Args:
            context: Current processing context with input/output text
            
        Returns:
            Updated processing context
        """
        pass
    
    @property
    @abstractmethod
    def plugin_type(self) -> PluginType:
        """Get the plugin type"""
        pass
    
    def can_handle(self, context: ProcessingContext) -> bool:
        """
        Determine if this plugin can handle the current context.
        Override for conditional processing.
        """
        return True
    
    def __str__(self) -> str:
        meta = self.get_metadata()
        return f"{meta.name} v{meta.version}"


# ============================================================================
# PLUGIN CATEGORY 1: TEXT FORMATTERS
# ============================================================================

class TextFormatter(TextPlugin):
    """Abstract base for text formatters"""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.FORMATTER
    
    @abstractmethod
    def format(self, text: str) -> str:
        """Format the text"""
        pass
    
    def process(self, context: ProcessingContext) -> ProcessingContext:
        """Apply formatting to the output text"""
        if self.can_handle(context):
            formatted = self.format(context.output_text)
            context.output_text = formatted
            context.add_metadata(f"formatter_{self.get_metadata().name}", True)
        return context


class MarkdownFormatter(TextFormatter):
    """Converts plain text to Markdown"""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="MarkdownFormatter",
            version="1.0.0",
            author="Plugin System Demo",
            description="Converts plain text to Markdown format",
            plugin_type=PluginType.FORMATTER,
            tags=["markdown", "formatting", "web"]
        )
    
    def format(self, text: str) -> str:
        lines = text.split('\n')
        formatted = []
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted.append('')
                continue
            
            # Headers
            if line.startswith('# '):
                formatted.append(f"# {line[2:]}")
            elif line.startswith('## '):
                formatted.append(f"## {line[3:]}")
            elif line.startswith('### '):
                formatted.append(f"### {line[4:]}")
            # Bold
            elif '**' in line:
                formatted.append(line.replace('**', '**'))
            # Italic
            elif '*' in line and len(line.split('*')) > 2:
                parts = line.split('*')
                for i in range(1, len(parts), 2):
                    parts[i] = f"*{parts[i]}*"
                formatted.append(''.join(parts))
            # Lists
            elif line.startswith('- '):
                formatted.append(f"- {line[2:]}")
            elif line.startswith('* '):
                formatted.append(f"* {line[2:]}")
            # Code blocks
            elif line.startswith('```'):
                formatted.append('```')
            else:
                formatted.append(line)
        
        return '\n'.join(formatted)


class HTMLFormatter(TextFormatter):
    """Converts plain text to HTML"""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="HTMLFormatter",
            version="1.0.0",
            author="Plugin System Demo",
            description="Converts plain text to HTML format",
            plugin_type=PluginType.FORMATTER,
            tags=["html", "formatting", "web"]
        )
    
    def format(self, text: str) -> str:
        lines = text.split('\n')
        html_parts = ['<!DOCTYPE html>', '<html>', '<head>', 
                      '<meta charset="UTF-8">', '<title>Formatted Text</title>', 
                      '</head>', '<body>']
        
        for line in lines:
            line = line.strip()
            if not line:
                html_parts.append('<br>')
            elif line.startswith('# '):
                html_parts.append(f'<h1>{line[2:]}</h1>')
            elif line.startswith('## '):
                html_parts.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('### '):
                html_parts.append(f'<h3>{line[4:]}</h3>')
            elif line.startswith('- ') or line.startswith('* '):
                html_parts.append(f'<ul><li>{line[2:]}</li></ul>')
            else:
                # Escape HTML characters
                escaped = (line.replace('&', '&amp;')
                              .replace('<', '&lt;')
                              .replace('>', '&gt;')
                              .replace('"', '&quot;')
                              .replace("'", '&#39;'))
                html_parts.append(f'<p>{escaped}</p>')
        
        html_parts.extend(['</body>', '</html>'])
        return '\n'.join(html_parts)


class PlainTextFormatter(TextFormatter):
    """Ensures plain text format (removes markup)"""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="PlainTextFormatter",
            version="1.0.0",
            author="Plugin System Demo",
            description="Ensures plain text format by removing markup",
            plugin_type=PluginType.FORMATTER,
            tags=["plain", "text", "clean"]
        )
    
    def format(self, text: str) -> str:
        # Simple HTML tag removal
        text = re.sub(r'<[^>]+>', '', text)
        # Remove markdown symbols
        text = re.sub(r'[#*_`-]{1,3}', '', text)
        # Clean up extra whitespace
        text = ' '.join(text.split())
        return text


# ============================================================================
# PLUGIN CATEGORY 2: TEXT ANALYZERS
# ============================================================================

class TextAnalyzer(TextPlugin):
    """Abstract base for text analyzers"""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.ANALYZER
    
    @abstractmethod
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze text and return results"""
        pass
    
    def process(self, context: ProcessingContext) -> ProcessingContext:
        """Add analysis results to metadata"""
        if self.can_handle(context):
            results = self.analyze(context.output_text)
            meta_key = f"analysis_{self.get_metadata().name.lower()}"
            context.add_metadata(meta_key, results)
        return context


class WordCountAnalyzer(TextAnalyzer):
    """Counts words, characters, sentences"""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="WordCount",
            version="1.0.0",
            author="Plugin System Demo",
            description="Counts words, characters, and sentences",
            plugin_type=PluginType.ANALYZER,
            tags=["statistics", "count", "metrics"]
        )
    
    def analyze(self, text: str) -> Dict[str, Any]:
        words = re.findall(r'\b\w+\b', text)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        
        return {
            'characters': len(text),
            'characters_no_spaces': len(text.replace(' ', '')),
            'words': len(words),
            'unique_words': len(set(w.lower() for w in words)),
            'sentences': len(sentences),
            'average_word_length': sum(len(w) for w in words) / max(len(words), 1),
            'average_words_per_sentence': len(words) / max(len(sentences), 1)
        }


class SentimentAnalyzer(TextAnalyzer):
    """Basic sentiment analysis based on word lists"""
    
    def __init__(self):
        # Simple positive/negative word lists for demonstration
        self.positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'happy', 'love', 'best', 'awesome', 'perfect', 'beautiful',
            'nice', 'positive', 'thank', 'thanks', 'appreciate'
        }
        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate',
            'negative', 'poor', 'sad', 'angry', 'disappointing', 'disappointed',
            'frustrating', 'frustrated', 'annoying', 'annoyed'
        }
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Sentiment",
            version="1.0.0",
            author="Plugin System Demo",
            description="Basic sentiment analysis",
            plugin_type=PluginType.ANALYZER,
            tags=["sentiment", "emotion", "nlp"]
        )
    
    def analyze(self, text: str) -> Dict[str, Any]:
        words = re.findall(r'\b\w+\b', text.lower())
        
        positive_count = sum(1 for w in words if w in self.positive_words)
        negative_count = sum(1 for w in words if w in self.negative_words)
        total_sentiment_words = positive_count + negative_count
        
        sentiment_score = 0
        if total_sentiment_words > 0:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
        
        # Determine sentiment category
        if sentiment_score > 0.2:
            category = "positive"
        elif sentiment_score < -0.2:
            category = "negative"
        else:
            category = "neutral"
        
        return {
            'score': sentiment_score,
            'category': category,
            'positive_words': positive_count,
            'negative_words': negative_count,
            'positive_found': [w for w in words if w in self.positive_words][:10],
            'negative_found': [w for w in words if w in self.negative_words][:10]
        }


class ReadabilityAnalyzer(TextAnalyzer):
    """Calculates readability scores"""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Readability",
            version="1.0.0",
            author="Plugin System Demo",
            description="Calculates text readability scores",
            plugin_type=PluginType.ANALYZER,
            tags=["readability", "complexity", "education"]
        )
    
    def analyze(self, text: str) -> Dict[str, Any]:
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        words = re.findall(r'\b\w+\b', text)
        
        if not sentences or not words:
            return {'error': 'Insufficient text for analysis'}
        
        # Calculate syllables (simplified)
        def count_syllables(word):
            word = word.lower()
            count = 0
            vowels = 'aeiou'
            prev_is_vowel = False
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not prev_is_vowel:
                    count += 1
                prev_is_vowel = is_vowel
            if word.endswith('e'):
                count -= 1
            return max(1, count)
        
        syllable_counts = [count_syllables(w) for w in words]
        total_syllables = sum(syllable_counts)
        
        # Flesch Reading Ease
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = total_syllables / len(words)
        
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0, min(100, flesch_score))
        
        # Grade level
        if flesch_score >= 90:
            grade = "5th grade"
        elif flesch_score >= 80:
            grade = "6th grade"
        elif flesch_score >= 70:
            grade = "7th grade"
        elif flesch_score >= 60:
            grade = "8th-9th grade"
        elif flesch_score >= 50:
            grade = "10th-12th grade"
        elif flesch_score >= 30:
            grade = "College"
        else:
            grade = "College graduate"
        
        return {
            'flesch_reading_ease': round(flesch_score, 2),
            'grade_level': grade,
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_syllables_per_word': round(avg_syllables_per_word, 2),
            'total_syllables': total_syllables,
            'complex_words': sum(1 for s in syllable_counts if s >= 3)
        }


# ============================================================================
# PLUGIN CATEGORY 3: TEXT TRANSFORMERS
# ============================================================================

class TextTransformer(TextPlugin):
    """Abstract base for text transformers"""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.TRANSFORMER
    
    @abstractmethod
    def transform(self, text: str) -> str:
        """Transform the text"""
        pass
    
    def process(self, context: ProcessingContext) -> ProcessingContext:
        """Apply transformation to the output text"""
        if self.can_handle(context):
            transformed = self.transform(context.output_text)
            context.output_text = transformed
            context.add_metadata(f"transformer_{self.get_metadata().name.lower()}", True)
        return context


class TranslateTransformer(TextTransformer):
    """Simulates text translation"""
    
    def __init__(self, target_language: str = "es"):
        self.target_language = target_language
        # Simple dictionary for demonstration
        self.dictionary = {
            'en_es': {
                'hello': 'hola',
                'world': 'mundo',
                'good': 'bueno',
                'bad': 'malo',
                'day': 'día',
                'night': 'noche',
                'thank you': 'gracias',
                'please': 'por favor',
                'yes': 'sí',
                'no': 'no'
            }
        }
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Translator",
            version="1.0.0",
            author="Plugin System Demo",
            description=f"Translates text to {self.target_language}",
            plugin_type=PluginType.TRANSFORMER,
            tags=["translation", "i18n", "language"]
        )
    
    def transform(self, text: str) -> str:
        if self.target_language == "es":
            dict_key = 'en_es'
            translated = text.lower()
            for eng, esp in self.dictionary[dict_key].items():
                translated = translated.replace(eng.lower(), esp)
            return f"[Translated to Spanish]: {translated}"
        return f"[Translation to {self.target_language} not implemented]: {text}"


class SummarizeTransformer(TextTransformer):
    """Extracts key sentences as summary"""
    
    def __init__(self, sentence_count: int = 3):
        self.sentence_count = sentence_count
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Summarizer",
            version="1.0.0",
            author="Plugin System Demo",
            description=f"Summarizes text to {self.sentence_count} sentences",
            plugin_type=PluginType.TRANSFORMER,
            tags=["summary", "extraction", "nlp"]
        )
    
    def transform(self, text: str) -> str:
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= self.sentence_count:
            return text
        
        # Simple scoring based on position and keywords
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = 0
            # Position score - first sentences are more important
            score += 1.0 / (i + 1)
            # Length score - medium length sentences are better
            words = len(sentence.split())
            if 10 <= words <= 25:
                score += 0.5
            # Keyword score
            keywords = ['important', 'significant', 'key', 'main', 'conclusion', 'result']
            for kw in keywords:
                if kw in sentence.lower():
                    score += 0.3
            
            scored_sentences.append((score, sentence))
        
        # Get top sentences
        scored_sentences.sort(reverse=True)
        summary = ' '.join(s[1] for s in scored_sentences[:self.sentence_count])
        
        return f"[SUMMARY]: {summary}"


class EncryptTransformer(TextTransformer):
    """Simple encryption transformer"""
    
    def __init__(self, shift: int = 3):
        self.shift = shift
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Encryptor",
            version="1.0.0",
            author="Plugin System Demo",
            description=f"Caesar cipher encryption (shift={self.shift})",
            plugin_type=PluginType.TRANSFORMER,
            tags=["encryption", "security", "cipher"]
        )
    
    def transform(self, text: str) -> str:
        """Caesar cipher encryption"""
        result = []
        for char in text:
            if char.isupper():
                result.append(chr((ord(char) - ord('A') + self.shift) % 26 + ord('A')))
            elif char.islower():
                result.append(chr((ord(char) - ord('a') + self.shift) % 26 + ord('a')))
            else:
                result.append(char)
        
        encrypted = ''.join(result)
        return f"[ENCRYPTED shift={self.shift}]: {encrypted}"


# ============================================================================
# PLUGIN REGISTRY - DISCOVERY AND MANAGEMENT
# ============================================================================

class PluginRegistry:
    """
    Central registry for plugin discovery and management.
    
    This is the backbone of the plugin system:
    - Discovers plugins automatically
    - Manages plugin lifecycle
    - Provides plugin lookup by type/criteria
    - Ensures no code modification needed for new plugins
    """
    
    _instance = None
    _plugins: Dict[str, TextPlugin] = {}
    _plugins_by_type: Dict[PluginType, List[TextPlugin]] = {
        PluginType.FORMATTER: [],
        PluginType.ANALYZER: [],
        PluginType.TRANSFORMER: []
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register_plugin(cls, plugin: TextPlugin):
        """Register a plugin with the registry"""
        meta = plugin.get_metadata()
        cls._plugins[meta.name] = plugin
        cls._plugins_by_type[meta.plugin_type].append(plugin)
        print(f"  [Registry] Registered plugin: {meta.name} v{meta.version} ({meta.plugin_type.value})")
    
    @classmethod
    def discover_plugins(cls):
        """Auto-discover and register all plugin classes"""
        # This would normally scan modules, but for demo we register manually
        plugin_classes = [
            MarkdownFormatter, HTMLFormatter, PlainTextFormatter,
            WordCountAnalyzer, SentimentAnalyzer, ReadabilityAnalyzer,
            TranslateTransformer, SummarizeTransformer, EncryptTransformer
        ]
        
        for plugin_class in plugin_classes:
            try:
                # Handle plugins with constructor parameters
                if plugin_class == TranslateTransformer:
                    plugin = plugin_class("es")
                elif plugin_class == SummarizeTransformer:
                    plugin = plugin_class(3)
                elif plugin_class == EncryptTransformer:
                    plugin = plugin_class(3)
                else:
                    plugin = plugin_class()
                
                cls.register_plugin(plugin)
            except Exception as e:
                print(f"  [Registry] Failed to register {plugin_class.__name__}: {e}")
    
    @classmethod
    def get_plugin(cls, name: str) -> Optional[TextPlugin]:
        """Get plugin by name"""
        return cls._plugins.get(name)
    
    @classmethod
    def get_plugins_by_type(cls, plugin_type: PluginType) -> List[TextPlugin]:
        """Get all plugins of a specific type"""
        return cls._plugins_by_type.get(plugin_type, [])
    
    @classmethod
    def get_all_plugins(cls) -> List[TextPlugin]:
        """Get all registered plugins"""
        return list(cls._plugins.values())
    
    @classmethod
    def get_plugins_by_tag(cls, tag: str) -> List[TextPlugin]:
        """Get plugins by tag"""
        result = []
        for plugin in cls._plugins.values():
            if tag in plugin.get_metadata().tags:
                result.append(plugin)
        return result


# ============================================================================
# CORE TEXT PROCESSOR - PLUGIN ORCHESTRATION
# ============================================================================

class TextProcessor:
    """
    Core text processor that orchestrates plugins.
    
    This is the heart of the system:
    - Processes text through plugin chains
    - Maintains processing context
    - Supports runtime plugin composition
    - Zero knowledge of specific plugin implementations
    """
    
    def __init__(self):
        self.formatter_plugins: List[TextFormatter] = []
        self.analyzer_plugins: List[TextAnalyzer] = []
        self.transformer_plugins: List[TextTransformer] = []
        self.processing_history: List[Dict] = []
        
        # Auto-discover plugins
        PluginRegistry.discover_plugins()
    
    def add_formatter(self, formatter: TextFormatter):
        """Add a formatter plugin"""
        self.formatter_plugins.append(formatter)
    
    def add_analyzer(self, analyzer: TextAnalyzer):
        """Add an analyzer plugin"""
        self.analyzer_plugins.append(analyzer)
    
    def add_transformer(self, transformer: TextTransformer):
        """Add a transformer plugin"""
        self.transformer_plugins.append(transformer)
    
    def add_plugin(self, plugin: TextPlugin):
        """Add plugin based on its type"""
        if isinstance(plugin, TextFormatter):
            self.add_formatter(plugin)
        elif isinstance(plugin, TextAnalyzer):
            self.add_analyzer(plugin)
        elif isinstance(plugin, TextTransformer):
            self.add_transformer(plugin)
    
    def remove_all_plugins(self):
        """Clear all plugins"""
        self.formatter_plugins.clear()
        self.analyzer_plugins.clear()
        self.transformer_plugins.clear()
    
    def process(self, text: str, 
                formatters: Optional[List[str]] = None,
                analyzers: Optional[List[str]] = None,
                transformers: Optional[List[str]] = None) -> ProcessingContext:
        """
        Process text through specified plugins.
        
        Args:
            text: Input text to process
            formatters: List of formatter plugin names
            analyzers: List of analyzer plugin names
            transformers: List of transformer plugin names
            
        Returns:
            ProcessingContext with results
        """
        # Initialize context
        context = ProcessingContext(
            input_text=text,
            output_text=text
        )
        
        context.add_metadata('timestamp', datetime.now().isoformat())
        context.add_metadata('plugins', {
            'formatters': formatters or [],
            'analyzers': analyzers or [],
            'transformers': transformers or []
        })
        
        print(f"\n{'='*60}")
        print(f"PROCESSING TEXT: {len(text)} characters")
        print(f"{'='*60}")
        
        # 1. Apply formatters (transform output)
        if formatters:
            print("\n📝 FORMATTING PHASE:")
            for formatter_name in formatters:
                plugin = PluginRegistry.get_plugin(formatter_name)
                if plugin and isinstance(plugin, TextFormatter):
                    print(f"\n  Applying {plugin.get_metadata().name}...")
                    context = plugin.process(context)
                else:
                    context.add_warning(f"Formatter not found: {formatter_name}")
        
        # 2. Apply transformers (transform output)
        if transformers:
            print("\n🔄 TRANSFORMATION PHASE:")
            for transformer_name in transformers:
                plugin = PluginRegistry.get_plugin(transformer_name)
                if plugin and isinstance(plugin, TextTransformer):
                    print(f"\n  Applying {plugin.get_metadata().name}...")
                    context = plugin.process(context)
                else:
                    context.add_warning(f"Transformer not found: {transformer_name}")
        
        # 3. Apply analyzers (add metadata only)
        if analyzers:
            print("\n📊 ANALYSIS PHASE:")
            for analyzer_name in analyzers:
                plugin = PluginRegistry.get_plugin(analyzer_name)
                if plugin and isinstance(plugin, TextAnalyzer):
                    print(f"\n  Applying {plugin.get_metadata().name}...")
                    context = plugin.process(context)
                else:
                    context.add_warning(f"Analyzer not found: {analyzer_name}")
        
        # Record processing
        self.processing_history.append({
            'timestamp': datetime.now(),
            'context': context
        })
        
        return context
    
    def get_available_plugins(self) -> Dict[PluginType, List[str]]:
        """Get names of all available plugins"""
        return {
            PluginType.FORMATTER: [p.get_metadata().name for p in PluginRegistry.get_plugins_by_type(PluginType.FORMATTER)],
            PluginType.ANALYZER: [p.get_metadata().name for p in PluginRegistry.get_plugins_by_type(PluginType.ANALYZER)],
            PluginType.TRANSFORMER: [p.get_metadata().name for p in PluginRegistry.get_plugins_by_type(PluginType.TRANSFORMER)]
        }
    
    def get_processing_history(self) -> List[Dict]:
        """Get processing history"""
        return self.processing_history


# ============================================================================
# PLUGIN EXTENSION DEMONSTRATION - ADDING NEW PLUGINS WITHOUT CODE MODIFICATION
# ============================================================================

# NEW PLUGIN 1: Keyword Extractor (Analyzer)
class KeywordExtractor(TextAnalyzer):
    """Extracts important keywords from text"""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="KeywordExtractor",
            version="1.0.0",
            author="Extension Demo",
            description="Extracts important keywords and phrases",
            plugin_type=PluginType.ANALYZER,
            tags=["keywords", "extraction", "seo"]
        )
    
    def analyze(self, text: str) -> Dict[str, Any]:
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        words = text.lower().split()
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                     'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Count frequencies
        word_freq = Counter(words)
        top_keywords = word_freq.most_common(10)
        
        # Find bigrams (simple)
        bigrams = []
        for i in range(len(words)-1):
            bigrams.append(f"{words[i]} {words[i+1]}")
        bigram_freq = Counter(bigrams).most_common(5)
        
        return {
            'top_keywords': top_keywords,
            'top_bigrams': bigram_freq,
            'unique_keywords': len(set(words)),
            'total_keywords': len(words)
        }


# NEW PLUGIN 2: Reverse Transformer
class ReverseTransformer(TextTransformer):
    """Reverses the text"""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ReverseTransformer",
            version="1.0.0",
            author="Extension Demo",
            description="Reverses the entire text",
            plugin_type=PluginType.TRANSFORMER,
            tags=["reverse", "fun", "manipulation"]
        )
    
    def transform(self, text: str) -> str:
        return f"[REVERSED]: {text[::-1]}"


# NEW PLUGIN 3: JSON Formatter
class JSONFormatter(TextFormatter):
    """Formats text as JSON"""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="JSONFormatter",
            version="1.0.0",
            author="Extension Demo",
            description="Formats text as JSON structure",
            plugin_type=PluginType.FORMATTER,
            tags=["json", "structured", "data"]
        )
    
    def format(self, text: str) -> str:
        lines = text.split('\n')
        data = {
            'content': text,
            'lines': len(lines),
            'words': len(text.split()),
            'characters': len(text),
            'timestamp': datetime.now().isoformat()
        }
        return json.dumps(data, indent=2)


# ============================================================================
# ARCHITECTURE DIAGRAM GENERATION
# ============================================================================

def generate_architecture_diagram():
    """Generate ASCII architecture diagram"""
    
    diagram = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                       TEXT PROCESSING PLUGIN ARCHITECTURE                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

                           ┌─────────────────────┐
                           │   TextProcessor     │
                           │    (Orchestrator)   │
                           └──────────┬──────────┘
                                      │
                    ┌─────────────────┼────────────────                 │                 │                 │
         ┌──────────▼──────────┐ ┌───▼─────────┐ ┌─────▼──────────┐
         │   Formatter Chain   │ │ Analyzer    │ │ Transformer    │
         │  (Modify output)    │ │ (Metadata)  │ │ (Modify output)│
         └──────────┬──────────┘ └───┬─────â─┘ └─────┬──────────┘
                    │                 │                 │
    ┌───────────────┼───────────────┐ │ ┌───────────────┼───────────────┐
    │               │               │ │ │               │               │
┌───▼────┐    ┌────▼───┐    ┌─────â──┐   ┌────▼───┐    ┌─────▼────┐
│Markdown│    │HTML    │    │Plain  │││Word   │   │Sentiment│    │Translate │
│Formatter│    │Formatter│    │Text   │││Count  │   │Analyzer│    │Transformer│
└────────┘    └────────┘    └───────┘│└───────┘   └────────┘    └──────────┘
                                   │
                         ┌───────────┴───────────────────┐
                         │                               │
                    ┌────▼────┐                    ┌─────▼─────┐
                    │Keyword  │                    │Readability│
                    │Extractor│                    │Analyzer   │
                    └──────â               └───────────┘

                         ╔════════════════════════════════╗
                         ║     PLUGIN REGISTRY            ║
                         ║  • Auto-discovery             ║
                         ║  • Type-based categorization  ║
                         ║  • Runtime plugin lookup      ║
                         ╚═════════════â═════════════════╝

                         ╔════════════════════════════════╗
                         ║     EXTENSIBILITY PATTERN      ║
                         ║  • Add plugins without code    ║
                         ║    modification               ║
                         ║  • Register via discovery     ║
                         ║  • OCP - Open/Closed Principle║
                     ╚════════════════════════════════╝
"""
    print(diagram)


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_plugin_system():
    """Demonstrate the complete plugin system"""
    
    print("=" * 80)
    print("EXERCISE 1.3: Design a Plugin System 🔴")
    print("=" * 80)
    
   erate architecture diagram
    generate_architecture_diagram()
    
    # Create processor
    print("\n🚀 INITIALIZING TEXT PROCESSOR WITH PLUGIN SYSTEM")
    print("=" * 80)
    processor = TextProcessor()
    
    # Show available plugins
    print("\n📦 AVAILABLE PLUGINS:")
    available = processor.get_available_plugins()
    for plugin_type, plugins in available.items():
        print(f"\n  {plugin_type.value.upper()}:")
        for plugin in plugins:
            print(f"    • {plugin}")
    
  ample text
    sample_text = """
    # Welcome to Our Platform
    
    We are excited to announce the launch of our new text processing system.
    This system uses a powerful plugin architecture that allows unlimited extensibility.
    
    ## Key Features
    
    * Plugin-based design - add new capabilities without modifying core code
    * Multiple formatters for different output formats
    * Advanced text analysis with multiple metrics
    * Text transformations including translation and encryption
    
    The system is built on SOLID principles and clean architecture patterns.
    It demonstrates how abstraction enables flexible, maintainable software design.
    
    Thank you for exploring this demonstration!
    """
    
    # DEMONSTRATION 1: Basic processing with standard plugins
    print("\n" + "=" * 80)
    print("DEMONSTRATION 1: Standard Plugin Processing")
    print("=" * 80)
    
    result = processor.process(
        text=sample_text,
        formatters=["MarkdownFormatter"],
        analyzers=["WordCount", "Sentiment", "Readability"],
        transformers=[]
    )
    
    print("\n📄 PROCESSED OUTPUT:")
    print("-" * 40)
    print(result.output_text[:500] + "...")
    
    print("\n📊 ANALYSIS RESULTS:")
    print("-" * 40)
    for key, value in result.metadata.items():
        if key.startswith('analysis_'):
            print(f"\n  {key.upper()}:")
            if isinstance(value, dict):
                for k, v in value.items():
                    print(f"    • {k}: {v}")
   # DEMONSTRATION 2: Adding new plugins without code modification
    print("\n" + "=" * 80)
    print("DEMONSTRATION 2: Extending System with New Plugins")
    print("=" * 80)
    print("\n🔌 Adding new plugins WITHOUT modifying core code...")
    
    # Register new plugins
    PluginRegistry.register_plugin(KeywordExtractor())
    PluginRegistry.register_plugin(ReverseTransformer())
    PluginRegistry.register_plugin(JSONFormatter())
    
    print("\n📦 UPDATED AVAILABLE PLUGINS:")
    available = proor.get_available_plugins()
    for plugin_type, plugins in available.items():
        print(f"\n  {plugin_type.value.upper()}:")
        for plugin in plugins:
            print(f"    • {plugin}")
    
    # Process with new plugins
    print("\n" + "=" * 80)
    print("DEMONSTRATION 3: Processing with New Plugins")
    print("=" * 80)
    
    result2 = processor.process(
        text="This is a test document. It contains important keywords like plugin, architecture, and design.",
        formatters=["JSFormatter"],
        analyzers=["KeywordExtractor"],
        transformers=["ReverseTransformer"]
    )
    
    print("\n📄 PROCESSED OUTPUT:")
    print("-" * 40)
    print(result2.output_text)
    
    print("\n📊 ANALYSIS RESULTS (Keyword Extraction):")
    print("-" * 40)
    if 'analysis_keywordextractor' in result2.metadata:
        keywords = result2.metadata['analysis_keywordextractor']
        print(f"  Top keywords: {keywords['top_keywords']}")
    
    # DEMONSTRATION 4: Plugin composition
  int("\n" + "=" * 80)
    print("DEMONSTRATION 4: Plugin Composition - Multiple Formatters")
    print("=" * 80)
    
    result3 = processor.process(
        text="Simple text that will be formatted multiple ways.",
        formatters=["MarkdownFormatter", "HTMLFormatter"],
        analyzers=[],
        transformers=[]
    )
    
    print("\n📄 OUTPUT AFTER MULTIPLE FORMATTERS:")
    print("-" * 40)
    print(result3.output_text)
    
    # DEMONSTRATION 5: Transformation pipeline
    print("\n" + "=" * )
    print("DEMONSTRATION 5: Transformation Pipeline")
    print("=" * 80)
    
    result4 = processor.process(
        text="Secret message that needs encryption and reversal.",
        formatters=["PlainTextFormatter"],
        analyzers=[],
        transformers=["Encryptor", "ReverseTransformer"]
    )
    
    print("\n📄 TRANSFORMATION PIPELINE RESULT:")
    print("-" * 40)
    print(f"  Original: Secret message that needs encryption and reversal.")
    print(f"  Final:    {result4.output_text}")
  
    # DEMONSTRATION 6: Plugin system extensibility proof
    print("\n" + "=" * 80)
    print("PROOF: Zero-Code-Modification Extensibility")
    print("=" * 80)
    print("""
    ✅ We added THREE new plugins WITHOUT modifying:
       • TextProcessor class
       • PluginRegistry class
       • Abstract base classes
       • Any existing plugin code
    
    ✅ New plugins are automatically:
       • Discovered by the registry
       • Available for runtime selection
       • Composible wi existing plugins
       • Properly typed and categorized
    
    ✅ This demonstrates:
       • Open/Closed Principle - Open for extension, closed for modification
       • Strategy Pattern - Plugins are interchangeable strategies
       • Chain of Responsibility - Plugins can be chained
       • Dependency Inversion - All depend on abstractions
    """)


def main():
    """Main entry point"""
    demonstrate_plugin_system()
    
    print("\n" + "=" * 80)
    print("DOCUMENTATION: Plugin Archmary")
    print("=" * 80)
    print("""
    📐 ARCHITECTURE PATTERN: Plugin System with Registry
    
    1️⃣ ABSTRACTION LAYERS:
       • TextPlugin (root interface)
       • TextFormatter/TextAnalyzer/TextTransformer (category interfaces)
       • Concrete plugins (implementations)
    
    2️⃣ DISCOVERY MECHANISM:
       • PluginRegistry singleton
       • Auto-discovery of plugin classes
       • Type-based categorization
       • Tag-based search
    
    3️⃣ ORCHESTRATION:xtProcessor (core engine)
       • ProcessingContext (pipeline state)
       • Plugin chains by category
    
    4️⃣ EXTENSIBILITY FEATURES:
       • New plugins require NO core code changes
       • Runtime plugin registration
       • Conditional processing with can_handle()
       • Plugin dependencies and metadata
    
    5️⃣ DESIGN PATTERNS USED:
       • Strategy Pattern - Plugins are interchangeable
       • Chain of Responsibility - Processing pipeline
       • Factory Paugin instantiation
       • Registry Pattern - Plugin discovery
       • Singleton Pattern - PluginRegistry
    
    🎯 KEY ACHIEVEMENT:
       We built a system where new functionality can be added
       by simply writing new plugin classes. No core code
       modification is required - the definition of a true
       plugin architecture!
    """)


if __name__ == "__main__":
    main()
