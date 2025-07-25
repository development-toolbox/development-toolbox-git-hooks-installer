# User Memory Profile - Development Preferences and Methodologies

Copy each section below into separate `<user-memory-input>` tags:

## Section 1: Development Workflow Preferences
```
<user-memory-input>
User Development Workflow Preferences:
- Prefers development branch workflow: main (protected) ← development ← feature branches
- NEVER allows direct commits to main branch
- Always requires PR reviews for code quality and security
- Values security-first approach - always validate safety implications of any git operations
- Wants comprehensive documentation for future AI instances
- Uses structured todo management with markdown files in organized folders
- Appreciates methodology that can be reused across projects
- Expects conventional commits with proper scopes, never generic types
- Prefers commit messages stored in markdown format in commit/ folder
- Likes visual analysis with mermaid diagrams for complex program flows
</user-memory-input>
```

## Section 2: Analysis and Documentation Standards
```
<user-memory-input>
User Analysis and Documentation Standards:
- For complex issues, always create analysis folders: `todo/analysis/issue-name-date/`
- Analysis structure: problem identification → current flow analysis → safe proposals → testing strategies → README overview
- Use mermaid diagrams for program logic (fix syntax: no emojis, simple node names, proper styling with colors)
- Document dangerous code paths with visual flow diagrams
- Create comprehensive testing strategies including security validation
- Always update CLAUDE.md for future AI instances with commands, workflows, architecture
- Add `.claude/` to .gitignore (local user settings, never commit to git)
- Use CLAUDE.md for shared AI context, not .claude directory
- Include safety warnings and security considerations in all documentation
</user-memory-input>
```

## Section 3: Conventional Commit Rules
```
<user-memory-input>
Conventional Commit Rules (User Requirements):
- Format: type(scope): description (scope is REQUIRED, never optional)
- Types: feat, fix, docs, style, refactor, test, chore, perf, ci, build
- Multiple scopes allowed and encouraged: type(scope1,scope2,scope3): description
- Description: lowercase, imperative mood, no period at end
- NEVER use generic types: "feat:" or "fix:" without meaningful scope
- Examples of CORRECT format:
  * feat(installer,security): add repository validation checks
  * fix(testing,docker): resolve Python 3.12 compatibility issues
  * docs(workflow,security,analysis): add git flow and vulnerability analysis
- Always store commit messages in markdown format in commit/ folder
- User will correct if generic types are used without proper scopes
</user-memory-input>
```

## Section 4: Security-First Development Philosophy
```
<user-memory-input>
Security-First Development Philosophy:
- Always validate repository clean state before any git operations
- NEVER auto-merge to main - always require manual PR review
- NEVER auto-commit user files - only commit explicitly tracked installer files
- Add comprehensive security testing for any code that performs git operations (git add, commit, merge, push)
- Test scenarios: dirty repository protection, secret file protection, work-in-progress protection
- Document all dangerous code paths with visual diagrams showing risks
- Create negative test cases (what should NOT happen)
- Validate that user's untracked files (.env, secrets, temp files) are never committed
- Security testing includes: malicious file detection, accidental secret exposure, unauthorized access prevention
</user-memory-input>
```

## Section 5: User Story Testing Methodology
```
<user-memory-input>
User Story Testing Methodology:
- Always write User Stories before creating tests
- Format: "As a [user type], I want [goal], so that [benefit]"
- Analyze User Story validity: realistic, testable, valuable, security-conscious
- Create tests that directly match User Story scenarios
- Include negative User Stories (what should NOT happen for security)
- Validate each User Story for: business realism, security implications, edge cases
- Create Docker test environments that simulate real User Story scenarios
- Examples of valid User Stories:
  * "As a developer with secrets in .env, I want safe git hook installation, so that my API keys are never committed"
  * "As a team lead, I want all changes reviewed via PR, so that code quality is maintained"
- Examples of INVALID User Stories that should be rejected:
  * "As a developer in a hurry, I want to auto-merge to main, so that I can deploy quickly" (security risk)
</user-memory-input>
```

## Section 6: Todo Management System
```
<user-memory-input>
Todo Management System Requirements:
- Use `todo/` folder with markdown files for all task tracking
- File naming: `task-description-YYYY-MM-DD.md`
- Include in each todo: date created, status, priority, detailed description, validation steps
- Status options: pending, in_progress, completed
- Only move to `todo/done/` folder with explicit user confirmation
- Create `todo/analysis/` subfolders for complex technical issues
- Each analysis folder should contain: critical issues, current analysis, safe proposals, testing strategies, README overview
- Todo files provide transparency and allow user to track AI progress
- Never use internal todo tracking - always create visible markdown files
- User expects to review and approve todo completion before moving files
</user-memory-input>
```