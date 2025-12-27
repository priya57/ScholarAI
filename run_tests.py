#!/usr/bin/env python3
"""
Test runner script for ScholarAI
Provides different test execution options
"""

import subprocess
import sys
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*50}")
    
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"[FAIL] {description} failed with exit code {result.returncode}")
        return False
    else:
        print(f"[PASS] {description} completed successfully")
        return True

def run_unit_tests():
    """Run unit tests only"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/test_document_processor.py",
        "tests/test_vector_store.py", 
        "tests/test_rag_engine.py",
        "-v", "--tb=short"
    ]
    return run_command(cmd, "Unit Tests")

def run_integration_tests():
    """Run integration tests"""
    cmd = [
        "python", "-m", "pytest",
        "tests/test_integration.py",
        "-v", "--tb=short"
    ]
    return run_command(cmd, "Integration Tests")

def run_api_tests():
    """Run API tests"""
    cmd = [
        "python", "-m", "pytest",
        "tests/test_api.py",
        "-v", "--tb=short"
    ]
    return run_command(cmd, "API Tests")

def run_cli_tests():
    """Run CLI tests"""
    cmd = [
        "python", "-m", "pytest",
        "tests/test_cli.py",
        "-v", "--tb=short"
    ]
    return run_command(cmd, "CLI Tests")

def run_performance_tests():
    """Run performance tests"""
    cmd = [
        "python", "-m", "pytest",
        "tests/test_performance.py",
        "-v", "--tb=short", "-s"
    ]
    return run_command(cmd, "Performance Tests")

def run_all_tests():
    """Run all tests"""
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "-v", "--tb=short"
    ]
    return run_command(cmd, "All Tests")

def run_tests_with_coverage():
    """Run tests with coverage report"""
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "--cov=src",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v"
    ]
    return run_command(cmd, "Tests with Coverage")

def run_fast_tests():
    """Run fast tests only (exclude performance tests)"""
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "-v", "--tb=short",
        "-k", "not performance"
    ]
    return run_command(cmd, "Fast Tests (excluding performance)")

def main():
    parser = argparse.ArgumentParser(description="ScholarAI Test Runner")
    parser.add_argument(
        "test_type",
        choices=[
            "unit", "integration", "api", "cli", "performance", 
            "all", "coverage", "fast"
        ],
        help="Type of tests to run"
    )
    
    args = parser.parse_args()
    
    # Check if pytest is available
    try:
        subprocess.run(["python", "-m", "pytest", "--version"], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("[FAIL] pytest is not installed. Please install test requirements:")
        print("pip install -r requirements-test.txt")
        sys.exit(1)
    
    # Run the appropriate tests
    success = False
    
    if args.test_type == "unit":
        success = run_unit_tests()
    elif args.test_type == "integration":
        success = run_integration_tests()
    elif args.test_type == "api":
        success = run_api_tests()
    elif args.test_type == "cli":
        success = run_cli_tests()
    elif args.test_type == "performance":
        success = run_performance_tests()
    elif args.test_type == "all":
        success = run_all_tests()
    elif args.test_type == "coverage":
        success = run_tests_with_coverage()
    elif args.test_type == "fast":
        success = run_fast_tests()
    
    if success:
        print(f"\n[SUCCESS] {args.test_type.title()} tests completed successfully!")
        if args.test_type == "coverage":
            print("[INFO] Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n[FAILED] {args.test_type.title()} tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()