# SynthLang CLI

A powerful command-line interface for the SynthLang framework, providing advanced prompt engineering, framework translation, and optimization capabilities using DSPy.

## What is SynthLang?
Reduce AI costs by up to 95% with SynthLang's efficient prompt optimization. Experience up to 1100% faster processing while maintaining effectiveness.

Transform your AI interactions with mathematically-structured prompts. Symbolic Scribe brings academic rigor to prompt engineering, helping you create more precise, reliable, and powerful AI interactions.
SynthLang is a revolutionary framework for prompt engineering and language model optimization. It introduces a structured, mathematical approach to prompt design that makes prompts more consistent, measurable, and effective. The framework uses a unique symbolic notation system that bridges natural language and computational thinking.

### Core Concepts

- **Symbolic Notation**: Uses mathematical symbols (↹, ⊕, Σ) to represent input, process, and output
- **Compositional Design**: Break complex prompts into atomic operations
- **Measurable Quality**: Quantitative metrics for prompt effectiveness
- **Evolutionary Optimization**: Systematic improvement through genetic algorithms
- **Framework Translation**: Convert between different prompt engineering approaches

### How It Works

SynthLang transforms natural language prompts into a structured format:

1. **Input (↹)**: Define data sources and parameters
2. **Process (⊕)**: Specify transformations and operations
3. **Output (Σ)**: Describe expected results and formats
4. **Operators**: Use mathematical symbols (+, >, <, ^) for relationships
5. **Joins (•)**: Connect related concepts

## Metrics & Performance

SynthLang evaluates prompts across multiple dimensions:

### Clarity Score (0-1)
- Symbol usage correctness
- Structure adherence
- Concept separation
- Line length optimization

### Specificity Score (0-1)
- Operator precision
- Join relationships
- Transformation clarity
- Parameter definition

### Consistency Score (0-1)
- Symbol alignment
- Format compliance
- Terminology usage
- Pattern adherence

### Task Completion Score (0-1)
- Test case success
- Output matching
- Error handling
- Edge case coverage

## Features

- 🔄 **Framework Translation**: Convert natural language to SynthLang format
- ⚡ **Prompt Optimization**: Enhance prompts using DSPy techniques
- 🧬 **Evolutionary Algorithms**: Evolve prompts through genetic algorithms
- 📊 **Performance Metrics**: Track clarity, specificity, and consistency scores
- 🎯 **Task-Based Testing**: Evaluate prompts against specific test cases
- 🔍 **Smart Classification**: Categorize and analyze prompts
- 🛠️ **Extensible Architecture**: Build custom modules and pipelines

## Benefits

- **Improved Efficiency**: Streamline prompt engineering workflow
- **Better Results**: Generate more effective and consistent prompts
- **Rapid Iteration**: Quick experimentation and optimization
- **Quality Metrics**: Quantitative feedback on prompt quality
- **Framework Integration**: Seamless integration with existing tools
- **DSPy Powered**: Leverage advanced language model techniques

## Installation

```bash
pip install synthlang
```

## Basic Usage

1. **Translate Natural Language to SynthLang**
```bash
synthlang translate "Analyze customer feedback and generate sentiment insights"
```

2. **Optimize a Prompt**
```bash
synthlang optimize "path/to/prompt.txt" --iterations 5
```

3. **Evolve Prompts**
```bash
synthlang evolve "initial_prompt" --generations 10 --population 5
```

4. **Classify Prompts**
```bash
synthlang classify "prompt_text" --labels "task,query,instruction"
```

## Advanced Usage

### Custom Evolution Parameters

```bash
synthlang evolve "prompt" \
  --generations 20 \
  --population 10 \
  --mutation-rate 0.3 \
  --tournament-size 3 \
  --fitness-type hybrid
```

### Test-Driven Optimization

```bash
synthlang optimize "prompt" \
  --test-cases tests.json \
  --target-score 0.95 \
  --max-iterations 50
```

### Batch Processing

```bash
synthlang batch-translate prompts.txt \
  --output translated/ \
  --format json \
  --parallel 4
```

### Environment Configuration

Create a `.env` file:
```env
OPENAI_API_KEY=your_key_here
SYNTHLANG_MODEL=gpt-4o-mini
SYNTHLANG_TEMPERATURE=0.7
```

## Examples

### Framework Translation
```bash
# Input
synthlang translate "Get news articles about AI and analyze their sentiment"

# Output
↹ news•ai
⊕ fetch => articles
⊕ analyze => sentiment
Σ results + metrics
```

### Prompt Evolution
```bash
# Start with basic prompt
synthlang evolve "Summarize text" \
  --test-cases summary_tests.json \
  --generations 5

# Evolution produces optimized versions:
# Generation 1: "Extract key points and create concise summary"
# Generation 2: "Identify main themes and synthesize core message"
# Generation 3: "Analyze content, extract insights, generate summary"
```

### Classification Pipeline
```bash
# Classify multiple prompts
synthlang classify-batch prompts.txt \
  --labels "query,task,instruction,conversation" \
  --output classifications.json
```

### Metrics Analysis
```bash
# Get detailed metrics for a prompt
synthlang analyze "prompt.txt" --detailed

# Output
{
  "clarity_score": 0.95,
  "specificity_score": 0.87,
  "consistency_score": 0.92,
  "task_score": 0.89,
  "overall_quality": 0.91
}
```

## Development

1. Clone the repository:
```bash
git clone https://github.com/ruvnet/SynthLang.git
cd SynthLang/cli
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

3. Run tests:
```bash
pytest
```

## Credits

SynthLang CLI is part of the SynthLang Framework created by [@ruvnet](https://github.com/ruvnet).

- **Framework**: [SynthLang](https://github.com/ruvnet/SynthLang)
- **Creator**: [@ruvnet](https://github.com/ruvnet)
- **Documentation**: [synthlang.org](https://synthlang.org)
- **License**: MIT

## Contributing

Contributions are welcome! Please check out our [Contributing Guidelines](CONTRIBUTING.md) for details on how to submit pull requests, report issues, and contribute to the project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
