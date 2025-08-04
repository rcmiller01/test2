# Technical Flow Diagram - AI Companion Message Processing

## User Message Processing Flow

```
┌─────────────────┐
│   User Input    │
│ "I'm stressed   │
│  about work"    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ process_message │ ◄── Entry point: emotional_ai.py:104
│ (user_id,       │     • Creates/retrieves ConversationContext
│  thread_id,     │     • Adds message to history
│  message)       │     • Analyzes intent
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ _analyze_intent │ ◄── emotional_ai.py:143
│                 │     • Scans for keywords
│ Keywords found: │     • "stressed" → emotional intent
│ ["stress"]      │     • Returns: {"type": "emotional", 
│                 │       "confidence": 0.9}
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│_handle_emotional│ ◄── emotional_ai.py:500
│_conversation    │     • Analyzes emotional context
│                 │     • Detects "needs_support": True
│ Emotional       │     • Increases trust_level += 0.05
│ Context:        │     • Increases emotional_bond += 0.03
│ needs_support:  │
│ True            │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│_analyze_emotional│ ◄── emotional_ai.py:635
│_context         │     • Scans for emotional indicators
│                 │     • therapeutic_indicators: ["stressed"]
│ Adjusts bonds:  │     • Updates ConversationContext
│ trust: 0.5→0.55 │     • Returns emotional_context dict
│ bond: 0.0→0.03  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│_build_adaptive_ │ ◄── emotional_ai.py:665
│emotional_prompt │     • Creates therapeutic prompt
│                 │     • "User needs emotional support.
│ Generated:      │       Use active listening..."
│ Therapeutic     │     • Includes user message in context
│ System Prompt   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│_call_local_model│ ◄── emotional_ai.py:610
│                 │     • Sends prompt to emollama
│ Payload:        │     • Uses context.personality_temperature
│ • prompt        │     • Returns empathetic response
│ • temperature   │
│ • max_tokens    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   AI Response   │
│ "I understand   │ ◄── Therapeutic, supportive response
│  you're feeling │     • Acknowledges emotions
│  stressed. Work │     • Offers validation and support
│  can be really  │     • Builds emotional connection
│  overwhelming   │
│  sometimes..."  │
└─────────────────┘
```

## Alternative Flow: Utility Request

```
┌─────────────────┐
│   User Input    │
│ "Send SMS to    │
│  John saying    │
│  hello"         │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ _analyze_intent │ ◄── Keywords: ["send", "sms"]
│                 │     Returns: {"type": "utility", 
│ Result:         │      "confidence": 0.7}
│ "utility"       │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│_handle_utility_ │ ◄── emotional_ai.py:175
│request          │     • Calls _parse_utility_request
│                 │     • Identifies function needed
│                 │     • Executes via N8N workflow
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│_parse_utility_  │ ◄── emotional_ai.py:190
│request          │     • Scans message for patterns
│                 │     • "sms" keyword → sms_messaging
│ Returns:        │     • Extracts parameters
│ {function:      │
│  "sms_messaging"│
│  parameters:... │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ N8N Workflow    │ ◄── n8n_client.execute_workflow
│ Execution       │     • Routes to _handle_sms_messaging
│                 │     • Simulates SMS sending
│ _handle_sms_    │     • Returns success response
│ messaging()     │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│_format_utility_ │ ◄── emotional_ai.py:410
│response         │     • Formats response for user
│                 │     • "📱 SMS sent to John: hello"
│ Result:         │     • User-friendly messaging
│ Formatted       │
│ Success Message │
└─────────────────┘
```

## Code Analysis Flow: OpenRouter Integration

```
┌─────────────────┐
│   User Input    │
│ "Debug this     │
│  Python code:   │
│  def hello():"  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ _analyze_intent │ ◄── Keywords: ["debug", "code"]
│                 │     Returns: {"type": "coding",
│ Result:         │      "confidence": 0.8}
│ "coding"        │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│_handle_coding_  │ ◄── emotional_ai.py:165
│request          │     • Routes to OpenRouter
│                 │     • Specialized for code analysis
│                 │     • Uses external AI expertise
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ OpenRouter API  │ ◄── openrouter_client.generate_code
│                 │     • Sends to specialized code model
│ Processes:      │     • Returns detailed analysis
│ • Code debugging│     • Professional code review
│ • Optimization  │
│ • Best practices│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   AI Response   │
│ "I've processed │ ◄── Wraps OpenRouter response
│  your coding    │     • Indicates specialized processing
│  request through│     • Provides code solution
│  my specialized │     • Maintains conversational tone
│  coding         │
│  assistant..."  │
└─────────────────┘
```

## Relationship Development Over Time

```
Day 1: First Contact
┌─────────────────┐
│ ConversationContext Created
│ • emotional_bond_level: 0.0
│ • intimacy_level: 0.0  
│ • trust_level: 0.5
│ • current_mood: "neutral"
└─────────────────┘
          │
          ▼ Each successful interaction
┌─────────────────┐
│ Bond Adjustments
│ • Utility success: trust += 0.05
│ • Emotional support: bond += 0.03
│ • Affection shown: intimacy += 0.1
│ • Vulnerability shared: trust += 0.08
└─────────────────┘
          │
          ▼ Continuous adaptation
┌─────────────────┐
│ Response Style Evolution
│ if trust > 0.7 and bond > 0.6:
│   style = "intimate and connected"
│ elif bond > 0.4:
│   style = "warm and friendly"
│ else:
│   style = "helpful and professional"
└─────────────────┘
```

## Memory System Integration

```
┌─────────────────┐
│ "Remember that  │
│  I prefer       │
│  coffee over    │
│  tea"           │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│_parse_utility_  │ ◄── Detects "remember" keyword
│request          │     Routes to memory_system
│                 │
│ Function:       │
│ memory_system   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│_handle_memory_  │ ◄── emotional_ai.py:863
│system           │     • Stores personal preference
│                 │     • Increases emotional_bond
│ Action: store   │     • Returns confirmation
│ Content: coffee │
│ preference      │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Later Reference │
│ "What's my      │ ◄── AI can recall and reference
│  drink          │     stored preferences in future
│  preference?"   │     conversations, showing
│                 │     personal attention and care
│ → "You prefer   │
│    coffee!"     │
└─────────────────┘
```

## Error Handling & Graceful Degradation

```
┌─────────────────┐
│ User Request    │
│ (Any type)      │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Try Processing  │
│ • Intent analysis
│ • Function routing
│ • Execution
└─────────┬───────┘
          │
          ▼ If error occurs
┌─────────────────┐
│ Exception       │
│ Handling        │ ◄── Multiple try/catch blocks
│                 │     • Log error details
│ • Log error     │     • Return helpful message
│ • Graceful      │     • Maintain conversation flow
│   response      │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ User-Friendly   │
│ Error Response  │ ◄── "I had trouble with that.
│                 │      Could you try rephrasing?"
│ • Acknowledges  │     • Keeps user engaged
│   issue         │     • Suggests alternatives
│ • Offers help   │     • Maintains helpfulness
└─────────────────┘
```
