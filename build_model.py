import numpy as np
import pandas as pd

#データ分割用
from sklearn.model_selection import train_test_split

#LightGBM
import lightgbm as lgb

#pickle
import pickle

#データ読み込み
df_train = pd.read_csv("train.csv")
df_test = pd.read_csv("test.csv")

#データ結合
df_train["TrainFlag"] = True
df_test["TrainFlag"] = False

df_all = df_train.append(df_test)
df_all.index = df_all["Id"]
df_all.drop("Id", axis = 1, inplace = True)

#ダミー変数化
df_all = pd.get_dummies(df_all, drop_first=True)

#df_allを訓練データとテストデータに再度分ける
df_train = df_all[df_all["TrainFlag"] == True]
df_train = df_train.drop(["TrainFlag"], axis = 1)

df_test = df_all[df_all["TrainFlag"] == False]
df_test = df_test.drop(["TrainFlag"], axis = 1)
df_test = df_test.drop(["SalePrice"], axis = 1)

#データ分割
y = df_train["SalePrice"].values
X = df_train.drop("SalePrice", axis=1).values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1234)

#LGBMのデータ作成
lgb_train = lgb.Dataset(X_train, y_train)
lgb_eval = lgb.Dataset(X_test, y_test)

#パラメータ設定
params = {
        # 回帰問題
        'random_state':1234, 'verbose':0,
        # 学習用の指標 (RMSE)
        'metrics': 'rmse',
    }
num_round = 100

#モデル訓練
model = lgb.train(params, lgb_train, num_boost_round = num_round)

#モデルを保存
pickle.dump(model, open("lgb_model.pickle", "wb"))
