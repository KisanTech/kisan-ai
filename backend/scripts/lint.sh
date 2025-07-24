#!/bin/bash
# Kisan AI - Quick Lint & Format Script
# Usage: ./scripts/lint.sh

echo "🔧 Running ruff linter and formatter..."

# Fix linting issues
echo "📝 Fixing linting issues..."
uv run ruff check --fix

# Format code
echo "🎨 Formatting code..."
uv run ruff format

# Final check
echo "✅ Verifying code quality..."
if uv run ruff check && uv run ruff format --check; then
    echo "🎉 All good! Code is ready for commit."
else
    echo "❌ Some issues remain. Please check manually."
    exit 1
fi 