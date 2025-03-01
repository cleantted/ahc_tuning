import os
import subprocess
import argparse
import multiprocessing
import re
import csv

def process_file(filename: str, input_dir: str, output_dir: str, binary: str = "./run"):
    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, filename)
    
    if os.path.isfile(input_path):  # ファイルのみ処理（ディレクトリは無視）
        try:
            with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                result = subprocess.run([binary], stdin=infile, stdout=outfile, stderr=subprocess.PIPE, text=True, check=True)
                loop_count_match = re.search(r"loop_count:\s*(\d+)", result.stderr)
                loop_count = int(loop_count_match.group(1)) if loop_count_match else None
                return filename, loop_count
        except subprocess.CalledProcessError as e:
            print(f"Error processing {filename}: {e.stderr.decode()}")
    return filename, None

def process_files(input_dir: str, output_dir: str, binary: str = "./run"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    
    with multiprocessing.Pool() as pool:
        results = pool.starmap(process_file, [(f, input_dir, output_dir, binary) for f in files])
    
    return dict(results)

def evaluate_results(input_dir: str, output_dir: str, loop_counts: dict, vis_binary: str = "./vis", result_file: str = "result.csv"):
    results = []
    files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    
    for filename in files:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        try:
            result = subprocess.run([vis_binary, input_path, output_path], capture_output=True, text=True, check=True)
            match = re.search(r"Score\s*=\s*(\d+)", result.stdout)
            if match:
                score = int(match.group(1))
                loop_count = loop_counts.get(filename, None)
                results.append((filename, score, loop_count))
        except subprocess.CalledProcessError as e:
            print(f"Error evaluating {filename}: {e.stderr.decode()}")
    
    results.sort()  # ファイル名でソート
    
    with open(result_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Filename", "Score", "Loop Count"])
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process files with a binary and evaluate results.")
    parser.add_argument("input_dir", help="Path to the input directory")
    parser.add_argument("output_dir", help="Path to the output directory")
    args = parser.parse_args()
    
    loop_counts = process_files(args.input_dir, args.output_dir)
    evaluate_results(args.input_dir, args.output_dir, loop_counts)
