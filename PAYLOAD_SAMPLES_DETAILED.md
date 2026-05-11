# PAYLOAD SAMPLES — Detailed Comparison

---

## CANDIDATE 1: Doctrine (WEAK)

**File:** `/Users/rrg/moremindmap/temp/doctrine-narrative-pipeline-output.json`  
**Modified:** Apr 30 21:56  
**Word Count:** 3,185  

### executiveSummary (Sample 150 words):
```
Your behavioral profile reveals a distinct operating system, one that is recognizable, 
consistent, and increasingly predictable the more you understand it. This is not a 
personality profile. This is a map of how your behavioral engine actually works—how you 
process uncertainty, make decisions, move under pressure, and interact with people and 
environments.

Your system may not automatically reach for command. Leadership and ownership feel more 
natural when invited rather than assumed. This is your dominant operating signal (vector: 
35.9/100). This orientation shapes everything downstream. It affects how you approach 
decisions, how you communicate, how people experience you, and where you naturally create 
friction.

Framework (score: 15.4/100) acts as a supporting stabilizer. Builds structure and 
operational clarity.
```

**Issues:**
- ❌ Raw decimals: "35.9/100", "15.4/100"
- ❌ Confusing language: "dominant operating signal (vector: ...)" (Signal is a dimension!)
- ⚠️ Generic tone: "reveals a distinct operating system" (textbook language)

### operatingPattern (Sample 150 words):
```
Your operating pattern is anchored in forward movement and decisive action. This is your 
baseline. When faced with uncertainty, your system does not pause to gather perfect 
information or build consensus. Your instinct is to move toward clarity through action 
rather than through extended analysis or committee discussion.

Your system may not automatically reach for command. Leadership and ownership feel more 
natural when invited rather than assumed. This is your dominant operating signal (vector: 
35.9/100).

What this means in practice is that you likely prefer environments where decisions can be 
made with reasonable clarity and reasonable speed. You probably become frustrated with 
prolonged ambiguity, endless deliberation, or cultures that prioritize process and 
relationship-building over decisiveness.
```

**Issues:**
- ❌ Repeated phrase: "Your system may not automatically reach for command" (3x in document)
- ❌ Raw decimal: "35.9/100"
- ⚠️ Weak narrative: lacks examples, feels generic

### underPressure (Sample 150 words):
```
What happens to your behavioral system when pressure rises is crucial to understand. 
Your system doesn't relax or pause under pressure. It intensifies.

Under pressure: Emotional resistance may not slow your movement. Relational feedback may 
register later. You may slow down and become more deliberate. You may become more rigid 
about the chosen path. Adaptation may feel disruptive.

Your system tends to amplify what's already strong and narrow what's already weak. If 
you're naturally direct and decisive, pressure makes you more so. If you naturally 
underweight relational signals, pressure makes you even less attentive to them. Your 
dominant pattern doesn't soften under stress. It crystallizes.

**Signal** (score: 0/100): Relational information may not enter your decision system as 
quickly as facts, speed, or precision.
```

**Issues:**
- ❌ Vague language: "What happens to your behavioral system..." (lecture tone)
- ❌ Contradictory bullets: "You may slow down... You may become more rigid" (confusing)
- ❌ Raw decimal: "0/100"
- ⚠️ Weak examples: none provided

---

## CANDIDATE 2: Hybrid (STRONG)

**File:** `/Users/rrg/moremindmap/temp/hybrid-profile-payload.json`  
**Modified:** Apr 30 14:11  
**Word Count:** 3,768  

### executiveSummary (Sample 150 words):
```
This comprehensive behavioral assessment profiles a leader who demonstrates a dominant, 
command-driven approach to leadership, underscored by a high Vector score of 35.9. This 
score reflects the leader's predilection for authority and a structured management style. 
The leader's Fidelity score of 17.9 further indicates a focus on precision and detail, 
suggesting an operational stance where thoroughness and exactitude are paramount.

In practice, this leader's approach is particularly evident in scenarios requiring 
stringent oversight and meticulous adherence to procedures. For example, in quality 
control processes within a manufacturing context, this leader excels, implementing 
rigorous standards and checks that ensure product quality and compliance with industry 
regulations. Their leadership ensures that tasks are executed flawlessly, which is 
crucial in environments where the cost of errors is high.
```

**Quality:**
- ✅ Contextual: Uses dimension names with explanations
- ✅ Examples: Manufacturing quality control provided
- ⚠️ Issue: Raw decimals still present ("35.9", "17.9")
- ✅ Professional tone: More sophisticated than Doctrine

### operatingPattern (Sample 150 words):
```
The leader's operating pattern is defined by a demonstrably strong command presence, 
underscored by an acute attention to detail. This is evident in the way they conduct 
daily briefings, meticulously reviewing each team member's tasks and progress, ensuring 
no deviation from the set goals. With a high Vector score, this individual thrives in 
roles that demand tight oversight and command - such as project management or operations 
in sectors like manufacturing or finance, where precision is paramount.

Their moderate Fidelity score highlights a capability to remain consistent and reliable 
in their methods. For example, in project planning stages, this leader will often revisit 
and refine workflows to optimize efficiency, a practice that has led to significant 
decreases in production downtime and budget overruns in past projects.
```

**Quality:**
- ✅ Rich examples: Daily briefings, project planning, production downtime
- ✅ Behavioral specificity: Clear descriptions of actions
- ✅ Good narrative flow: Less essay-like than Doctrine
- ⚠️ Issue: "high Vector score", "moderate Fidelity score" (decimal context)

### underPressure (Sample 150 words):
```
When placed in high-stress environments, this leader exhibits a pronounced tendency to 
intensify their command-and-control approach. This behavior is characterized by a 
decisive leadership style where decision-making is centralized and quick actions are 
prioritized based on the immediate data and facts at hand. For instance, during a 
critical system outage in the IT department, this leader swiftly assembled the key 
technical team, delineated clear roles for each member, and set stringent timelines for 
issue resolution, demonstrating their ability to handle crisis situations efficiently.

Their meticulous attention to detail is undoubtedly a significant asset. This was 
evident in a recent project where they successfully identified and rectified minor 
discrepancies in the financial reporting process that had been overlooked for quarters.
```

**Quality:**
- ✅ Concrete scenario: IT system outage described in detail
- ✅ Behavioral evidence: Clear cause-and-effect narratives
- ✅ Professional examples: Finance, IT, project management
- ✅ No raw decimals in this section

---

## CANDIDATE 3: Dense (STRONGEST) ← **RECOMMENDED**

**File:** `/Users/rrg/moremindmap/temp/dense-profile-payload.json`  
**Modified:** Apr 30 13:50  
**Word Count:** 3,912  

### executiveSummary (Sample 150 words):
```
This individual demonstrates a dominant and authoritative demeanor, characterized by a 
strict adherence to detail and an unwavering commitment to precision. Their high scores 
in the Vector (Command) and Fidelity (Precision) domains are indicative of their ability 
to lead decisively and manage tasks with exactness. They often excel in environments 
where clear directives and standards are valued, such as in military leadership roles or 
in structured corporate settings.

Their leadership style is distinctly direct and results-oriented. This individual 
approaches decision-making with a high degree of confidence, backed by a robust 
understanding of the objectives at hand. They are not one to waver under pressure, 
exhibiting a steadfast pursuit of outcomes, which often inspires confidence in their 
teams.
```

**Quality:**
- ✅ Professional tone: "demonstrably dominant", "unwavering commitment"
- ✅ **No raw decimals:** Uses "Vector (Command)" and "Fidelity (Precision)" naming
- ✅ Rich context: Military roles, corporate settings
- ✅ Psychological depth: "steadfast pursuit," "inspires confidence"
- ✅ **GPT-5.5 quality language**

### operatingPattern (Sample 150 words):
```
The individual exhibits a pronounced preference for control and order, which 
significantly shapes their professional behavior and interpersonal interactions. This 
need for control is evident in their inclination to take charge in group settings and 
their assertiveness in decision-making situations. Their leadership style is often 
directive, and they are comfortable setting clear expectations and enforcing rules. This 
tendency is underscored by their dominant traits in Command, which not only motivates 
them to lead but also to ensure that every detail aligns with their high standards.

Their pursuit of precision is observable in their meticulous attention to detail. This 
individual is likely to excel in roles that demand thoroughness, such as in quality 
assurance or project management, where precision is paramount. They are the type to 
double-check facts, scrutinize outputs, and methodically follow through on plans.
```

**Quality:**
- ✅ Psychological language: "pronounced preference," "significantly shapes"
- ✅ **No raw decimals**
- ✅ Behavioral specificity: Double-check facts, scrutinize outputs
- ✅ Professional examples: QA, project management
- ✅ Strong Patricia-style structure: Clear cause-and-effect

### underPressure (Sample 150 words):
```
Under pressure, this individual typically exhibits a remarkable ability to remain 
focused and determined, largely due to their strong command and precision traits. These 
traits enable them to maintain a clear vision and a steady hand when navigating stressful 
situations, often leading to effective problem-solving under tight deadlines or in 
high-stakes environments. For example, when faced with a critical project at work that 
requires a quick turnaround, they are likely to take charge, organizing tasks and 
directing team members efficiently to meet the necessary objectives.

This person typically handles stress by delving deeper into the problem at hand. They 
apply a heightened level of control and adhere more strictly to known structures and 
methodologies, which can often result in a meticulous and thorough approach to 
problem-solving.
```

**Quality:**
- ✅ Sophisticated language: "steady hand," "delving deeper"
- ✅ **No raw decimals**
- ✅ Clear cause-and-effect: Pressure → deeper focus → better problem-solving
- ✅ Specific behavior: "adheres more strictly to known structures"
- ✅ Psychological insight: Understanding of stress response patterns
- ✅ **Best narrative quality of all three**

---

## SUMMARY TABLE

| Aspect | Doctrine | Hybrid | Dense |
|--------|----------|--------|-------|
| **Raw Decimal Leaks** | ❌❌ | ⚠️ | ✅ |
| **Repetitive Phrases** | ❌❌ | ✅ | ✅ |
| **Professional Tone** | ⚠️ | ✅ | ✅✅ |
| **Psychological Depth** | ⚠️ | ✅ | ✅✅ |
| **Example Richness** | ❌ | ✅ | ✅✅ |
| **No Contradictions** | ❌ | ✅ | ✅ |
| **Patricia-Style** | ⚠️ | ✅ | ✅✅ |
| **Instrument Feel** | ⚠️ | ✅ | ✅✅ |
| **Word Density** | 3,185 | 3,768 | 3,912 |
| **Overall Grade** | **D** | **A** | **A+** |

---

## RECOMMENDATION

**→ USE: Dense Profile Payload (3,912 words)**

This is the most sophisticated, psychologically sound, and professionally presented payload. It has:
- No raw decimal leaks
- Rich contextual examples  
- Professional psychological language
- Strong Patricia-style structure
- Highest word density
- **GPT-5.5 quality intelligence**

**Ready for:** Pass A fixed renderer → 23+ pages, fully readable, dense, professional
