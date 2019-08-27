############################################################################
# Sample Algorithm

import pandas as pd
import pandas.tseries.offsets as offsets

def initialize(ctx):
    # 設定
    ctx.logger.debug("initialize() called")
    ctx.configure(
      target="jp.stock.daily",
      channels={          # 利用チャンネル
        "jp.stock": {
          "symbols": [
            "jp.stock.1420", #サンヨーホームズ
            "jp.stock.2931", #ユーグレナ
            "jp.stock.6134", #FUJI
            "jp.stock.4776", #サイボウズ
            "jp.stock.9613", #NTT Data 
            "jp.stock.3092", #ZOZO
            "jp.stock.7779", #サイバーダイン
            "jp.stock.4284", #ソルクシーズ
            "jp.stock.6460", #セガサミーホールディングス
            #"jp.stock.9434", #ソフトバンク
            "jp.stock.7867", #タカラトミー
            "jp.stock.4689"
          ],
          "columns": [
            "open_price_adj",    # 始値(株式分割調整後)
            #"high_price_adj",    # 高値(株式分割調整後)
            #"low_price_adj",     # 安値(株式分割調整後)
            #"volume_adj",         # 出来高
            #"txn_volume",         # 売買代金
            "close_price",        # 終値
            "close_price_adj",    # 終値(株式分割調整後) 
          ]
        }
      }
    )



    def _mavg_signal(data):
        open = data["close_price_adj"].fillna(method='ffill').rolling(window=1, center=False).mean()
        end = data["close_price_adj"].fillna(method='ffill').rolling(window=1, center=False).mean()
        m360 = data["close_price_adj"].fillna(method='ffill').rolling(window=1080, center=False).mean()
        m180 = data["close_price_adj"].fillna(method='ffill').rolling(window=180, center=False).mean()
        
        ratio = end / open
        ratio2 = m180/m360

        buy_sig = (ratio < 0.90) & (ratio2 > 1)
        
        return {
            "buy:sig": buy_sig,
        }

    # シグナル登録
    ctx.regist_signal("mavg_signal", _mavg_signal)


def handle_signals(ctx, date, current):
    '''
    current: pd.DataFrame
    '''
    
    #ctx.logger.debug ("today:")
    #ctx.logger.debug (date)
    #ctx.logger.debug ("yesterday:")
    #ctx.logger.debug (date + offsets.Day(-1))
    #ctx.logger.debug (date + datetime.timedelta(days = 1))
    
    #下記のポートフォリオはシグナルが呼ばれない限り呼び出されることはない
    
    ls = []
    for (key) in ctx.portfolio.positions.keys():
      ls.append(key)
    if len(ls)==0 :
      pass  
    else: 
      ctx.logger.debug (ls[0])

    #dict = ctx.portfolio.positions.keys()
    #items = list(ctx.portfolio.positions)
    #ctx.logger.debug (dict)
    #ctx.logger.debug (items)
    
    done_syms = set([])

    for (sym,val) in ctx.portfolio.positions.items(): #それぞれの証券コードごとに同じ操作を繰り返す意図。symは証券コードで、valはそれに緋づくすべてのアイテム
        returns = val["returns"]
        if returns < -0.03:
          sec = ctx.getSecurity(sym)
          sec.order(-val["amount"], comment="損切り(%f)" % returns)
          done_syms.add(sym)
        
        elif returns > 0.08:
          sec = ctx.getSecurity(sym)
          sec.order(-val["amount"], comment="利益確定売(%f)" % returns)
          done_syms.add(sym)


    buy = current["buy:sig"].dropna()
    for (sym,val) in buy.items():
        if sym in done_syms:
          continue
        sec = ctx.getSecurity(sym)
        sec.order(sec.unit() * 1, comment="SIGNAL BUY")
        #ctx.logger.debug("BUY: %s,  %f" % (sec.code(), val))
        pass
    
    '''  
    sell = current["sell:sig"].dropna()
    for (sym,val) in sell.items():
        if sym in done_syms:
          continue
        sec = ctx.getSecurity(sym)
        sec.order(sec.unit() * -1, comment="SIGNAL SELL")
        #ctx.logger.debug("SELL: %s,  %f" % (sec.code(), val))
        pass
    '''  
