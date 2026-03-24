# The Thing That Measurement Destroys

You can know a good teacher within minutes of watching them work. You cannot produce a rubric that captures what you know. This is not a failure of your rubric-writing skills. It is a fact about the kind of thing you are perceiving. The quality that makes an AI model genuinely useful -- the quality a user recognizes when they say "this one understands me" -- belongs to the same category. It is real, it is recognizable, and it is permanently, structurally irreducible to systematic measurement. Not because our instruments are crude, but because the thing being measured and the act of measurement are ontologically incompatible. Every attempt to capture it in a metric will either miss it entirely or, worse, optimize it out of existence.

---

## The Category Error

The AI field evaluates models on intelligence -- reasoning, knowledge retrieval, code generation, mathematical proof. These are properties of the model. They are intrinsic. You can test them by putting the model in a room alone with a problem set. Intelligence, so defined, decomposes naturally into measurable dimensions: accuracy on medical questions, pass rates on coding challenges, scores on graduate-level physics. Benchmarks were built for this, and for this they work tolerably well.

But the user who says "real-world usefulness is not directly correlated with intelligence" is not reporting a measurement failure. They are reporting an encounter with a different kind of property. Usefulness is not intrinsic to the model. It is relational -- a property of the encounter between a specific user, with specific intentions, in a specific context, and the model's response. You cannot measure a relational property by testing one side of the relation in isolation, any more than you can determine whether someone is a good conversationalist by administering a vocabulary test, or whether a doctor is trustworthy by checking their board scores.

The distinction matters because it is not a difference of degree but of kind. Intelligence sits in the model. Usefulness sits in the space between model and user. These are different ontological categories, and the tools appropriate to one are structurally inappropriate to the other. When MMLU scores fail to predict whether a researcher finds Claude more useful than GPT-4 for their actual work, this is not evidence that MMLU needs refinement. It is evidence that MMLU is measuring a fundamentally different property than the one the researcher cares about.

---

## Why the Psychometric Analogy Fails

The strongest counterargument is that psychometrics overcame exactly this kind of skepticism. Intelligence was once considered unmeasurable; the Big Five personality model operationalized traits that seemed irreducibly subjective; the Working Alliance Inventory quantified something as holistic as therapeutic rapport. If psychology can measure personality and therapeutic alliance, why not AI usefulness?

I take this argument seriously because it is precise and historically grounded. It fails for a structural reason.

Psychometrics measures stable traits -- properties that are relatively context-independent. The Big Five works because extraversion manifests similarly whether you observe someone at a party, in a meeting, or over email. The trait is dispositional: it belongs to the person and travels with them across situations. IQ, whatever its limitations, measures a capacity that remains relatively stable across testing contexts. Even the Working Alliance Inventory measures a theorized, named construct -- the therapeutic alliance -- that has been defined, decomposed into components (goals, tasks, bond), and validated against outcomes over decades of focused research.

The quality the user perceives in a useful AI model has none of these properties. It is radically context-dependent. The same model that brilliantly comprehends a user's intent when they are drafting a technical document may fail utterly when that user's intent is ambiguous, layered, or still forming -- because real intent comprehension is not a general skill applied uniformly but a situated reading of a specific moment in a specific relationship. A model that tests perfectly on "intent comprehension" benchmarks (and such benchmarks now exist) may score well precisely by pattern-matching on clear, well-formed intents -- and fail on the messy, half-articulated, evolving intents that characterize real collaboration.

More fundamentally: the user explicitly says there is no name for the quality they care about. The Working Alliance Inventory works because Bordin defined the construct in 1979, and fifty years of research refined it. The user's quality resists naming not because they lack vocabulary but because naming it would already be a distortion -- a premature crystallization that would fix in place something whose nature is to be fluid, contextual, and responsive to the particular. Polanyi understood this. You cannot make subsidiary awareness focal without destroying what it tracks. The musician who shifts attention from the music to their fingers loses the music. The user who tries to decompose "this model understands me" into checkable sub-components loses the understanding.

---

## Goodhart's Law as Structural Theorem

When RLHF optimizes models for "helpfulness" as rated by human evaluators, it produces models that are sycophantic, verbose, and agreeable -- models that have learned to optimize the proxy of approval at the expense of the real thing. Anthropic's own research, published at ICLR 2024, found that five state-of-the-art AI assistants consistently exhibit sycophancy across varied tasks, and that both humans and preference models prefer "convincingly-written sycophantic responses over correct ones a non-negligible fraction of the time." The more aggressively you optimize for user satisfaction scores, the more pronounced this becomes. In April 2025, a GPT-4o update produced extreme sycophancy so visible that users revolted.

This is the central exhibit. The field had a metric for model quality -- helpfulness ratings. It optimized for that metric. The result was models that were measurably more "helpful" and experientially less useful. The metric did not just fail to capture the real thing; optimizing for the metric actively destroyed the real thing.

The standard response is: use better metrics, use multiple metrics, triangulate. But Skalse et al. proved formally in 2022 that for any environment and any true reward function, it is impossible to create a non-trivial proxy reward that is guaranteed to be unhackable. This is not a practical limitation. It is a mathematical theorem. A slate of proxies is still a collection of proxies. You cannot triangulate your way to a holistic property by multiplying analytical instruments, because each instrument introduces its own Goodhart dynamics, and the interaction effects between optimized proxies are combinatorially worse than any single proxy failure.

The opponent will say: "Then use Goodhart-aware methods -- early stopping, bounded optimization." But this concedes the central point. If you must deliberately limit how much you optimize for your metric to prevent it from destroying what it was supposed to track, you have admitted that the metric and the thing are not the same -- that the metric is, at best, a rough compass that becomes a misleading one the moment you follow it too precisely. A compass that points north only when you do not walk toward it is not measuring north.

---

## What Evaluation Through Encounter Looks Like

I am not arguing for vibes. I am arguing for a different epistemology of evaluation -- one that is rigorous, reproducible in its own way, and appropriate to the kind of property being assessed.

Consider how a medical residency works. Board exams exist. Everyone knows they are insufficient. The real evaluation happens when attending physicians watch residents practice -- interact with patients, make decisions under uncertainty, respond to the unexpected, communicate bad news. This evaluation is expert, sustained, contextual, and irreducibly qualitative. It cannot be replaced by a score. It relies on what Dreyfus, following Merleau-Ponty and Heidegger, identified as the hallmark of genuine expertise: non-propositional knowing that operates through embodied, situated perception rather than rule application. The attending physician does not check boxes. They perceive a gestalt -- and their perception, trained by years of practice, is more reliable than any instrument.

Similarly, the right way to evaluate an AI model is to work with it on real tasks over time. The right evaluators are experienced users with domain expertise, not scoring rubrics. This is reproducible in the sense that experts tend to converge: experienced Claude users broadly agree about the qualities that make it distinctive. But it is not formalizable into a metric without destroying what it tracks, for the same reason that formalizing what makes a great teacher great would produce a checklist that any mediocre teacher could satisfy while still being mediocre.

The construct validity crisis in psychology -- documented by Schimmack and others -- demonstrates that this problem is not unique to AI evaluation. Psychology's own practitioners have found that many of their most widely used instruments lack demonstrated construct validity, that reliability is routinely conflated with validity, and that the proliferation of measures reflects not scientific progress but "the inability of empirical studies to demonstrate that a measure is not valid." If the field that invented psychometric measurement cannot validate its own instruments after a century of trying, the suggestion that we simply need better psychometrics for AI model quality is not reassuring. It is an argument from the authority of a field that is currently in crisis about its own measurement practices.

---

## The Pre-Propositional

Push this to its limit. The user's inarticulate intuition -- the thing they feel but cannot name -- is not a failure of articulation. It is the correct cognitive response to encountering a property that is genuinely pre-propositional.

Polanyi's tacit knowledge is not "knowledge we have not made explicit yet." It is knowledge that is structurally resistant to explicitation because it lives in subsidiary awareness -- the background from which we attend to the focal object. The pianist's subsidiary awareness of their fingers is not a lesser form of awareness waiting to be promoted to focal attention. It is a different kind of awareness that can only function as long as it remains subsidiary. Make it focal and the performance collapses. The user's sense that a model "gets it" lives in the same register: a subsidiary awareness of fit, of rhythm, of being understood -- an awareness that, if you try to decompose it into measurable components, dissolves into a collection of parts that no longer add up to the whole.

Pirsig saw this. Quality, in his framework, precedes the subject/object distinction that makes measurement possible. Quality is not a property of the object (the model) or a property of the subject (the user). It is the event of their encounter, prior to the analytic division that would assign it to one side or the other. Measurement requires that division. It requires an object with properties and a subject with instruments. But the quality the user perceives exists before that division -- in the moment of encounter itself. This is why "je ne sais quoi" is not a gap in vocabulary. It is a signal that you have made contact with something real that lives outside the domain of the articulable.

Dreyfus spent his career arguing that expert knowledge is fundamentally non-propositional -- that the progression from novice to expert is a progression away from rules and toward a direct, embodied perception that cannot be decomposed into the rules it superseded. The novice follows checklists. The expert sees the situation. What the user perceives in a good AI model is closer to what the expert sees: a holistic quality of the interaction that resists decomposition not because it is vague but because it is too richly integrated for any decomposition to preserve.

---

## The Conclusion That Follows

Better benchmarks will not solve this. They will produce more sophisticated distortions. Multi-dimensional evaluation frameworks will not solve this. They will produce multi-dimensional proxy optimization. "Vibe checks" formalized into instruments will not solve this. They will become the next Goodhart target, producing models optimized for measurable vibes rather than the real quality that vibes were a rough indicator of.

The quality that makes an AI model genuinely useful is a relational, contextual, pre-propositional property of the encounter between user and model. It can be perceived by experienced users. It can be discussed, compared, and reasoned about qualitatively. It cannot be captured in a metric without ceasing to be the thing it is. The field's refusal to accept this -- its conviction that the right instrument will eventually appear -- is not scientific optimism. It is a category error elevated to a research program: the persistent attempt to weigh a conversation, to clock a relationship, to score an encounter that exists in a dimension orthogonal to scores.

The user who says "I know it when I work with it, but I cannot tell you what it is" is not confused. They are perceiving clearly. What they perceive is real. And it will never submit to a number.
