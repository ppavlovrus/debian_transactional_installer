#!/bin/bash

# Build documentation script for Debian Transactional Installer
# This script converts markdown documentation to HTML using pandoc

set -e

echo "📚 Building documentation..."

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo "❌ pandoc is not installed. Please install it first:"
    echo "   Ubuntu/Debian: sudo apt-get install pandoc"
    echo "   macOS: brew install pandoc"
    echo "   Or download from: https://pandoc.org/installing.html"
    exit 1
fi

# Create docs/build directory
mkdir -p docs/build

# Copy CSS file if it exists
if [ -f "docs/style.css" ]; then
    cp docs/style.css docs/build/
fi

# Create a simple CSS file if it doesn't exist
if [ ! -f "docs/style.css" ]; then
    cat > docs/build/style.css << 'EOF'
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    line-height: 1.6;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    color: #333;
}

h1, h2, h3, h4, h5, h6 {
    color: #2c3e50;
    margin-top: 30px;
    margin-bottom: 15px;
}

h1 {
    border-bottom: 3px solid #3498db;
    padding-bottom: 10px;
}

h2 {
    border-bottom: 2px solid #ecf0f1;
    padding-bottom: 8px;
}

code {
    background-color: #f8f9fa;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
}

pre {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
    border-left: 4px solid #3498db;
}

pre code {
    background-color: transparent;
    padding: 0;
}

a {
    color: #3498db;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: left;
}

th {
    background-color: #f8f9fa;
    font-weight: bold;
}

blockquote {
    border-left: 4px solid #3498db;
    margin: 20px 0;
    padding: 10px 20px;
    background-color: #f8f9fa;
}

.nav {
    background-color: #2c3e50;
    padding: 15px 0;
    margin-bottom: 30px;
}

.nav a {
    color: white;
    margin-right: 20px;
    font-weight: bold;
}

.nav a:hover {
    color: #3498db;
}

.footer {
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid #ecf0f1;
    text-align: center;
    color: #7f8c8d;
}
EOF
fi

# Convert markdown files to HTML
echo "🔄 Converting markdown files to HTML..."

# Main documentation files
files=(
    "docs/index.md:docs/build/index.html"
    "docs/user-guide.md:docs/build/user-guide.html"
    "docs/architecture.md:docs/build/architecture.html"
    "docs/api-reference.md:docs/build/api-reference.html"
    "docs/examples.md:docs/build/examples.html"
)

for file_pair in "${files[@]}"; do
    IFS=':' read -r input output <<< "$file_pair"
    
    if [ -f "$input" ]; then
        echo "  Converting $input -> $output"
        pandoc "$input" \
            --standalone \
            --css=style.css \
            --metadata title="Debian Transactional Installer - $(basename "$input" .md | sed 's/-/ /g' | sed 's/\b\w/\U&/g')" \
            --toc \
            --toc-depth=3 \
            -o "$output"
    else
        echo "  ⚠️  Warning: $input not found, skipping..."
    fi
done

# Create navigation
echo "🔗 Creating navigation..."

cat > docs/build/nav.html << 'EOF'
<div class="nav">
    <a href="index.html">🏠 Home</a>
    <a href="user-guide.html">📖 User Guide</a>
    <a href="architecture.html">🏗️ Architecture</a>
    <a href="api-reference.html">📚 API Reference</a>
    <a href="examples.html">💡 Examples</a>
</div>
EOF

# Add navigation to each HTML file
for html_file in docs/build/*.html; do
    if [ -f "$html_file" ]; then
        # Insert navigation after <body> tag
        sed -i.bak 's/<body>/<body>\n<!-- NAVIGATION -->\n<div class="nav">\n    <a href="index.html">🏠 Home<\/a>\n    <a href="user-guide.html">📖 User Guide<\/a>\n    <a href="architecture.html">🏗️ Architecture<\/a>\n    <a href="api-reference.html">📚 API Reference<\/a>\n    <a href="examples.html">💡 Examples<\/a>\n<\/div>/' "$html_file"
        rm "${html_file}.bak"
    fi
done

# Create a simple index page
cat > docs/build/README.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Debian Transactional Installer Documentation</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="nav">
        <a href="index.html">🏠 Home</a>
        <a href="user-guide.html">📖 User Guide</a>
        <a href="architecture.html">🏗️ Architecture</a>
        <a href="api-reference.html">📚 API Reference</a>
        <a href="examples.html">💡 Examples</a>
    </div>
    
    <h1>Debian Transactional Installer Documentation</h1>
    
    <p>Welcome to the comprehensive documentation for the Debian Transactional Installer.</p>
    
    <h2>Documentation Sections</h2>
    
    <ul>
        <li><a href="index.html">🏠 Home</a> - Overview and quick start guide</li>
        <li><a href="user-guide.html">📖 User Guide</a> - Complete user guide with step-by-step instructions</li>
        <li><a href="architecture.html">🏗️ Architecture</a> - System architecture and design documentation</li>
        <li><a href="api-reference.html">📚 API Reference</a> - Complete API documentation for all modules</li>
        <li><a href="examples.html">💡 Examples</a> - Comprehensive examples for various use cases</li>
    </ul>
    
    <h2>Quick Start</h2>
    
    <p>To get started quickly:</p>
    
    <ol>
        <li>Read the <a href="user-guide.html">User Guide</a> for installation and basic usage</li>
        <li>Check the <a href="examples.html">Examples</a> for practical use cases</li>
        <li>Refer to the <a href="api-reference.html">API Reference</a> for technical details</li>
    </ol>
    
    <div class="footer">
        <p>Debian Transactional Installer Documentation</p>
    </div>
</body>
</html>
EOF

echo "✅ Documentation built successfully!"
echo "📁 HTML files are available in: docs/build/"
echo "🌐 Open docs/build/index.html in your browser to view the documentation"
echo ""
echo "📋 Files generated:"
ls -la docs/build/*.html | sed 's/.*\//  /'

echo ""
echo "🚀 To serve the documentation locally:"
echo "   cd docs/build && python3 -m http.server 8000"
echo "   Then open http://localhost:8000 in your browser"
