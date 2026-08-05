const fs = require('fs');
const assert = require('assert');

// Read app.js
const content = fs.readFileSync('app.js', 'utf8');
const startIdx = content.indexOf('function renderMarkdown(md) {');
if (startIdx === -1) {
    throw new Error('renderMarkdown function not found in app.js');
}

// Find matching closing brace for the function
let braceCount = 0;
let endIdx = -1;
for (let i = startIdx; i < content.length; i++) {
    if (content[i] === '{') {
        braceCount++;
    } else if (content[i] === '}') {
        braceCount--;
        if (braceCount === 0) {
            endIdx = i + 1;
            break;
        }
    }
}

if (endIdx === -1) {
    throw new Error('Could not find closing brace for renderMarkdown');
}

const renderMarkdownCode = content.substring(startIdx, endIdx);
eval(renderMarkdownCode);

const adversarialCases = [
    {
        name: "Mixed Unordered Delimiters (*, -, +)",
        md: "* Asterisk\n- Dash\n+ Plus",
        expected: '<ul><li>Asterisk</li><li>Dash</li><li>Plus</li></ul>'
    },
    {
        name: "Carriage Returns (\\r\\n) in Lists",
        md: "1. One\r\n2. Two\r\n3. Three",
        expected: '<ol><li value="1">One</li><li value="2">Two</li><li value="3">Three</li></ol>'
    },
    {
        name: "Different Indentations (spaces and tabs)",
        md: "  * Indented two spaces\n\t* Indented one tab",
        expected: '<ul><li>Indented two spaces</li><li>Indented one tab</li></ul>'
    },
    {
        name: "Empty List Items (trailing spaces only)",
        md: "* \n-  \n+   ",
        expected: '<ul><li></li><li> </li><li>  </li></ul>'
    },
    {
        name: "No space after list prefix",
        md: "*NoSpace\n1.NoSpace",
        expected: '<p>*NoSpace<br>1.NoSpace</p>'
    },
    {
        name: "Deep nesting of lists (behavior check)",
        md: "* Level 1\n  * Level 2\n    * Level 3",
        expected: '<ul><li>Level 1</li><li>Level 2</li><li>Level 3</li></ul>'
    },
    {
        name: "List with formatting inside items",
        md: "* **Bold** item\n* *Italic* item\n* **Bold and *Italic* mixed**",
        expected: '<ul><li><strong>Bold</strong> item</li><li><em>Italic</em> item</li><li><strong>Bold and <em>Italic</em> mixed</strong></li></ul>'
    },
    {
        name: "HTML elements inside lists (injection safety check)",
        md: "* <script>alert('xss')</script>\n* <div>Safe text</div>",
        expected: '<ul><li>&lt;script&gt;alert(\'xss\')&lt;/script&gt;</li><li>&lt;div&gt;Safe text&lt;/div&gt;</li></ul>'
    },
    {
        name: "Paragraph separated by lists",
        md: "* Item A\n\nParagraph text here\n\n* Item B",
        expected: '<ul><li>Item A</li></ul><p>Paragraph text here</p><ul><li>Item B</li></ul>'
    },
    {
        name: "List item with multiple lines (no blank line)",
        md: "* Item A\nLine 2 of item A\n* Item B",
        expected: '<ul><li>Item A</li></ul><p>Line 2 of item A</p><ul><li>Item B</li></ul>'
    }
];

let failed = false;
adversarialCases.forEach(tc => {
    console.log(`--- Testing: ${tc.name} ---`);
    const result = renderMarkdown(tc.md);
    try {
        assert.strictEqual(result, tc.expected);
        console.log(`PASS: ${tc.name}`);
    } catch (err) {
        console.error(`FAIL: ${tc.name}`);
        console.error(`  Expected: ${JSON.stringify(tc.expected)}`);
        console.error(`  Got:      ${JSON.stringify(result)}`);
        failed = true;
    }
});

if (failed) {
    process.exit(1);
} else {
    console.log("All adversarial Markdown parser tests completed.");
    process.exit(0);
}
