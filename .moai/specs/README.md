# AI-Publishing SPEC Documents

This directory contains all **SPEC (Specification)** documents for the AI-Publishing project, following SPEC-First TDD methodology.

## 📋 What is a SPEC?

A **SPEC** is a structured requirements document using **EARS format** (Easy Approach to Requirements Syntax) that defines:
- **What** the system should do (functional requirements)
- **When** it should do it (events and triggers)
- **How** to verify it works (test scenarios)
- **Why** it matters (business context)

Each SPEC is **testable**, **traceable**, and **versioned**.

---

## 📚 SPEC Documents

### SPEC-000: Baseline Requirements
- **Status**: ✅ FOUNDATIONAL
- **Scope**: Project-wide architecture, security, quality standards
- **Document**: `SPEC-000-baseline.md`
- **Use**: Reference for all subsequent SPECs

### SPEC-001: Development Environment Initialization
- **Status**: ✅ READY FOR IMPLEMENTATION
- **Scope**: Project setup, dependencies, development workflow
- **Document**: `SPEC-001-initialization.md`
- **Phase**: Phase 0
- **Precondition**: SPEC-000 (baseline)

### SPEC-002: Authentication System (Coming)
- **Status**: PLANNED
- **Scope**: User login, JWT tokens, session management
- **Phase**: Phase 1
- **Precondition**: SPEC-001 (initialization)

### SPEC-003: Content Publishing API (Coming)
- **Status**: PLANNED
- **Scope**: CRUD operations for published content
- **Phase**: Phase 1
- **Precondition**: SPEC-001 (initialization)

---

## 🎯 EARS Format Quick Reference

### 1. UBIQUITOUS (System-wide rules)
```markdown
> The system SHALL [action]
> The system SHALL [constraint]
```
**Example**: "The system SHALL validate all inputs against security rules"

### 2. EVENT-DRIVEN (When something happens)
```markdown
WHEN [trigger event]
THEN the system SHALL [response]
```
**Example**:
```
WHEN user submits login form
THEN the system SHALL authenticate and issue JWT token
```

### 3. UNWANTED BEHAVIOR (What to prevent)
```markdown
IF [unwanted condition]
THEN the system SHALL [prevention action]
```
**Example**:
```
IF password is incorrect
THEN the system SHALL reject login and log attempt
```

### 4. STATE-DRIVEN (While in a state)
```markdown
WHILE [system state]
The system SHALL [continuous action]
```
**Example**: "WHILE user session is active, the system SHALL validate token on each request"

### 5. OPTIONAL (User-controlled features)
```markdown
WHERE [user condition]
The system SHALL [feature]
```
**Example**: "WHERE user enables two-factor authentication, the system SHALL send SMS verification"

---

## 🔄 SPEC Workflow

```
1. Create SPEC (EARS format)
   └─ Define requirements clearly

2. Write Tests (RED phase)
   └─ All tests fail initially

3. Implement Code (GREEN phase)
   └─ Minimal code to pass tests

4. Refactor & Polish (REFACTOR phase)
   └─ Improve code quality

5. Auto-Generate Docs (SYNC phase)
   └─ Documentation updated automatically
```

---

## 📖 How to Use SPECs

### For Developers
1. **Read the SPEC**: Understand requirements before coding
2. **Write tests from SPEC**: Each requirement becomes a test
3. **Implement code**: Make tests pass
4. **Verify coverage**: Ensure all requirements tested

### For Project Leads
1. **Review SPEC**: Validate requirements with stakeholders
2. **Track progress**: Monitor which requirements are implemented
3. **Update SPEC**: Add or modify requirements as needed
4. **Link to code**: Reference SPEC in commits and PRs

### For New Team Members
1. **Read SPEC-000**: Understand project baseline
2. **Read relevant SPEC**: For the feature you're working on
3. **Follow TDD**: Write tests → Implement → Refactor
4. **Update SPEC**: Document any deviations

---

## 🎓 Learning Resources

### SPEC-First Philosophy
See `.moai/learning/spec-first-intro.md` for:
- Why SPEC-First prevents bugs
- Real-world examples
- How to read EARS format
- Common pitfalls

### TDD Workflow
See `.moai/learning/tdd-workflow.md` for:
- Red-Green-Refactor cycle
- Writing testable requirements
- Test patterns and examples
- Coverage targets

### MoAI-ADK Standards
See `.moai/STRUCTURE.md` for:
- Project conventions
- File naming standards
- Code organization patterns
- Quality gates

---

## 🔗 Related Documents

- `.moai/config/config.json` - Project configuration
- `CLAUDE.md` - Development philosophy
- `.moai/learning/` - Learning materials
- `.moai/memory/` - Session notes and patterns

---

## 📝 SPEC Template

When creating a new SPEC, use this template:

```markdown
# SPEC-XXX: [Feature Name]

**Version**: 0.25.7
**Status**: [DRAFT|READY FOR IMPLEMENTATION|IMPLEMENTED]
**Phase**: [Phase number]
**Created**: [Date]
**Language**: English (Conversation: 한국어)
**Owner**: @user

---

## Overview
[1-2 sentence summary]

---

## UBIQUITOUS Requirements

> The system SHALL ...

---

## EVENT-DRIVEN Requirements

### WHEN [event]
```
GIVEN [context]
WHEN [trigger]
THEN the system SHALL [response]
```

---

## UNWANTED BEHAVIOR

### IF [condition]
```
THEN the system SHALL [prevention]
```

---

## Test Scenarios

- [ ] Scenario 1: [description]
- [ ] Scenario 2: [description]

---

## Acceptance Criteria

- ✅ [criterion 1]
- ✅ [criterion 2]

---

## Related SPECs

- SPEC-XXX - [Related spec]
```

---

## 🚀 Next Steps

1. **Read SPEC-000** for project baseline
2. **Read SPEC-001** for development environment setup
3. **Run /alfred:1-plan** to create implementation plan
4. **Run /alfred:2-run SPEC-001** to implement initialization
5. **Run /alfred:3-sync** to auto-generate documentation

---

**Last Updated**: 2025-11-16
**Total SPECs**: 2 baseline + N planned
**Status**: Ready for Phase 1 Planning
