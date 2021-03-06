import tushare as ts
import baostock as bs
import pandas as pd
import os
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
save_path = 'I:\workspace\python_space\stock_market\stock'
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


def getNoramlData():
    #获取基础信息数据，包括股票代码、名称、上市日期、退市日期等
    pool = pro.stock_basic(exchange='',
                           list_status='L',
                           adj='qfq',
                           fields='ts_code,symbol,name,area,industry,fullname,list_date, market,exchange,is_hs')
    #print(pool.head())

    # 因为穷没开通创业板和科创板权限，这里只考虑主板和中心板
    pool = pool[pool['market'].isin(['主板', '中小板'])].reset_index()
    pool.to_csv(os.path.join(save_path, 'company_info.csv'), index=False, encoding='utf-8')

    print('获得上市股票总数：', len(pool)-1)
    j = 0
    for i in pool.ts_code:
        j += 1
        # if j <=1789:
        #     continue
        print('正在获取第%d家，股票代码%s.' % (j, i))
        #接口限制访问200次/分钟，加一点微小的延时防止被ban
        path = os.path.join(save_path, 'OldData', i + '_NormalData.csv')    

        time.sleep(0.301)
        df = ts.pro_bar(ts_code=i, adj='qfq', start_date=startdate, end_date=enddate,
                        ma=[5, 10, 13, 21, 30, 60, 120], factors=['tor', 'vr'])
        try:
            df = df.sort_values('trade_date', ascending=True)
            df.to_csv(path, index=False)
        except:
            print(i)


# 暂时没用到这个数据
def getLimitData():
    #获取基础信息数据，包括股票代码、名称、上市日期、退市日期等
    pool = pro.stock_basic(exchange='',
                           list_status='L',
                           adj='qfq',
                           fields='ts_code,symbol,name,area,industry,fullname,list_date, market,exchange,is_hs')
    #print(pool.head())

    # 因为穷没开通创业板和科创板权限，这里只考虑主板和中心板
    pool = pool[pool['market'].isin(['主板', '中小板'])].reset_index()
    # pool.to_csv(os.path.join(save_path, 'company_info.csv'), index=False, encoding='ANSI')

    print('获得上市股票总数：', len(pool)-1)
    j = 1
    for i in pool.ts_code:
        print('正在获取第%d家，股票代码%s.' % (j, i))
        #接口限制访问200次/分钟，加一点微小的延时防止被ban
        path = os.path.join(save_path, 'LimitData', i + '.csv')
        j += 1
        # if j < 2000:
        #     continue
        # if os.path.exists(path):
        #     continue
        time.sleep(0.301)
        df = pro.stk_limit(ts_code=i,
                           adj='qfq',
                       start_date=startdate,
                       end_date=enddate)
        df = df.sort_values('trade_date', ascending=True)
        df.to_csv(path, index=False)

    # df = pro.limit_list(start_date=startdate, end_date=enddate)
    # path = os.path.join(save_path, 'LimitData', 'all.csv')
    # df.to_csv(path, index=False)

    # df = pro.limit_list(start_date=startdate, end_date=enddate)
    # path = os.path.join(save_path, 'LimitData', 'all.csv')
    # df.to_csv(path, index=False)


# 暂时没用到
# 获得个股资金流向（大单 小单 等）
def getMoneyData():
    pool = pro.stock_basic(exchange='',
                           list_status='L',
                           adj='qfq',
                           fields='ts_code,symbol,name,area,industry,fullname,list_date, market,exchange,is_hs')
    pool = pool[pool['market'].isin(['主板', '中小板'])].reset_index()
    print('获得上市股票总数：', len(pool)-1)
    j = 1
    for i in pool.ts_code:
        print('正在获取第%d家，股票代码%s.' % (j, i))
        path = os.path.join(save_path, 'MoneyData', i + '.csv')
        j += 1
        # if j < 1255:
        #     continue
        time.sleep(0.101)
        df = pro.moneyflow(ts_code=i, start_date=startdate, end_date=enddate)
        df.to_csv(path, index=False)


def getOtherData():
    index_df = pd.read_csv(os.path.join(save_path, 'OldData', '000001.SH' + '_NormalData.csv'))

    day = np.sort(list(index_df['trade_date']))

    #  统计涨跌停股票
    j = 0
    for tmp_day in tqdm(day):
        j = j + 1
        # if j < 1190:
        #     continue
        df = pro.limit_list(trade_date=str(tmp_day))
        path = os.path.join(save_path, 'OhterData', 'limit_list_' + str(tmp_day) + '.csv')
        time.sleep(0.601)
        if len(df) == 0:
            continue

        df.to_csv(path, index=False)

    # 获取沪深港通资金流向， 暂时没用到
    df_all = pd.DataFrame()
    skip = 200
    for i in range(0, len(day), skip):  # 每次最多返回300条
        sd = str(day[i])
        if i + skip-1 > len(day):
            ed = str(day[-1])
        else:
            ed = str(day[i+skip-1])
        df = pro.moneyflow_hsgt(start_date=sd, end_date=ed)
        time.sleep(0.5)
        df_all = pd.concat((df_all, df))
    path = os.path.join(save_path, 'OhterData', 'moneyflow_hsgt' + '.csv')
    df_all.to_csv(path, index=False)

    # 港股通每日成交， 暂时没用到
    df_all = pd.DataFrame()
    skip = 900
    for i in range(0, len(day), skip):  # 每次最多返回1000条
        sd = str(day[i])
        if i + skip-1 > len(day):
            ed = str(day[-1])
        else:
            ed = str(day[i+skip-1])
        df = pro.ggt_daily(start_date=sd, end_date=ed)
        time.sleep(60)
        df_all = pd.concat((df_all, df))
    path = os.path.join(save_path, 'OhterData', 'ggt_daily' + '.csv')
    df_all.to_csv(path, index=False)

    # 港股通每月成交
    # df_all = pd.DataFrame()
    # skip = 800
    # for i in range(0, len(day), skip):  # 每次最多返回300条
    #     sd = day[i]
    #     if i + skip-1 > len(day):
    #         ed = day[-1]
    #     else:
    #         ed = day[i+skip-1]
    #     df = pro.ggt_daily(start_date=sd, end_date=ed)
    #     df_all = pd.concat((df_all, df))
    # path = os.path.join(save_path, 'OhterData', 'ggt_monthly' + '.csv')
    # df_all.to_csv(path, index=False)

    # 沪深股通持股明细
    # 待定


def getIndexData():
    # 上交所指数信息
    df = pro.index_basic(market='SSE')
    df.to_csv(os.path.join(save_path, 'SSE.csv'), index=False, encoding='utf-8')

    # 深交所指数信息
    df = pro.index_basic(market='SZSE')
    df.to_csv(os.path.join(save_path, 'SZSE.csv'), index=False, encoding='utf-8')

    # 获取指数历史信息
    # 这里获取几个重要的指数 【上证综指，上证50，上证A指，深证成指，深证300，中小300，创业300，中小板综，创业板综】
    index = ['000001.SH', '000016.SH', '000002.SH', '399001.SZ', '399007.SZ', '399008.SZ', '399012.SZ', '399101.SZ',
             '399102.SZ']
    for i in index:
        path = os.path.join(save_path, 'OldData', i + '_NormalData.csv')
        df = pro.index_daily(ts_code=i,
                             start_date=startdate,
                             end_date=enddate,
                             fields='ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, '
                                    'vol, amount')
        df = df.sort_values('trade_date', ascending=True)
        df.to_csv(path, index=False)



if __name__ == '__main__':
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
