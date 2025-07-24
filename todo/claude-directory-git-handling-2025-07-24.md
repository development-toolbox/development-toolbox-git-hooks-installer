# .claude Directory Git Handling Guidelines

**Date Created**: 2025-07-24  
**Status**: 📋 GUIDELINE - Best Practices  
**Priority**: Medium  

## Should .claude be in Git?

**Answer: NO** - The `.claude` directory should be added to `.gitignore`

## Why .claude Should NOT be in Git

### 1. **Contains Local State**
- User-specific settings and preferences
- Local workspace configurations
- Session-specific data
- Machine-specific paths

### 2. **Privacy Concerns**
- May contain API keys or tokens
- User-specific identifiers
- Local file paths that reveal system information
- Conversation history that may include sensitive data

### 3. **Unnecessary Repository Bloat**
- Binary files or caches
- Temporary session data
- Large conversation histories
- Auto-generated content

### 4. **Collaboration Issues**
- Different team members have different Claude configurations
- Merging .claude directories would cause conflicts
- Each developer needs their own Claude workspace

## Recommended .gitignore Entry

Add to your `.gitignore`:

```gitignore
# Claude AI workspace
.claude/

# Alternative patterns if needed
**/.claude/
.claude/**
```

## What SHOULD be in Git Instead

### 1. **CLAUDE.md** ✅
- Project-specific documentation for AI instances
- Shared across all team members
- Contains project context and guidelines
- Version controlled and reviewed

### 2. **Project Documentation** ✅
- README.md with AI-friendly sections
- Architecture documentation
- Coding guidelines
- Testing strategies

### 3. **Todo Management** ✅
- `todo/` folder with task tracking
- Analysis folders for complex issues
- Shared understanding of project state

## Best Practices

### For Individual Developers
```bash
# Check if .claude is already tracked
git status .claude/

# If tracked, remove from git but keep locally
git rm -r --cached .claude/
echo ".claude/" >> .gitignore
git add .gitignore
git commit -m "chore: Remove .claude from version control"
```

### For New Projects
```bash
# Initialize project with proper ignores
echo ".claude/" >> .gitignore
git add .gitignore
git commit -m "chore: Add .claude to gitignore"
```

### For Teams
1. Document in README.md that .claude should not be committed
2. Add .claude/ to .gitignore template
3. Use CLAUDE.md for shared AI context
4. Regular code reviews to ensure no .claude files slip through

## Alternative Approaches

### If You Need to Share Claude Context

Instead of committing .claude, consider:

1. **CLAUDE.md File** (Recommended)
   - Manually curated project context
   - Version controlled
   - Team reviewed

2. **Project Templates**
   - Create `.claude.template/` with example configs
   - Developers copy to their local `.claude/`
   - Template can be version controlled

3. **Documentation Folder**
   - `docs/ai-context/` for shared context
   - Markdown files with project information
   - Structured for AI consumption

## Summary

- ❌ **Never commit .claude directory**
- ✅ **Always add .claude/ to .gitignore**
- ✅ **Use CLAUDE.md for shared context**
- ✅ **Document AI guidelines in version control**

This ensures clean repositories, protects privacy, and maintains proper separation between local workspace and shared project files.

---

**Action Required: Check if .claude is in your .gitignore and add it if missing.**