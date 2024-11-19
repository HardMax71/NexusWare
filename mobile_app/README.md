# NexusWare Mobile App

## Overview

NexusWare Mobile is built using the Toga framework, providing a native mobile experience for warehouse management tasks. 
This README provides detailed instructions for setting up, installing, and running the mobile application.

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git
- Xcode (for iOS development on macOS)
- Android Studio and SDK (for Android development)

## Development Environment Setup

### macOS Setup for iOS Development
1. Install Xcode from the App Store
2. Install Xcode Command Line Tools:
  `xcode-select --install`
3. Accept Xcode license:
  `sudo xcodebuild -license accept`

### Android Setup
1. Install Android Studio
2. Install Android SDK through Android Studio
3. Add the following to your ~/.bash_profile or ~/.zshrc:
  ```bash
  export ANDROID_SDK_ROOT=$HOME/Library/Android/sdk
  export PATH=$PATH:$ANDROID_SDK_ROOT/tools/bin
  export PATH=$PATH:$ANDROID_SDK_ROOT/platform-tools
  ```

## Project Setup

1. Clone the repository and navigate to mobile app directory:
  ```bash
  git clone https://github.com/HardMax71/NexusWare.git
  cd NexusWare
  git checkout -b mobile_app
  cd mobile_app
  ```

2. Create and activate virtual environment:
```bash
  python3 -m venv venv
  source venv/bin/activate  # On macOS/Linux
  # or
  .\venv\Scripts\activate  # On Windows
```

3. Install required packages:
  `pip install toga briefcase`

4. Project Structure:

```  
mobile_app/
  ├── src/
  │   └── nexusware/
  │       ├── __init__.py
  │       ├── __main__.py
  │       └── app.py
  ├── pyproject.toml
  └── LICENSE
```

## Development

### Running in Dev Mode
To test the application during development:
`briefcase dev`

### Creating Platform-Specific Projects
Create scaffolding for different platforms:
# For iOS
`briefcase create ios`

# For Android
`briefcase create android`

### Building the Application
Build for specific platforms:
# For iOS
`briefcase build ios`

# For Android
`briefcase build android`

### Running on Devices/Simulators
# Run on iOS simulator
`briefcase run ios`

# Run on Android emulator
`briefcase run android`

### Debugging
- Logs are stored in the `logs/` directory
- Use briefcase run ios -v or briefcase run android -v for verbose output
- Check iOS console logs in Xcode
- Use Android Studio's logcat for Android debugging

## Support
- Create issues in GitHub repository
- Check Toga documentation: https://toga.readthedocs.io/
- Check Briefcase documentation: https://briefcase.readthedocs.io/

## License
This project is licensed under the MIT License - see the LICENSE file for details.