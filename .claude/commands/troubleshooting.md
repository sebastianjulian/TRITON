# Troubleshooting Command

**Command**: `/troubleshooting`
**Description**: Initiates systematic troubleshooting process by reading the troubleshooting guide and waiting for problem description

## Usage
```
/troubleshooting
```

## Behavior
1. Reads the comprehensive troubleshooting guide from `TROUBLESHOOTING.md`
2. Presents the systematic methodology overview
3. Waits for user to describe the specific problem
4. Follows the documented troubleshooting phases systematically
5. Loops through investigation-fix-test cycle until issue is resolved

## Implementation
When `/troubleshooting` is invoked:
1. Read and present key sections from `TROUBLESHOOTING.md`
2. Ask user to describe the problem following the Phase 1 format
3. Proceed through troubleshooting phases systematically
4. Test each fix thoroughly before marking as complete
5. Continue until user confirms issue is resolved

## Files Referenced
- `TROUBLESHOOTING.md`: Main troubleshooting methodology document
- Project files as needed during investigation

## Expected Flow
1. User types `/troubleshooting`
2. Assistant reads troubleshooting guide
3. Assistant asks for problem description
4. Assistant follows systematic phases from the guide
5. Assistant tests fixes comprehensively
6. Loop continues until problem is fully resolved