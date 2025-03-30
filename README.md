# これはなに？

## バッチ処理を実行するスクリプト (batch.py)

AHC 用のバッチで流すためのスクリプト。並列処理するので早いはず。

### 実行方法

1. 実行用のバイナリをルートに `run` として用意する
1. スコア計算用のバイナリをルートに `vis` として用意する
1. 以下を実行する。結果は `result.csv` にできる

```bash
python3 batch.py <input_dir> <output_dir>
```

### 仕様

- 実行時のバイナリで、標準エラー出力に `loop_count: \d+` として出力していると、数字を出す
- スコア計算用のバイナリのスコアは、 `Score = \d+` を期待する

## パラメータチューニングするためのスクリプト (tuning.py)

### 実行方法 (大体 batch.py と同じ)

1. 実行用のバイナリをルートに `run` として用意する
1. スコア計算用のバイナリをルートに `vis` として用意する
1. チューニングしたいパラメータを、 `tuning.py` を編集して設定する。具体的には 
1. 以下を実行する。結果は 標準出力される

```python
def objective(trial):
    """Optuna objective function to maximize the total score."""
    # https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/002_configurations.html#pythonic-search-space
    # note: params を編集する
    params = [
        trial.suggest_int("param1", 1, 100),
        trial.suggest_int("param2", 1, 100),
        trial.suggest_int("param3", 1, 100),
    ]
```

```bash
python3 tuning.py <input_dir> <output_dir>
```

## TODO

- チューニングするパラメータが設定しやすく(わかりやすく)するように
- インタラクティブ用に公式に用意されているバイナリの、出力形式を合わせたものにする
