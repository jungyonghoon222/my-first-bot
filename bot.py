import time
import ccxt
import schedule
import telebot

# ──────────────────────────────────────────────────────────────────────────────
# ① 내 텔레그램 설정
TG_TOKEN   = '7967466074:AAEcMa2HfVrSF2S7Aki-C1yjRGBbQUIYxHg'
TG_CHAT_ID = 7274365626
bot = telebot.TeleBot(TG_TOKEN)
# ──────────────────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────────────────────
# ② Bitget USDT 선물 거래소 객체 생성
exchange = ccxt.bitget({
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',  # USDT 선물 마켓으로 설정
    },
})
# ──────────────────────────────────────────────────────────────────────────────

def check_entry():
    # 1) 전체 티커 불러오기
    tickers = exchange.fetch_tickers()
    # 2) USDT 마켓만 필터링 (심볼에 '/USDT' 포함)
    usdt = {
        sym: info
        for sym, info in tickers.items()
        if '/USDT' in sym
    }
    # 3) quoteVolume 기준 상위 40개 추출
    top40 = sorted(
        usdt.keys(),
        key=lambda s: usdt[s].get('quoteVolume', 0),
        reverse=True
    )[:40]

    for sym in top40:
        try:
            # 4) 1분봉 21개 가져오기
            ohlcv  = exchange.fetch_ohlcv(sym, '1m', limit=21)
            closes = [candle[4] for candle in ohlcv]
            entry    = closes[-1]
            prev20_hi = max(closes[:-1])  # 직전 20개 고가 중 최고

            # 5) 진입 조건: Turtle20 고가 돌파
            if entry > prev20_hi:
                sl = entry * 0.99   # 예시 손절가: 진입가의 1% 아래
                tp = entry * 1.02   # 예시 목표가: 진입가의 2% 위
                msg = (
                    f"🔔 {sym} 롱 진입 신호 🔔\n"
                    f"Entry : {entry:.6f}\n"
                    f"SL    : {sl:.6f}\n"
                    f"TP    : {tp:.6f}\n"
                    f"이유   : Turtle20 1분봉 고가 돌파\n"
                )
                bot.send_message(TG_CHAT_ID, msg)
                time.sleep(0.5)  # 스팸 방지

        except Exception as e:
            print(f"[Error] {sym} → {e}")

# 1분마다 check_entry() 실행
schedule.every().minute.do(check_entry)

if __name__ == "__main__":
    bot.send_message(TG_CHAT_ID, "✅ 알림봇 가동 시작!")
    while True:
        schedule.run_pending()
        time.sleep(1)
