# Image Analysis Command

**Command**: `/image`
**Description**: Finds the latest screenshot from OneDrive Screenshots folder and analyzes its content for visual input

## Usage
```
/image [optional: specific filename]
```

## Behavior
1. Searches the OneDrive Screenshots folder for the most recent screenshot
2. Uses robust error handling for file access and sorting
3. Falls back to alternative methods if primary approach fails
4. Uses the Read tool to analyze the image content
5. Provides detailed description of what's displayed in the screenshot
6. Enables user to provide visual input for troubleshooting or feature requests

## Implementation
When `/image` is invoked, the assistant will:

### Step 1: Robust File Discovery
Try multiple approaches to find the latest screenshot, in order of preference:

**Primary Method (PowerShell):**
```bash
powershell "Get-ChildItem 'C:\Users\sebi\OneDrive - Öffentliches Schottengymnasium der Benediktiner in Wien\Pictures\Screenshots\*.png' | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Select-Object Name, LastWriteTime"
```

**Fallback Method 1 (ls with error handling):**
```bash
ls -la "C:\Users\sebi\OneDrive - Öffentliches Schottengymnasium der Benediktiner in Wien\Pictures\Screenshots"/*.png 2>/dev/null | tail -1
```

**Fallback Method 2 (dir command):**
```bash
dir "C:\Users\sebi\OneDrive - Öffentliches Schottengymnasium der Benediktiner in Wien\Pictures\Screenshots" /b /o-d 2>nul | findstr "\.png$" | head -1
```

**Fallback Method 3 (Manual parsing):**
Parse the file listing manually and extract the most recent timestamp.

### Step 2: Error Handling
- Handle cases where no screenshots exist
- Handle permission errors gracefully
- Handle malformed file names or paths
- Provide clear error messages to user

### Step 3: Image Analysis
- Attempt to read the identified screenshot file
- Handle image format errors gracefully
- Provide fallback if image cannot be processed

### Step 4: User Feedback
- Always inform user which screenshot is being analyzed
- Include timestamp and filename information
- Provide clear description of image content

## Folder Path
```
C:\Users\sebi\OneDrive - Öffentliches Schottengymnasium der Benediktiner in Wien\Pictures\Screenshots
```

## Expected Flow
1. User types `/image` or `/image [filename]`
2. Assistant attempts to find latest screenshot using robust methods
3. If successful: reads and analyzes the screenshot content
4. If failed: provides clear error message and suggests alternatives
5. Assistant describes what's shown in the image with filename/timestamp
6. Assistant asks how to help with the visual content

## Error Handling Scenarios
- **No screenshots found**: "No screenshots found in OneDrive folder. Please take a screenshot first."
- **Permission denied**: "Cannot access OneDrive Screenshots folder. Please check permissions."
- **Image read error**: "Found screenshot but cannot read image file. File may be corrupted."
- **Command errors**: Gracefully fall back to alternative file discovery methods
- **Path issues**: Handle spaces and special characters in file paths properly

## Use Cases
- Visual troubleshooting (showing bugs, UI issues)
- Feature requests based on current state
- Code review with visual context
- Design feedback and improvements
- Error reporting with screenshots
- UI/UX analysis and improvements
- Documentation with visual examples

## File Types Supported
- PNG, JPG, JPEG, GIF, BMP, WEBP
- Any image format that the Read tool can process

## Advanced Features
- **Specific file selection**: User can specify a particular screenshot filename
- **Timestamp reporting**: Shows when the screenshot was taken
- **Multiple fallback methods**: Ensures command works even if primary method fails
- **Clear error messaging**: User knows exactly what went wrong and how to fix it
- **Path safety**: Properly handles paths with spaces and special characters