import tushare as ts
import baostock as bs
import pandas as pd
import os
import sys
import numpy as np
import time
from tqdm import tqdm


"""
获取历史数据
"""
# token 获取
mytoken = 'b22a0b7894d2e6024cd9e1a655c4c17ef9a16011b6cea6bebd053783'
ts.set_token(mytoken)
ts.set_token(mytoken)

pro = ts.pro_api()

def getNormalDataForBaoStock(start_date,end_date):
    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    #### 获取沪深A股历史K线数据 ####
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    hs300_stocks = []
    rs = bs.query_hs300_stocks()

    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        hs300_stocks.append(rs.get_row_data())
    for stock_info in hs300_stocks:
        code=stock_info[1]
        rs = bs.query_history_k_data_plus(code,
                                          "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                          start_date=start_date, end_date=end_date,
                                          frequency="d", adjustflag="1")
        print('query_history_k_data_plus respond error_code:' + rs.error_code)
        print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

        #### 打印结果集 ####
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)

        #### 结果集输出到csv文件 ####
        file_directory=os.path.join(save_path,code)
        if not os.path.exists(file_directory):
            os.makedirs(file_directory)
        result.to_csv(os.path.join(save_path,code,"history_A_stock_k_data.csv"), index=False)
        print(result)

    #### 登出系统 ####
    bs.logout()





if __name__ == '__main__':
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # path in linux
    relative_path_in_linux = "../stock";
    # path in windows
    relative_path_in_windows = relative_path_in_linux.replace("/","\\");

    save_path = os.path.join(modpath, relative_path_in_linux)

    #设置起始日期
    startdate = '2012-01-01'
    enddate = '2020-11-11'
    getNormalDataForBaoStock(startdate,enddate)

    #主程序 1789
    #getNoramlData()
    # getIndexData()
    # getLimitData() # 暂时没用到，平时不用更新
    # getOtherData()
    # getMoneyData()
