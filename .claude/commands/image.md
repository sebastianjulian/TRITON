# Image Analysis Command

**Command**: `/image`
**Description**: Finds the latest screenshot from OneDrive Screenshots folder and analyzes its content for visual input

## Usage
```
/image
```

## Behavior
1. Searches the OneDrive Screenshots folder for the most recent screenshot
2. Uses the Read tool to analyze the image content
3. Provides detailed description of what's displayed in the screenshot
4. Enables user to provide visual input for troubleshooting or feature requests

## Implementation
When `/image` is invoked:
1. Find latest file in `C:\Users\sebi\OneDrive - Öffentliches Schottengymnasium der Benediktiner in Wien\Pictures\Screenshots`
2. Sort files by modification time (newest first)
3. Use Read tool to analyze the most recent screenshot
4. Provide comprehensive description of image content
5. Ask user what they want to know about the screenshot

## Folder Path
```
C:\Users\sebi\OneDrive - Öffentliches Schottengymnasium der Benediktiner in Wien\Pictures\Screenshots
```

## Expected Flow
1. User types `/image`
2. Assistant finds latest screenshot in OneDrive folder
3. Assistant reads and analyzes the screenshot content
4. Assistant describes what's shown in the image
5. Assistant asks how to help with the visual content
6. User can then ask questions or request actions based on the screenshot

## Use Cases
- Visual troubleshooting (showing bugs, UI issues)
- Feature requests based on current state
- Code review with visual context
- Design feedback and improvements
- Error reporting with screenshots

## File Types Supported
- PNG, JPG, JPEG, GIF, BMP, WEBP
- Any image format that the Read tool can process