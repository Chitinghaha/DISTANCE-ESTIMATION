import threading

## 一池子thread用法 --------------------------------------------------- #
# 子執行緒的工作函數
def job(name):
  print("HI " + name)

# 建立存放執行序的list(存放thread)
threads = []

# 放入執行序
t = threading.Thread(target=job, args=('Nash',)) #
threads.append(t) # 將程序放入threads

# 開始
for t in threads:
    t.start()

# 等待所有子執行緒結束
for t in threads:
    t.join()