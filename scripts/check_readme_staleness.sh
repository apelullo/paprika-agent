#!/usr/bin/env bash
if git diff --cached --name-only | grep -q "^server\.py$" &&
   ! git diff --cached --name-only | grep -q "^README\.md$"; then
    echo "Warning: server.py was modified but README.md was not."
    echo "Consider updating README.md if the change affects tools or architecture."
fi
exit 0
