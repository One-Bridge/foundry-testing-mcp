# Google Docs Compatible Documentation Rules
# Generate documentation that copies cleanly from Markdown to Google Docs
# Optimize for copy-paste workflow and formatting compatibility

## Core Formatting Rules

### Headers
- Use only ## (H2) through #### (H4) headers - avoid # (H1) as it can cause formatting issues
- Keep headers simple with no special characters, code, or inline formatting
- Use title case for headers
- Add extra line breaks around headers for clean spacing

### Code and Technical Content
- Replace code blocks with simple indented text using 4 spaces instead of triple backticks
- Replace inline code with quotes or italics instead of backticks
- For file paths, use italics: *src/components/Button.js*
- For commands, use quotes: "npm install package-name"
- For variable names, use italics: *variableName*

### Lists and Structure
- Use simple bullet points (-) only, avoid numbered lists when possible
- Keep list nesting to maximum 2 levels
- Use consistent spacing with blank lines between major list sections
- Avoid mixing bullet styles within the same document

### Tables
- Avoid complex tables - use simple bullet point lists instead
- If tables are necessary, keep them to 2-3 columns maximum
- Use simple headers without special formatting

### Links and References
- Use descriptive text with links in parentheses: "Visit the documentation (https://example.com)"
- Avoid complex link formatting or reference-style links
- Group all links at the end of sections when possible

### Text Formatting
- Use **bold** sparingly for key terms only
- Use *italics* for emphasis instead of code formatting
- Avoid combining multiple formatting styles (bold + italic + code)
- Use plain text whenever possible

## Content Structure Rules

### Document Organization
- Start with a clear title (##)
- Include a brief overview section
- Use consistent section naming
- End with a summary or next steps section

### Paragraphs and Spacing
- Keep paragraphs short (2-4 sentences maximum)
- Use double line breaks between sections
- Avoid long blocks of text
- Use bullet points to break up information

### Technical Examples
- Present code examples as indented text blocks
- Include clear explanations before and after technical content
- Use step-by-step formatting for processes
- Replace complex diagrams with simple text descriptions

## Specific Google Docs Optimization

### Compatibility Guidelines
- Avoid horizontal rules (---) - use section headers instead
- Don't use blockquotes (>) - use indented paragraphs with italics
- Avoid footnotes and complex references
- Use simple ASCII characters only

### Copy-Paste Friendly Elements
- Structure content in clear, copyable sections
- Use consistent indentation (4 spaces)
- Avoid special markdown extensions
- Test formatting with simple text editors first

## Documentation Generation Instructions

When generating documentation from codebases:

1. Apply all above formatting rules automatically
2. Structure content for easy section-by-section copying
3. Replace all technical syntax with Google Docs-friendly alternatives
4. Prioritize clarity and simplicity over complex formatting
5. Test that content reads well in plain text format

## Example Code Block Formatting

Instead of:
```javascript
const example = "code";
```

Use:
    const example = "code";

Instead of:
`variableName` or `function()`

Use:
*variableName* or "function()"