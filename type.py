# -*- coding: utf-8 -*-
"""Untitled0.ipynb のコピー

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1y_Pv8q4oZHZOCZHaBhiyS_C9RlFhD2LT
"""

# Commented out IPython magic to ensure Python compatibility.
from sklearn.model_selection import train_test_split
import random
from sklearn.utils import shuffle
import numpy as np
from mpl_toolkits.mplot3d import Axes3D





# 数字の文字をID化
char2id = {str(i) : i for i in range(10)}

# 空白(10)：系列の長さを揃えるようのパディング文字
# -(11)：マイナスの文字
# _(12)：系列生成開始を知らせる文字
char2id.update({" ":10, "-":11, "_":12})

# 各バッチデータの予測値の分散を求める
def cal_variance(y_str, p_str):

  y_float = float(y_str)
  p_float = float(p_str)

  # 分散もどきの計算
  tmp = ((y_float - p_float)**2)
  return tmp

def cal_deviation(var, nc):
  if nc==15000:
    nc=14999
  dec = np.sqrt(var/(15000-nc))
  return dec

def check_number(p_str):
    f = 0

    if len(p_str) < 2:
      f = 1
    else:
      for check in range(len(p_str)-1):
        if p_str[check+1]=='-':
          f=1
    return f




# データをバッチ化するための関数
def train2batch(input_data, output_data, batch_size=100):
    input_batch = []
    output_batch = []
    input_shuffle, output_shuffle = shuffle(input_data, output_data)
    for i in range(0, len(input_data), batch_size):
      input_batch.append(input_shuffle[i:i+batch_size])
      output_batch.append(output_shuffle[i:i+batch_size])
    return input_batch, output_batch

import torch
import torch.nn as nn
import torch.optim as optim


# 空白込みの３桁の数字をランダムに生成
def generate_number(dig):
    number = [random.choice(list("0123456789")) for _ in range(random.randint(1, dig))]
    return int("".join(number))


# 系列の長さを揃えるために空白パディング
def add_padding(number, dig, is_input=True):
    number = "{: <{width1}}".format(number, width1=1+dig*2) if is_input else "{: <{width2}}".format(number, width2=2+2*dig)
    return number

embedding_dim = 200 # 文字の埋め込み次元数
hidden_dim = 128 # LSTMの隠れ層のサイズ
vocab_size = len(char2id) # 扱う文字の数。今回は１３文字

# GPU使う用
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Encoderクラス
class Encoder(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim):
        super(Encoder, self).__init__()
        self.hidden_dim = hidden_dim
        self.word_embeddings = nn.Embedding(vocab_size, embedding_dim, padding_idx=char2id[" "])
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True)

    def forward(self, sequence):
        embedding = self.word_embeddings(sequence)
        # Many to Oneなので、第２戻り値を使う
        _, state = self.lstm(embedding)
        # state = (h, c)
        return state

# Decoderクラス
class Decoder(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim):
        super(Decoder, self).__init__()
        self.hidden_dim = hidden_dim
        self.word_embeddings = nn.Embedding(vocab_size, embedding_dim, padding_idx=char2id[" "])
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
        # LSTMの128次元の隠れ層を13次元に変換する全結合層
        self.hidden2linear = nn.Linear(hidden_dim, vocab_size)

    def forward(self, sequence, encoder_state):
        embedding = self.word_embeddings(sequence)
        # Many to Manyなので、第１戻り値を使う。
        # 第２戻り値は推論時に次の文字を生成するときに使います。
        output, state = self.lstm(embedding, encoder_state)
        output = self.hidden2linear(output)
        return output, state

# Decoderのアウトプットのテンソルから要素が最大のインデックスを返す。つまり生成文字を意味する
def get_max_index(decoder_output):
  results = []
  for h in decoder_output:
    results.append(torch.argmax(h))
  return torch.tensor(results, device=device).view(BATCH_NUM, 1)
  

# GPU使えるように。
encoder = Encoder(vocab_size, embedding_dim, hidden_dim).to(device)
decoder = Decoder(vocab_size, embedding_dim, hidden_dim).to(device)

# 損失関数
criterion = nn.CrossEntropyLoss()

# 最適化
encoder_optimizer = optim.Adam(encoder.parameters(), lr=0.001)
decoder_optimizer = optim.Adam(decoder.parameters(), lr=0.001)


# 確認
#num = generate_number(dig)
#print("\"" + str(add_padding(num, dig)) + "\"")
# "636    "
# 7

#生成する数の桁数
dig = 5
dig_losses=[]


BATCH_NUM = 100
EPOCH_NUM = 100
dig_dic0 = []
dig_col0 = []
dig_nc0 = []
dig_dic1 = []
dig_col1 = []
dig_nc1 = []
dig_dic2 = []
dig_col2 = []
dig_nc2 = []
dig_dic3 = []
dig_col3 = []
dig_nc3 = []

dig_bun=0
no_count=0

rate_bar = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
epock_bar = [0, 20, 40, 60, 80, 100]
dig_bar = list(range(1, dig+1, 1))

#演算の種類 足し算:0 引き算:1 掛け算:2


all_losses = []
for cal in range(4):
  if cal == 0:
    print("和")
  if cal == 1:
    print("差(正負)")
  if cal == 2:
    print("積")
  if cal == 3:
    print("差(正のみ)")
  for k in range(dig):
    dig_num = k+1
    print("桁数:%d" %dig_num)
    
    # データ準備
    input_data = []
    output_data = []

  # データを５００００件準備する
    while len(input_data) < 50000:

      x = generate_number(dig_num)
      if (cal==0):
        y = generate_number(dig_num)
        z = x + y   
      if (cal==1):
        y = generate_number(dig_num)
        z = x - y   
      if (cal==2):
        y = generate_number(dig_num)
        z = x * y   
      if (cal==3):
        y = random.randint(0, x)
        z = x - y
      input_char = add_padding(str(x) + "-" + str(y), dig_num)
      output_char = add_padding("_" + str(z), dig, is_input=False)

      # データをIDにに変換
      input_data.append([char2id[c] for c in input_char])
      output_data.append([char2id[c] for c in output_char])

  # 確認
    #print(input_data[987])
    #print(output_data[987])
  # [1, 5, 11, 2, 6, 6, 10]　（←"15-266"）
  # [12, 11, 2, 5, 1]　（←"_-251"）

  # ７：３にデータをわける
    train_x, test_x, train_y, test_y = train_test_split(input_data, output_data, train_size= 0.7)





    #print("training ...")
    for epoch in range(1, EPOCH_NUM+1):
      epoch_loss = 0 # epoch毎のloss

      # データをミニバッチに分ける
      input_batch, output_batch = train2batch(train_x, train_y, batch_size=BATCH_NUM)

      for i in range(len(input_batch)):

          # 勾配の初期化
          encoder_optimizer.zero_grad()
          decoder_optimizer.zero_grad()

          # データをテンソルに変換
          input_tensor = torch.tensor(input_batch[i], device=device)
          output_tensor = torch.tensor(output_batch[i], device=device)

          # Encoderの順伝搬
          encoder_state = encoder(input_tensor)

          # Decoderで使うデータはoutput_tensorを１つずらしたものを使う
          # Decoderのインプットとするデータ
          source = output_tensor[:, :-1]

          # Decoderの教師データ
          # 生成開始を表す"_"を削っている
          target = output_tensor[:, 1:]

          loss = 0
          # 学習時はDecoderはこのように１回呼び出すだけでグルっと系列をループしているからこれでOK
          # sourceが４文字なので、以下でLSTMが4回再帰的な処理してる
          decoder_output, _ = decoder(source, encoder_state)
          # decoder_output.size() = (100,4,13)
          # 「13」は生成すべき対象の文字が13文字あるから。decoder_outputの3要素目は
          # [-14.6240,  -3.7612, -11.0775,  ...,  -5.7391, -15.2419,  -8.6547]
          # こんな感じの値が入っており、これの最大値に対応するインデックスを予測文字とみなす

          for j in range(decoder_output.size()[1]):
              # バッチ毎にまとめてloss計算
              # 生成する文字は4文字なので、4回ループ
              loss += criterion(decoder_output[:, j, :], target[:, j])

          epoch_loss += loss.item()

          # 誤差逆伝播
          loss.backward()

          # パラメータ更新
          # Encoder、Decoder両方学習
          encoder_optimizer.step()
          decoder_optimizer.step()

      # 損失を表示
      if epoch % 10 == 0:
        print("Epoch %d: %.2f" % (epoch, epoch_loss))
      all_losses.append(epoch_loss)
      #if epoch_loss < 1: break

        # 評価用データ
      test_input_batch, test_output_batch = train2batch(test_x, test_y)
      input_tensor = torch.tensor(test_input_batch, device=device)

      predicts = []
      for i in range(len(test_input_batch)):
        with torch.no_grad(): # 勾配計算させない
          encoder_state = encoder(input_tensor[i])

          # Decoderにはまず文字列生成開始を表す"_"をインプットにするので、"_"のtensorをバッチサイズ分作成
          start_char_batch = [[char2id["_"]] for _ in range(BATCH_NUM)]
          decoder_input_tensor = torch.tensor(start_char_batch, device=device)

          # 変数名変換
          decoder_hidden = encoder_state

          # バッチ毎の結果を結合するための入れ物を定義
          batch_tmp = torch.zeros(100,1, dtype=torch.long, device=device)
          # print(batch_tmp.size())
          # (100,1)

          for _ in range(2+2*dig):
            decoder_output, decoder_hidden = decoder(decoder_input_tensor, decoder_hidden)
            # 予測文字を取得しつつ、そのまま次のdecoderのインプットとなる
            decoder_input_tensor = get_max_index(decoder_output.squeeze())
            # バッチ毎の結果を予測順に結合
            batch_tmp = torch.cat([batch_tmp, decoder_input_tensor], dim=1)

          # 最初のbatch_tmpの0要素が先頭に残ってしまっているのでスライスして削除
          predicts.append(batch_tmp[:,1:])

      # バッチ毎の予測結果がまとまって格納されてます。
      #print(len(predicts))
      # 150
      #print(predicts[0].size())
      # (100, 5)

      import pandas as pd
      id2char = {str(i) : str(i) for i in range(10)}
      id2char.update({"10":"", "11":"-", "12":""})
      row = []
      for i in range(len(test_input_batch)):
        batch_input = test_input_batch[i]
        batch_output = test_output_batch[i]
        batch_predict = predicts[i]
        for inp, output, predict in zip(batch_input, batch_output, batch_predict):
          x = [id2char[str(idx)] for idx in inp]
          y = [id2char[str(idx)] for idx in output]
          p = [id2char[str(idx.item())] for idx in predict]

          x_str = "".join(x)
          y_str = "".join(y)
          p_str = "".join(p)

          judge = "O" if y_str == p_str else "X"
          row.append([x_str, y_str, p_str, judge])
          if (check_number(p_str)!=1):
            dig_bun += cal_variance(y_str, p_str)
          else:
            no_count += 1

      predict_df = pd.DataFrame(row, columns=["input", "answer", "predict", "judge"])
      if cal == 0:
        dig_dic0.append(cal_deviation(dig_bun, no_count))
        dig_col0.append(len(predict_df.query('judge == "O"')) / len(predict_df))
        dig_nc0.append(no_count)
      if cal == 1:
        dig_dic1.append(cal_deviation(dig_bun, no_count))
        dig_col1.append(len(predict_df.query('judge == "O"')) / len(predict_df))
        dig_nc1.append(no_count)
      if cal == 2:
        dig_dic2.append(cal_deviation(dig_bun, no_count))
        dig_col2.append(len(predict_df.query('judge == "O"')) / len(predict_df))
        dig_nc2.append(no_count)
      if cal == 3:
        dig_dic3.append(cal_deviation(dig_bun, no_count))
        dig_col3.append(len(predict_df.query('judge == "O"')) / len(predict_df))
        dig_nc3.append(no_count)

      dig_bun = 0
      no_count = 0

    

  
print("Done")
# training ...
# Epoch 1: 1889.10
# Epoch 2: 1395.36
# Epoch 3: 1194.29
# Epoch 4: 1049.05
# Epoch 5: 931.19
# Epoch 6: 822.30
# 〜略〜
# Epoch 96: 4.47
# Epoch 97: 126.06
# Epoch 98: 32.81
# Epoch 99: 12.69
# Epoch 100: 6.20
# Done

dig_col0 = np.array(dig_col0).reshape([dig, EPOCH_NUM])
dig_nc0 = np.array(dig_nc0).reshape([dig, EPOCH_NUM])
dig_dic0 = np.array(dig_dic0).reshape([dig, EPOCH_NUM])
dig_col1 = np.array(dig_col1).reshape([dig, EPOCH_NUM])
dig_nc1 = np.array(dig_nc1).reshape([dig, EPOCH_NUM])
dig_dic1 = np.array(dig_dic1).reshape([dig, EPOCH_NUM])
dig_col2 = np.array(dig_col2).reshape([dig, EPOCH_NUM])
dig_nc2 = np.array(dig_nc2).reshape([dig, EPOCH_NUM])
dig_dic2 = np.array(dig_dic2).reshape([dig, EPOCH_NUM])
dig_col3 = np.array(dig_col3).reshape([dig, EPOCH_NUM])
dig_nc3 = np.array(dig_nc3).reshape([dig, EPOCH_NUM])
dig_dic3 = np.array(dig_dic3).reshape([dig, EPOCH_NUM])





import matplotlib.pyplot as plt
# %matplotlib inline

fig = plt.figure()
dig_col02 = dig_col0[:,EPOCH_NUM-1]
ax = fig.add_subplot(111, xlabel='INPUT DIGIT', ylabel='accuracy rate', xticks = dig_bar)
plt.plot(dig_bar, dig_col02, marker = '.', color = 'red')

print("和　正解率")
print(dig_col02)

dig_col12 = dig_col1[:,EPOCH_NUM-1]
#ax = fig.add_subplot(111, title='COLLECT RATE' , xlabel='DIGIT', ylabel='COLLECT RATE')
plt.plot(dig_bar, dig_col12, marker = 'P', color = 'green')

print("差(正負)　正解率")
print(dig_col12)

dig_col22 = dig_col2[:,EPOCH_NUM-1]
#ax = fig.add_subplot(111, title='COLLECT RATE' , xlabel='DIGIT', ylabel='COLLECT RATE', ylim=(0, 1.0))
plt.plot(dig_bar, dig_col22, marker = '^', color = 'blue')

print("積　正解率")
print(dig_col22)

dig_col32 = dig_col3[:,EPOCH_NUM-1]
#ax = fig.add_subplot(111, title='COLLECT RATE' , xlabel='DIGIT', ylabel='COLLECT RATE', ylim=(0, 1.0))
plt.plot(dig_bar, dig_col32, marker = 'D', color = 'pink')

print("差(正のみ)　正解率")
print(dig_col32)

plt.show()

fig = plt.figure()
dig_dic02 = dig_dic0[:,EPOCH_NUM-1]
ax = fig.add_subplot(111, xlabel='INPUT DIGIT', ylabel='deviation', xticks = dig_bar)
plt.plot(dig_bar, dig_dic02, marker = '.', color = 'red')

print("和　偏差")
print(dig_dic02)

dig_dic12 = dig_dic1[:,EPOCH_NUM-1]
#ax = fig.add_subplot(111, title='DEVIATION' , xlabel='DIGIT', ylabel='DEVIATION')
plt.plot(dig_bar, dig_dic12, marker = 'P', color = 'green')

print("差(正負)　偏差")
print(dig_dic12)

dig_dic22 = dig_dic2[:,EPOCH_NUM-1]
#ax = fig.add_subplot(111, title='DEVIATION' , xlabel='DIGIT', ylabel='DEVIATION')
plt.plot(dig_bar, dig_dic22, marker = '^', color = 'blue')

print("積　偏差")
print(dig_dic22)


print("差(正のみ)　偏差")
print(dig_dic32)

plt.show()

fig = plt.figure()
dig_dic32 = dig_dic3[:,EPOCH_NUM-1]
ax = fig.add_subplot(111, title='PRODUCT' , xlabel='INPUT DIGIT', ylabel='deviation', xticks = dig_bar)
plt.plot(dig_bar, dig_dic32, marker = 'D', color = 'pink')
plt.show()

fig = plt.figure()
dig_nc02 = dig_nc0[:,EPOCH_NUM-1]
ax = fig.add_subplot(111, xlabel='INPUT DIGIT', ylabel='NOT NUMBER', xticks = dig_bar)
plt.plot(dig_bar, dig_nc02, marker = '.', color = 'red')

print("和　数外")
print(dig_nc02)

dig_nc12 = dig_nc1[:,EPOCH_NUM-1]
#ax = fig.add_subplot(111, title='NOT NUMBERE' , xlabel='INPUT DIGIT', ylabel='AMOUNT')
plt.plot(dig_bar, dig_nc12, marker = 'P', color = 'green')

print("差(正負)　数外")
print(dig_nc12)

dig_nc22 = dig_nc2[:,EPOCH_NUM-1]
#ax = fig.add_subplot(111, title='NOT NUMBER' , xlabel='INPUT DIGIT', ylabel='AMOUNT')
plt.plot(dig_bar, dig_nc22, marker = '^', color = 'blue')

print("積　数外")
print(dig_nc22)

dig_nc32 = dig_nc3[:,EPOCH_NUM-1]
#ax = fig.add_subplot(111, title='NOT NUMBER' , xlabel='INPUT DIGIT', ylabel='AMOUNT')
plt.plot(dig_bar, dig_nc22, marker = 'D', color = 'pink')

print("差(正のみ)　数外")
print(dig_nc32)

plt.show()

print("和　正解率")
print(dig_col0)
print("差(正負)　正解率")
print(dig_col1)
print("積　正解率")
print(dig_col2)
print("差(正のみ)　正解率")
print(dig_col3)
print("和　偏差")
print(dig_dic0)
print("差(正負)　偏差")
print(dig_dic1)
print("積　偏差")
print(dig_dic2)
print("差(正のみ)　偏差")
print(dig_dic3)
print("和　数外")
print(dig_nc0)
print("差(正負)　数外")
print(dig_nc1)
print("積　数外")
print(dig_nc2)
print("差(正のみ)　数外")
print(dig_nc3)
# 正解率を表示
#print(len(predict_df.query('judge == "O"')) / len(predict_df))
x = np.arange(1, EPOCH_NUM+1, 1)
y = np.array(dig_bar)

X, Y = np.meshgrid(x, y)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d', title = 'SUM', xlabel='EPOCK', ylabel='INPUT DIGIT', zlabel='accuracy rate', xticks = epock_bar, yticks = dig_bar, zticks = rate_bar)
ax.plot_wireframe(X, Y, dig_col0, color = 'red')
plt.show()

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d', title = 'DIFFENRENCE', xlabel='EPOCK', ylabel='INPUT DIGIT', zlabel='accuracy rate', xticks = epock_bar, yticks = dig_bar, zticks = rate_bar)
ax.plot_wireframe(X, Y, dig_col1, color = 'blue')
plt.show()

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d', title = 'PRODUCT', xlabel='EPOCK', ylabel='INPUT DIGIT', zlabel='accuracy rate', xticks = epock_bar, yticks = dig_bar, zticks = rate_bar)
ax.plot_wireframe(X, Y, dig_col2, color = 'green')
plt.show()

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d', title = 'DIFFERENCE(≧0)', xlabel='EPOCK', ylabel='INPUT DIGIT', zlabel='accuracy rate', xticks = epock_bar, yticks = dig_bar, zticks = rate_bar)
ax.plot_wireframe(X, Y, dig_col3, color = 'pink')
plt.show()




# 0.8492
# 間違えたデータを一部見てみる
#print(predict_df.query('judge == "X"').head(10))

print(random.randint(1, 3))

plt.plot(all_losses)
dig_losses=np.array(all_losses).reshape([dig, EPOCH_NUM])
x = np.arange(1, EPOCH_NUM+1, 1)
y = np.arange(1, dig+1, 1)
X, Y = np.meshgrid(x, y)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d', title='Seq2Seq' , xlabel='EPOCK', ylabel='DIGIT')
ax.plot_wireframe(X, Y, dig_losses)
plt.show()