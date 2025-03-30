import argparse
import subprocess
import os
import optuna
import matplotlib.pyplot as plt
import multiprocessing

def process_file(filename: str, input_dir: str, output_dir: str, params: list):
    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, filename)
    
    if os.path.isfile(input_path):  # ファイルのみ処理（ディレクトリは無視）
        try:
            with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                result = subprocess.run(["./run"] + list(map(str, params)), stdin=infile, stdout=outfile, stderr=subprocess.PIPE, text=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error processing {filename}: {e.stderr.decode()}")

def run_binary(input_dir: str, output_dir: str, params):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    
    with multiprocessing.Pool() as pool:
        pool.starmap(process_file, [(f, input_dir, output_dir, params) for f in files])

def get_score(input_file, output_file):
    """Executes the `vis` binary and extracts the score from its output."""
    result = subprocess.run(["./vis", input_file, output_file], capture_output=True, text=True, check=True)
    for line in result.stdout.split("\n"):
        if "Score =" in line:
            return int(line.split("=")[1].strip())
    return 0  # Default if score is not found

def objective(trial):
    """Optuna objective function to maximize the total score."""
    # https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/002_configurations.html#pythonic-search-space
    # note: params を編集する
    params = [
        trial.suggest_int("param1", 1, 100),
        trial.suggest_int("param2", 1, 100),
        trial.suggest_int("param3", 1, 100),
    ]
    
    run_binary(objective.input_dir, objective.output_dir, params)
    total_score = 0
    for file in os.listdir(objective.input_dir):
        input_file = os.path.join(objective.input_dir, file)
        output_file = os.path.join(objective.output_dir, file)
        total_score += get_score(input_file, output_file)
    
    return total_score

def main(input_dir, output_dir):
    """Runs the Optuna optimization and visualizes the results."""
    objective.input_dir = input_dir
    objective.output_dir = output_dir
    
    study = optuna.create_study(direction="maximize")
    # study.optimize(objective, n_trials=50)
    study.optimize(objective)
    
    print("Best parameters:", study.best_params)
    print("Best score:", study.best_value)
    
    optuna.visualization.matplotlib.plot_optimization_history(study)
    plt.savefig("optimization_history.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=str, help="Path to input directory")
    parser.add_argument("output_dir", type=str, help="Path to output directory")
    args = parser.parse_args()
    
    main(args.input_dir, args.output_dir)
