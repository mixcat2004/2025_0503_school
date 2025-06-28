import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import re
from pathlib import Path

# --- Part 1: Intelligent Data Downloading ---

def get_latest_local_date(data_folder: Path, stock_prefix: str) -> tuple[datetime.date | None, list[Path]]:
    """
    掃描資料夾，找到指定股票的最新本地CSV檔案日期，並返回該股票的所有檔案路徑。
    
    Args:
        data_folder: 資料夾的路徑物件。
        stock_prefix: 股票代碼前綴 (例如: '2330')。

    Returns:
        一個元組，包含：
        - 找到的最新日期 (如果沒有有效檔案則為 None)。
        - 該股票所有檔案的路徑列表。
    """
    date_pattern = re.compile(rf"^{stock_prefix}_(\d{{4}}-\d{{2}}-\d{{2}})\.csv$")
    all_files = list(data_folder.glob(f"{stock_prefix}_*.csv"))
    
    valid_dates = []
    for f in all_files:
        match = date_pattern.match(f.name)
        if match:
            try:
                valid_dates.append(datetime.strptime(match.group(1), "%Y-%m-%d").date())
            except ValueError:
                continue # 忽略格式錯誤的日期
    
    latest_date = max(valid_dates) if valid_dates else None
    return latest_date, all_files

def download_data():
    """
    智慧地為指定股票下載最新的可用交易資料。
    - 使用 yfinance history 檢查最新的實際交易日。
    - 將其與本地最新下載的檔案日期進行比較。
    - 僅在本地資料過時的情況下才進行下載。
    - 成功下載後，它會清理該股票的所有舊檔案，確保只保留最新的資料檔案。
    """
    stock_ids = ["2330.TW", "2303.TW", "2454.TW", "2317.TW"]
    data_folder = Path("data")
    data_folder.mkdir(exist_ok=True)

    for stock_id in stock_ids:
        print(f"\n--- 正在處理 {stock_id} ---")
        base_stock_id = stock_id.split('.')[0]

        # 1. 從 Yahoo Finance 找到最新的交易日
        try:
            ticker = yf.Ticker(stock_id)
            # 獲取最近7天的歷史記錄以安全地找到最後一個條目
            hist = ticker.history(period="7d")
            if hist.empty:
                print(f"警告：無法檢索 {stock_id} 的近期歷史記錄。跳過。")
                continue
            latest_trading_day = hist.index[-1].date()
        except Exception as e:
            print(f"獲取 {stock_id} 的歷史記錄時出錯：{e}。跳過。")
            continue

        # 2. 找到我們本地最新的檔案日期
        latest_local_date, old_files = get_latest_local_date(data_folder, base_stock_id)
        
        # 3. 決定是否需要下載
        if latest_local_date and latest_local_date >= latest_trading_day:
            print(f"{stock_id} 的資料已是最新 (日期: {latest_local_date})。無需下載。")
            continue

        print(f"{stock_id} 的本地資料已過期或不存在。")
        print(f"市場最新交易日: {latest_trading_day}, 本地最新檔案: {latest_local_date}")
        print(f"嘗試下載 {latest_trading_day} 的資料...")

        # 4. 為最新的交易日下載新資料
        start_date_str = latest_trading_day.strftime("%Y-%m-%d")
        # yf.download 的 'end' 參數是不包含的，所以我們需要下一天
        end_date_str = (latest_trading_day + timedelta(days=1)).strftime("%Y-%m-%d")
        
        data = yf.download(stock_id, start=start_date_str, end=end_date_str, progress=False)

        # 5. 儲存新檔案並清理舊檔案
        if not data.empty:
            new_file_path = data_folder / f"{base_stock_id}_{start_date_str}.csv"
            data.to_csv(new_file_path)
            print(f"成功儲存新資料至: {new_file_path.name}")

            # 清理此股票所有先前存在的檔案
            for old_file in old_files:
                old_file.unlink()
                print(f"已刪除舊檔案: {old_file.name}")
        else:
            print(f"在 {start_date_str} 下載 {stock_id} 時未返回資料。檔案未更改。")

# --- Part 2: Data Processing and Consolidation ---

def process_data():
    """
    讀取每支股票的最新CSV，提取'Close'價格，並將它們合併成一個單一的DataFrame，
    使用中文欄位名稱。
    """
    print("\n--- 正在處理和整合資料 ---")
    data_folder = Path("data")
    stock_map = {"2330": "台積電", "2303": "聯電", "2454": "聯發科", "2317": "鴻海"}
    
    all_closes = []
    for stock_prefix, name_chinese in stock_map.items():
        files = sorted(data_folder.glob(f"{stock_prefix}_*.csv"), reverse=True)
        if files:
            latest_file = files[0]
            print(f"正在讀取 {name_chinese} 的最新檔案: {latest_file.name}")
            df = pd.read_csv(latest_file, index_col='Date', parse_dates=True)
            all_closes.append(df['Close'].rename(name_chinese))
    
    if all_closes:
        final_df = pd.concat(all_closes, axis=1).sort_index()
        print("\n整合後的 DataFrame:")
        print(final_df)

def main():
    """主函式，執行下載和處理步驟。"""
    download_data()
    process_data()

if __name__ == '__main__':
    main()