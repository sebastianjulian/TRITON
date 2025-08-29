# FEATURE IMPLEMENTATION WORKFLOW

**⚠️ MANDATORY: Read this file FIRST before implementing any new feature**

This document defines the precise workflow for implementing new features in the TRITON project to ensure consistency, thoroughness, and error-free delivery.

## 🔄 THE 5-STEP IMPLEMENTATION PROCESS

### **STEP 1: READ THIS WORKFLOW FILE**
- **ALWAYS** read this entire file before starting any feature implementation
- Understand the complete process before taking any action
- Familiarize yourself with templates and examples provided

### **STEP 2: CREATE DETAILED PLAN & TRACK PROGRESS**

#### 2.1 Create Todo List
Use the `TodoWrite` tool to create a comprehensive todo list that includes:

**Required Todo Structure:**
```
1. "Research existing codebase for [feature area]" - Understanding current implementation
2. "Design [feature] architecture/approach" - Planning the solution
3. "Implement [specific component 1]" - Actual implementation steps
4. "Implement [specific component 2]" - Break down into granular tasks
5. "Add error handling for [feature]" - Security and robustness
6. "Write/update tests for [feature]" - Verification
7. "Update documentation for [feature]" - Maintenance
8. "Verify compilation and functionality" - Final validation
```

#### 2.2 Progress Tracking
- Mark todos as `in_progress` BEFORE starting work on them
- Mark todos as `completed` IMMEDIATELY after finishing each task
- **NEVER** batch multiple completions - update in real-time
- Add new todos if you discover additional requirements during implementation

#### 2.3 Document Lessons Learned
For each completed task, document:
- **What was implemented**: Brief description of what was done
- **Why this approach**: Reasoning behind implementation choices
- **Challenges faced**: Problems encountered and how they were solved
- **Key insights**: Important discoveries or patterns learned
- **Future considerations**: Things to remember for similar tasks

**Lessons Learned Template:**
```markdown
## Lessons Learned - [Feature Name]

### Task: [Task Description]
- **Implementation**: [What was done]
- **Reasoning**: [Why this approach was chosen]
- **Challenges**: [Problems encountered and solutions]
- **Insights**: [Key learnings]
- **Future Notes**: [Things to remember next time]
```

### **STEP 3: FINAL REVIEW LOOP**

Before providing your final answer, perform a comprehensive review:

#### 3.1 Completeness Check
- ✅ All todos marked as completed
- ✅ All requirements from user request addressed
- ✅ All edge cases considered and handled
- ✅ Error handling implemented where needed
- ✅ Code follows existing project conventions
- ✅ All lessons learned have been applied to the implementation

#### 3.2 Quality Review
- ✅ Code is readable and well-structured
- ✅ Variable names are descriptive and consistent
- ✅ No hardcoded values where configuration is needed
- ✅ Security best practices followed
- ✅ No sensitive information exposed or logged

#### 3.3 Integration Review
- ✅ New feature integrates properly with existing codebase
- ✅ Dependencies are correctly handled
- ✅ Import statements are correct
- ✅ File paths and references are accurate
- ✅ Configuration files updated if needed

### **STEP 4: COMPILATION & FUNCTIONALITY VERIFICATION**

#### 4.1 Compilation Check
Run appropriate commands to verify code compiles:
```bash
# Python projects
python -m py_compile [modified_files]

# For Flask apps
python src/app.py --check  # or similar validation

# For projects with specific linting
npm run lint  # if applicable
npm run typecheck  # if applicable
```

#### 4.2 Functionality Testing
- Test the new feature manually
- Run existing tests if available
- Verify integration with other components
- Test error conditions and edge cases
- Confirm no regressions in existing functionality

### **STEP 5: LOOP UNTIL ERROR-FREE**

#### 5.1 Error Resolution Process
If any errors are found:
1. **Document the error** in lessons learned
2. **Create new todo** for fixing the specific error
3. **Implement the fix**
4. **Re-run all verification steps** (Steps 3-4)
5. **Repeat until no errors remain**

#### 5.2 Success Criteria
Only provide final answer when:
- ✅ All todos completed successfully
- ✅ All verification steps pass
- ✅ No compilation errors
- ✅ No runtime errors in basic testing
- ✅ Feature works as requested
- ✅ All lessons learned documented

## 📋 TEMPLATES

### Todo List Template
```markdown
## Feature Implementation: [Feature Name]

### Research Phase
- [ ] Research existing codebase for [relevant area]
- [ ] Identify integration points and dependencies
- [ ] Review similar implementations in project

### Design Phase  
- [ ] Design feature architecture
- [ ] Plan data structures and interfaces
- [ ] Consider error handling and edge cases

### Implementation Phase
- [ ] Implement core functionality
- [ ] Add error handling and validation
- [ ] Integrate with existing systems
- [ ] Add logging/debugging as needed

### Verification Phase
- [ ] Test basic functionality
- [ ] Test error conditions
- [ ] Verify integration works correctly
- [ ] Run compilation checks

### Documentation Phase
- [ ] Update relevant documentation
- [ ] Document lessons learned
- [ ] Add code comments if needed
```

### Verification Checklist Template
```markdown
## Pre-Delivery Verification Checklist

### Code Quality
- [ ] Code compiles without errors
- [ ] Code follows project conventions
- [ ] No hardcoded values inappropriately used
- [ ] Error handling implemented
- [ ] Security considerations addressed

### Functionality
- [ ] Feature works as specified
- [ ] Edge cases handled appropriately
- [ ] Integration with existing code verified
- [ ] No regressions introduced

### Documentation
- [ ] All todos completed and documented
- [ ] Lessons learned recorded
- [ ] Code is self-documenting or commented appropriately
```

## 🎯 SUCCESS METRICS

A feature implementation is considered successful when:
1. **Complete**: All user requirements fully addressed
2. **Correct**: Code compiles and runs without errors
3. **Documented**: Full todo tracking and lessons learned recorded
4. **Verified**: All verification steps completed successfully
5. **Integrated**: Works seamlessly with existing codebase

## ⚡ EFFICIENCY TIPS

- **Use TodoWrite tool consistently** - Don't skip progress tracking
- **Research first, implement second** - Understanding saves time
- **Test early and often** - Catch issues before they compound
- **Document as you go** - Don't leave documentation for the end
- **Follow existing patterns** - Consistency reduces cognitive load

---

**Remember: The goal is not just to implement features, but to implement them correctly, thoroughly, and in a way that enhances the overall project quality.**