# Context Briefing: Evaluating AI Models Beyond Benchmarks

## The Question
Is there a better way to assess AI model capabilities than testing performance on Q&A benchmarks?

## The User's Position
The user is skeptical that benchmark scores reflect real-world usefulness. They suspect benchmarks may be measuring the wrong things entirely. They care most about an inarticulate quality — the "je ne sais quoi" of a model being genuinely useful, creative, and reliable in open-ended situations. They offered a critical observation: **"real-world usefulness is not directly correlated with intelligence."**

The user explicitly does NOT have a decision riding on this. This is intellectual exploration of a genuine tension.

The user has direct experiential evidence: Claude models "far outstrip others in intent comprehension and real-world usefulness" despite not necessarily leading on all benchmarks. They do not tend to follow benchmark scores and regard them mostly as noise.

When offered several framings of what might be "off" about benchmarks, the user found all plausible but could not commit to any. They stated: "what I have here is an intuition, not a fully-formed argument." The dialectic should help surface what the intuition points toward.

## The Core Tension
Systematic evaluation requires decomposing capability into measurable dimensions. But the quality that determines whether an AI is actually useful may be holistic, relational, and irreducible to dimensions — not because it's mystical, but because it's the kind of property that exists in the interaction between user and system, not in the system alone. Yet without systematic measurement, you can't do science, you can't make rational comparisons, and you're left with "vibes" — which are demonstrably subject to bias.

## Key Research Findings

### The Case Against Current Benchmarks
- **Saturation**: Frontier models push past 90% on MMLU, HumanEval, GSM8K. New harder benchmarks (GPQA, HLE) follow the same lifecycle.
- **Contamination**: Multi-method audit found 13.8% contamination on MMLU overall, up to 66.7% in Philosophy. Phi-4 scores 85 on MMLU but only 3 on SimpleQA.
- **Quality problems**: 6.5% of MMLU questions contain errors. LLM accuracy changes by up to 25 percentage points depending on prompt format.
- **Benchmarketing**: Model providers optimize for benchmark scores because those scores drive adoption. The metric becomes the target (Goodhart).
- **Thomas & Uminsky (2022)**: "Reliance on metrics is a fundamental challenge for AI." Case studies showing metric optimization leads to real-world harms.
- **Raji & Bender**: Whether one model is preferred depends on context and values, not a single score.

### Alternative Evaluation Paradigms
- **Chatbot Arena (LMSYS/LMArena)**: 1M+ pairwise human preference votes. Most influential alternative. But also gameable.
- **VibeCheck (2024)**: Academic work discovering "vibe" traits that predict model identity with 80% accuracy and preference with 61%.
- **Task-based evaluation**: SWE-bench, Vibe Code Bench — evaluate on complete real-world tasks.
- **Stanford HELM**: 7 metrics across 42 scenarios. Self-acknowledges incompleteness.

### Model Character and Disposition
- **Anthropic's "Soul Document"**: Shapes Claude's character at the level of identity, values, personality rather than rules. Persona vectors show character and capability are somewhat independent dimensions.
- **"Personality alignment" as research direction**: Distinct from standard alignment.

### Goodhart's Law Applied to AI
- Formal proof that Goodhart effect depends on tail distribution of discrepancy between true goal and proxy.
- In RL: formally demonstrated that for any environment and true reward function, it's impossible to create a non-trivial unhackable proxy reward.
- **Strong Goodhart**: Extreme optimization on any proxy will eventually make things actively worse.

### Measurement Theory and Holistic Properties
- **Polanyi's Tacit Knowledge**: "We can know more than we can tell." Measurement instruments relying on explicit decomposition are necessarily incomplete.
- **Construct validity crisis**: "One does not validate a test, but only a principle for making inferences."
- **Buber's I-Thou vs I-It**: Benchmarks treat models as objects (I-It). Usefulness may be an I-Thou quality — emerging in encounter.
- **Usefulness as relational property**: Like weight, it exists between user and system.

### The Case FOR Systematic Evaluation
- **Psychometrics overcame skepticism**: Mental qualities were once considered unmeasurable.
- **Intuition is demonstrably unreliable**: Cognitive biases in 36.5-77% of medical case-scenarios.
- **Bean & Rocher (2025, Oxford)**: 40 researchers argue for better benchmarks, not no benchmarks.
- **The alternative (subjective judgment) is demonstrably worse**.

### Intelligence vs. Usefulness
- **Yale**: "AI Is Getting Smarter — and Less Reliable."
- **Mollick**: "The same model can behave very differently depending on what harness it's operating in."
- **HCI research**: "A less intelligent model in a well-designed harness can be more useful than a more intelligent model in a poor one."

### Analogies from Other Fields
- **Wine tasting**: Expert judges vary ±4 points on same wine. Holistic "synthetic properties" are real but resist decomposition. Algorithms predict 91% accuracy from physicochemical variables; 68% of experts dismiss them as "soulless."
- **Clinical judgment**: Algorithms outperform experts on structured tasks; experts essential for unstructured/novel situations. Best practice integrates both.
- **Pirsig's "Quality"**: Precedes subject/object distinction. Cannot be defined analytically, yet universally recognizable.

## The Ontological Question
What kind of property is "model quality" — and does the answer determine what kind of evaluation is possible?
