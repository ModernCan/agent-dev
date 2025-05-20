# Water Quality Analysis Workflow: Sequential Problem-Solving with Prompt Chaining

This document explains how the prompt chaining pattern is applied to water quality analysis, creating a sequential workflow where each step builds upon the previous one to produce comprehensive, high-quality assessments.

## What is Prompt Chaining?

Prompt chaining is a pattern that breaks down complex tasks into a sequence of simpler steps, where each step:
- Focuses on a specific aspect of the overall task
- Uses the output from previous steps as context
- May include quality checks to ensure proper progression

This approach is similar to a water treatment plant itself, where water moves through multiple treatment stages, with each stage handling a specific aspect of purification, and quality checks ensuring the process is working correctly.

## The Water Quality Analysis Workflow

Our implementation demonstrates a four-stage workflow for analyzing water quality samples:

1. **Parameter Analysis**: Basic assessment of water quality parameters
2. **Treatment Recommendations**: Suggested methods to address water quality issues
3. **Compliance Evaluation**: Assessment of regulatory compliance
4. **Report Generation**: Comprehensive report combining all analyses

Between stages 1 and 2, there's a quality gate that ensures the initial analysis covers key water quality aspects before proceeding.

## How It Works

### 1. Parameter Analysis
The workflow begins with raw water sample data containing measurements like pH, turbidity, dissolved oxygen, etc. The first LLM call analyzes these parameters to provide an initial assessment of water quality, potential contamination issues, and health concerns.

```python
def analyze_parameters(self, state: WaterQualityState) -> Dict[str, str]:
    """First analysis step: Assess basic water quality parameters."""
    parameters_text = "\n".join([f"- {param}: {value}" for param, value in state['sample_data'].items()])
    
    prompt = f"""Analyze the following water quality parameters and provide an initial assessment:
    {parameters_text}
    Consider potential contaminants, general water quality, and any immediate concerns.
    """
    
    msg = self.llm.invoke(prompt)
    return {"initial_analysis": msg.content}
```

### 2. Quality Gate
Before proceeding to treatment recommendations, the workflow checks if the initial analysis meets quality standards:

```python
def check_analysis_quality(self, state: WaterQualityState) -> str:
    """Quality gate to verify if the initial analysis is sufficient."""
    required_topics = ["pH", "turbidity", "dissolved solids", "contaminant"]
    analysis_text = state["initial_analysis"].lower()
    
    # Count how many required topics are mentioned
    topics_covered = sum(1 for topic in required_topics if topic in analysis_text)
    
    # Pass if at least 3 of the required topics are covered
    if topics_covered >= 3 and len(analysis_text) > 200:
        return "Pass"
    return "Fail"
```

### 3. Treatment Recommendations
If the initial analysis passes the quality gate, the workflow proceeds to generate treatment recommendations. This step uses both the sample data and the initial analysis as context:

```python
def recommend_treatment(self, state: WaterQualityState) -> Dict[str, str]:
    """Second analysis step: Recommend appropriate water treatment methods."""
    prompt = f"""Based on the following water quality analysis, recommend appropriate treatment methods:
    WATER QUALITY ANALYSIS:
    {state['initial_analysis']}
    SAMPLE DATA:
    {state['sample_data']}
    Provide specific treatment recommendations including...
    """
```

### 4. Compliance Evaluation
Next, the workflow evaluates regulatory compliance, building on all previous analyses:

```python
def evaluate_compliance(self, state: WaterQualityState) -> Dict[str, str]:
    """Third analysis step: Evaluate regulatory compliance of the water sample."""
    prompt = f"""Evaluate the regulatory compliance of this water sample based on the following information:
    WATER QUALITY ANALYSIS:
    {state['initial_analysis']}
    SAMPLE DATA:
    {state['sample_data']}
    RECOMMENDED TREATMENTS:
    {state['treatment_recommendations']}
    """
```

### 5. Report Generation
Finally, the workflow combines all analyses into a comprehensive report:

```python
def generate_report(self, state: WaterQualityState) -> Dict[str, str]:
    """Final analysis step: Generate comprehensive water quality report."""
    prompt = f"""Create a comprehensive water quality report based on all the following analyses:
    SAMPLE DATA:
    {state['sample_data']}
    INITIAL ANALYSIS:
    {state['initial_analysis']}
    TREATMENT RECOMMENDATIONS:
    {state['treatment_recommendations']}
    COMPLIANCE EVALUATION:
    {state['compliance_evaluation']}
    """
```

## Business Value for Water Utilities

This sequential approach delivers significant benefits for water quality analysis:

1. **Improved Accuracy**: Each step focuses on a specific aspect, allowing for more detailed and accurate analysis
2. **Quality Assurance**: Built-in quality gates ensure analyses meet standards before proceeding
3. **Comprehensive Context**: Later steps have access to all previous analyses, enabling more informed recommendations
4. **Transparent Process**: The sequential workflow makes it easy to trace how conclusions were reached
5. **Modular Design**: Each step can be independently improved or updated as regulations or best practices change

## Practical Applications

This pattern is valuable for water utilities in scenarios like:

- **Routine Water Quality Monitoring**: Processing regular samples with consistent, high-quality analysis
- **Contamination Incident Response**: Analyzing emergency samples with a standardized, thorough approach
- **Regulatory Reporting**: Ensuring complete documentation for compliance submissions
- **Treatment Plant Optimization**: Analyzing samples to fine-tune treatment processes
- **Source Water Assessment**: Evaluating new water sources with comprehensive analysis

## Implementation Considerations

When implementing this pattern:

1. **Define Clear Step Boundaries**: Each step should have a specific, well-defined purpose
2. **Design Effective Quality Gates**: Create meaningful checks that prevent low-quality analyses from proceeding
3. **Ensure Context Transfer**: Make sure each step has access to relevant information from previous steps
4. **Balance Detail and Efficiency**: Optimize prompts to get thorough analysis without excessive verbosity
5. **Maintain Traceability**: Preserve intermediate results for audit trails and explanation

By implementing the prompt chaining pattern for water quality analysis, utilities can create more reliable, thorough, and transparent assessment processes that improve both operational efficiency and regulatory compliance.
