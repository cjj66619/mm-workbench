#import "../lib.typ": *

// 官方模板：附录先列支撑材料文件清单，再放源代码；每段代码前说明语言与作用，AI 生成的代码需标注工具信息。
#three-line-table(
  [支撑材料文件清单],
  (auto, 1fr),
  ([文件], [说明]),
  (
    [`q1_main.py`], [问题一数据预处理与模型求解],
    [`q1_results.csv`], [问题一结果表],
  ),
)

*代码 1*：Python，问题一模型求解（该部分代码使用 AI 工具：工具名称, 版本/型号, 开发机构, YYYY-MM-DD）

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

data = pd.read_csv('data.csv')
X = data.drop('target', axis=1); y = data['target']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
print(f'R2: {r2_score(y_test, model.predict(X_test)):.4f}')
```
