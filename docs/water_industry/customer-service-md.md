# Water Utility Customer Service: Smart Routing for Specialized Support

This document explains how the routing pattern is applied to water utility customer service, enabling more effective and specialized handling of diverse customer inquiries.

## What is Routing?

Routing is a pattern that:
1. Analyzes and classifies incoming requests
2. Directs each request to a specialized handler optimized for that category
3. Processes the request with category-specific expertise and information
4. Returns appropriate, specialized responses

This approach resembles how a water utility's front desk might direct customers to different departments—sending billing questions to the finance department, water quality concerns to the water quality team, and service disruptions to the operations team.

## The Water Utility Customer Service System

Our implementation demonstrates a comprehensive customer service routing system with six specialized handlers:

1. **Billing Specialist**: Handles inquiries about bills, payments, and accounts
2. **Service Disruption Responder**: Addresses outages, leaks, and pressure issues
3. **Water Quality Expert**: Responds to concerns about water taste, odor, and safety
4. **Conservation Advisor**: Provides guidance on water efficiency and restrictions
5. **New Service Coordinator**: Facilitates new connections and service changes
6. **General Information Provider**: Handles miscellaneous inquiries

The system not only categorizes inquiries but also assigns priority levels, enabling appropriate urgency in responses.

## How It Works

### 1. Inquiry Classification

The system first analyzes each customer inquiry to determine both its category and priority:

```python
def classify_inquiry(self, state: CustomerServiceState) -> Dict[str, str]:
    """Classifies a customer inquiry by category and priority."""
    classification = self.router.invoke([
        SystemMessage(
            content="""You are a water utility customer service classifier. 
            Analyze customer inquiries and classify them by category and priority.
            
            Categories:
            - billing: Questions about bills, payments, rates, or account status
            - service_disruption: Reports of service outages, low pressure, or leaks
            - water_quality: Concerns about water taste, odor, color, or safety
            ...
            
            Priority levels:
            - low: General information requests with no time sensitivity
            - medium: Issues that should be addressed in the next 1-2 business days
            - high: Urgent issues requiring same-day attention
            - emergency: Critical issues requiring immediate response
            """
        ),
        HumanMessage(content=state["inquiry"]),
    ])
    
    return {
        "category": classification.category,
        "priority": classification.priority
    }
```

### 2. Intelligent Routing

Based on the classification, the system routes the inquiry to the appropriate specialized handler:

```python
def route_inquiry(self, state: CustomerServiceState) -> str:
    """Routes the inquiry to the appropriate specialized handler."""
    return f"handle_{state['category']}"

# In the workflow definition:
cs_workflow.add_conditional_edges(
    "classify_inquiry",
    self.route_inquiry,
    {
        "billing": "handle_billing",
        "service_disruption": "handle_service_disruption",
        "water_quality": "handle_water_quality",
        "conservation": "handle_conservation",
        "new_service": "handle_new_service",
        "general": "handle_general",
    },
)
```

### 3. Specialized Handling

Each handler is optimized for its specific domain, with prompts tailored to the category and priority:

```python
def handle_water_quality(self, state: CustomerServiceState) -> Dict[str, str]:
    """Specialized handler for water quality inquiries."""
    prompt = f"""You are a water quality specialist at a water utility. Provide a helpful response to the following customer inquiry:

    Customer inquiry: {state['inquiry']}

    This has been classified as a {state['priority']} priority water quality inquiry.

    Address the inquiry with:
    1. Acknowledgment of their water quality concern
    2. Factual information about water quality standards and testing procedures
    3. Common causes for water quality issues like taste, odor, or appearance
    ...
    """
    
    msg = self.llm.invoke(prompt)
    return {"response": msg.content}
```

Some handlers, like the service disruption handler, include special logic for high-priority situations:

```python
def handle_service_disruption(self, state: CustomerServiceState) -> Dict[str, str]:
    """Specialized handler for service disruption inquiries."""
    # Emergency priorities get a special response
    if state['priority'] == "emergency":
        emergency_prompt = f"""You are a water utility emergency response specialist...
```

## Business Value for Water Utilities

This routing approach delivers significant benefits for water utility customer service:

1. **Specialized Expertise**: Each customer inquiry receives domain-specific knowledge
2. **Appropriate Urgency**: Response tone and content match the priority level
3. **Consistent Quality**: Standardized handling within each category ensures reliability
4. **Scalability**: Easy to add new specialized handlers as needs evolve
5. **Enhanced Customer Experience**: More relevant, accurate responses increase satisfaction

## Practical Applications

This pattern is valuable for water utilities in scenarios like:

- **Customer Service Centers**: Efficient handling of diverse customer inquiries
- **Emergency Response Systems**: Prioritizing and routing service disruption reports
- **Online Support Portals**: Directing web form submissions to appropriate departments
- **Email Management**: Categorizing and routing incoming customer emails
- **Social Media Monitoring**: Classifying and addressing social media mentions

## Implementation Considerations

When implementing this pattern:

1. **Clear Category Definitions**: Define distinct, comprehensive categories that cover all likely inquiries
2. **Effective Classification Prompts**: Provide detailed classification criteria to ensure accurate routing
3. **Priority Handling**: Design special handling for emergencies and high-priority inquiries
4. **Specialized Knowledge**: Create handler prompts with specific domain expertise
5. **Fallback Mechanisms**: Include general handlers for inquiries that don't fit neatly into categories

## Advanced Applications

This pattern can be extended in several ways:

1. **Multi-Level Routing**: Add sub-categories for more specialized handling
2. **Hybrid Human-AI Systems**: Route complex cases to human experts while AI handles routine inquiries
3. **Context-Aware Routing**: Include customer history, location, or other context in routing decisions
4. **Learning Systems**: Update routing rules based on feedback about routing accuracy
5. **Cross-Category Inquiries**: Develop mechanisms for inquiries that span multiple categories

By implementing the routing pattern for customer service, water utilities can create more efficient, effective support systems that deliver specialized expertise for every customer inquiry while maintaining consistent quality and appropriate urgency.
