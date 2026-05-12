import sys
import os
import subprocess
from glob import glob
from io import StringIO
from unittest.mock import patch

def run_tests():
    testcases_dir = os.path.join(os.path.dirname(__file__), "testcases")
    in_files = sorted(glob(os.path.join(testcases_dir, "*.in")))
    
    overall_passed = True
    
    with open("test_result.out", "w", encoding="utf-8") as out_file:
        for in_file in in_files:
            base_name = os.path.basename(in_file)
            test_name = base_name.replace(".in", "")
            out_file_expected = os.path.join(testcases_dir, f"{test_name}.out")
            
            if not os.path.exists(out_file_expected):
                out_file.write(f"[SKIP] {test_name}: Expected output file not found.\n")
                continue
                
            with open(in_file, 'r', encoding='utf-8') as f:
                input_data = f.read()
                
            with open(out_file_expected, 'r', encoding='utf-8') as f:
                expected_output = f.read().strip()
                
            # Run main.py using subprocess to feed input
            process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=os.path.dirname(__file__),
                text=True,
                encoding='utf-8'
            )
            
            actual_output, _ = process.communicate(input=input_data)
            actual_output = actual_output.strip()
            
            if actual_output == expected_output:
                out_file.write(f"[PASS] {test_name}\n")
            else:
                out_file.write(f"[FAIL] {test_name}\n")
                out_file.write("--- EXPECTED ---\n")
                out_file.write(expected_output + "\n")
                out_file.write("--- ACTUAL ---\n")
                out_file.write(actual_output + "\n")
                overall_passed = False
                
        if overall_passed:
            out_file.write("\nAll tests passed!\n")
        else:
            out_file.write("\nSome tests failed. Please review the output above.\n")

if __name__ == "__main__":
    run_tests()
