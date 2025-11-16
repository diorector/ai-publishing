# Repository Cleanup Checklist - Phase 2 Complete

**Date**: 2025-11-16 KST
**Purpose**: Clean repository before Phase 3 documentation work
**Estimated Time**: 30-45 minutes
**User**: You

---

## Pre-Cleanup Verification

Before starting cleanup, verify everything is ready:

- [ ] Code implementation complete (translator.py, orchestrator.py)
- [ ] SYNC_ANALYSIS_REPORT.md reviewed and approved
- [ ] GIT_COMMIT_PLAN.md reviewed and understood
- [ ] Backup/git is on master branch ready to commit
- [ ] No uncommitted code changes you want to keep
- [ ] Ready to archive test scripts and outputs

---

## Step 1: Create Directory Structure (5 minutes)

### 1.1 Create scripts/ directory structure

```bash
# Open PowerShell/Command Prompt in project root
cd C:\Users\dio9\Desktop\moaicamp\ai-publishing

# Create scripts directory
mkdir -p scripts/phase-2-validation
```

**Verify**:
```bash
ls scripts/
# Should show: phase-2-validation (empty directory)
```

### 1.2 Create archive directory structure

```bash
# Create archive directories
mkdir -p .archive/phase-2-outputs
mkdir -p .archive/phase-2-drafts
mkdir -p .archive/phase-2-scripts
```

**Verify**:
```bash
ls .archive/
# Should show: phase-2-outputs, phase-2-drafts, phase-2-scripts (all empty)
```

---

## Step 2: Move Test Scripts (5 minutes)

### 2.1 Move Python test scripts to scripts/phase-2-validation/

**Files to move**:
1. quick_test.py
2. test_pdf_extract.py
3. test_pdf_simple.py
4. test_pdf_with_claude.py
5. extract_pdf_with_structure.py
6. translate_full_pdf.py
7. translate_parallel_chapters.py
8. translate_with_structure.py

**Action**:
```bash
# Move test scripts to archive
mv quick_test.py scripts/phase-2-validation/
mv test_pdf_*.py scripts/phase-2-validation/
mv extract_pdf_*.py scripts/phase-2-validation/
mv translate_*.py scripts/phase-2-validation/
```

**Verify**:
```bash
ls scripts/phase-2-validation/
# Should show: 8 Python files
```

---

## Step 3: Move Generated Outputs (5 minutes)

### 3.1 Move Markdown output files

**Files to move**:
1. output_laf_translated.md
2. output_pdf_structure.md
3. output_laf_structured.md
4. output_laf_full_translated.md
5. output_chapters/ (entire directory)

**Action**:
```bash
# Move output files
mv output_*.md .archive/phase-2-outputs/
mv output_chapters/ .archive/phase-2-outputs/
```

**Verify**:
```bash
ls .archive/phase-2-outputs/
# Should show: 4 .md files + output_chapters/ directory
```

---

## Step 4: Move Draft Documents (10 minutes)

### 4.1 Move redundant/draft documentation files

**Files to move**:
1. CLAUDE_API_SETUP.md
2. COMPLETE_IMPLEMENTATION_SUMMARY.md
3. IMPLEMENTATION_GUIDE.md
4. IMPLEMENTATION_MANIFEST.md
5. PHASE1_COMPLETION_SUMMARY.md
6. QUICK_START_GUIDE.md
7. SOURCE_CODE_REFERENCE.md
8. PARALLEL_TRANSLATION_GUIDE.md
9. EXECUTION_REPORT.md
10. FILES_DELIVERED.md

**Action**:
```bash
# Move draft documents
mv CLAUDE_API_SETUP.md .archive/phase-2-drafts/
mv COMPLETE_IMPLEMENTATION_SUMMARY.md .archive/phase-2-drafts/
mv IMPLEMENTATION_GUIDE.md .archive/phase-2-drafts/
mv IMPLEMENTATION_MANIFEST.md .archive/phase-2-drafts/
mv PHASE1_COMPLETION_SUMMARY.md .archive/phase-2-drafts/
mv QUICK_START_GUIDE.md .archive/phase-2-drafts/
mv SOURCE_CODE_REFERENCE.md .archive/phase-2-drafts/
mv PARALLEL_TRANSLATION_GUIDE.md .archive/phase-2-drafts/
mv EXECUTION_REPORT.md .archive/phase-2-drafts/
mv FILES_DELIVERED.md .archive/phase-2-drafts/
```

**Verify**:
```bash
ls .archive/phase-2-drafts/
# Should show: 10 .md files
```

---

## Step 5: Update .gitignore (5 minutes)

### 5.1 Add ignore patterns for archived directories

**Current .gitignore location**: Check if exists at project root

**If .gitignore exists**:
```bash
cat >> .gitignore << 'EOF'

# Phase 2 validation and archives
scripts/phase-2-validation/
.archive/
EOF
```

**If .gitignore doesn't exist**:
```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.env
.env.local

# Test outputs
.pytest_cache/
.coverage
htmlcov/

# Project specific
.moai/cache/*
logs/
output_*/

# Phase 2 validation and archives
scripts/phase-2-validation/
.archive/
EOF
```

**Verify**:
```bash
cat .gitignore | grep -E "phase-2|\.archive"
# Should show both ignore rules
```

---

## Step 6: Verify Cleanup Completeness (10 minutes)

### 6.1 Check root directory is clean

```bash
# List remaining files in root (should be mostly documentation and config)
ls -la | grep -E "^-" | wc -l
# After cleanup, should have <20 files (down from ~28)
```

**Expected files remaining**:
```
✅ README.md
✅ CLAUDE.md
✅ SYNC_ANALYSIS_REPORT.md (NEW - keep for Phase 3)
✅ GIT_COMMIT_PLAN.md (NEW - keep for Phase 3)
✅ PHASE_2_SYNC_SUMMARY.md (NEW - keep for Phase 3)
✅ CLEANUP_CHECKLIST.md (this file)
✅ requirements.txt
✅ .gitignore (updated)
✅ .moai/ (directory)
✅ src/ (directory - source code)
✅ tests/ (directory if exists)
✅ .github/ (if exists)
```

**Unexpected files remaining**:
```
❌ quick_test.py (should be moved)
❌ test_pdf_*.py (should be moved)
❌ output_*.md (should be moved)
❌ output_chapters/ (should be moved)
❌ CLAUDE_API_SETUP.md (should be moved)
❌ etc. (all draft docs should be moved)
```

### 6.2 Check archive directories have content

```bash
ls -R scripts/phase-2-validation/
# Should show 8 Python files

ls -R .archive/phase-2-outputs/
# Should show 4 MD files + output_chapters/

ls -R .archive/phase-2-drafts/
# Should show 10 MD files
```

### 6.3 Verify git status

```bash
git status --short

# Expected output:
# M  .moai/cache/git-info.json
# ?? SYNC_ANALYSIS_REPORT.md
# ?? GIT_COMMIT_PLAN.md
# ?? PHASE_2_SYNC_SUMMARY.md
# ?? CLEANUP_CHECKLIST.md
# ?? scripts/phase-2-validation/ (if added to git)
# ?? .archive/ (if added to git)

# Should NOT show:
# ?? quick_test.py
# ?? test_pdf_*.py
# ?? output_*.md
# ?? CLAUDE_API_SETUP.md
# etc.
```

---

## Step 7: Final Verification (5 minutes)

### 7.1 Run cleanup verification script

```bash
# Count files in root directory
ls -1 | wc -l
# Should be approximately 20-25 files (down from 50+)

# Check no test scripts in root
ls -1 *.py 2>/dev/null | wc -l
# Should be 0 (all moved to scripts/)

# Check no output files in root
ls -1 output_* 2>/dev/null | wc -l
# Should be 0 (all moved to .archive/)

# Check .gitignore exists and has archive patterns
grep "phase-2" .gitignore
# Should print ignore patterns
```

### 7.2 Verify source code untouched

```bash
# Check source code files exist
ls src/translation/translator.py
# Should exist

ls src/orchestrator.py
# Should exist

# Check no source files were accidentally moved
ls src/ | wc -l
# Should show expected number of directories
```

### 7.3 Check analysis documents in place

```bash
# Verify new analysis documents exist
ls -1 | grep -E "SYNC_ANALYSIS|GIT_COMMIT|PHASE_2_SYNC|CLEANUP"
# Should show all 4 documents:
# CLEANUP_CHECKLIST.md
# GIT_COMMIT_PLAN.md
# PHASE_2_SYNC_SUMMARY.md
# SYNC_ANALYSIS_REPORT.md
```

---

## Cleanup Completion Checklist

### Verify all steps completed:

- [ ] Step 1: Created scripts/phase-2-validation/ and .archive/ directories
- [ ] Step 2: Moved 8 test scripts to scripts/phase-2-validation/
- [ ] Step 3: Moved output files to .archive/phase-2-outputs/
- [ ] Step 4: Moved 10 draft documents to .archive/phase-2-drafts/
- [ ] Step 5: Updated .gitignore with archive patterns
- [ ] Step 6: Verified cleanup completeness
- [ ] Step 7: Ran final verification script

### Success criteria met:

- [ ] Root directory has <25 files (cleaned up)
- [ ] No test scripts in root (all moved)
- [ ] No output files in root (all moved)
- [ ] No draft docs in root (all moved)
- [ ] 4 new analysis documents in root (for Phase 3)
- [ ] Source code files untouched (translator.py, orchestrator.py)
- [ ] .gitignore updated with ignore patterns
- [ ] git status clean (ready for commit)

---

## Troubleshooting

### Issue: "File not found" when trying to move

**Solution**: File may have been deleted or already moved
```bash
# Check if file exists
ls <filename>

# If not found, that's OK - skip to next file
# If found but won't move, check permissions:
ls -la <filename>
# Look for "rw" or "rwx" in permissions
```

### Issue: Cannot create directory (Permission Denied)

**Solution**: Run with elevated permissions
```bash
# On Windows PowerShell:
# Run as Administrator, or

# On macOS/Linux:
sudo mkdir -p .archive/phase-2-outputs
```

### Issue: .gitignore not updating

**Solution**: Verify file location and syntax
```bash
# Check .gitignore exists
ls .gitignore

# Check it has correct content
cat .gitignore | tail -10
# Should show archive patterns at bottom
```

### Issue: Files still showing in git status

**Solution**: Git may have cached files before ignore
```bash
# Remove from git cache (but keep local)
git rm --cached <filename>

# Or for directories:
git rm -r --cached scripts/phase-2-validation/
git rm -r --cached .archive/

# Re-commit .gitignore
git add .gitignore
```

---

## What's Next After Cleanup

### Immediate (After cleanup completes):

1. **Verify Cleanup**
   - Review this checklist one more time
   - Confirm all success criteria met

2. **Prepare for Commit**
   - Review GIT_COMMIT_PLAN.md
   - Run pre-commit verification

3. **Create Commit**
   - Use provided commit message
   - Verify commit successful

### Then Phase 3 Begins:

1. **Documentation Implementation** (11-14 hours)
   - Follow SYNC_ANALYSIS_REPORT.md priorities
   - Create 10+ documentation files

2. **Testing Implementation**
   - Unit tests for translator module
   - Integration tests for pipeline

3. **Project Improvements**
   - Logging configuration
   - Performance monitoring
   - Development server setup

---

## Time Tracking

| Step | Task | Time | Status |
|------|------|------|--------|
| 1 | Create directories | 5 min | [ ] |
| 2 | Move test scripts | 5 min | [ ] |
| 3 | Move outputs | 5 min | [ ] |
| 4 | Move drafts | 10 min | [ ] |
| 5 | Update .gitignore | 5 min | [ ] |
| 6 | Verify cleanup | 10 min | [ ] |
| 7 | Final verification | 5 min | [ ] |
| **TOTAL** | **Repository Cleanup** | **45 min** | [ ] |

---

## Quick Reference

### Archive Directory Structure After Cleanup
```
.archive/
├── phase-2-outputs/        (15 files)
│   ├── output_*.md (4 files)
│   └── output_chapters/ (11 chapter files)
├── phase-2-drafts/         (10 files)
│   ├── CLAUDE_API_SETUP.md
│   ├── COMPLETE_IMPLEMENTATION_SUMMARY.md
│   ├── ... (8 more draft docs)
│   └── FILES_DELIVERED.md
└── .gitkeep               (if empty dirs need to be tracked)

scripts/
└── phase-2-validation/     (8 files)
    ├── quick_test.py
    ├── test_pdf_extract.py
    ├── test_pdf_simple.py
    ├── test_pdf_with_claude.py
    ├── extract_pdf_with_structure.py
    ├── translate_full_pdf.py
    ├── translate_parallel_chapters.py
    └── translate_with_structure.py
```

### Files in Root After Cleanup (Primary Documentation)
```
Root/
├── README.md (main project docs)
├── CLAUDE.md (project instructions)
├── SYNC_ANALYSIS_REPORT.md (Phase 3 blueprint) ← NEW
├── GIT_COMMIT_PLAN.md (commit strategy) ← NEW
├── PHASE_2_SYNC_SUMMARY.md (completion summary) ← NEW
├── CLEANUP_CHECKLIST.md (this file) ← NEW
├── requirements.txt (dependencies)
├── .gitignore (updated with archives)
├── .moai/ (MoAI configuration)
└── src/ (source code - untouched)
```

---

## Completion

### When to Mark Cleanup Complete

Cleanup is **COMPLETE** when:

1. ✅ All 8 test scripts moved to scripts/phase-2-validation/
2. ✅ All 15 output files moved to .archive/phase-2-outputs/
3. ✅ All 10 draft docs moved to .archive/phase-2-drafts/
4. ✅ .gitignore updated with ignore patterns
5. ✅ Root directory has <25 files
6. ✅ All 4 analysis documents in root
7. ✅ Source code files unchanged (translator.py, orchestrator.py)
8. ✅ git status shows expected changes only

### Then You're Ready For:

✅ Creating Phase 2 completion commit
✅ Starting Phase 3 documentation work
✅ Beginning test implementation

---

**Estimated Total Time**: 45 minutes
**Complexity**: Low (mostly file moving)
**Risk Level**: Very Low (archived files, not deleted)
**Rollback**: Easy (move files back if needed)

**Note**: Take your time and verify each step. It's better to move slowly and accurately than quickly and have to redo it.

---

Document: CLEANUP_CHECKLIST.md
Purpose: Step-by-step cleanup before Phase 3
Status: Ready to Execute
User Guide: Follow steps 1-7 in order
Estimated Time: 45 minutes
