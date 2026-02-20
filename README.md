# Task & Reminder Widget App

A sleek, floating desktop widget for managing tasks with an integrated Pomodoro timer, dark/light mode, and comprehensive settings.

## Features

✨ **Core Features:**
- ✅ Circle checkbox system for task completion
- 🎯 Integrated Pomodoro timer with visual progress circle
- 🌙 Dark mode and light mode themes
- 💾 Persistent storage of tasks and settings
- 🔊 Sound notifications for timer completion
- ⏰ Customizable break intervals
- 🪟 Floating window (stays on top, draggable anywhere)

## System Requirements

- Windows 7 or later
- Python 3.9+ (if running from source)
- ~200MB disk space (if building to EXE)

## Installation & Setup

### Option 1: Run from Python (Recommended for Development)

1. **Install Python 3.9 or higher** from [python.org](https://www.python.org)
   - Make sure to check "Add Python to PATH" during installation

2. **Download the files** and place them in a folder

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```
   python task_widget_app.py
   ```

   Or simply double-click `run.bat`

### Option 2: Build Standalone EXE (Recommended for Distribution)

1. **Install Python 3.9 or higher** from [python.org](https://www.python.org)

2. **Download the files** and open command prompt in that folder

3. **Build the executable:**
   ```
   build.bat
   ```

   The executable will be created in the `dist` folder as `TaskWidget.exe`

4. **Run the EXE:**
   - Double-click `TaskWidget.exe`
   - Or create a shortcut on your desktop/taskbar

## How to Use

### Basic Task Management
1. **Add a task:** Type in the text field and press Enter or click "Add"
2. **Complete a task:** Click the circle checkbox next to any task
3. **Clear completed:** Click the "🗑 Clear" button to remove all checked tasks

### Pomodoro Timer

The circular timer at the top displays your work session:

- **Green circle:** Shows your remaining time (fills as you progress)
- **Start button:** Begin the timer
- **Pause button:** Pause the current session
- **Reset button:** Reset to initial duration

**How it works:**
1. Click "Start" to begin a 25-minute work session (default)
2. Timer counts down and shows remaining time
3. When time's up: beep sound → automatic short break (5 min)
4. After 4 sessions: long break (15 min) instead
5. Customize all durations in Settings

### Theme & Appearance

**Theme Button (🌙):**
- Toggle between dark mode (default) and light mode
- Changes instantly across all elements
- Setting is saved for next session

### Settings (⚙ Icon)

Open Settings to customize:

**Sound Settings:**
- ☑ Sound Enabled: Toggle notification beeps on/off

**Reminder Settings:**
- ☑ Reminder Enabled: Toggle reminder notifications
- Reminder Interval: (future implementation for task reminders)

**Pomodoro Settings:**
- Pomodoro Duration: Work session length (5-60 min)
- Short Break: Rest after each session (1-30 min)
- Long Break: Extended break after 4 sessions (1-60 min)

**Task Settings:**
- Dark Mode: Currently toggled via theme button

### Floating Window

The widget stays on top of other windows:

- **Move it:** Click and drag the window anywhere
- **Position saved:** Window position is remembered next time you launch
- **Always visible:** Widget stays above other windows unless minimized

## File Storage

App data is stored in your user profile:

```
C:\Users\YourUsername\.task_widget\
├── config.json    (Settings and window position)
└── tasks.json     (Your tasks and completion status)
```

You can delete these files to reset the app to defaults.

## Keyboard Shortcuts

- **Enter** (in task input): Add a new task
- **Click + Drag**: Move the window

## Troubleshooting

**"Python not found" error:**
- Install Python from python.org
- Make sure "Add Python to PATH" is checked
- Restart your computer after installing

**"PyQt6 not found" error:**
- Run: `pip install PyQt6`

**App won't start:**
- Check that Python 3.9+ is installed: `python --version`
- Delete `.task_widget` folder in your home directory to reset
- Try running `run.bat` again

**Sound not working:**
- Check that your volume is on
- Ensure "Sound Enabled" is checked in Settings

**Can't move window:**
- Click and drag from the title bar or any empty area
- If no title bar, click and drag from the top of the window

## Building the EXE

If you want to create a standalone executable:

1. Run `build.bat` in the folder with all files
2. Wait for the build to complete (takes 1-2 minutes)
3. Find `TaskWidget.exe` in the `dist` folder
4. Copy this file anywhere and run it - no Python installation needed!

**Note:** First run of the exe takes longer to extract. Subsequent runs are instant.

## Tips & Tricks

💡 **Multi-monitor setup:** The widget remembers which monitor you last placed it on

💡 **Keyboard input:** Use Tab to navigate between buttons without clicking

💡 **High DPI screens:** The app auto-scales to your display

💡 **Minimize behavior:** Click the minimize button to hide the widget (stays in taskbar)

## Feature Roadmap

Future improvements:
- [ ] Categories/Tags for tasks
- [ ] Due dates and time-based reminders
- [ ] Task statistics and history
- [ ] Custom colors and themes
- [ ] Integration with calendar
- [ ] Data sync to cloud
- [ ] Android/iOS companion app

## License

Free to use and modify for personal use.

## Support

For issues or suggestions:
1. Check the Troubleshooting section above
2. Ensure you're using the latest version
3. Try deleting `.task_widget` folder to reset

Enjoy your productivity! 🚀
