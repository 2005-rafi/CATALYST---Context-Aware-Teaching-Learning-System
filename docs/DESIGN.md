# CATALYST — DESIGN SYSTEM & UI/UX SPECIFICATION

> **Document purpose:** Master UI/UX and frontend design specification for the CATALYST AI chatbot / agentic interface.
>
> **Audience:** AI coding agents, frontend developers, UI/UX designers, and future maintainers.
>
> **Status:** Production design specification.
>
> **Primary objective:** Build a professional, distinctive, responsive, accessible, reusable, and production-grade AI interface without unnecessary architectural or visual complexity.

---

# 1. PRODUCT DEFINITION

## 1.1 Product

**CATALYST** is an AI-powered conversational interface capable of:

* Natural-language conversation
* Streaming AI responses
* Long-form text generation
* Agentic operations
* Tool execution
* Intermediate agent states
* Context-aware interactions
* Potential file / attachment interactions
* Dynamic response rendering
* Future extensibility toward multi-step AI workflows

CATALYST must therefore be designed as an **AI workspace**, not as a traditional messaging application.

---

# 2. PRIMARY DESIGN OBJECTIVE

The interface must communicate:

```text
Intelligence
      +
Professionalism
      +
Speed
      +
Control
      +
Clarity
```

The user should feel that CATALYST is:

* Fast
* Reliable
* Focused
* Technically capable
* Calm
* Modern
* Professional
* Predictable
* Easy to control

The interface must NOT feel:

* Toy-like
* Overly futuristic
* Visually noisy
* Generic
* Like a standard messaging application
* Like a conventional SaaS dashboard
* Overloaded with cards
* Dependent on gradients and decorative effects

---

# 3. CORE DESIGN PHILOSOPHY

## 3.1 CATALYST Design Principle

> **"The interface should disappear behind the intelligence."**

The UI should support the conversation rather than compete with it.

The visual system must establish:

```text
Conversation = Primary
AI state     = Secondary
Controls     = Supporting
Metadata     = Tertiary
Decoration   = Minimal
```

---

# 4. DESIGN LANGUAGE

## 4.1 Design Language Name

### CATALYST — "Intelligent Precision"

The visual language combines:

* Functional minimalism
* Editorial typography
* Controlled spatial asymmetry
* Technical precision
* Responsive composition
* Subtle motion
* Strong hierarchy
* Controlled visual depth

The interface should feel **engineered rather than decorated**.

---

# 5. BRAND CHARACTER

CATALYST should visually communicate:

| Characteristic | UI Expression                     |
| -------------- | --------------------------------- |
| Intelligent    | Clear information hierarchy       |
| Fast           | Responsive interaction and motion |
| Professional   | Restrained visual system          |
| Technical      | Precise spacing and states        |
| Human          | Comfortable typography            |
| Powerful       | Strong interaction hierarchy      |
| Trustworthy    | Transparent system states         |
| Modern         | Adaptive layouts                  |
| Distinctive    | Controlled asymmetry              |

---

# 6. VISUAL IDENTITY

CATALYST should NOT copy:

* ChatGPT
* Claude
* Gemini
* Copilot
* Slack
* Discord
* Traditional SaaS dashboards

Existing AI interfaces may establish interaction conventions, but CATALYST must develop its own visual identity.

---

# 7. VISUAL PRINCIPLE — CONTROLLED ASYMMETRY

CATALYST should avoid making every component symmetrical and card-based.

Use:

```text
Aligned structure
+
Intentional asymmetry
+
Strong whitespace
```

Examples:

* User messages may use a constrained content region.
* AI responses should prioritize readable editorial width.
* Tool states may use compact technical indicators.
* Supporting information may occupy secondary visual regions.
* Desktop layouts can introduce contextual side regions without permanently dividing the interface.

Asymmetry must remain intentional and functional.

---

# 8. COLOR SYSTEM

## 8.1 Existing Color Foundation

The current implementation already uses Material-style semantic color tokens:

```text
--md-sys-color-primary
--md-sys-color-secondary
--md-sys-color-tertiary
--md-sys-color-background
--md-sys-color-surface
--md-sys-color-surface-container
--md-sys-color-outline
--md-sys-color-error
...
```

These tokens must remain the **centralized color foundation**.

However:

> Material Design is the token foundation, NOT the visual identity of CATALYST.

Do not build a visually generic Material UI.

---

# 9. COLOR ARCHITECTURE

The existing semantic system should be interpreted through CATALYST's own design language.

## 9.1 Color hierarchy

```text
Background
    ↓
Surface
    ↓
Surface Container
    ↓
Content
    ↓
Primary Interaction
    ↓
Semantic State
```

---

# 10. COLOR ROLES

## Primary

Used for:

* Primary CTA
* Active interaction
* Important controls
* Selected state
* Focus state where appropriate

Do NOT use primary color everywhere.

---

## Secondary

Used for:

* Supporting controls
* Secondary actions
* Supporting visual emphasis

---

## Tertiary

Used sparingly for:

* Additional system distinction
* Agent/tool state
* Special contextual information

---

## Background

The application canvas.

It must remain visually calm.

---

## Surface

Used for:

* Input area
* Floating interaction regions
* Secondary panels
* Contextual areas

---

## Surface Container

Used to establish depth without excessive shadows.

Prefer:

```text
Surface differentiation
>
Heavy shadows
```

---

## Outline

Used for:

* Boundaries
* Input states
* Dividers
* Subtle structural separation

Borders should be subtle.

---

# 11. DARK THEME

Dark mode must NOT be treated as a simple color inversion.

The existing dark tokens establish:

```text
Deep background
+
Layered surfaces
+
Soft foreground
+
Controlled accent
```

Maintain this principle.

Avoid pure:

```text
#000000
```

for the primary application background unless specifically required.

Avoid excessive pure white text.

---

# 12. LIGHT THEME

Light mode should feel:

* Clean
* Soft
* Professional
* Spacious
* Calm

Avoid making the interface pure white everywhere.

Use the existing surface hierarchy to create subtle separation.

---

# 13. COLOR RULES

### Rule 01

Every color must have a semantic purpose.

### Rule 02

No arbitrary component-level colors.

### Rule 03

No hardcoded colors in component CSS.

### Rule 04

All colors must originate from centralized design tokens.

### Rule 05

Light and dark themes must use the same semantic token names.

### Rule 06

Changing the theme must not require component-level rewrites.

---

# 14. TYPOGRAPHY

Typography is one of the primary identity elements of CATALYST.

Prioritize:

```text
Readability
+
Hierarchy
+
Density control
+
Long-form comfort
```

---

## 14.1 Typography hierarchy

Define centralized typography tokens for:

```text
Display
Heading 1
Heading 2
Heading 3
Body Large
Body
Body Small
Label
Caption
Code
```

Do not individually define arbitrary font sizes inside components.

---

# 15. AI RESPONSE TYPOGRAPHY

AI-generated text can become extremely long.

Therefore:

### AI responses must optimize for reading.

Use:

* Comfortable line height
* Controlled paragraph width
* Clear headings
* List spacing
* Code block separation
* Table readability
* Quote differentiation
* Inline emphasis
* Link distinction

Avoid extremely wide text containers.

---

# 16. CONTENT WIDTH

Long-form AI text should have an intentional reading width.

Recommended conceptual structure:

```text
Application width
        ↓
Conversation width
        ↓
Response reading width
```

The AI response should not automatically stretch across the entire desktop viewport.

---

# 17. SPACING SYSTEM

All spacing must be tokenized.

Example conceptual scale:

```text
space-1
space-2
space-3
space-4
space-5
space-6
space-8
space-10
space-12
...
```

The exact values should be controlled centrally.

Components must consume spacing tokens.

Never create random values such as:

```css
margin: 13px;
padding: 19px;
gap: 27px;
```

unless the value is intentionally encoded as a design token.

---

# 18. BORDER RADIUS

Use restrained geometry.

Avoid:

```text
Everything = pill
Everything = huge rounded rectangle
```

Use different radius tokens for:

```text
Small controls
Inputs
Messages
Panels
Dialogs
Large containers
```

Radius should establish hierarchy.

---

# 19. ELEVATION

CATALYST should use **layering before shadows**.

Preferred hierarchy:

```text
Background
   ↓
Surface
   ↓
Surface Container
   ↓
Floating Surface
```

Shadows should communicate elevation rather than decoration.

Avoid excessive shadows.

---

# 20. LAYOUT ARCHITECTURE

CATALYST is fundamentally a:

> **Conversation-first adaptive workspace.**

The primary desktop structure may conceptually follow:

```text
┌────────────────────────────────────────────────────┐
│                 Application Header                 │
├──────────────┬──────────────────────┬──────────────┤
│              │                      │              │
│ Navigation   │    Conversation      │ Context /    │
│              │                      │ Activity     │
│              │                      │              │
│              │                      │              │
├──────────────┴──────────────────────┴──────────────┤
│                Composer / Input                    │
└────────────────────────────────────────────────────┘
```

However:

> This is a structural model, not a requirement for permanent three-column UI.

The contextual region should appear only when useful.

---

# 21. RESPONSIVE ARCHITECTURE

## Desktop

Use available horizontal space for:

* Conversation
* Optional navigation
* Optional context
* Agent activity

---

## Tablet

Reduce simultaneous regions.

Potential structure:

```text
Navigation
     ↓
Conversation
     ↓
Context = collapsible
```

---

## Mobile

Conversation becomes the dominant interface.

```text
┌────────────────────┐
│ Header             │
├────────────────────┤
│                    │
│ Conversation       │
│                    │
│                    │
├────────────────────┤
│ Composer           │
└────────────────────┘
```

Do not simply shrink desktop components.

---

# 22. MOBILE RULE

Mobile must be designed around:

```text
Thumb reach
+
Keyboard
+
Viewport changes
+
Scrolling
+
Input accessibility
```

The composer must remain usable when the mobile keyboard appears.

---

# 23. COMPONENT ARCHITECTURE

The component architecture must follow:

```text
Design Tokens
      ↓
Primitive Components
      ↓
Composite Components
      ↓
Conversation Components
      ↓
Agent Components
      ↓
Layout Components
      ↓
Pages
```

---

# 24. DESIGN TOKEN LAYER

Centralize:

```text
Colors
Typography
Spacing
Radius
Elevation
Motion
Breakpoints
Z-index
Component dimensions
```

No component should own global design decisions.

---

# 25. PRIMITIVE COMPONENTS

Build reusable primitives:

```text
Button
IconButton
Input
Textarea
Avatar
Badge
Tooltip
Divider
Spinner
Skeleton
Popover
Dialog
Dropdown
Tabs
Checkbox
Switch
Progress
```

Primitives must remain generic.

---

# 26. COMPOSITE COMPONENTS

Examples:

```text
SearchInput
MessageActions
AttachmentPreview
FileReference
StatusIndicator
ContextSelector
AgentStatus
ToolStatus
ResponseToolbar
```

Composite components should combine primitives rather than recreate them.

---

# 27. CONVERSATION COMPONENTS

Core components:

```text
Conversation
Message
UserMessage
AssistantMessage
MessageContent
MessageActions
MessageMetadata
Attachment
Citation
CodeBlock
MarkdownContent
StreamingIndicator
RegenerateAction
FeedbackAction
```

---

# 28. AGENT COMPONENTS

Agentic workflows require dedicated state components.

Examples:

```text
AgentActivity
AgentPlanning
AgentThinking
ToolExecution
ToolResult
AgentWaiting
AgentApproval
AgentSuccess
AgentError
```

These components must communicate system state without exposing unnecessary internal reasoning.

---

# 29. AI STATE MODEL

The UI should conceptually support:

```text
IDLE
  ↓
SUBMITTING
  ↓
PROCESSING
  ↓
STREAMING
  ↓
COMPLETED
```

Agentic operations may additionally use:

```text
PLANNING
TOOL_RUNNING
WAITING_FOR_INPUT
WAITING_FOR_APPROVAL
FAILED
CANCELLED
```

The frontend should render state rather than infer state from arbitrary UI conditions.

---

# 30. STREAMING RESPONSE DESIGN

Streaming is a primary CATALYST interaction.

The interface must not wait for the complete response before rendering content.

Conceptual flow:

```text
User submits
      ↓
Immediate UI feedback
      ↓
Assistant message created
      ↓
Streaming begins
      ↓
Content progressively appears
      ↓
User can continue observing / scrolling
      ↓
Stream completes
      ↓
Final actions become available
```

---

# 31. STREAMING ANIMATION

Streaming must feel natural rather than simulated.

Do NOT:

* Animate every character independently
* Use excessive typewriter effects
* Delay already-received content artificially
* Make the user wait for decorative animation

Prefer:

```text
Real response stream
      +
Subtle rendering transition
      +
Minimal cursor/activity indicator
```

---

# 32. STREAMING CURSOR

A subtle streaming indicator may communicate:

```text
AI is still producing content
```

The indicator must disappear when streaming completes.

It should never remain permanently visible.

---

# 33. STREAMING SCROLL BEHAVIOR

Scrolling must be intelligent.

### User is at bottom:

Automatically follow new content.

```text
Streaming
    ↓
Viewport follows response
```

### User manually scrolls upward:

Do NOT force the viewport back to the bottom.

Instead:

```text
New content available
        ↓
[Jump to latest]
```

This is mandatory for long responses.

---

# 34. SCROLL LAW

Never steal scrolling control from the user.

The system may follow content only while the user is clearly following the conversation.

Once the user intentionally scrolls away:

> User owns the viewport.

---

# 35. MESSAGE APPEARANCE

Avoid traditional:

```text
User = giant bubble
AI = giant bubble
```

Instead use **editorial conversation blocks**.

The distinction between speakers should primarily come from:

* Alignment
* Typography
* Identity
* Spacing
* Subtle surface treatment
* Actions

This makes long conversations easier to read.

---

# 36. USER MESSAGE

User messages should be visually compact.

Prioritize:

```text
Message content
+
Attachments
+
Timestamp / metadata where useful
```

Avoid oversized containers around short prompts.

---

# 37. AI MESSAGE

AI messages receive more visual space because they contain more information.

Structure:

```text
AI Identity
      ↓
Response
      ↓
Supporting content
      ↓
Sources / metadata
      ↓
Actions
```

---

# 38. RESPONSE ACTIONS

Common actions:

```text
Copy
Regenerate
Edit
Retry
Feedback
Share
More
```

Actions should remain visually secondary to the response.

Do not permanently display every possible action at maximum prominence.

---

# 39. CODE BLOCKS

Code is a first-class AI output type.

Code blocks require:

* Dedicated surface
* Language identification
* Copy action
* Horizontal overflow handling
* Good contrast
* Readable monospace typography
* Responsive behavior

Never allow code to break the main page layout.

---

# 40. MARKDOWN

Markdown rendering must be treated as a design system.

Define consistent styling for:

```text
H1
H2
H3
Paragraph
List
Ordered List
Quote
Link
Code
Code Block
Table
Divider
Image
```

Do not allow browser-default Markdown styles.

---

# 41. TABLES

AI-generated tables must:

* Remain readable
* Support horizontal scrolling
* Maintain alignment
* Avoid breaking mobile layout

On mobile, large tables should become horizontally scrollable rather than compressed into unreadable text.

---

# 42. ATTACHMENTS

Attachments should communicate:

```text
File type
Name
Size
Status
Action
```

Do not create oversized file cards.

---

# 43. LOADING STATES

Loading should represent actual system activity.

Use:

```text
Skeleton
Spinner
Progress
Activity indicator
Streaming cursor
```

according to context.

Do not use skeletons for every component automatically.

---

# 44. SKELETON RULE

Skeleton UI is appropriate when:

```text
Expected content structure is known
+
Loading takes meaningful time
```

For fast operations, subtle state changes are preferable.

---

# 45. EMPTY STATES

Empty states must explain:

```text
What is this area?
What can the user do?
What should happen next?
```

Avoid empty screens containing only:

> "No data."

---

# 46. ERROR UX

Errors must be:

```text
Clear
Specific
Recoverable
Non-threatening
```

Example structure:

```text
Something went wrong.

The response could not be completed.

[Retry]
```

Avoid exposing raw backend errors directly.

---

# 47. AGENT ERROR UX

For agent operations:

```text
Action
   ↓
Failure
   ↓
Reason
   ↓
Recovery option
```

Where possible:

```text
Retry
Cancel
Edit input
Try another method
```

---

# 48. CONFIRMATION UX

Consequential operations require explicit user control.

```text
Agent proposes action
        ↓
User reviews
        ↓
User approves
        ↓
Action executes
```

Do not hide consequential actions behind ambiguous buttons.

---

# 49. TRUST & TRANSPARENCY

The interface should distinguish:

```text
AI generated
Retrieved
User supplied
System generated
Tool executed
Action proposed
Action completed
```

The user should not need to guess what actually happened.

---

# 50. HICK'S LAW

## Principle

> The more choices a user has, the longer the decision takes.

### CATALYST application

Do not expose every available AI operation simultaneously.

Instead:

```text
Primary action
    ↓
Secondary actions
    ↓
Advanced actions
```

Example:

```text
[Send]
```

rather than:

```text
[Send] [Regenerate] [Export] [Share] [Fork] [Analyze] [Retry] [Save] ...
```

Primary interactions must remain obvious.

### Rule

> Reduce visible decisions without reducing available capability.

Use progressive disclosure for advanced functionality.

---

# 51. FITTS'S LAW

## Principle

> The easier a target is to reach and the larger its effective target area, the easier and faster it is to interact with.

### CATALYST application

Important actions must have:

* Adequate target size
* Clear boundaries
* Predictable positioning
* Sufficient spacing

Critical mobile controls must be thumb-friendly.

Do not place tiny controls beside other tiny controls.

---

# 52. JAKOB'S LAW

## Principle

> Users expect interfaces to behave similarly to interfaces they already know.

CATALYST should respect established conventions for:

* Text input
* Sending
* Copying
* Scrolling
* Keyboard behavior
* Navigation
* Dialogs
* Buttons
* Selection
* File upload

However:

> Familiar interaction behavior does not require copying another product's visual identity.

CATALYST should innovate primarily through:

```text
Visual language
+
Composition
+
Agent interaction
+
Motion
```

while maintaining familiar interaction mechanics.

---

# 53. MILLER'S LAW

## Principle

> Working memory is limited; excessive simultaneous information increases cognitive load.

Do not make the user mentally track:

```text
Conversation
Agent state
Tool state
Sources
Context
Navigation
Settings
Notifications
Actions
```

all at once.

Use:

```text
Grouping
Hierarchy
Progressive disclosure
Whitespace
Sections
```

to reduce cognitive load.

### Important interpretation

Do not mechanically design around the old "7 ± 2" number.

Use the broader principle:

> **Break complex information into meaningful chunks.**

---

# 54. TESLER'S LAW

## Principle

> Every system has an irreducible amount of complexity. That complexity must live somewhere.

CATALYST should absorb complexity into the system wherever possible.

Example:

Instead of requiring the user to understand:

```text
Streaming protocol
Agent execution
Tool lifecycle
Context state
Request status
```

the interface should communicate:

```text
Working...
Searching...
Waiting for approval...
Completed.
```

The complexity should be handled by the product rather than transferred to the user.

---

# 55. COMBINED UX LAW

The five laws should work together:

```text
HICK
Reduce unnecessary choices
        ↓
FITTS
Make important actions easy to reach
        ↓
JAKOB
Use familiar interaction patterns
        ↓
MILLER
Reduce cognitive load
        ↓
TESLER
Absorb system complexity
```

Result:

```text
Simple interaction
+
Powerful underlying system
```

---

# 56. UX PRINCIPLE — USER CONTROL

The user must remain in control of:

```text
Input
Scrolling
Generation
Navigation
Agent actions
Context
Confirmation
```

Important actions must never feel irreversible unless clearly communicated.

---

# 57. UX PRINCIPLE — PROGRESSIVE DISCLOSURE

Default interface:

```text
Simple
```

Expanded interface:

```text
Detailed
```

Advanced interface:

```text
Technical
```

Do not expose technical complexity by default.

---

# 58. MOTION DESIGN

CATALYST uses motion as a functional communication system.

Motion communicates:

```text
Entry
Exit
State change
Progress
Relationship
Feedback
```

---

# 59. MOTION PRINCIPLES

### Fast interaction

Use short transitions.

### Content transition

Use subtle movement.

### Major layout transition

Use slightly longer transitions.

### Continuous agent activity

Use restrained motion.

Never make the interface feel constantly animated.

---

# 60. MOTION HIERARCHY

```text
Micro interaction
    ↓
Short
    ↓
Component transition
    ↓
Moderate
    ↓
Major layout transition
    ↓
Controlled / deliberate
```

Exact timing must be centralized through motion tokens.

---

# 61. REDUCED MOTION

Respect:

```text
prefers-reduced-motion
```

When enabled:

* Remove unnecessary animation
* Reduce movement
* Preserve functional feedback
* Avoid parallax
* Avoid excessive transitions

---

# 62. ACCESSIBILITY

CATALYST must follow accessibility-first principles.

Required:

```text
Keyboard navigation
Focus states
Semantic HTML
Screen reader compatibility
Color contrast
Accessible labels
Non-color state indicators
Reduced motion
Responsive text
```

---

# 63. KEYBOARD UX

Desktop users must be able to operate the primary conversation flow efficiently.

Examples:

```text
Enter      → Send
Shift+Enter → New line
Escape     → Cancel/close contextual UI where appropriate
Tab        → Navigate controls
```

Exact shortcuts should remain discoverable.

---

# 64. FOCUS MANAGEMENT

Every interactive element must have a visible focus state.

Never remove focus indicators simply for visual cleanliness.

---

# 65. RESPONSIVE BREAKPOINTS

Breakpoints must be centralized.

Do not scatter arbitrary media-query values throughout components.

Conceptually:

```text
Mobile
Tablet
Desktop
Wide Desktop
```

The exact breakpoint values belong to the design-token layer.

---

# 66. NO HARDCODED DESIGN VALUES

Do not hardcode:

```text
Colors
Spacing
Typography
Radius
Shadows
Breakpoints
Animation durations
Z-index values
Component dimensions
```

inside individual components.

All should originate from centralized tokens.

---

# 67. TOKEN ARCHITECTURE

Recommended structure:

```text
tokens/
│
├── color
├── typography
├── spacing
├── radius
├── elevation
├── motion
├── breakpoint
├── layout
└── component
```

The exact implementation can differ according to the frontend stack.

The principle must remain unchanged.

---

# 68. COMPONENT API PRINCIPLE

Components must be configurable through semantic properties.

Prefer:

```text
Button
variant
size
state
icon
loading
disabled
```

over creating separate components for every visual variation.

---

# 69. SOLID PRINCIPLES

## Single Responsibility

A component should have one clear responsibility.

Bad:

```text
ChatMessage
  ├── API request
  ├── Markdown parsing
  ├── state management
  ├── animation
  ├── theme logic
  └── rendering
```

Prefer separation:

```text
Data/state
    ↓
Presentation
    ↓
Reusable UI
```

---

## Open/Closed

Components should be extendable through configuration without constant modification.

---

## Liskov Substitution

Reusable components must maintain predictable contracts.

---

## Interface Segregation

Avoid components receiving huge configuration objects containing unrelated properties.

---

## Dependency Inversion

UI components should not directly depend on backend implementation details.

---

# 70. OOPS PRINCIPLE

Use object-oriented concepts where they genuinely simplify the architecture.

Encapsulate:

```text
State
Behavior
Configuration
Responsibilities
```

Do not introduce classes merely because "OOPS" requires them.

The goal is maintainability, not theoretical complexity.

---

# 71. REUSABILITY RULE

Before creating a new component, ask:

```text
Is this behavior already represented?
Can an existing component support this through configuration?
Does this pattern appear elsewhere?
```

Avoid duplicate components.

---

# 72. DRY PRINCIPLE

Do not duplicate:

* Colors
* Styles
* Layout logic
* State logic
* Animation definitions
* Responsive rules
* Message actions
* Agent status rendering

But:

> Do not abstract code merely because two things look similar.

Abstraction should follow genuine reuse.

---

# 73. YAGNI PRINCIPLE

Do not build functionality because it may be needed someday.

Build:

```text
Required
+
Clearly reusable
```

Avoid:

```text
Potential future abstraction
+
Speculative architecture
```

---

# 74. NO OVER-ENGINEERING

CATALYST should prefer:

```text
Simple architecture
+
Strong conventions
+
Reusable primitives
+
Centralized tokens
```

over:

```text
Complex framework
+
Multiple abstraction layers
+
Premature optimization
```

---

# 75. FILE / COMPONENT ORGANIZATION

A conceptual organization:

```text
design-system/
│
├── tokens/
├── primitives/
├── components/
├── conversation/
├── agent/
├── layout/
├── motion/
└── accessibility/
```

Business logic and backend services must remain separated from visual components.

---

# 76. STATE SEPARATION

Separate:

```text
UI state
Conversation state
Agent state
Network state
Application state
```

Do not allow individual UI components to become the source of truth for the entire application.

---

# 77. PERFORMANCE

The interface must remain responsive during:

* Streaming
* Long conversations
* Markdown rendering
* Code rendering
* Tool activity
* Large responses

Avoid unnecessary rerenders.

Long conversations should be architected so that the UI does not become progressively slower.

---

# 78. LONG CONVERSATION UX

Long conversations require:

* Stable scrolling
* Efficient rendering
* Clear message grouping
* Jump-to-latest
* Search/navigation where required
* Preserved context
* Minimal layout shifting

---

# 79. LAYOUT STABILITY

Avoid content unexpectedly moving the user's viewport.

Streaming should not create unnecessary jumps.

Images, code blocks, and dynamic content should reserve appropriate space when possible.

---

# 80. INPUT COMPOSER

The composer is one of the most important components.

It should support a scalable structure:

```text
┌─────────────────────────────────────┐
│ Context / attachment if present     │
│                                     │
│ Write your message...               │
│                                     │
│ [Attach] [Tools]        [Send]      │
└─────────────────────────────────────┘
```

The exact visual design should remain uniquely CATALYST.

---

# 81. COMPOSER PRINCIPLES

The composer must:

* Be immediately discoverable
* Remain accessible
* Expand for long input
* Support multiline text
* Support attachments if enabled
* Clearly communicate sending
* Clearly communicate generation state
* Provide a stop action during generation

---

# 82. GENERATION STATE

When AI is generating:

```text
Send
```

may transition to:

```text
Stop
```

The interaction must communicate that generation is active.

---

# 83. INPUT VALIDATION

Avoid aggressive validation.

Natural language input should generally be accepted.

Only prevent submission when there is a meaningful reason.

---

# 84. NOTIFICATION SYSTEM

Notifications should not interrupt conversation unnecessarily.

Prefer:

```text
Inline feedback
Toast
Contextual status
```

over modal interruptions.

Use modal dialogs only when the user must make a decision.

---

# 85. TOOL EXECUTION VISUALIZATION

Tool execution should communicate:

```text
What is happening
Whether it is running
Whether it succeeded
Whether it failed
```

Example conceptual pattern:

```text
● Searching knowledge base
  Completed
```

Avoid exposing raw technical logs unless explicitly requested.

---

# 86. AGENT APPROVAL

When an agent requires permission:

```text
Agent wants to perform an action

[Review] [Approve] [Cancel]
```

The action must be understandable before approval.

---

# 87. SOURCES / CITATIONS

If the AI response includes sources:

```text
Response
   ↓
Sources
```

Sources should support trust without visually dominating the answer.

---

# 88. METADATA

Metadata should remain secondary.

Examples:

```text
Model
Timestamp
Token information
Execution time
Tool
Source
```

Do not display technical metadata by default unless useful.

---

# 89. SETTINGS

Settings should not clutter the main conversation.

Use dedicated configuration surfaces.

Potential categories:

```text
Appearance
Conversation
Model
Agent
Tools
Keyboard
Accessibility
Privacy
```

---

# 90. THEME SWITCHING

Theme switching must operate entirely through semantic tokens.

Components should never contain:

```text
if dark:
   use color X
else:
   use color Y
```

Instead:

```text
semantic token
      ↓
theme implementation
```

---

# 91. DESIGN SYSTEM RULE

The design system should answer:

```text
What does this component look like?
How does it behave?
What states does it support?
How does it respond?
How does it behave responsively?
How does it behave in dark mode?
How does it behave with reduced motion?
```

A component is not production-ready until these questions are answered.

---

# 92. COMPONENT STATES

Every interactive component should consider:

```text
Default
Hover
Focus
Active
Selected
Disabled
Loading
Error
Success
```

Not every component requires every state.

Only implement meaningful states.

---

# 93. ERROR STATES

Errors must visually differ from normal information but must not dominate the entire interface.

Use semantic error tokens.

Never hardcode red values inside components.

---

# 94. HOVER

Hover is supplementary, not essential.

All important interactions must remain understandable without hover, especially on touch devices.

---

# 95. TOUCH

Interactive touch targets must be sufficiently large and separated.

Avoid dense clusters of tiny icon buttons.

---

# 96. ICONOGRAPHY

Icons must follow one consistent visual language.

Do not mix:

```text
Outlined
Filled
3D
Colorful
Different stroke systems
```

without intentional design reasoning.

Icons must support text rather than replace essential meaning.

---

# 97. ICON + TEXT

For unfamiliar or high-impact actions:

```text
Icon + label
```

is preferable to an icon alone.

Icon-only controls should be reserved for well-understood actions.

---

# 98. VISUAL NOISE CONTROL

Every component must justify its visual presence.

Remove:

* Unnecessary borders
* Excessive shadows
* Redundant labels
* Decorative icons
* Excessive badges
* Repeated metadata
* Unnecessary containers

---

# 99. CARD USAGE

Cards should NOT become the default layout mechanism.

Use cards when content is:

```text
Independent
Grouped
Actionable
Contextually separated
```

Do not put every message, tool result, and section inside a card.

---

# 100. WHITESPACE

Whitespace is an active design element.

Use it to communicate:

```text
Grouping
Hierarchy
Transition
Importance
Breathing room
```

Do not fill empty space merely because it exists.

---

# 101. INFORMATION DENSITY

CATALYST should support two modes of perception:

```text
Conversation mode
    ↓
Low cognitive load

Agent / technical mode
    ↓
Higher information density
```

Complexity should appear when necessary.

---

# 102. BRAND DIFFERENTIATION

CATALYST's uniqueness should come from:

```text
Editorial conversation layout
+
Controlled asymmetry
+
Precise typography
+
Technical state visualization
+
Subtle motion
+
Adaptive composition
```

Not from:

```text
Gradient overload
+
Glow effects
+
Floating blobs
+
AI robot graphics
+
Excessive glassmorphism
```

---

# 103. PROFESSIONALISM RULE

Professional does not mean boring.

CATALYST may be expressive through:

* Typography
* Spatial composition
* Motion
* Micro-interactions
* Accent placement
* Responsive transitions

while maintaining functional discipline.

---

# 104. ANIMATION RULE

Every animation must answer:

> **What does this animation communicate?**

If the answer is:

> "It looks cool."

remove it.

---

# 105. TRANSITION RULE

Transitions should preserve spatial relationships.

When something moves:

```text
User should understand:
Where it came from
Where it went
Why it changed
```

---

# 106. AI RESPONSE TRANSITIONS

AI content should appear progressively without producing visual jitter.

Prefer:

```text
Stable message container
+
Incremental content
+
Minimal opacity / position transition
```

Avoid:

```text
Every word slides in
Every character fades
Entire response repeatedly re-animates
```

---

# 107. SCROLL PERFORMANCE

Scrolling must remain smooth while streaming.

Avoid expensive layout operations during every streamed token.

Streaming rendering should be optimized to avoid unnecessary DOM/UI updates.

---

# 108. ACCESSIBILITY + MOTION

Animations must never be the only mechanism communicating state.

Example:

Bad:

```text
Animated dots = AI working
```

Better:

```text
AI is working
+
Subtle animated indicator
```

---

# 109. DESIGN QA

Every major component must be checked against:

```text
Light theme
Dark theme
Mobile
Tablet
Desktop
Keyboard
Touch
Loading
Error
Disabled
Streaming
Long content
Short content
Accessibility
Reduced motion
```

---

# 110. RESPONSIVE QA

Test:

```text
Small mobile
Large mobile
Tablet portrait
Tablet landscape
Laptop
Desktop
Wide desktop
```

Do not optimize only for the developer's current screen.

---

# 111. CONTENT QA

Test AI responses containing:

```text
One sentence
Long paragraph
Heading hierarchy
Nested lists
Code
Long code
Table
Long URL
Citation
Image
Attachment
Error
Mixed Markdown
Very long response
```

---

# 112. PRODUCTION DESIGN CHECKLIST

Before considering the interface production-ready:

### Design

* [ ] Design language is consistent
* [ ] CATALYST branding is distinctive
* [ ] Material tokens are used as foundation
* [ ] Visual identity is not generic Material UI

### Color

* [ ] All colors are centralized
* [ ] Light theme works
* [ ] Dark theme works
* [ ] Semantic states are consistent
* [ ] Contrast is acceptable

### Typography

* [ ] Typography tokens are centralized
* [ ] Long-form AI text is readable
* [ ] Markdown is controlled
* [ ] Code typography is consistent

### Components

* [ ] Components are reusable
* [ ] No unnecessary duplication
* [ ] No hardcoded visual values
* [ ] Components have predictable APIs
* [ ] States are defined

### Responsive

* [ ] Mobile works
* [ ] Tablet works
* [ ] Desktop works
* [ ] Composer works with mobile keyboard
* [ ] Context panels collapse appropriately

### Streaming

* [ ] Responses stream progressively
* [ ] Streaming indicator exists
* [ ] Stop generation works
* [ ] Auto-scroll works correctly
* [ ] User scrolling is respected
* [ ] Jump-to-latest exists where necessary
* [ ] Streaming does not cause excessive layout shifts

### Agentic UX

* [ ] Agent state is visible
* [ ] Tool execution is understandable
* [ ] Errors are recoverable
* [ ] Consequential actions require appropriate control
* [ ] Internal reasoning is not unnecessarily exposed

### Accessibility

* [ ] Keyboard navigation
* [ ] Focus states
* [ ] Semantic markup
* [ ] Screen reader labels
* [ ] Contrast
* [ ] Reduced motion
* [ ] Touch targets

### Architecture

* [ ] SOLID principles applied pragmatically
* [ ] UI and business logic separated
* [ ] Design tokens centralized
* [ ] Components reusable
* [ ] No speculative abstractions
* [ ] No unnecessary frameworks/layers

---

# 113. AI DEVELOPMENT AGENT RULES

Any AI coding agent working on the CATALYST frontend must follow these rules.

## Rule 01 — Do not redesign randomly

All UI changes must conform to this document.

## Rule 02 — Do not introduce arbitrary colors

Use centralized semantic tokens.

## Rule 03 — Do not introduce arbitrary spacing

Use spacing tokens.

## Rule 04 — Do not create duplicate components

Search for existing reusable components first.

## Rule 05 — Do not hardcode responsive values

Use centralized breakpoints.

## Rule 06 — Do not break dark mode

Every visual component must support both themes.

## Rule 07 — Do not break mobile

Every layout change must be responsive.

## Rule 08 — Do not add decorative complexity

Visual effects must serve UX.

## Rule 09 — Do not expose unnecessary technical complexity

The UI should simplify the underlying AI system.

## Rule 10 — Do not modify the token architecture casually

Design tokens are the centralized source of truth.

## Rule 11 — Prefer composition

Compose existing primitives instead of duplicating implementations.

## Rule 12 — Keep components focused

One component should have one clear responsibility.

## Rule 13 — Preserve user control

Never introduce automatic behavior that unexpectedly takes control of scrolling, navigation, generation, or consequential actions.

## Rule 14 — Streaming is a first-class state

Do not treat streaming as a loading spinner attached to a completed message.

## Rule 15 — Long content is normal

Every response component must work with realistic long AI-generated content.

---

# 114. IMPLEMENTATION PRIORITY

When rebuilding the frontend, use this order:

```text
1. Design tokens
       ↓
2. Typography
       ↓
3. Layout primitives
       ↓
4. Base components
       ↓
5. Conversation system
       ↓
6. Composer
       ↓
7. Streaming system
       ↓
8. Agent states
       ↓
9. Responsive behavior
       ↓
10. Motion
       ↓
11. Accessibility
       ↓
12. Visual refinement
```

Do not begin with decorative details.

---

# 115. REBUILD STRATEGY

Because the current interface was initially created primarily for backend testing, the frontend may be rebuilt completely.

The rebuild should prioritize:

```text
Design system first
      ↓
Reusable components
      ↓
Real interaction states
      ↓
Real streaming behavior
      ↓
Responsive behavior
      ↓
Visual refinement
```

Do not preserve poor existing UI architecture merely for compatibility.

Preserve useful business logic and backend contracts where practical.

---

# 116. DESIGN SYSTEM SOURCE OF TRUTH

The hierarchy is:

```text
DESIGN.md
    ↓
Design Tokens
    ↓
Reusable Components
    ↓
Pages / Features
```

Feature-specific styling must not override the design system without an intentional design-system decision.

---

# 117. FINAL CATALYST DESIGN RULES

The entire system can be reduced to the following principles:

```text
01. Conversation comes first.

02. Intelligence should feel calm.

03. Complexity belongs in the system, not the user's head.

04. Familiar interactions; distinctive visual identity.

05. Use Material semantic color architecture without producing generic Material UI.

06. Centralize every design decision that can reasonably be tokenized.

07. Prefer reusable components over duplicated UI.

08. Prefer composition over unnecessary abstraction.

09. Never hardcode visual values inside feature components.

10. Light and dark themes are equal citizens.

11. Mobile is a first-class interface.

12. Streaming is a core interaction, not an afterthought.

13. Never steal scrolling control from the user.

14. Agent actions must be understandable.

15. Consequential actions require appropriate user control.

16. Motion communicates state; it does not decorate.

17. Long AI responses must remain readable.

18. Accessibility is part of the design, not a later patch.

19. Do not over-engineer.

20. Do not make the interface look like another AI product.

21. Every visual element must have a purpose.

22. Every interaction must have predictable feedback.

23. Every abstraction must justify its existence.

24. Every component must support realistic content and states.

25. The final interface should feel like CATALYST — not a clone of an existing chatbot.
```

---

# 118. CATALYST DESIGN NORTH STAR

The final experience should communicate:

```text
                 CATALYST
                    │
          ┌─────────┴─────────┐
          │                   │
       HUMAN               AI
       CONTROL           CAPABILITY
          │                   │
          └─────────┬─────────┘
                    │
               INTELLIGENT
               INTERACTION
                    │
          ┌─────────┴─────────┐
          │                   │
       CLARITY             POWER
          │                   │
          └─────────┬─────────┘
                    │
              SIMPLE UX
```

### Final principle

> **CATALYST should make complex AI capabilities feel simple without making the interface simplistic.**

The system should be visually distinctive, technically disciplined, responsive, accessible, and calm enough for long-duration professional use.

**Design for intelligence.
Design for control.
Design for clarity.
Design CATALYST.**
