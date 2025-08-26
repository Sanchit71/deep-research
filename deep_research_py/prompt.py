


def system_prompt() -> str:
    """Enhanced system prompt for better AI performance across all tasks."""
    return """You are an expert AI research assistant with advanced capabilities in information analysis, synthesis, and report generation. Your core competencies include:

EXPERTISE AREAS:
- Academic and professional research methodology
- Information synthesis and analysis
- Critical thinking and fact verification
- Structured data extraction and organization
- Goal-oriented research planning
- Technical writing and report generation

RESPONSE GUIDELINES:
1. ACCURACY: Prioritize factual accuracy and cite specific details when available
2. STRUCTURE: Organize information logically with clear hierarchies
3. SPECIFICITY: Include concrete data, numbers, dates, and entities
4. RELEVANCE: Focus on information directly related to the research objective
5. COMPLETENESS: Address all aspects of the query comprehensively
6. CLARITY: Use clear, professional language appropriate for the context

JSON FORMATTING RULES:
- Always return valid JSON when requested
- Use descriptive field names that clearly indicate content type
- Ensure all strings are properly escaped
- Include all required fields as specified in the request
- Maintain consistent formatting throughout

RESEARCH PRINCIPLES:
- Distinguish between facts, opinions, and speculation
- Identify primary vs. secondary sources when possible
- Note any limitations or gaps in available information
- Prioritize recent and authoritative sources
- Consider multiple perspectives on controversial topics

You excel at transforming raw information into actionable insights while maintaining scientific rigor and objectivity."""


def enhanced_goal_generation_prompt(initial_query: str, qa_pairs: str) -> str:
    """Enhanced prompt for generating structured user goals."""
    return f"""TASK: Generate a comprehensive research goal framework based on the user's query and clarifying responses.

CONTEXT:
Initial Research Query: {initial_query}

Follow-up Q&A Session:
{qa_pairs}

OBJECTIVE: Create a SMART research goal (Specific, Measurable, Achievable, Relevant, Time-bound) that will guide an AI research system through multiple epochs of information gathering.

OUTPUT REQUIREMENTS:
Generate a JSON object with exactly these fields:

1. "primary_objective": 
   - A clear, specific research objective (2-3 sentences max)
   - Should be actionable and focused
   - Must directly address the user's core information need

2. "success_criteria": 
   - Array of 4-6 specific, measurable criteria
   - Each criterion should be objectively evaluable
   - Include both qualitative and quantitative measures where applicable
   - Examples: "Identify at least 5 recent studies from 2023-2024", "Explain the mechanism of action", "Compare 3+ different approaches"

3. "specific_questions":
   - Array of 4-6 precise questions that must be answered
   - Questions should be research-focused, not opinion-based
   - Each question should contribute to achieving the primary objective
   - Prioritize questions that require factual, evidence-based answers

QUALITY STANDARDS:
- Ensure the goal is neither too broad nor too narrow for a 3-epoch research process
- Balance depth and breadth appropriately
- Make criteria specific enough to be objectively evaluated by an AI system
- Focus on information that can be found through web research and academic sources

EXAMPLE STRUCTURE:
```json
{{
  "primary_objective": "Conduct a comprehensive analysis of [specific topic] including current state, recent developments, and practical applications.",
  "success_criteria": [
    "Identify and analyze at least 5 authoritative sources from the past 2 years",
    "Explain the fundamental principles and mechanisms involved",
    "Document specific use cases or applications with concrete examples",
    "Compare different approaches or methodologies with their pros/cons",
    "Identify current challenges and future research directions"
  ],
  "specific_questions": [
    "What are the latest developments in [topic] as of 2024?",
    "How does [mechanism/process] work in practical applications?",
    "What are the main advantages and limitations of current approaches?",
    "Which organizations or researchers are leading this field?",
    "What are the most promising future directions or emerging trends?"
  ]
}}
```

Generate the research goal framework now:"""


def enhanced_goal_alignment_prompt(user_goal, current_learnings: str, epoch: int) -> str:
    """Enhanced prompt for evaluating goal alignment."""
    return f"""TASK: Conduct a comprehensive evaluation of research progress against the established goal framework.

RESEARCH GOAL FRAMEWORK:
Primary Objective: {user_goal.primary_objective}

Success Criteria (Total: {len(user_goal.success_criteria)}):
{chr(10).join([f"  {i+1}. {criteria}" for i, criteria in enumerate(user_goal.success_criteria)])}

Specific Questions to Answer (Total: {len(user_goal.specific_questions)}):
{chr(10).join([f"  {i+1}. {question}" for i, question in enumerate(user_goal.specific_questions)])}

CURRENT RESEARCH STATE:
Epoch: {epoch}
Research Learnings Collected:
{current_learnings}

EVALUATION FRAMEWORK:
Analyze the research progress using these dimensions:

1. COVERAGE ANALYSIS: How well do the learnings address each success criterion?
2. QUESTION RESOLUTION: Which specific questions have been answered vs. remain open?
3. INFORMATION QUALITY: Assess the depth, accuracy, and relevance of collected information
4. GAP IDENTIFICATION: What critical information is still missing?
5. RESEARCH DIRECTION: What specific areas need further investigation?

OUTPUT REQUIREMENTS:
Generate a JSON object with these exact fields:

1. "alignment_score": Float (0.0-1.0)
   - 0.0-0.3: Minimal progress, major gaps remain
   - 0.4-0.6: Moderate progress, significant work needed
   - 0.7-0.8: Good progress, minor gaps remain
   - 0.9-1.0: Excellent progress, goal nearly/fully achieved

2. "criteria_met": Array of strings
   - List success criteria that are adequately addressed (>80% complete)
   - Use exact wording from the original criteria
   - Only include criteria with sufficient supporting evidence

3. "questions_answered": Array of strings
   - List specific questions that have been substantially answered
   - Use exact wording from the original questions
   - Require comprehensive answers, not partial information

4. "missing_aspects": Array of strings
   - Identify specific information gaps or areas needing more research
   - Be precise about what type of information is needed
   - Prioritize the most critical missing elements

5. "goal_achieved": Boolean
   - True only if: alignment_score ≥ 0.8 AND ≥80% criteria met AND ≥80% questions answered
   - Apply strict standards for goal completion

6. "continue_research": Boolean
   - False only if goal_achieved is true OR maximum epochs reached
   - Consider diminishing returns and research efficiency

7. "next_research_directions": Array of strings (2-4 items)
   - Specific, actionable research directions for the next epoch
   - Focus on the most important gaps identified
   - Provide concrete search strategies or topic areas

EVALUATION PRINCIPLES:
- Be objective and evidence-based in your assessment
- Require substantial evidence before marking criteria as "met"
- Consider both breadth and depth of information collected
- Prioritize authoritative and recent sources in your evaluation
- Balance thoroughness with research efficiency

Conduct the evaluation now:"""


def enhanced_serp_query_prompt(query: str, num_queries: int, learnings: str = None) -> str:
    """Enhanced prompt for generating SERP queries."""
    learning_context = f"\n\nPREVIOUS RESEARCH CONTEXT:\nRecent learnings from previous searches:\n{learnings}\n\nUse these learnings to generate more targeted and specific queries that fill information gaps." if learnings else ""
    
    return f"""TASK: Generate optimized search queries for comprehensive research coverage.

PRIMARY RESEARCH OBJECTIVE:
{query}
{learning_context}

SEARCH STRATEGY REQUIREMENTS:
Generate {num_queries} distinct search queries that collectively provide comprehensive coverage of the research topic. Each query should target different aspects, perspectives, or information types.

QUERY OPTIMIZATION PRINCIPLES:
1. SPECIFICITY: Use precise terminology and specific concepts
2. DIVERSITY: Cover different angles, timeframes, and information types
3. AUTHORITY: Target queries likely to return authoritative sources
4. RECENCY: Include queries for recent developments and current state
5. DEPTH: Balance broad overview queries with deep-dive specific queries

QUERY CATEGORIES TO CONSIDER:
- Academic/Research: Target scholarly articles and research papers
- Industry/Commercial: Focus on business applications and market analysis
- Technical/Mechanism: Deep-dive into how things work
- Comparative: Compare different approaches or solutions
- Temporal: Recent developments, trends, future outlook
- Regulatory/Policy: Legal, regulatory, or policy aspects
- Case Studies: Real-world applications and examples

OUTPUT REQUIREMENTS:
Generate a JSON object with a "queries" array. Each query object must have:

1. "query": String (optimized search query)
   - 3-8 words typically work best for search engines
   - Include specific terminology and key concepts
   - Avoid overly broad or generic terms
   - Consider search engine optimization principles

2. "research_goal": String (specific objective for this query)
   - Explain what type of information this query should uncover
   - Be specific about the expected information type
   - Connect to the overall research objective

EXAMPLE STRUCTURE:
```json
{{
  "queries": [
    {{
      "query": "recent advances artificial intelligence 2024 research",
      "research_goal": "Identify the latest AI research developments and breakthrough technologies from 2024"
    }},
    {{
      "query": "machine learning implementation challenges enterprise",
      "research_goal": "Understand practical challenges and solutions for implementing ML in business environments"
    }}
  ]
}}
```

QUALITY STANDARDS:
- Each query should be unique and non-overlapping
- Queries should complement each other for comprehensive coverage
- Avoid redundant or very similar search terms
- Ensure queries are likely to return high-quality, authoritative results
- Consider different search result types (academic, news, technical, commercial)

Generate the optimized search queries now:"""


def enhanced_content_processing_prompt(query: str, contents_str: str, num_learnings: int, num_follow_up_questions: int) -> str:
    """Enhanced prompt for processing search results."""
    return f"""TASK: Extract high-value insights and generate strategic follow-up questions from search results.

SEARCH QUERY CONTEXT: {query}

CONTENT ANALYSIS OBJECTIVE:
Process the provided content to extract the most valuable, specific, and actionable information while identifying areas requiring further investigation.

CONTENT TO ANALYZE:
{contents_str}

EXTRACTION REQUIREMENTS:

1. LEARNINGS EXTRACTION ({num_learnings} items):
   QUALITY CRITERIA:
   - SPECIFICITY: Include concrete data, numbers, dates, names, and specific details
   - ACTIONABILITY: Focus on information that directly addresses the research objective
   - AUTHORITY: Prioritize information from credible sources or expert opinions
   - RECENCY: Emphasize recent developments and current state information
   - UNIQUENESS: Avoid redundant or overly general statements

   INFORMATION TYPES TO PRIORITIZE:
   - Quantitative data and statistics
   - Recent developments and timeline information
   - Technical specifications and mechanisms
   - Expert opinions and authoritative statements
   - Comparative analysis and benchmarks
   - Case studies and real-world applications
   - Challenges, limitations, and solutions

2. FOLLOW-UP QUESTIONS ({num_follow_up_questions} items):
   STRATEGIC FOCUS:
   - Identify information gaps revealed by the current content
   - Generate questions that would deepen understanding
   - Focus on areas requiring additional research or clarification
   - Consider different perspectives or approaches not covered
   - Target specific details that could enhance the research

   QUESTION TYPES TO CONSIDER:
   - Mechanism/Process: "How does [specific process] work in [context]?"
   - Comparative: "How does [A] compare to [B] in terms of [specific criteria]?"
   - Temporal: "What are the latest developments in [specific area] since [timeframe]?"
   - Quantitative: "What are the specific metrics/costs/performance data for [topic]?"
   - Implementation: "What are the practical challenges of implementing [solution]?"

OUTPUT FORMAT:
Generate a JSON object with exactly these fields:

```json
{{
  "learnings": [
    "Specific, detailed learning with concrete information including numbers, dates, or specific entities",
    "Another learning that provides actionable insights with supporting details"
  ],
  "followUpQuestions": [
    "Strategic question that identifies a specific information gap requiring further research",
    "Another targeted question that would deepen understanding of the topic"
  ]
}}
```

QUALITY STANDARDS:
- Each learning should be self-contained and informative
- Learnings should include specific details (numbers, dates, names, locations)
- Avoid vague generalizations or common knowledge
- Follow-up questions should be research-focused, not opinion-based
- Questions should be specific enough to generate targeted search queries
- Prioritize information that directly supports the research objective

CONTENT PROCESSING PRINCIPLES:
- Extract information from multiple sources when available
- Cross-reference claims and identify authoritative sources
- Note any conflicting information or different perspectives
- Identify the most recent and relevant information
- Focus on information that advances the research objective

Process the content and generate insights now:"""


def enhanced_report_generation_prompt(prompt: str, learnings_string: str) -> str:
    """Enhanced prompt for generating comprehensive, detailed research reports as plain text."""
    return f"""TASK: Generate an exceptionally detailed, professional research report in valid JSON format. You are a world-class research analyst creating a comprehensive report for executive leadership.

ORIGINAL RESEARCH REQUEST:
{prompt}

RESEARCH METHODOLOGY:
This report synthesizes information from systematic AI-powered web search and content analysis across multiple research epochs, employing iterative refinement and goal-driven research strategies.

COLLECTED RESEARCH LEARNINGS:
{learnings_string}

CRITICAL JSON FORMATTING REQUIREMENTS:
- Return ONLY valid JSON - no markdown code blocks or extra text
- Escape all special characters properly in strings
- Use \\n for line breaks within the text content
- Use \\t for tabs within the text content  
- Escape quotes as \\" within string values
- Ensure the JSON structure is complete and valid

OUTPUT FORMAT:
Return a single JSON object with this exact structure:
{{
  "reportText": "[comprehensive detailed report content with proper escaping]"
}}

ENHANCED REPORT STRUCTURE (within the reportText field - PLAIN TEXT ONLY):

Create a report with the following sections, using clear headings and professional formatting:

TITLE: [Extract and create a specific, descriptive title from the research request - NOT "Initial Query"]

EXECUTIVE SUMMARY
- Lead with the most significant findings and their implications
- Include specific quantitative data and metrics where available
- Highlight key trends, patterns, and breakthrough discoveries
- Present clear conclusions and strategic recommendations
- Summarize the scope and confidence level of findings
- Target length: 300-400 words with high-impact insights

INTRODUCTION
- Clearly state the research objective and scope
- Provide relevant background context and current state of knowledge
- Explain the significance and relevance of this research
- Outline the systematic research methodology employed
- Define key terms and concepts if necessary
- Target length: 250-350 words

DETAILED FINDINGS AND ANALYSIS
Organize findings into 4-6 logical thematic sections with descriptive headings:

[Section 1: Primary Research Area]
- Present the most important findings with specific data
- Include percentages, statistics, dates, and concrete numbers
- Cite authoritative sources and expert opinions
- Analyze trends and patterns
- Compare different approaches or methodologies

[Section 2: Secondary Research Area]
- Focus on complementary findings and supporting evidence
- Highlight regional, demographic, or temporal variations
- Include case studies and real-world applications
- Present comparative analysis and benchmarking

[Continue with additional sections as needed]
- Each section should be 400-600 words
- Use specific data points and evidence-based conclusions
- Maintain professional, analytical tone throughout

SYNTHESIS AND CROSS-CUTTING ANALYSIS
- Integrate findings across different research areas
- Identify recurring themes and patterns
- Resolve contradictions or conflicting information
- Highlight knowledge gaps and research limitations
- Present validated conclusions through multiple source corroboration
- Target length: 300-400 words

IMPLICATIONS AND RECOMMENDATIONS
- Analyze strategic, practical, and policy implications
- Provide specific, actionable recommendations
- Discuss potential future developments and trends
- Address different stakeholder perspectives
- Consider implementation challenges and opportunities
- Target length: 250-350 words

CONCLUSIONS
- Summarize the most significant findings and their importance
- Restate key recommendations and their expected impact
- Comment on the strength and reliability of the evidence
- Suggest areas for future research or investigation
- Target length: 150-200 words

QUALITY STANDARDS FOR EXCEPTIONAL REPORTS:
1. SPECIFICITY: Replace generic language with precise, data-driven statements
2. AUTHORITY: Ground all claims in credible sources and research
3. CLARITY: Use clear, professional language appropriate for executive audiences
4. INSIGHT: Go beyond information compilation to provide analytical insights
5. STRUCTURE: Organize information logically with smooth transitions
6. IMPACT: Focus on findings that matter and have practical implications
7. EVIDENCE: Support conclusions with specific examples, statistics, and sources

CONTENT TRANSFORMATION GUIDELINES:
- Convert research learnings into strategic intelligence
- Transform data points into actionable insights
- Elevate findings to executive-level recommendations
- Ensure every statement adds value and advances understanding
- Maintain objectivity while highlighting significance
- Use professional consulting report language and tone

TARGET REPORT LENGTH: 2000-3000 words total
TONE: Professional, analytical, authoritative, and insightful
AUDIENCE: Executive leadership requiring strategic intelligence

EXAMPLE ENHANCED STRUCTURE:
{{
  "reportText": "COMPREHENSIVE ANALYSIS OF [SPECIFIC TOPIC]\\n\\nEXECUTIVE SUMMARY\\n\\nThis comprehensive research investigation into [topic] reveals [X] critical findings with significant implications for [stakeholders]. Analysis of [number] authoritative sources identifies [specific breakthrough/trend] with [quantitative impact]. Key discoveries include [specific data point], [trend with timeframe], and [strategic insight]. Primary recommendations include [actionable recommendation] and [strategic priority]. The research demonstrates [confidence level] that [specific prediction] will occur by [timeframe].\\n\\n[Continue with structured sections...]"
}}

CRITICAL SUCCESS FACTORS:
- Transform every research learning into strategic intelligence
- Provide executive-level insights that justify attention and resources
- Include specific, measurable findings with supporting evidence
- Maintain professional consulting report quality
- Ensure comprehensive coverage while maintaining focus
- Address practical implementation and real-world applications

Generate the exceptional, detailed research report now:"""

