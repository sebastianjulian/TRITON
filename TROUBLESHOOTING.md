# TRITON Troubleshooting Guide

## Overview
This document provides comprehensive troubleshooting methodologies for the TRITON project, based on real-world debugging experiences and systematic problem-solving approaches.

## Case Study: Theme Switching Malfunction

### Problem Description
**Issue**: Theme switching buttons worked on dashboard but not on homepage. Themes would sync when changed on dashboard and then navigating to homepage, but homepage buttons were unresponsive.

**Symptoms**:
- Theme buttons visible and styled correctly on homepage
- Click events not triggering theme changes
- Theme persistence working (localStorage functional)
- Dashboard theme switching working perfectly
- Cross-page theme synchronization working

### Root Cause Analysis
**Discovery Process**:
1. **JavaScript Investigation**: Found ThemeManager class present on both pages
2. **Event Listener Analysis**: Discovered mismatch between CSS classes and JavaScript selectors
3. **HTML/CSS Comparison**: Homepage used `.theme-button` class, dashboard used `.theme-option`
4. **JavaScript Selector Mismatch**: Homepage JavaScript was searching for `.theme-option` (incorrect)

**Root Cause**: CSS class selector mismatch in JavaScript event listeners
- Homepage HTML: `<div class="theme-button" data-theme="...">` 
- Homepage JS: `document.querySelectorAll('.theme-option')` (incorrect)
- Should be: `document.querySelectorAll('.theme-button')` (correct)

### Solution Implemented
1. **Fixed Event Listeners**: Updated `setupEventListeners()` method to use `.theme-button`
2. **Fixed Active State Updates**: Updated `updateActiveButton()` method to use `.theme-button`
3. **Verified Data Attributes**: Confirmed all theme buttons have correct `data-theme` values
4. **Tested Functionality**: Restarted website and verified both pages work independently

---

## Systematic Troubleshooting Methodology

### Phase 1: Problem Definition & Symptom Analysis
**Objective**: Clearly define the problem and gather comprehensive symptom data

#### Step 1.1: Document the Problem
- **What**: Write clear problem description
- **When**: Note when problem occurs (always, intermittently, specific conditions)
- **Where**: Identify affected components/pages/features
- **Who**: Note if problem affects all users or specific scenarios

#### Step 1.2: Gather Symptoms
- Test the functionality manually
- Note what works vs. what doesn't
- Check browser console for JavaScript errors
- Verify network requests (if applicable)
- Test across different scenarios/pages

**Why**: Understanding the full scope prevents tunnel vision and helps identify patterns

### Phase 2: Environment & State Verification
**Objective**: Ensure the testing environment is stable and consistent

#### Step 2.1: Verify Basic Functionality
```bash
# Test server responsiveness
curl -s -o nul -w "%{http_code}" http://localhost:5000
curl -s -o nul -w "%{http_code}" http://localhost:5000/dashboard
```

#### Step 2.2: Check Application State
- Verify website is running latest code changes
- Check if recent deployments/changes might be related
- Confirm no caching issues (browser cache, server cache)

**Why**: Eliminates environmental variables that could mask or cause the real issue

### Phase 3: Comparative Analysis
**Objective**: Identify differences between working and non-working components

#### Step 3.1: Compare Working vs. Broken Components
```bash
# Compare implementations between components
diff -u <(grep -A 10 "functionality" working_file.html) <(grep -A 10 "functionality" broken_file.html)
```

#### Step 3.2: Isolate Differences
- Compare HTML structure
- Compare CSS classes and selectors  
- Compare JavaScript implementations
- Compare data attributes and IDs

**Why**: Often bugs arise from inconsistencies between similar implementations

### Phase 4: Deep Dive Investigation
**Objective**: Systematically examine each component of the failing functionality

#### Step 4.1: Frontend Investigation (for UI issues)
```bash
# Search for specific patterns
grep -n "event.*listener" src/templates/*.html
grep -n "addEventListener" src/templates/*.html
grep -n "querySelector" src/templates/*.html
```

#### Step 4.2: Examine Key Components
- **HTML Elements**: Check classes, IDs, data attributes
- **CSS Selectors**: Verify styling rules target correct elements
- **JavaScript**: Examine event listeners, selectors, function calls
- **Data Flow**: Track how data moves through the system

#### Step 4.3: Console & Network Analysis
- Open browser developer tools
- Check console for JavaScript errors
- Monitor network tab for failed requests
- Test JavaScript functions directly in console

**Why**: Systematic examination prevents missing critical details

### Phase 5: Hypothesis Formation & Testing
**Objective**: Form specific hypotheses about the root cause and test them

#### Step 5.1: Form Hypotheses
Based on investigation, create specific testable hypotheses:
- "The JavaScript is looking for wrong CSS class"
- "Event listener not attached to correct elements"
- "Timing issue with DOM loading"

#### Step 5.2: Test Each Hypothesis
```javascript
// Example: Test if elements are found
console.log('Theme buttons found:', document.querySelectorAll('.theme-button').length);
console.log('Theme options found:', document.querySelectorAll('.theme-option').length);
```

**Why**: Targeted testing is more efficient than trial-and-error fixes

### Phase 6: Implementation & Validation
**Objective**: Implement fix and thoroughly validate the solution

#### Step 6.1: Implement Minimal Fix
- Make the smallest possible change to fix the root cause
- Avoid "while we're here" improvements that could introduce new issues
- Document what change was made and why

#### Step 6.2: Test Fix Comprehensively
- Test the specific reported issue
- Test related functionality that might be affected
- Test edge cases and different scenarios
- Restart application and retest

#### Step 6.3: Regression Testing
- Test that other functionality still works
- Verify no new issues were introduced
- Test across different pages/scenarios

**Why**: Ensures the fix actually works and doesn't break anything else

### Phase 7: Documentation & Prevention
**Objective**: Document the solution and prevent similar issues

#### Step 7.1: Document the Solution
- Record the problem, root cause, and solution
- Update relevant documentation
- Share knowledge with team if applicable

#### Step 7.2: Identify Prevention Measures
- Could this be caught by automated testing?
- Should coding standards be updated?
- Are there patterns that led to this issue?

**Why**: Prevents recurring issues and builds organizational knowledge

---

## Common Troubleshooting Patterns

### JavaScript Event Issues
**Symptoms**: Buttons/elements don't respond to clicks
**Common Causes**:
- CSS selector mismatch (`querySelector` targeting wrong class)
- Event listeners attached before DOM elements exist
- Event propagation issues
- JavaScript errors preventing execution

**Investigation Steps**:
1. Check browser console for errors
2. Verify CSS selectors match HTML classes
3. Test if elements exist: `document.querySelectorAll('.target-class').length`
4. Check if event listeners are attached: `$0.getEventListeners()` in DevTools

### CSS Styling Issues
**Symptoms**: Elements appear wrong or don't match design
**Common Causes**:
- CSS specificity conflicts
- Missing or incorrect CSS classes
- Cascading order issues
- Media query problems

**Investigation Steps**:
1. Use browser DevTools to inspect computed styles
2. Check for CSS rule conflicts
3. Verify class names match between HTML and CSS
4. Test with CSS temporarily disabled

### Data Synchronization Issues
**Symptoms**: Data appears different between pages/components
**Common Causes**:
- LocalStorage/SessionStorage issues
- State management inconsistencies
- Timing issues with async operations
- Cache problems

**Investigation Steps**:
1. Check browser storage in DevTools
2. Monitor network requests for data fetching
3. Add logging to track data flow
4. Test with storage cleared

### Server/API Issues
**Symptoms**: Features work sometimes but not always
**Common Causes**:
- Server errors (500, 404, etc.)
- Rate limiting
- Database connection issues
- Configuration problems

**Investigation Steps**:
1. Check server logs
2. Monitor network requests
3. Test API endpoints directly
4. Verify server is running and accessible

---

## Troubleshooting Checklist

### Before Starting
- [ ] Define the problem clearly
- [ ] Reproduce the issue consistently
- [ ] Gather all relevant symptoms
- [ ] Check for obvious environmental issues

### During Investigation
- [ ] Compare working vs. broken implementations
- [ ] Check browser console for errors
- [ ] Verify HTML/CSS/JavaScript consistency
- [ ] Test individual components in isolation
- [ ] Form specific hypotheses before making changes

### After Implementing Fix
- [ ] Test the specific reported issue
- [ ] Test related functionality
- [ ] Perform regression testing
- [ ] Restart application and retest
- [ ] Document the solution

### Loop Until Success
If the fix doesn't work:
1. **Re-evaluate**: Was the hypothesis correct?
2. **Investigate Further**: Look for additional root causes
3. **Test Alternative Solutions**: Try different approaches
4. **Seek Additional Data**: Gather more diagnostic information
5. **Repeat Process**: Go through methodology again with new information

---

## Emergency Troubleshooting

### When Under Pressure
1. **Stay Systematic**: Don't skip steps even when rushed
2. **Focus on Root Cause**: Avoid symptomatic fixes that don't address the real problem
3. **Test Thoroughly**: A quick fix that breaks other things isn't really a fix
4. **Document Everything**: Future-you will thank you

### Escalation Criteria
Consider escalating or seeking help when:
- Issue affects critical functionality
- Root cause cannot be identified after systematic investigation
- Fix attempts are making the problem worse
- Time constraints require additional resources

---

## Tools and Commands

### Useful Bash Commands
```bash
# Compare files
diff -u file1.html file2.html

# Search for patterns
grep -rn "pattern" src/
grep -A 5 -B 5 "searchterm" file.html

# Check server status
curl -I http://localhost:5000

# Monitor logs (if applicable)
tail -f logfile.txt
```

### Browser DevTools
- **Console**: `console.log()`, error messages
- **Elements**: Inspect HTML/CSS, test style changes
- **Network**: Monitor requests, response codes
- **Application**: Check localStorage, sessionStorage
- **Sources**: Set breakpoints, step through JavaScript

### JavaScript Debugging
```javascript
// Check if elements exist
console.log('Elements found:', document.querySelectorAll('.selector').length);

// Test event listeners
document.querySelector('.button').addEventListener('click', () => console.log('Clicked!'));

// Check localStorage
console.log('Stored theme:', localStorage.getItem('triton-theme'));

// Verify function exists
console.log('Function exists:', typeof functionName !== 'undefined');
```

---

## Success Metrics

A troubleshooting session is successful when:
1. **Problem is resolved**: Original issue no longer occurs
2. **Root cause identified**: You understand why the problem happened
3. **Fix is minimal**: Solution addresses root cause without over-engineering
4. **No regressions**: Other functionality still works correctly
5. **Reproducible**: Fix works consistently across different scenarios
6. **Documented**: Solution is recorded for future reference

Remember: The goal is not just to make the problem go away, but to understand and solve it properly.