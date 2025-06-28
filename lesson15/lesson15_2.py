import yfinance as yf
from datetime import datetime, timedelta
import os

def download_data():
    """
    每日下載指定股票的資料，並儲存為CSV檔。
    1. 股票代碼: 2330.TW, 2303.TW, 2454.TW, 2317.TW
    2. 檔案會儲存在 'data' 資料夾內。
    3. 檔案名稱格式為 '代碼_YYYY-MM-DD.csv' (例如: 2330_2023-10-27.csv)。
    4. 如果當日的檔案已存在，則不會重複下載。
    5. 每次成功下載新檔案後，會刪除該股票對應的舊日期檔案，確保只保留最新的一份。
    """
    # --- 函式主體開始，所有程式碼都進行了縮排 ---
    stock_ids = ["2330.TW", "2303.TW", "2454.TW", "2317.TW"]
    data_folder = "data"

    # 確保 data 資料夾存在
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    # yf.download 的 end 日期不包含在內，所以要用明天
    tomorrow_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")

    for stock_id in stock_ids:
        # 從 "2330.TW" 取出 "2330" 作為檔案名前綴
        base_stock_id = stock_id.split('.')[0]
        new_file_name = os.path.join(data_folder, f"{base_stock_id}_{today_str}.csv")

        # 檢查檔案是否已存在
        if not os.path.exists(new_file_name):
            print(f"正在下載 {stock_id} 日期為 {today_str} 的資料...")
            data = yf.download(stock_id, start=today_str, end=tomorrow_str)
            
            # 檢查是否有下載到資料 (例如假日或無交易日)
            if not data.empty:
                data.to_csv(new_file_name)
                print(f"成功下載並儲存檔案: {new_file_name}")

                # 刪除此股票的舊檔案
                for f in os.listdir(data_folder):
                    # 檢查檔名是否為同個股票、是csv檔、且不是今天的新檔案
                    if f.startswith(f"{base_stock_id}_") and f.endswith(".csv") and f != os.path.basename(new_file_name):
                        os.remove(os.path.join(data_folder, f))
                        print(f"已刪除舊檔案: {f}")
            else:
                print(f"找不到 {stock_id} 在 {today_str} 的資料，略過儲存。")
        else:
            print(f"檔案 {new_file_name} 已存在，略過下載。")

def main():
    # 呼叫函式，也需要縮排
    download_data()

# 這是 Python 程式的標準進入點
if __name__ == '__main__':
    # 呼叫 main 函式，也需要縮排
    main()
