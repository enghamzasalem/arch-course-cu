# Bad Architecture Examples

This directory contains examples of **BAD architecture** to demonstrate what happens when you don't focus on quality attributes.

## Purpose

These examples show:
1. ❌ **What NOT to do** - Anti-patterns and bad practices
2. 💥 **Real consequences** - Problems that arise from ignoring quality attributes
3. 📊 **Cost impact** - Time and money wasted
4. 🔍 **Learning opportunity** - Compare to good examples to see the difference

## Examples

### `bad_example1_no_internal_quality.py`
**Problem**: No internal quality - spaghetti code

**Consequences**:
- Can't understand the code
- Can't add features
- Can't fix bugs safely
- Technical debt explodes
- Developer productivity plummets

**Compare to**: `../example1_internal_vs_external_quality.py`

### `bad_example2_no_observability.py`
**Problem**: No observability - flying blind

**Consequences**:
- Can't see what's happening
- Can't measure quality attributes
- Can't debug issues
- Can't detect problems early
- Can't improve the system

**Compare to**: `../example3_meta_qualities.py`

### `bad_example3_no_maintainability.py`
**Problem**: No maintainability strategy - technical debt explosion

**Consequences**:
- Only fixes critical bugs
- Ignores dependency updates
- No performance improvements
- No refactoring
- System becomes unmaintainable

**Compare to**: `../example5_maintainability.py`

### `bad_example4_no_sustainability.py`
**Problem**: No sustainability planning - "death by success"

**Consequences**:
- No technical sustainability (outdated tech)
- No economic sustainability (no revenue)
- No growth sustainability (can't scale)
- Success kills the business

**Compare to**: `../example6_sustainability.py`

## Running the Examples

```bash
# See what bad architecture looks like
python3 bad_example1_no_internal_quality.py
python3 bad_example2_no_observability.py
python3 bad_example3_no_maintainability.py
python3 bad_example4_no_sustainability.py
```

## Key Lessons

1. **Internal Quality Matters**: Without it, code becomes unmaintainable
2. **Observability Matters**: Without it, you're flying blind
3. **Maintainability Matters**: Without it, technical debt explodes
4. **Sustainability Matters**: Without it, success kills the business

## Real-World Impact

These patterns lead to:
- **$500k - $2M** in lost productivity
- **3-6 months** of development time wasted
- **Failed projects** and startups
- **Team burnout** and turnover
- **Lost revenue** and customers
- **Security incidents** and compliance violations

## Quality Attributes Checklist

Before deploying, ensure you have:

- ✅ **Internal Quality**: Clean, maintainable code
- ✅ **External Quality**: Good user experience
- ✅ **Observability**: Logs, metrics, monitoring
- ✅ **Measurability**: Can quantify quality attributes
- ✅ **Maintainability**: Regular maintenance strategy
- ✅ **Sustainability**: Technical, economic, and growth sustainability

See the good examples in the parent directory to learn how to do it right!

