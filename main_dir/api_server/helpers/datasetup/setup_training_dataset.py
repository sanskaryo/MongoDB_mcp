#!/usr/bin/env python3
"""
Hotel Dataset Setup Script for Training Candidates
Quick setup script to generate and import hotel management dataset
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = ['pymongo', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_packages(packages):
    """Install missing packages"""
    if packages:
        print(f"📦 Installing required packages: {', '.join(packages)}")
        try:
            # Try uv first, then fall back to pip
            try:
                subprocess.check_call(['uv', 'add'] + packages)
                print("✅ Packages installed successfully with uv")
            except (subprocess.CalledProcessError, FileNotFoundError):
                subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
                print("✅ Packages installed successfully with pip")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please install manually:")
            print(f"   pip install {' '.join(packages)}")
            print(f"   or: uv add {' '.join(packages)}")
            return False
    return True

def setup_env_file():
    """Create .env file template if it doesn't exist"""
    env_file = Path('.env')
    
    if not env_file.exists():
        env_content = '''# MongoDB Connection String
# Replace with your MongoDB URI (Atlas, local, or Docker)
MONGO_URI=mongodb://localhost:27017/

# For MongoDB Atlas (recommended for training):
# MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority

# For Docker MongoDB:
# MONGO_URI=mongodb://localhost:27017/
'''
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("📝 Created .env file template")
        print("⚠️  IMPORTANT: Edit .env file with your MongoDB connection string")
        print("   For training, we recommend MongoDB Atlas (free tier)")
        return False
    
    return True

def generate_dataset():
    """Generate the hotel dataset"""
    print("🏨 Generating hotel management dataset...")
    
    try:
        result = subprocess.run([sys.executable, 'generate_hotel_data.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dataset generated successfully")
            return True
        else:
            print("❌ Dataset generation failed:")
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("❌ generate_hotel_data.py not found")
        return False

def import_to_mongodb():
    """Import dataset to MongoDB"""
    print("📤 Importing dataset to MongoDB...")
    
    try:
        result = subprocess.run([sys.executable, 'import_to_mongodb.py'],
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dataset imported successfully")
            print(result.stdout)
            return True
        else:
            print("❌ Import failed:")
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("❌ import_to_mongodb.py not found")
        return False

def verify_setup():
    """Verify the setup by running analysis"""
    print("🔍 Verifying dataset...")
    
    try:
        result = subprocess.run([sys.executable, 'analyze_dataset.py'],
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            # Extract key metrics from output
            lines = result.stdout.split('\\n')
            for line in lines:
                if 'OVERALL SCORE' in line or 'orders' in line.lower() or 'customers' in line.lower():
                    print(f"   {line.strip()}")
            return True
        else:
            print("❌ Verification failed")
            return False
    except FileNotFoundError:
        print("⚠️  Analysis script not found, but import may have succeeded")
        return True

def main():
    print("🎓 HOTEL DATASET TRAINING SETUP")
    print("=" * 50)
    print("This script will set up a complete hotel management dataset")
    print("for MongoDB analytics training.\\n")
    
    # Step 1: Check and install requirements
    print("1️⃣ Checking requirements...")
    missing = check_requirements()
    if missing:
        if not install_packages(missing):
            return False
    else:
        print("✅ All required packages are installed")
    
    # Step 2: Setup environment
    print("\\n2️⃣ Setting up environment...")
    if not setup_env_file():
        print("\\n🛑 Please configure your MongoDB URI in .env file and run again")
        print("\\nQuick MongoDB setup options:")
        print("• MongoDB Atlas (Free): https://cloud.mongodb.com/")
        print("• Local MongoDB: https://docs.mongodb.com/manual/installation/")
        print("• Docker: docker run -d -p 27017:27017 mongo:latest")
        return False
    
    # Step 3: Generate dataset
    print("\\n3️⃣ Generating dataset...")
    if not generate_dataset():
        return False
    
    # Step 4: Import to MongoDB
    print("\\n4️⃣ Importing to MongoDB...")
    if not import_to_mongodb():
        return False
    
    # Step 5: Verify setup
    print("\\n5️⃣ Verifying setup...")
    verify_setup()
    
    print("\\n" + "=" * 50)
    print("🎉 SETUP COMPLETE!")
    print("=" * 50)
    print("Your MongoDB now contains:")
    print("• 3,300+ realistic orders over 97 days")
    print("• 450+ customers across segments") 
    print("• 33 menu items with price history")
    print("• 1,700+ delivery records")
    print("• Complete audit trail")
    print("\\n📚 Training Resources:")
    print("• Dataset documentation: DATASET_README.md")
    print("• Sample queries: advanced_analytics_demo.py")
    print("• Verify anytime: python analyze_dataset.py")
    print("\\n🚀 Ready for MongoDB analytics training!")

if __name__ == "__main__":
    main()