#!/usr/bin/env python3
"""
Altseason Sentinel - Quick Start Script
Automated setup and installation helper
"""

import subprocess
import sys
import os


def check_python_version():
    """Verify Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. You have {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def check_dependencies():
    """Check if required packages are installed"""
    required = ['requests', 'yaml', 'rich', 'pandas']
    missing = []
    
    for package in required:
        try:
            if package == 'yaml':
                __import__('yaml')
            else:
                __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} not found")
            missing.append(package)
    
    return missing


def install_dependencies(missing):
    """Install missing dependencies"""
    if not missing:
        return True
    
    print(f"\n📦 Installing missing packages: {', '.join(missing)}")
    
    # Map package import names to pip names
    pip_names = {
        'yaml': 'pyyaml',
        'dateutil': 'python-dateutil'
    }
    
    packages_to_install = [pip_names.get(pkg, pkg) for pkg in missing]
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            *packages_to_install
        ])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages")
        print("   Try manually: pip install -r requirements.txt")
        return False


def check_config():
    """Check if config file exists and is valid"""
    if not os.path.exists('config.yaml'):
        print("❌ config.yaml not found")
        return False
    
    print("✅ config.yaml found")
    
    # Read and check basic config
    try:
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Check if Discord webhook is configured
        webhook = config.get('discord', {}).get('webhook_url', '')
        if webhook == 'YOUR_DISCORD_WEBHOOK_URL':
            print("⚠️  Discord webhook not configured (terminal-only mode)")
            print("   See README.md for Discord setup instructions")
        else:
            print("✅ Discord webhook configured")
        
        return True
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False


def run_sentinel():
    """Start the sentinel"""
    print("\n" + "=" * 60)
    print("🚀 Starting Altseason Sentinel...")
    print("=" * 60)
    print("\nPress Ctrl+C to stop\n")
    
    try:
        subprocess.run([sys.executable, 'altseason_sentinel.py'])
    except KeyboardInterrupt:
        print("\n\n👋 Sentinel stopped. See you next time!")


def main():
    print("=" * 60)
    print("🔧 Altseason Sentinel - Quick Start")
    print("=" * 60)
    print()
    
    # Step 1: Check Python version
    if not check_python_version():
        print("\n❌ Please install Python 3.8 or higher")
        sys.exit(1)
    
    # Step 2: Check dependencies
    print()
    missing = check_dependencies()
    
    # Step 3: Install if needed
    if missing:
        print()
        response = input("Install missing packages now? (y/n): ").strip().lower()
        if response == 'y':
            if not install_dependencies(missing):
                sys.exit(1)
        else:
            print("Please install manually: pip install -r requirements.txt")
            sys.exit(1)
    
    # Step 4: Check config
    print()
    if not check_config():
        print("\n⚠️  Config issues detected. Please check config.yaml")
    
    print("\n✅ All checks passed!")
    
    # Step 5: Offer to run
    print()
    response = input("Start Altseason Sentinel now? (y/n): ").strip().lower()
    if response == 'y':
        run_sentinel()
    else:
        print("\nTo start later, run: python altseason_sentinel.py")
        print("For Discord setup, see README.md")


if __name__ == "__main__":
    main()
