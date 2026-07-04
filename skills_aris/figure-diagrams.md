# Figure Diagrams

Text-to-diagram generation for flowcharts, sequence diagrams, architecture diagrams, and more. Use `figures/figure-styling` for the academic visual standards that apply here.

## Diagram Type Selection

| Type | Use Cases |
| ---- | --------- |
| Flowchart | Processes, decisions, steps |
| Sequence Diagram | Interactions, messaging, API calls |
| Class Diagram | Class structure, inheritance, associations |
| State Diagram | State machines, state transitions |
| ER Diagram | Database design, entity relationships |
| Gantt Chart | Project planning, timelines |
| Mindmap | Hierarchical structures, knowledge graphs |
| Timeline | Historical events, milestones |
| C4 Diagram | System architecture (C4 model) |
| Sankey Diagram | Flow, conversions |
| Block Diagram | System components, modules |
| Architecture Diagram | System architecture |
| User Journey | User experience flows |

## Architecture Diagram Best Practices

Use junction nodes as virtual anchor points on an invisible grid to precisely control placement — route connections through junctions to control vertical/horizontal positioning. For floating components with no logical connection to other nodes, use a junction combined with `{group}` modifier to position without adding a semantically incorrect edge.

## Math Formulas

When the diagram involves math, use KaTeX notation: wrap expressions in `$$` delimiters inside quoted strings. Node labels with math MUST be quoted. Use `\text{}` for non-math text inside `$$` block. Common patterns: subscript `$$W_Q$$`, superscript `$$x^2$$`, fraction `$$\frac{QK^T}{\sqrt{d_k}}$$`, Greek `$$\alpha, \beta$$`, softmax `$$\text{softmax}(z_i)$$`. Use math for academic/technical audiences; plain text for general audiences.

## Quality Rules

- Use semantic node naming (not A, B, C — use authServer, userDB, etc.)
- Use `<br/>` for line breaks inside node labels — never `\n`
- Verify arrow directions — wrong direction = automatic fail
- Verify block content — wrong content = automatic fail
- Use descriptive kebab-case file names
