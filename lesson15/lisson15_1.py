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

    stock_ids = ["2330.TW", "2303.TW", "2454.TW", "2317.TW"]
    data_folder = "data"

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    tomorrow_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")

    for stock_id in stock_ids:
        base_stock_id = stock_id.split('.')[0]
        new_file_name = os.path.join(data_folder, f"{base_stock_id}_{today_str}.csv")

        if not os.path.exists(new_file_name):
            print(f"Downloading {stock_id} for {today_str}...")
            data = yf.download(stock_id, start=today_str, end=tomorrow_str)
            if not data.empty:
                data.to_csv(new_file_name)
                print(f"Successfully downloaded and saved {new_file_name}")

                # Delete old files for this stock
                for f in os.listdir(data_folder):
                    if f.startswith(f"{base_stock_id}_") and f.endswith(".csv") and f != os.path.basename(new_file_name):
                        os.remove(os.path.join(data_folder, f))
                        print(f"Deleted old file: {f}")
            else:
                print(f"No data available for {stock_id} on {today_str}, skipping save.")
        else:
            print(f"{new_file_name} already exists, skipping download.")

def main():
    download_data()

if __name__ == '__main__':
    main()
    
