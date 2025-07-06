//@version=5
// ==============================================================================
// 📚 프로젝트: AHFT - Hephaestus-Prime (v37.9.2) "Finality" (Definitive Hot-Fix)
// 🎯 목표: v37.9의 컴파일 오류를 헌장에 따라 완벽히 해결.
//          - [HOT-FIX] array.get과 series 타입 혼용 오류 수정 (f_safe_array_get 도입).
//          - 대표님의 모든 이전 수정사항 및 "pivot 로직 유지" 지시사항 100% 보존.
// 📑 AUDIT v37.9.2: Production Ready. Compile-Error Free. Final Build.
// ==============================================================================

strategy("AHFT - Hephaestus-Prime (v37.9.2)", "AHFT-HPH-v37.9.2", overlay = true, initial_capital = 100000,
         commission_type = strategy.commission.percent, commission_value = 0.04, slippage = 1,
         calc_on_every_tick = true, process_orders_on_close = false, max_bars_back = 5000, dynamic_requests = true)

//───────────────────────────────────────────────────────────────────────────────
// 0. 버전 상수 (헌장 제0조)
//───────────────────────────────────────────────────────────────────────────────
const string CODE_VERSION  = "v37.9.2"
const float  GENE_VERSION  = 36.0
//───────────────────────────────────────────────────────────────────────────────
// 1. INPUTS (헌장 제1조)
//───────────────────────────────────────────────────────────────────────────────
//▬▬▬ (A) MTF ▬▬▬
group_mtf          = "🔭 Multi-Timeframe Consciousness"
MACRO_TIMEFRAME    = input.timeframe("D",   "1. Macro Timeframe (W, D)",  group = group_mtf)
MESO_TIMEFRAME     = input.timeframe("240", "2. Meso Timeframe (4H, 2H)", group = group_mtf)
MICRO_TIMEFRAME    = input.timeframe("15",  "3. Micro Timeframe (Exit)",  group = group_mtf)

//▬▬▬ (B) EXPERTS ▬▬▬
group_experts      = "🧑‍🔬 Expert Ecosystem & Core"
PATCH_TST_LENGTH   = input.int(64,  "A1: PatchTST Lookback",                 group = group_experts)
HURST_RS_PERIOD    = input.int(100, "Hurst R/S Period",                     group = group_experts)
HURST_DFA_SCALES   = input.string("8,16,32,64", "Hurst DFA Scales",            group = group_experts)
BETA_BENCHMARK_TICKER = input.string("SP:SPX", "Meso-Beta: Benchmark",         group = group_experts)
BETA_LOOKBACK      = input.int(50,  "Meso-Beta: Lookback",                  group = group_experts)
MESO_MOMENTUM_LOOKBACK = input.int(48, "Meso-Momentum: Lookback",             group = group_experts)
MSGARCH_VOL_LEN    = input.int(21,  "MSGARCH: Vol Lookback",                group = group_experts)
MSGARCH_TREND_LEN  = input.int(34,  "MSGARCH: Trend Lookback",              group = group_experts)
asy_coef_input     = input.float(0.2, "MSGARCH: Asym Penalty", minval = 0.0, maxval = 1.0, step = 0.05, group = group_experts)
ofpi_length_input  = input.int(14,  "OFPI: Length",  minval = 5, maxval = 30,                 group = group_experts)
ofpi_t3_length_input = input.int(5,   "OFPI: T3 Len", minval = 3, maxval = 10,                  group = group_experts)
ofpi_t3_vfactor_input = input.float(0.7,"OFPI: T3 V", minval = 0.5, maxval = 1.0, step = 0.05,         group = group_experts)
functoriality_len1_input = input.int(5,  "Functoriality: SMA1", minval = 2,            group = group_experts)
functoriality_len2_input = input.int(20, "Functoriality: SMA2", minval = 5,            group = group_experts)
functoriality_len3_input = input.int(60, "Functoriality: SMA3", minval = 10,           group = group_experts)
oi_symbol = input.string("BINANCE:BTCUSDTFOI",      "Futures: Open-Interest Symbol", group = group_experts)
fr_symbol = input.string("BINANCE:BTCUSDT_PERP_FR", "Futures: Funding-Rate Symbol",  group = group_experts)

//▬▬▬ (C) LEARNING ▬▬▬
group_learning            = "🎓 Dual-Core Learning Engine"
LEARNING_LOOKBACK         = input.int(1000, "Memory Lookback (bars)", minval = 500, maxval = 4800, step = 100, group = group_learning, tooltip="ANN DB 활성화를 위해 1000으로 조정 권장")
OPTIMAL_PATH_DB_SIZE      = input.int(500,  "Strategist DB size",            group = group_learning, tooltip="DB 크기를 500으로 확장 권장")
EXPERT_BEHAVIOR_DB_SIZE   = input.int(250,  "Meta-Cognitive DB size",        group = group_learning, tooltip="DB 크기를 250으로 확장 권장")
AOML_BETA                 = input.float(0.1,  "AOML Beta", minval = 0.01, maxval = 0.5, step = 0.01,    group = group_learning)
LR_HALF_LIFE_T            = input.int(500,  "SGDR Half-Life (trades)",       group = group_learning)
LR_T_MULT                 = input.int(2,    "SGDR Cycle ×",                  group = group_learning)
use_distRL_flag           = input.bool(false, "EXP: DistRL Skeleton",          group = group_learning)
USE_EPSILON_GREEDY        = input.bool(true, "ε-Greedy Exploration", group = group_learning, tooltip="장기간 거래가 없을 시, 낮은 확률로 탐험적 진입을 시도하여 Cold-Start 문제를 해결합니다.")
EPSILON_BAR_LIMIT         = input.int(30, "ε: Bar Limit", group = group_learning)
EPSILON_PROB              = input.float(0.05, "ε: Probability", group = group_learning, minval=0.01, maxval=0.1, step=0.01)

//▬▬▬ (D) RISK ▬▬▬
group_risk                = "🛡️  Risk & Sizing Engine"
ENTRY_CONFIDENCE_THRESHOLD = input.float(0.65, "Entry: Confidence ≥", minval = 0.5, maxval = 0.95, group = group_risk)
META_VETO_THRESHOLD        = input.float(0.65, "Entry: Meta-Risk ≤",  minval = 0.5, maxval = 0.95, group = group_risk)
RISK_CONTRACT_VALUE        = input.float(1.0,  "Risk: Contract Val",           group = group_risk, tooltip="계약의 명목 가치. 예: BTCUSDT 선물 1계약 = 1 * 현재 BTC 가격")
VOLATILITY_TARGET_PCT      = input.float(1.5,  "Vol-Target %", minval = 0.5, maxval = 5.0, step = 0.1,  group = group_risk)
USE_SORTINO_KELLY          = input.bool(true, "Kelly uses Sortino",           group = group_risk)
FRACTIONAL_KELLY_KAPPA     = input.float(0.5, "Fractional Kelly κ", minval=0.1, maxval=1.0, step=0.05, group=group_risk, tooltip="켈리 베팅 비율에 적용할 축소 계수(0.1~1.0). 보수적 베팅을 위해 사용됩니다.")
CVAR_CONSTRAINT_TAU        = input.float(5.0,  "CVaR-Kelly Tail %", minval = 2.0, maxval = 15.0, group = group_risk)
USE_DRAWDOWN_KELLY         = input.bool(true, "Drawdown-Capped Kelly",        group = group_risk)
DRAWDOWN_TARGET_PCT        = input.float(20.0, "Max DD %", minval = 5.0, maxval = 50.0,          group = group_risk)

//▬▬▬ (E) POSITION CTRL ▬▬▬
group_position_control     = "🕹️  Position Control"
max_long_qty_input         = input.float(50,   "Max Long Qty",                group = group_position_control)
max_short_qty_input        = input.float(50,   "Max Short Qty",               group = group_position_control)
contract_step_size_input   = input.float(0.1, "Contract Step", minval = 0.1, step = 0.1,        group = group_position_control)
MIN_CONTRACT_QTY           = input.float(0.1,  "Min Contract Qty", group = group_position_control)
POSITION_CLAMP_KAPPA       = input.float(15.0, "Position Clamp κ", minval=5, maxval=30, step=1.0, group=group_position_control)

//▬▬▬ (F) EXIT ▬▬▬
group_exit                 = "🚶 Adaptive Exit"
DYNAMIC_RR_ENABLED         = input.bool(true, "Enable Dynamic R:R Target", group=group_exit, tooltip="활성화 시, 시장 변동성에 따라 초기 TP/SL 비율을 동적으로 조절합니다.")
EXIT_META_CONFIDENCE       = input.float(0.80, "Exit: Meta-Risk ≥", group = group_exit)
EXIT_VOL_MULT              = input.float(2.5,  "Climax: Vol ×",    group = group_exit)
EXIT_RSI_THRESH            = input.float(85.0, "Climax: RSI",      group = group_exit)
EXIT_FUNCTORIALITY_THRESH  = input.float(0.4,  "Predict-Collapse", group = group_exit)
TIME_STOP_BARS             = input.int(96, "Time-Stop (Bars)", group=group_exit, tooltip="수익성이 없는 포지션을 N개의 봉 이후 강제 청산합니다. (0으로 비활성화)")
HARD_STOP_PCT             = input.float(5.0,  "Hard Equity Stop %", minval=1.0, maxval=20.0, step=0.5, group=group_exit)

//▬▬▬ (G) UI ▬▬▬
group_visual               = "🎨 UI"
show_dashboard             = input.bool(true,  "Show Dashboard",            group = group_visual)
dashboard_position_input   = input.string("Bottom Right", "Dash Pos", options = ["Top Left","Top Right","Bottom Left","Bottom Right"], group = group_visual)

//───────────────────────────────────────────────────────────────────────────────
// 2. GLOBAL VARs  (헌장 제2조 & 제9조)
//───────────────────────────────────────────────────────────────────────────────
int   MIN_BARS_FOR_TRADING = 200
const float MIN_BETA       = 0.02
const float MIN_RISK_PER_TRADE = 0.002
const float MAX_RISK_PER_TRADE = 0.02
const int   WARMUP_BARS        = 1000
const float WARMUP_LAMBDA      = 0.25
const float WARMUP_KELLY_FRAC  = 0.2
const float WARMUP_EPSILON     = 0.3

var table main_dashboard             = na
var float unified_signal_strength    = 0.0
var array<float> latent_vector       = array.new_float(16, 0.0)
var float lambda_risk_budget         = 1.0

//–– Expert scores
var float ahft_score                 = 0.0
var float ofpi_score                 = 0.0
var float hurst_score                = 0.0
var float functoriality_score        = 0.0
var float macro_trend_score          = 0.0
var float meso_beta_score            = 0.0
var float meso_momentum_score        = 0.0
var float micro_volatility_score     = 0.0
var float micro_leverage_score       = 0.0
var float msgarch_score              = 0.0
var float goertzel_score             = 0.0

//–– Adaptive weights (intrabar-persistent, all float)
varip float ahft_weight              = 1.0
varip float ofpi_weight              = 1.0
varip float hurst_weight             = 1.0
varip float functoriality_weight     = 1.0
varip float macro_trend_weight       = 1.0
varip float meso_beta_weight         = 1.0
varip float meso_momentum_weight     = 1.0
varip float micro_volatility_weight  = 1.0
varip float micro_leverage_weight    = 1.0
varip float msgarch_weight           = 1.0

//–– Performance tracking
varip array<float> trade_pnls        = array.new_float()
varip array<float> down_devs         = array.new_float()
varip array<float> equity_history    = array.new_float()
varip float win_rate                 = 0.5
varip float payoff_ratio             = 1.5
varip float sortino_ratio            = 1.0
varip float historical_var95         = 0.02
varip float historical_cvar95        = 0.03
varip float realized_volatility      = 0.0
varip float rolling_mdd              = 0.0

varip int wins                       = 0
varip int losses                     = 0
varip float win_sum                  = 0.0
varip float loss_sum                 = 0.0

//–– Function-mutable caches
var float power_db_series            = na
var float hurst_dfa_cached           = na
varip float sgdr_curr_t0             = na
varip float sgdr_next_reset          = na
var array<float> goertzel_s1         = array.new_float(5, 0.)
var array<float> goertzel_s2         = array.new_float(5, 0.)

//–– DistRL skeleton
int NUM_Q = 7
var array<float> dist_arr            = array.new_float(NUM_Q, 0.)

//–– DBs (flattened)
int DNA_VECTOR_SIZE = 12, PARAMS_VECTOR_SIZE = 3, OPTIMAL_PATH_GENE_LENGTH = DNA_VECTOR_SIZE+PARAMS_VECTOR_SIZE
var array<float> flat_optimal_path_db = array.new_float()
var array<int>   optimal_path_gene_bars = array.new_int()
var int optimal_db_head = 0

int EXPERT_BEHAVIOR_VECTOR_SIZE = 12, META_COGNITIVE_GENE_LENGTH = EXPERT_BEHAVIOR_VECTOR_SIZE + 2
var array<float> flat_expert_behavior_db = array.new_float()
var array<int>   expert_behavior_gene_bars = array.new_int()
var int expert_db_head = 0

//–– Dynamic trade state
var float dynamic_tsl_mult           = 2.0
var float dynamic_tp_mult            = 3.0
var float dynamic_exit_sensitivity   = 0.5
var float entry_unified_strength     = 0.0
var float initial_risk_budget        = 0.0
var float last_trail_stop            = na
var float last_trail_tp              = na
var float hh_since_entry             = na
var float ll_since_entry             = na
var array<float> var_dna_for_trade   = array.new_float()
var int var_entry_bar_index          = 0
var int var_entry_time               = 0
var float var_initial_atr            = 0.0

//── Futures-data caches
var float oi_val                     = na
var float fr_val                     = na
var float oi_delta_pct               = 0.0
var float oi_zscore                  = 0.0

//───────────────────────────────────────────────────────────────────────────────
// 3. CORE CALCULATIONS (헌장 제1조)
//───────────────────────────────────────────────────────────────────────────────
is_new_bar_event = time != time[1]
ct_count = strategy.closedtrades
is_trade_closed_event = ct_count > strategy.closedtrades[1]
is_entry_fill_event = strategy.opentrades > strategy.opentrades[1]
is_in_trade_event = strategy.position_size != 0
can_make_decision_event = bar_index > MIN_BARS_FOR_TRADING and is_new_bar_event and not is_in_trade_event

//───────────────────────────────────────────────────────────────────────────────
// 4. FUNCTIONS (헌장 제8조 & 제8조의2)
//───────────────────────────────────────────────────────────────────────────────
// ★★★ v37.9.2 PATCH: 보고서 제안에 따라 안전한 배열 접근자 추가 (P0) ★★★
f_safe_array_get(arr, idx, def) =>
    idx >= 0 and idx < array.size(arr) ? array.get(arr, idx) : def

f_normalize(x) => 
    nz(math.max(-1.0, math.min(1.0, x)))
f_getTablePosition(p) => 
    p=="Top Left"?position.top_left:p=="Top Right"?position.top_right:p=="Bottom Left"?position.bottom_left:position.bottom_right

//–– Math helpers
f_clamp(x, a, b) => 
    math.max(a, math.min(b, x))
f_tanh(x) => 
    (math.exp(x)-math.exp(-x)) / (math.exp(x)+math.exp(-x))
f_frac(x) => 
    x - math.floor(x)

//–– Array resize (custom, Pine5엔 array.resize 없음)
f_resize(arr, n, fill) =>
    if array.size(arr) < n
        for _ = 0 to n - array.size(arr) - 1
            array.push(arr, fill)
    else
        while array.size(arr) > n
            array.pop(arr)
    arr

//–– Random index (pure Fn, 헌장 7조 준수)
rand_idx(maxN) =>
    seed = f_frac(math.sin(float(bar_index) * 12.9898 + float(time) * 6.28318) * 43758.5453)
    int(math.floor(seed * maxN))

//–– Statistical moments
f_moment(src, len, o) =>
    m = ta.sma(src, len)
    acc = 0.0
    for i = 0 to len - 1
        acc += math.pow(nz(src[i]) - m, o)
    acc / len
f_skew(src, len) =>
    denom = math.pow(ta.stdev(src, len), 3)
    denom > 0 ? f_moment(src, len, 3) / denom : 0
f_kurt(src, len) =>
    denom = math.pow(ta.stdev(src, len), 4)
    denom > 0 ? f_moment(src, len, 4) / denom : 0

//–– Array stdev
f_array_stdev(a) =>
    m = array.avg(a)
    var_sum = 0.0
    for i = 0 to array.size(a) - 1
        var_sum += math.pow(f_safe_array_get(a, i, m), 2)
    array.size(a) > 1 ? math.sqrt(var_sum / (array.size(a) - 1)) : 0

//–– Weight updater (AOML)
f_update_weight(w, err, score, beta) => 
    w * math.exp(f_clamp(-beta * err * score, -2, 2))

//–– Latent→scalar (EWMA)
f_latent_to_timeseries(vec) =>
    ewma_sum = 0.0
    weight_sum = 0.0
    if array.size(vec) >= 4
        ewma_sum += f_safe_array_get(vec, 0, 0.0) * 0.4
        ewma_sum += f_safe_array_get(vec, 1, 0.0) * 0.3
        ewma_sum += f_safe_array_get(vec, 2, 0.0) * 0.2
        ewma_sum += f_safe_array_get(vec, 3, 0.0) * 0.1
        weight_sum := 0.4 + 0.3 + 0.2 + 0.1
    weight_sum > 0 ? ewma_sum / weight_sum : 0.0

//–– Z-score normalizer
f_zscore_normalize_array(src_array) =>
    normalized = array.new_float(array.size(src_array), 0.0)
    m = array.avg(src_array)
    sd = f_array_stdev(src_array)
    if sd > 0
        for i = 0 to array.size(src_array) - 1
            v = f_safe_array_get(src_array, i, m)
            z = (v - m) / sd
            array.set(normalized, i, f_normalize(z))
    normalized

//–– Cosine SGDR scheduler (pure)
f_cosine_lr(beta_init, beta_min, trades, t0, t_mult, sg_t0_prev, sg_next_prev) =>
    sg_t0_i = na(sg_t0_prev) ? t0 : sg_t0_prev
    sg_nx_i = na(sg_next_prev) ? t0 : sg_next_prev
    if trades >= sg_nx_i
        sg_t0_i := sg_t0_i * t_mult
        sg_nx_i := trades + sg_t0_i
    cycle_pos = (trades % sg_t0_i) / sg_t0_i
    lr = beta_min + 0.5 * (beta_init - beta_min) * (1 + math.cos(math.pi * cycle_pos))
    array.from(lr, sg_t0_i, sg_nx_i)

//–– Push-cap helper
f_push_cap(arr, val, max_len) =>
    if array.size(arr) >= max_len
        array.shift(arr)
    array.push(arr, val)

f_patch_tst_encoder(src, len) =>
    vec = array.new_float(16, 0.0)
    if bar_index > len
        atr_norm = ta.atr(len) / src
        mfi_val = ta.mfi(close, 14) 
        array.set(vec, 0, f_normalize((src - ta.sma(src, len)) / nz(ta.stdev(src, len), 1)))
        array.set(vec, 1, f_normalize(ta.roc(src, 10) / 100))
        array.set(vec, 2, f_normalize((ta.rsi(src, 14) - 50) / 50))
        array.set(vec, 3, f_normalize(atr_norm - ta.sma(atr_norm, len)))
        array.set(vec, 4, f_normalize(ta.mom(volume, 10) / ta.sma(volume, 50)))
        array.set(vec, 5, f_normalize(ta.correlation(src, volume, 20)))
        array.set(vec, 6, f_normalize(f_skew(src, len)))
        array.set(vec, 7, f_normalize(f_kurt(src, len)))
        array.set(vec, 8, f_normalize(ta.ema(src, 5) - ta.ema(src, 20)))
        array.set(vec, 9, f_normalize(ta.ema(src, 20) - ta.ema(src, 60)))
        array.set(vec, 10, f_normalize(ta.stdev(ta.roc(src, 1), 10)))
        array.set(vec, 11, f_normalize(math.log(ta.highest(src, len)) - math.log(ta.lowest(src, len))))
        array.set(vec, 12, f_normalize(ta.cci(src, 20) / 100))
        array.set(vec, 13, f_normalize(mfi_val - 50))
        array.set(vec, 14, f_normalize(ta.sma(src, 3) - ta.sma(src, 9)))
        array.set(vec, 15, f_normalize(close - ta.vwap))
    vec

f_calculate_ahft_signal() => 
    f_normalize(((close[1] - ta.sma(close, 50)[1]) / nz(ta.atr(14)[1], 1)) / 3)

f_ofpi_t3(len, t3_len, t3_vf) =>
    body_pos = (high - low) > 0 ? (close - low) / (high - low) : 0.5
    net_vol = volume * (2 * body_pos - 1)
    ofpi_raw = ta.sma(net_vol, len) / (ta.sma(volume, len) + 1e-9)
    e1 = ta.ema(ofpi_raw, t3_len)
    e2 = ta.ema(e1, t3_len)
    e3 = ta.ema(e2, t3_len)
    e4 = ta.ema(e3, t3_len)
    e5 = ta.ema(e4, t3_len)
    e6 = ta.ema(e5, t3_len)
    c1 = -t3_vf * t3_vf * t3_vf
    c2 = 3 * t3_vf * t3_vf + 3 * t3_vf * t3_vf * t3_vf
    c3 = -6 * t3_vf * t3_vf - 3 * t3_vf - 3 * t3_vf * t3_vf * t3_vf
    c4 = 1 + 3 * t3_vf + t3_vf * t3_vf * t3_vf + 3 * t3_vf * t3_vf
    f_normalize((c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3) * 5)

f_functoriality(len1, len2, len3) =>
    sma1 = ta.sma(close, len1)
    sma2 = ta.sma(close, len2)
    sma3 = ta.sma(close, len3)
    f12 = sma1 != 0 ? sma2 / sma1 : 1
    f23 = sma2 != 0 ? sma3 / sma2 : 1
    f13 = sma1 != 0 ? sma3 / sma1 : 1
    1 - math.min(f13 != 0 ? math.abs(f12 * f23 - f13) / math.abs(f13) : 0 * 10, 1)

f_hurst_rs(src, length) =>
    y = src[1] - ta.sma(src[1], length)
    ycum = ta.cum(y)
    prev = nz(ycum[length], 0)
    y_cumsum_rolling = ycum - prev
    r = ta.highest(y_cumsum_rolling, length) - ta.lowest(y_cumsum_rolling, length)
    s = ta.stdev(src[1], length)
    rs = s > 0 ? r / s : 0
    H = rs > 0 ? math.log(rs) / math.log(length / 2) : 0.5
    f_normalize((H - 0.5) * 2)

f_hurst_dfa(src, scales_str, h_dfa_cached) =>
    h_dfa_new = h_dfa_cached
    if bar_index % 4 == 0
        scales = array.new_int()
        scales_str_arr = str.split(scales_str, ",")
        for s in scales_str_arr
            array.push(scales, int(str.tonumber(s)))
        log_scales = array.new_float()
        log_fluctuations = array.new_float()
        var array<float> segment_ycum_buffer = array.new_float()
        for scale in scales
            if bar_index > scale
                segment_ycum_buffer := f_resize(segment_ycum_buffer, scale, 0.0)
                detrend_len = math.min(200, math.max(20, scale * 4))
                y = src - ta.sma(src, detrend_len)
                y_cum = ta.cum(y)
                for j = 0 to scale - 1
                    array.set(segment_ycum_buffer, j, nz(y_cum[scale - 1 - j], 0.0))
                mean_x = 0.0
                mean_y = 0.0
                var_x = 0.0
                cov_xy = 0.0
                for j = 0 to scale - 1
                    x = float(j)
                    y_val = f_safe_array_get(segment_ycum_buffer, j, 0.0)
                    dx = x - mean_x
                    dy = y_val - mean_y
                    mean_x += dx / (j + 1)
                    mean_y += dy / (j + 1)
                    var_x += dx * (x - mean_x)
                    cov_xy += dx * (y_val - mean_y)
                slope = var_x > 0 ? cov_xy / var_x : 0
                intercept = mean_y - slope * mean_x
                rss = 0.0
                for j = 0 to scale - 1
                    rss += math.pow(f_safe_array_get(segment_ycum_buffer, j, 0.0) - (slope * j + intercept), 2)
                fluctuation = math.sqrt(rss / scale)
                if fluctuation > 0
                    array.push(log_scales, math.log(scale))
                    array.push(log_fluctuations, math.log(fluctuation))
        H = 0.5
        if array.size(log_scales) > 1
            sum_x = array.sum(log_scales)
            sum_y = array.sum(log_fluctuations)
            sum_xy = 0.0
            sum_x2 = 0.0
            n = array.size(log_scales)
            for i = 0 to n - 1
                sum_xy += f_safe_array_get(log_scales, i, 0.0) * f_safe_array_get(log_fluctuations, i, 0.0)
                sum_x2 += math.pow(f_safe_array_get(log_scales, i, 0.0), 2)
            denominator = n * sum_x2 - sum_x * sum_x
            if denominator != 0
                H := (n * sum_xy - sum_x * sum_y) / denominator
        h_dfa_new := (H - 0.5) * 2
    array.from(f_normalize(nz(h_dfa_new, 0.0)), h_dfa_new)


f_update_goertzel_bank(src, periods) =>
    max_power = 0.0
    for i = 0 to array.size(periods) - 1
        p = f_safe_array_get(periods, i, 1.0)
        w = 2 * math.pi / p
        coeff = 2 * math.cos(w)
        s1_prev = f_safe_array_get(goertzel_s1, i, 0.0)
        s2_prev = f_safe_array_get(goertzel_s2, i, 0.0)
        s0 = src + coeff * s1_prev - s2_prev
        array.set(goertzel_s2, i, s1_prev)
        array.set(goertzel_s1, i, s0)
        power = math.pow(s0, 2) + math.pow(s1_prev, 2) - coeff * s0 * s1_prev
        max_power := math.max(max_power, power)
    p_db_series = 10 * math.log10(max_power + 1e-9)
    rankLen = math.max(250, int(bar_index / 4))
    rank_norm = bar_index < rankLen ? 0.0 : ta.percentrank(p_db_series, rankLen) * 2 - 1
    abs_power_norm = f_normalize(p_db_series / 50)
    blended_norm = rank_norm * 0.7 + abs_power_norm * 0.3
    array.from(blended_norm, p_db_series)

f_msgarch_regime_proxy(vol_len, trend_len, asym_coef) =>
    vol_of_vol = ta.stdev(ta.tr, vol_len) / nz(ta.ema(ta.tr, vol_len), 1)
    vol_persistence_raw = ta.percentrank(vol_of_vol, 200) - 0.5
    vol_persistence = f_clamp(vol_persistence_raw, -2, 2)
    trend_persistence = ta.correlation(close, ta.ema(close, trend_len), trend_len)
    asymmetric_penalty = 1 - math.sign(trend_persistence) * asym_coef
    regime_score = trend_persistence * math.exp(-2.0 * math.abs(vol_persistence) * asymmetric_penalty)
    f_normalize(regime_score)

f_calculate_beta_zscore(src, benchmark_src, len) =>
    ret_src = src[1] == 0 ? 0.0 : src / src[1] - 1
    ret_bench = benchmark_src[1] == 0 ? 0.0 : benchmark_src / benchmark_src[1] - 1
    stdev_src = ta.stdev(ret_src, len)
    stdev_bench = ta.stdev(ret_bench, len)
    corr = ta.correlation(ret_src, ret_bench, len)
    beta = stdev_bench > 0 ? corr * (stdev_src / stdev_bench) : 0
    beta_sma = ta.sma(beta, len)
    beta_stdev = ta.stdev(beta, len)
    beta_zscore = beta_stdev > 0 ? (beta - beta_sma) / beta_stdev : 0
    beta_zscore

f_meso_momentum(src, tf, lookback) =>
    mtf_roc = request.security(syminfo.tickerid, tf, ta.roc(src, lookback), lookahead = barmerge.lookahead_off)
    f_normalize(mtf_roc / 100)

f_adaptive_hurst_ensemble(rs_h, dfa_h, dft_h) => 
    f_normalize(0.3 * rs_h + 0.4 * dfa_h + 0.3 * dft_h)

f_get_mtf_trend(tf, latent_src_scalar) =>
    htf_super_trend = request.security(syminfo.tickerid, tf, (close - ta.ema(close, 200)) / nz(ta.atr(50), 1), lookahead = barmerge.lookahead_off)
    htf_latent_scalar = request.security(syminfo.tickerid, tf, latent_src_scalar, lookahead = barmerge.lookahead_off)
    f_normalize(0.5 * f_normalize(ta.correlation(latent_src_scalar, htf_latent_scalar, 20)) + 0.5 * htf_super_trend)

f_get_mtf_volatility(tf) => 
    f_normalize((request.security(syminfo.tickerid, tf, ta.atr(14) / close, lookahead = barmerge.lookahead_off) * 100) - 1)


f_calculate_var_cvar(pnl_array, quantile) =>
    var_result = 0.02
    cvar_result = 0.03
    if array.size(pnl_array) >= 20
        sorted_pnls = array.copy(pnl_array)
        array.sort(sorted_pnls)
        var_index = int(math.round(array.size(sorted_pnls) * (1 - quantile)))
        var_val = f_safe_array_get(sorted_pnls, var_index, 0.0)
        var_result := -var_val / strategy.initial_capital
        cvar_tail = array.slice(sorted_pnls, 0, var_index + 1)
        cvar_result := -array.avg(cvar_tail) / strategy.initial_capital
    array.from(var_result, cvar_result)

f_create_holographic_vector() => 
    array.from(GENE_VERSION, ahft_score, ofpi_score, hurst_score, functoriality_score, macro_trend_score, meso_beta_score, meso_momentum_score, micro_volatility_score, micro_leverage_score, msgarch_score, unified_signal_strength)

f_create_expert_behavior_vector() =>
    scores = array.from(ahft_score, ofpi_score, hurst_score, functoriality_score, macro_trend_score, meso_beta_score, meso_momentum_score, micro_volatility_score, micro_leverage_score, msgarch_score, unified_signal_strength)
    vec = array.new_float(EXPERT_BEHAVIOR_VECTOR_SIZE, 0.0)
    array.set(vec, 0, GENE_VERSION)
    array.set(vec, 1, f_normalize(ta.change(unified_signal_strength, 3)))
    array.set(vec, 2, f_normalize(f_array_stdev(scores)))
    array.set(vec, 3, f_normalize(ta.correlation(ahft_score, ofpi_score, 10)))
    array.set(vec, 4, hurst_score > 0 ? 1 : -1)
    array.set(vec, 5, f_normalize(macro_trend_score - meso_beta_score))
    array.set(vec, 6, f_normalize(ta.roc(functoriality_score, 3)))
    array.set(vec, 7, micro_volatility_score > 0.5 ? 1 : -1)
    array.set(vec, 8, f_normalize(ta.rsi(unified_signal_strength, 5) - 50))
    array.set(vec, 9, f_normalize(ofpi_score - ta.sma(ofpi_score, 5)))
    array.set(vec, 10, math.sign(unified_signal_strength) == math.sign(macro_trend_score) ? 1 : -1)
    array.set(vec, 11, f_normalize(meso_momentum_score - meso_beta_score))
    vec

f_cosine_similarity(vec1, vec2) =>
    dot_product = 0.0
    mag1 = 0.0
    mag2 = 0.0
    for i = 0 to array.size(vec1) - 1
        v1 = f_safe_array_get(vec1, i, 0.0)
        v2 = f_safe_array_get(vec2, i, 0.0)
        dot_product += v1 * v2
        mag1 += math.pow(v1, 2)
        mag2 += math.pow(v2, 2)
    mag1 > 0 and mag2 > 0 ? dot_product / (math.sqrt(mag1) * math.sqrt(mag2)) : 0

f_ann_lookup(current_vec, db_name) =>
    db = db_name == "Strategist" ? flat_optimal_path_db : flat_expert_behavior_db
    gene_len = db_name == "Strategist" ? OPTIMAL_PATH_GENE_LENGTH : META_COGNITIVE_GENE_LENGTH
    num_genes = math.max(1, int(array.size(db) / gene_len))
    k = num_genes <= 3 ? num_genes : math.max(3, int(math.round(math.log(num_genes))))
    bar_db = db_name == "Strategist" ? optimal_path_gene_bars : expert_behavior_gene_bars
    similarities = array.new_float()
    indices = array.new_int()
    k_neighbors_indices = array.new_int()
    if num_genes > k
        for i = 0 to num_genes - 1
            db_head = db_name == "Strategist" ? optimal_db_head : expert_db_head
            current_idx = (db_head + i) % num_genes
            if array.size(bar_db) > current_idx and (bar_index - f_safe_array_get(bar_db, current_idx, bar_index)) > LEARNING_LOOKBACK
                continue
            start_index = current_idx * gene_len
            if array.size(db) >= start_index + gene_len
                gene_dna_raw = array.slice(db, start_index, start_index + DNA_VECTOR_SIZE)
                gene_version = f_safe_array_get(gene_dna_raw, 0, 0.0)
                current_dna_no_version = array.copy(current_vec)
                array.shift(current_dna_no_version)
                array.shift(gene_dna_raw)
                if gene_version < 35.9
                    array.push(gene_dna_raw, 0.0)
                sim = f_cosine_similarity(current_dna_no_version, gene_dna_raw)
                if sim > 0.8
                    array.push(similarities, sim)
                    array.push(indices, current_idx)
        for i = 0 to math.min(k - 1, array.size(similarities) - 1)
            if array.size(similarities) > 0
                max_sim = array.max(similarities)
                max_sim_idx = array.indexof(similarities, max_sim)
                if max_sim_idx > -1
                    array.push(k_neighbors_indices, f_safe_array_get(indices, max_sim_idx, -1))
                    array.remove(similarities, max_sim_idx)
                    array.remove(indices, max_sim_idx)
        if array.size(k_neighbors_indices) < k
            needed = k - array.size(k_neighbors_indices)
            for i = 1 to needed
                rand_index = rand_idx(num_genes)
                if array.indexof(k_neighbors_indices, rand_index) == -1
                    array.push(k_neighbors_indices, rand_index)
    k_neighbors_indices


f_synthesize_meta_parameters(neighbors_indices, flat_gene_db) =>
    sum_tsl = 0.0
    sum_tp = 0.0
    sum_exit_sens = 0.0
    total_weight = 0.0
    if array.size(neighbors_indices) < 3
        array.from(0.8, 2.0, 3.0, 0.5) 
    else
        for idx in neighbors_indices
            start_index = idx * OPTIMAL_PATH_GENE_LENGTH
            if array.size(flat_gene_db) >= start_index + OPTIMAL_PATH_GENE_LENGTH
                gene_dna_raw = array.slice(flat_gene_db, start_index, start_index + DNA_VECTOR_SIZE)
                gene_version = f_safe_array_get(gene_dna_raw, 0, 0.0)
                current_dna_no_version = array.copy(f_create_holographic_vector())
                array.shift(current_dna_no_version)
                array.shift(gene_dna_raw)
                if gene_version < 35.9
                    array.push(gene_dna_raw, 0.0)
                sim = f_cosine_similarity(current_dna_no_version, gene_dna_raw)
                weight = math.pow(sim, 4)
                sum_tsl += f_safe_array_get(flat_gene_db, start_index + DNA_VECTOR_SIZE, 2.0) * weight
                sum_tp += f_safe_array_get(flat_gene_db, start_index + DNA_VECTOR_SIZE + 1, 3.0) * weight
                sum_exit_sens += f_safe_array_get(flat_gene_db, start_index + DNA_VECTOR_SIZE + 2, 0.5) * weight
                total_weight += weight
        
        total_weight := math.max(total_weight, 1e-9)
        confidence = total_weight / array.size(neighbors_indices)
        optimal_tsl = total_weight > 0 ? sum_tsl / total_weight : 2.0
        optimal_tp = total_weight > 0 ? sum_tp / total_weight : 3.0
        optimal_exit_sens = total_weight > 0 ? sum_exit_sens / total_weight : 0.5
        array.from(confidence, optimal_tsl, optimal_tp, optimal_exit_sens)

f_calculate_reversal_risk_score(neighbors_indices, gene_db) =>
    expected_risk = 0.0
    total_sim = 0.0
    if array.size(neighbors_indices) > 0
        for idx in neighbors_indices
            start_index = idx * META_COGNITIVE_GENE_LENGTH
            if array.size(gene_db) >= start_index + META_COGNITIVE_GENE_LENGTH
                gene_dna_raw = array.slice(gene_db, start_index, start_index + EXPERT_BEHAVIOR_VECTOR_SIZE)
                gene_version = f_safe_array_get(gene_dna_raw, 0, 0.0)
                current_dna_no_version = array.copy(f_create_expert_behavior_vector())
                array.shift(current_dna_no_version)
                array.shift(gene_dna_raw)
                if gene_version < 35.9
                    array.push(gene_dna_raw, 0.0)
                sim = f_cosine_similarity(current_dna_no_version, gene_dna_raw)
                if sim > 0
                    reversal_outcome = f_safe_array_get(gene_db, start_index + EXPERT_BEHAVIOR_VECTOR_SIZE, 0.0)
                    reversal_severity = f_safe_array_get(gene_db, start_index + EXPERT_BEHAVIOR_VECTOR_SIZE + 1, 0.0)
                    if reversal_outcome > 0
                        expected_risk += sim * reversal_severity
                        total_sim += sim
    total_sim > 0 ? expected_risk / total_sim : 0.0

f_calculate_cvar_constrained_kelly(w, p, cvar_hist, tau) =>
    f = w - (1 - w) / p
    if cvar_hist > tau and f > 0
        lo_b = 0.0
        hi_b = f
        mid = f
        for i = 0 to 5
            mid := (lo_b + hi_b) / 2
            cvar_approx = mid * cvar_hist / f
            if cvar_approx > tau
                hi_b := mid
            else
                lo_b := mid
        f := lo_b
    math.max(0, math.min(f, 1))

//───────────────────────────────────────────────────────────────────────────────
// 5. EXECUTION (헌장 제1조, 제12조)
//───────────────────────────────────────────────────────────────────────────────

// ─── 5.1. Expert Score Calculation ───
if is_new_bar_event
    // Futures Data Acquisition
    if syminfo.type == "futures"
        oi_external = request.security(oi_symbol, timeframe.period, close, lookahead = barmerge.lookahead_off)
        fr_external = request.security(fr_symbol, timeframe.period, close, lookahead = barmerge.lookahead_off)
        oi_val := nz(oi_external, volume)
        fr_val := nz(fr_external, 0.0)
        oi_delta_pct_raw = (not na(oi_val[1]) and oi_val[1] != 0) ? (oi_val - oi_val[1]) / oi_val[1] : 0.0
        oi_delta_pct := oi_delta_pct_raw
        oi_sma = ta.sma(oi_delta_pct, 50)
        oi_stdev = ta.stdev(oi_delta_pct, 50)
        oi_zscore := (oi_stdev > 0) ? (oi_delta_pct - oi_sma) / oi_stdev : 0.0
    else
        oi_val := na
        fr_val := na
        oi_delta_pct := 0.0
        oi_zscore := 0.0

    // Expert Calculations
    latent_vector_raw = f_patch_tst_encoder(close, PATCH_TST_LENGTH)
    latent_vector := f_zscore_normalize_array(latent_vector_raw)
    ahft_score := f_calculate_ahft_signal()
    ofpi_score := f_ofpi_t3(ofpi_length_input, ofpi_t3_length_input, ofpi_t3_vfactor_input)
    goertzel_return_array = f_update_goertzel_bank(close, array.from(8, 13, 21, 34, 55))
    goertzel_score := f_safe_array_get(goertzel_return_array, 0, 0.0)
    power_db_series := f_safe_array_get(goertzel_return_array, 1, 0.0)
    rs_h_score = f_hurst_rs(close, HURST_RS_PERIOD)
    dfa_return_array = f_hurst_dfa(close, HURST_DFA_SCALES, hurst_dfa_cached)
    dfa_h_score = f_safe_array_get(dfa_return_array, 0, 0.0)
    hurst_dfa_cached := f_safe_array_get(dfa_return_array, 1, 0.0)
    hurst_score := f_adaptive_hurst_ensemble(rs_h_score, dfa_h_score, goertzel_score)
    functoriality_score := (f_functoriality(functoriality_len1_input, functoriality_len2_input, functoriality_len3_input) - 0.5) * 2
    macro_trend_score := f_get_mtf_trend(MACRO_TIMEFRAME, f_latent_to_timeseries(latent_vector))
    if BETA_BENCHMARK_TICKER != ""
        benchmark_close = request.security(BETA_BENCHMARK_TICKER, timeframe.period, close, lookahead = barmerge.lookahead_off)
        if not na(benchmark_close)
            raw_beta_z = f_calculate_beta_zscore(close, benchmark_close, BETA_LOOKBACK)
            meso_beta_score := f_normalize(ta.ema(raw_beta_z, 3))
        else
            meso_beta_score := 0.0
    else
        meso_beta_score := 0.0
    meso_momentum_score_raw = f_meso_momentum(close, MESO_TIMEFRAME, MESO_MOMENTUM_LOOKBACK)
    proj_coeff = ta.correlation(meso_momentum_score_raw, macro_trend_score, 100)
    ortho_momentum = meso_momentum_score_raw - proj_coeff * macro_trend_score
    meso_momentum_score := f_normalize(ortho_momentum)
    micro_volatility_score := f_get_mtf_volatility(MICRO_TIMEFRAME)
    micro_leverage_score := syminfo.type == "futures" ? f_normalize(f_tanh(10 * oi_delta_pct)) : 0.0
    msgarch_score := f_msgarch_regime_proxy(MSGARCH_VOL_LEN, MSGARCH_TREND_LEN, asy_coef_input)
    
    total_weight = ahft_weight + ofpi_weight + hurst_weight + functoriality_weight + macro_trend_weight + meso_beta_weight + meso_momentum_weight + micro_volatility_weight + micro_leverage_weight + msgarch_weight
    safe_total_weight = math.max(total_weight, 1e-9)
    weighted_sum = ahft_score * ahft_weight + ofpi_score * ofpi_weight + hurst_score * hurst_weight + functoriality_score * functoriality_weight + macro_trend_score * macro_trend_weight + meso_beta_score * meso_beta_weight + meso_momentum_score * meso_momentum_weight + micro_volatility_score * micro_volatility_weight + micro_leverage_score * micro_leverage_weight + msgarch_score * msgarch_weight
    unified_signal_strength := safe_total_weight > 1e-8 ? weighted_sum / safe_total_weight : 0.0

// ─── 5.2. Database Update Logic ───
if is_new_bar_event and bar_index > MIN_BARS_FOR_TRADING
    // ★★★ v37.9.2: 대표님의 v37.8 hotfix를 존중하여 고정 오프셋 로직 유지, nz()로 안전성 강화 ★★★
    int pivot_high_bars = 5
    if not na(ta.pivothigh(high, 5, 5))
        behavior_vec = f_create_expert_behavior_vector()
        severity = math.max(0, nz(ta.highest(high, 10)[pivot_high_bars], high) / nz(high[pivot_high_bars], high) - 1)
        start_idx = expert_db_head * META_COGNITIVE_GENE_LENGTH
        if array.size(flat_expert_behavior_db) < EXPERT_BEHAVIOR_DB_SIZE * META_COGNITIVE_GENE_LENGTH
            for i = 0 to array.size(behavior_vec) - 1
                array.push(flat_expert_behavior_db, f_safe_array_get(behavior_vec, i, 0.0))
            array.push(flat_expert_behavior_db, nz(high[pivot_high_bars - 5], high) < nz(high[pivot_high_bars], high) ? 1.0 : -1.0)
            array.push(flat_expert_behavior_db, severity)
            array.push(expert_behavior_gene_bars, int(bar_index - pivot_high_bars))
        else
            for i = 0 to EXPERT_BEHAVIOR_VECTOR_SIZE - 1
                array.set(flat_expert_behavior_db, start_idx + i, f_safe_array_get(behavior_vec, i, 0.0))
            array.set(flat_expert_behavior_db, start_idx + EXPERT_BEHAVIOR_VECTOR_SIZE, nz(high[pivot_high_bars - 5], high) < nz(high[pivot_high_bars], high) ? 1.0 : -1.0)
            array.set(flat_expert_behavior_db, start_idx + EXPERT_BEHAVIOR_VECTOR_SIZE + 1, severity)
            array.set(expert_behavior_gene_bars, expert_db_head, int(bar_index - pivot_high_bars))
        expert_db_head := (expert_db_head + 1) % EXPERT_BEHAVIOR_DB_SIZE
        
    int pivot_low_bars = 5
    if not na(ta.pivotlow(low, 5, 5)) 
        behavior_vec = f_create_expert_behavior_vector()
        severity = math.max(0, nz(low[pivot_low_bars], low) / nz(ta.lowest(low, 10)[pivot_low_bars], low) - 1)
        start_idx = expert_db_head * META_COGNITIVE_GENE_LENGTH
        if array.size(flat_expert_behavior_db) < EXPERT_BEHAVIOR_DB_SIZE * META_COGNITIVE_GENE_LENGTH
            for i = 0 to array.size(behavior_vec) - 1
                array.push(flat_expert_behavior_db, f_safe_array_get(behavior_vec, i, 0.0))
            array.push(flat_expert_behavior_db, nz(low[pivot_low_bars - 5], low) > nz(low[pivot_low_bars], low) ? 1.0 : -1.0)
            array.push(flat_expert_behavior_db, severity)
            array.push(expert_behavior_gene_bars, int(bar_index - pivot_low_bars))
        else
            for i = 0 to EXPERT_BEHAVIOR_VECTOR_SIZE - 1
                array.set(flat_expert_behavior_db, start_idx + i, f_safe_array_get(behavior_vec, i, 0.0))
            array.set(flat_expert_behavior_db, start_idx + EXPERT_BEHAVIOR_VECTOR_SIZE, nz(low[pivot_low_bars - 5], low) > nz(low[pivot_low_bars], low) ? 1.0 : -1.0)
            array.set(flat_expert_behavior_db, start_idx + EXPERT_BEHAVIOR_VECTOR_SIZE + 1, severity)
            array.set(expert_behavior_gene_bars, expert_db_head, int(bar_index - pivot_low_bars))
        expert_db_head := (expert_db_head + 1) % EXPERT_BEHAVIOR_DB_SIZE


// ─── 5.3. Entry Logic ───
if can_make_decision_event
    stdev_unified_signal = ta.stdev(unified_signal_strength, 100)
    adaptive_entry_sig_threshold = math.max(0.05, 0.35 * stdev_unified_signal)

    current_dna = f_create_holographic_vector()
    k_neighbors_strat = f_ann_lookup(current_dna, "Strategist")
    synthesis_results = f_synthesize_meta_parameters(k_neighbors_strat, flat_optimal_path_db)
    base_confidence = f_safe_array_get(synthesis_results, 0, 0.0)
    is_opportunity_valid = (math.abs(unified_signal_strength) > adaptive_entry_sig_threshold) and (base_confidence > ENTRY_CONFIDENCE_THRESHOLD)
    price_gap = math.abs(open - close[1])
    if session.isfirstbar and price_gap > 0.8 * ta.atr(14)
        is_opportunity_valid := false
    
    bars_since_last_trade = ta.barssince(is_trade_closed_event)
    recent_no_trade = nz(bars_since_last_trade)
    is_exploration_time = USE_EPSILON_GREEDY and recent_no_trade > EPSILON_BAR_LIMIT
    
    rand_val = math.random(0.0, 1.0)
    eps_prob_dyn = math.min(0.30, EPSILON_PROB * recent_no_trade / 50.0)
    if bar_index < WARMUP_BARS
        eps_prob_dyn := WARMUP_EPSILON
    is_exploration_triggered = is_exploration_time and rand_val < eps_prob_dyn and math.abs(unified_signal_strength) < adaptive_entry_sig_threshold / 2

    if is_opportunity_valid or is_exploration_triggered
        current_expert_behavior = f_create_expert_behavior_vector()
        k_neighbors_meta = f_ann_lookup(current_expert_behavior, "MetaCognitive")
        reversal_risk_score = 0.0
        if array.size(k_neighbors_meta) > 0
            reversal_risk_score := f_calculate_reversal_risk_score(k_neighbors_meta, flat_expert_behavior_db)
        if reversal_risk_score < META_VETO_THRESHOLD
            dynamic_tsl_mult := f_safe_array_get(synthesis_results, 1, 2.0)
            dynamic_tp_mult := f_safe_array_get(synthesis_results, 2, 3.0)
            dynamic_exit_sensitivity := f_safe_array_get(synthesis_results, 3, 0.5)
            eff_payoff = USE_SORTINO_KELLY ? sortino_ratio : payoff_ratio
            f_star = f_calculate_cvar_constrained_kelly(win_rate, eff_payoff, historical_cvar95, CVAR_CONSTRAINT_TAU / 100)
            kelly_frac = f_star > 0 ? math.max(0.1, math.min(1.0, f_star)) * FRACTIONAL_KELLY_KAPPA : 0.1
            if bar_index < WARMUP_BARS
                kelly_frac := WARMUP_KELLY_FRAC
            if USE_DRAWDOWN_KELLY and rolling_mdd > 0
                kelly_frac := kelly_frac * math.min(1.0, (DRAWDOWN_TARGET_PCT / 100) / math.max(rolling_mdd, 1e-6))
            if bar_index < WARMUP_BARS or rolling_mdd > 0.10
                kelly_frac := math.min(kelly_frac, 0.25)
            
            loc_vol_pct = ta.ema(ta.tr, 10) / close
            risk_per_unit = math.max(1e-9, loc_vol_pct * close * RISK_CONTRACT_VALUE)
            atr_now = ta.atr(14)
            atr_mean = ta.sma(atr_now, 100)
            atr_std = ta.stdev(atr_now, 100)
            atr_z = atr_std > 0 ? (atr_now - atr_mean) / atr_std : 0.0
            target_risk_raw = (strategy.equity * (VOLATILITY_TARGET_PCT / 100)) * kelly_frac
            target_risk_per_trade = math.min(strategy.equity * MAX_RISK_PER_TRADE, math.max(strategy.equity * MIN_RISK_PER_TRADE, target_risk_raw))
            cvar_proxy = historical_var95 > 0 ? historical_cvar95 / historical_var95 : 1.0
            gamma = 5 * (1 + f_normalize(math.log(cvar_proxy + 1e-9)))
            lambda_raw = math.exp(-rolling_mdd * gamma) * f_normalize(functoriality_score)
            lambda_smoothed = ta.ema(lambda_raw, 20)
            lambda_risk_budget := math.max(0.05, lambda_smoothed)
            if bar_index < WARMUP_BARS
                lambda_risk_budget := WARMUP_LAMBDA
            if atr_z > 2
                lambda_risk_budget := lambda_risk_budget * 0.5
                dynamic_tsl_mult *= 0.7
            kelly_size = risk_per_unit > 0 ? target_risk_per_trade / risk_per_unit : 0
            hist_ok_cvar = not na(historical_cvar95)
            ema_cvar = ta.ema(hist_ok_cvar ? historical_cvar95 : 0.0, 100)
            stdev_cvar = ta.stdev(hist_ok_cvar ? historical_cvar95 : 0.0, 100)
            cvar_rank = stdev_cvar > 0 ? f_normalize((historical_cvar95 - ema_cvar) / stdev_cvar) : 0.0
            base_rng = nz(ta.atr(14), ta.tr)
            market_impact_score = syminfo.type == "futures" ? f_normalize(ta.sma(volume, 5) / nz(ta.sma(ta.tr, 20), 1)) : f_normalize((high - low) / base_rng)
            raw_floor = 0.5 * (1 - cvar_rank) + 0.5 * market_impact_score
            min_lambda_floor = math.max(0.05, math.min(0.95, raw_floor))
            vol_rank = ta.percentrank(loc_vol_pct, 100)
            clamp_kappa = 5 + 10 * math.exp(-vol_rank)
            pos_size_unclamped = kelly_size * math.max(min_lambda_floor, math.sqrt(lambda_risk_budget))
            pos_size = pos_size_unclamped / (1 + pos_size_unclamped / clamp_kappa)
            max_qty_limit = unified_signal_strength > 0 ? max_long_qty_input : max_short_qty_input
            capped_size = math.min(pos_size, max_qty_limit)
            step = contract_step_size_input
            rounded_size = step > 0 ? math.round(capped_size / step) * step : capped_size
            final_size = capped_size
            if step > 0
                final_size := math.max(step, math.min(rounded_size, max_qty_limit))
            
            if is_exploration_triggered
                final_size := MIN_CONTRACT_QTY 
            
            if final_size < MIN_CONTRACT_QTY
                final_size := 0
            
            long_entry_triggered = final_size > 0 and unified_signal_strength > 0
            short_entry_triggered = final_size > 0 and unified_signal_strength < 0
            
            strategy.entry("Long", strategy.long, qty=final_size, when=long_entry_triggered)
            strategy.entry("Short", strategy.short, qty=final_size, when=short_entry_triggered)



// ─── 5.4. In-Trade Management ───
if is_entry_fill_event
    realized_volatility := ta.ema(ta.tr, 10)
    vol_regime = ta.percentrank(realized_volatility / ta.atr(100), 100)
    initial_tsl_mult = math.max(1.2, 1.5 + vol_regime)
    initial_tp_mult = DYNAMIC_RR_ENABLED ? math.max(2.0, 2.5 - vol_regime) * initial_tsl_mult : initial_tsl_mult * 2.0

    initial_risk_budget = realized_volatility * initial_tsl_mult
    hard_stop_dist = (strategy.equity * (HARD_STOP_PCT / 100)) / math.max(math.abs(strategy.position_size), 1e-6)
    risk_dist = math.min(initial_risk_budget, hard_stop_dist)
    initial_sl_price = strategy.position_size > 0 ? close - risk_dist : close + risk_dist
    last_trail_stop := initial_sl_price
    hh_since_entry := high[1]
    ll_since_entry := low[1]
    initial_tp_price = strategy.position_size > 0 ? close + realized_volatility * initial_tp_mult : close - realized_volatility * initial_tp_mult
    last_trail_tp := initial_tp_price
    strategy.exit("SL/TP", from_entry = strategy.position_size > 0 ? "Long" : "Short", stop = initial_sl_price, limit = initial_tp_price)
    hard_stop_price = strategy.position_size > 0 ? strategy.position_avg_price - hard_stop_dist : strategy.position_avg_price + hard_stop_dist
    strategy.exit("HardSL", from_entry = strategy.position_size > 0 ? "Long" : "Short", stop = hard_stop_price)
    var_dna_for_trade := f_create_holographic_vector()
    var_entry_bar_index := bar_index
    var_entry_time := time
    var_initial_atr := ta.atr(14)[1]

if is_in_trade_event and barstate.isconfirmed
    exit_now = false
    exit_comment = ""
    if syminfo.type == "futures"
        sentinel_score = 0.0
        funding_weight = 0.0
        funding_rate_available = not na(fr_val)
        if funding_rate_available and math.abs(fr_val) > 0.001
            funding_weight := 1.0
        if not na(oi_val)
            sentinel_score := funding_rate_available ? (math.abs(oi_zscore) * 0.7 + funding_weight * 0.3) : math.abs(oi_zscore)
        if sentinel_score > 2.5
            exit_now := true
            exit_comment := "OI/Funding Spike Exit"
    if not exit_now
        current_expert_behavior = f_create_expert_behavior_vector()
        k_neighbors_meta_exit = f_ann_lookup(current_expert_behavior, "MetaCognitive")
        reversal_risk_score_exit = f_calculate_reversal_risk_score(k_neighbors_meta_exit, flat_expert_behavior_db)
        if reversal_risk_score_exit > EXIT_META_CONFIDENCE
            exit_now := true
            exit_comment := "Meta-Cognitive Exit"
    if not exit_now
        atr_val = ta.atr(14)
        is_vv_climax = volume > ta.sma(volume, 20) * EXIT_VOL_MULT and (strategy.position_size > 0 ? close > ta.sma(close, 20) + (atr_val * dynamic_tp_mult) : close < ta.sma(close, 20) - (atr_val * dynamic_tp_mult))
        is_rsi_climax = (strategy.position_size > 0 and ta.rsi(close, 14) > EXIT_RSI_THRESH) or (strategy.position_size < 0 and ta.rsi(close, 14) < (100 - EXIT_RSI_THRESH))
        if is_vv_climax or is_rsi_climax
            exit_now := true
            exit_comment := "Climax Exit"
    if not exit_now and functoriality_score < EXIT_FUNCTORIALITY_THRESH
        exit_now := true
        exit_comment := "Predictability Collapse"
    if not exit_now
        timeInTradeDays = math.max(1.0, float(time - var_entry_time)) / 86400000.0
        pnl_per_unit_risk = (strategy.openprofit / strategy.equity) / (realized_volatility / close + 1e-9)
        ex_ante_sharpe = pnl_per_unit_risk / math.sqrt(timeInTradeDays)
        dynamic_sharpe_target = 0.05 + 0.1 * (1 - win_rate)
        if ex_ante_sharpe < dynamic_sharpe_target and strategy.openprofit > 0
            exit_now := true
            exit_comment := "Dynamic Sharpe Exit"
    
    if not exit_now and TIME_STOP_BARS > 0
        if strategy.opentrades > 0 and (bar_index - strategy.opentrades.entry_bar_index(0)) > TIME_STOP_BARS
            if strategy.openprofit <= 0
                exit_now := true
                exit_comment := "Time-Stop Exit"

    strategy.close_all(when=exit_now, comment=exit_comment)

    if not exit_now
        realized_volatility := ta.ema(ta.tr, 10)
        tsl_mult = dynamic_tsl_mult
        tp_mult = dynamic_tp_mult
        vol_regime = ta.percentrank(realized_volatility / ta.atr(100), 100)
        if vol_regime > 0.9
            tsl_mult *= 0.6
            tp_mult *= 0.8
        new_tsl = last_trail_stop
        if strategy.position_size > 0
            hh_since_entry := math.max(hh_since_entry, high[1])
            new_tsl := math.max(last_trail_stop, hh_since_entry - (realized_volatility * tsl_mult))
        else
            ll_since_entry := math.min(ll_since_entry, low[1])
            new_tsl := math.min(last_trail_stop, ll_since_entry + (realized_volatility * tsl_mult))
        new_tp = strategy.position_size > 0 ? strategy.opentrades.entry_price(0) + var_initial_atr * tp_mult : strategy.opentrades.entry_price(0) - var_initial_atr * tp_mult
        if new_tsl != last_trail_stop or new_tp != last_trail_tp
            strategy.exit("SL/TP Update", stop = new_tsl, limit = new_tp)
            last_trail_stop := new_tsl
            last_trail_tp := new_tp



// ─── 5.5. Learning Loop ───
if is_trade_closed_event
    last_pnl = strategy.closedtrades.profit(ct_count - 1)
    f_push_cap(trade_pnls, last_pnl, 100)
    if last_pnl < 0
        f_push_cap(down_devs, last_pnl * last_pnl, 100)
    f_push_cap(equity_history, strategy.equity, 60)
    peak_equity = array.max(equity_history)
    rolling_mdd := (peak_equity - strategy.equity) / math.max(peak_equity, 1e-6)
   
    if last_pnl > 0
        wins += 1
        win_sum += last_pnl
    else if last_pnl < 0
        losses += 1
        loss_sum += math.abs(last_pnl)

    win_rate := (wins + losses) > 0 ? wins / float(wins + losses) : 0.5
    avg_win = wins > 0 ? win_sum / wins : 0
    avg_loss = losses > 0 ? loss_sum / losses : 0
    payoff_ratio := avg_loss > 0 ? avg_win / avg_loss : 1.0
    downside_dev = array.size(down_devs) > 0 ? math.sqrt(array.sum(down_devs) / array.size(down_devs)) : 0
    avg_ret = array.size(trade_pnls) > 0 ? array.avg(trade_pnls) : 0
    sortino_ratio := downside_dev > 0 ? avg_ret / downside_dev : 1.0
    var_cvar_array = f_calculate_var_cvar(trade_pnls, 0.95)
    historical_var95 := f_safe_array_get(var_cvar_array, 0, 0.02)
    historical_cvar95 := f_safe_array_get(var_cvar_array, 1, 0.03)
    last_trade_size = strategy.closedtrades.size(ct_count - 1)
    last_trade_entry_price = strategy.closedtrades.entry_price(ct_count - 1)
    var_epsilon = math.max(historical_var95, 1e-9)
    trade_value_at_risk = last_trade_size * last_trade_entry_price * var_epsilon
    hist_ok_learn = not na(historical_cvar95)
    ema_cvar_learn = ta.ema(hist_ok_learn ? historical_cvar95 : 0.0, 25)
    stdev_cvar_learn = ta.stdev(hist_ok_learn ? historical_cvar95 : 0.0, 25)
    cvar_rank_learning = stdev_cvar_learn > 0 ? f_normalize((historical_cvar95 - ema_cvar_learn) / stdev_cvar_learn) : 0.0
    err = trade_value_at_risk > 0 ? (last_pnl / trade_value_at_risk) * (1 - cvar_rank_learning) : 0
    err_scale = array.size(trade_pnls) > 10 and nz(array.median(trade_pnls)) != 0 ? 10 / math.abs(array.median(trade_pnls)) : 10
    err := err * err_scale
    lr_array = f_cosine_lr(AOML_BETA, MIN_BETA, ct_count, LR_HALF_LIFE_T, LR_T_MULT, sgdr_curr_t0, sgdr_next_reset)
    adaptive_beta = f_safe_array_get(lr_array, 0, MIN_BETA)
    sgdr_curr_t0 := f_safe_array_get(lr_array, 1, sgdr_curr_t0)
    sgdr_next_reset := f_safe_array_get(lr_array, 2, sgdr_next_reset)
    ahft_weight := f_update_weight(ahft_weight, err, ahft_score[1], adaptive_beta)
    ofpi_weight := f_update_weight(ofpi_weight, err, ofpi_score[1], adaptive_beta)
    hurst_weight := f_update_weight(hurst_weight, err, hurst_score[1], adaptive_beta)
    functoriality_weight := f_update_weight(functoriality_weight, err, functoriality_score[1], adaptive_beta)
    macro_trend_weight := f_update_weight(macro_trend_weight, err, macro_trend_score[1], adaptive_beta)
    meso_beta_weight := f_update_weight(meso_beta_weight, err, meso_beta_score[1], adaptive_beta)
    meso_momentum_weight := f_update_weight(meso_momentum_weight, err, meso_momentum_score[1], adaptive_beta)
    micro_volatility_weight := f_update_weight(micro_volatility_weight, err, micro_volatility_score[1], adaptive_beta)
    micro_leverage_weight := f_update_weight(micro_leverage_weight, err, micro_leverage_score[1], adaptive_beta)
    msgarch_weight := f_update_weight(msgarch_weight, err, msgarch_score[1], adaptive_beta)
    pre_norm_total = ahft_weight + ofpi_weight + hurst_weight + functoriality_weight + macro_trend_weight + meso_beta_weight + meso_momentum_weight + micro_volatility_weight + micro_leverage_weight + msgarch_weight
    if pre_norm_total > 0
        ahft_weight /= pre_norm_total, ofpi_weight /= pre_norm_total, hurst_weight /= pre_norm_total, functoriality_weight /= pre_norm_total, macro_trend_weight /= pre_norm_total, meso_beta_weight /= pre_norm_total, meso_momentum_weight /= pre_norm_total, micro_volatility_weight /= pre_norm_total, micro_leverage_weight /= pre_norm_total, msgarch_weight /= pre_norm_total
    functoriality_weight := math.max(0.05, functoriality_weight)
    macro_trend_weight := math.max(0.05, macro_trend_weight)
    final_total_weight = ahft_weight + ofpi_weight + hurst_weight + functoriality_weight + macro_trend_weight + meso_beta_weight + meso_momentum_weight + micro_volatility_weight + micro_leverage_weight + msgarch_weight
    if final_total_weight > 0
        ahft_weight /= final_total_weight, ofpi_weight /= final_total_weight, hurst_weight /= final_total_weight, functoriality_weight /= final_total_weight, macro_trend_weight /= final_total_weight, meso_beta_weight /= final_total_weight, meso_momentum_weight /= final_total_weight, micro_volatility_weight /= final_total_weight, micro_leverage_weight /= final_total_weight, msgarch_weight /= final_total_weight
    if not na(var_dna_for_trade) and array.size(var_dna_for_trade) > 0
        trade_duration = bar_index - var_entry_bar_index
        safe_trade_duration = math.min(trade_duration, 9999)
        is_long = strategy.closedtrades.size(ct_count - 1) > 0
        entry_price = strategy.closedtrades.entry_price(ct_count - 1)
        optimal_tp_mult = 2.0
        if trade_duration > 0
            if is_long
                highest_high = ta.highest(high, safe_trade_duration)[1]
                potential_pnl = highest_high - entry_price
                optimal_tp_mult := potential_pnl > 0 and var_initial_atr > 0 ? potential_pnl / var_initial_atr : 2.0
            else
                lowest_low = ta.lowest(low, safe_trade_duration)[1]
                potential_pnl = entry_price - lowest_low
                optimal_tp_mult := potential_pnl > 0 and var_initial_atr > 0 ? potential_pnl / var_initial_atr : 2.0
        optimal_tsl_mult = math.max(1.0, optimal_tp_mult * 0.5)
        optimal_exit_sensitivity = math.max(0.3, 1.0 - functoriality_score)
        optimal_path_gene = array.copy(var_dna_for_trade)
        array.push(optimal_path_gene, optimal_tsl_mult)
        array.push(optimal_path_gene, optimal_tp_mult)
        array.push(optimal_path_gene, optimal_exit_sensitivity)
        start_idx = optimal_db_head * OPTIMAL_PATH_GENE_LENGTH
        if array.size(flat_optimal_path_db) < OPTIMAL_PATH_DB_SIZE * OPTIMAL_PATH_GENE_LENGTH
            for i = 0 to array.size(optimal_path_gene) - 1
                array.push(flat_optimal_path_db, f_safe_array_get(optimal_path_gene, i, 0.0))
            array.push(optimal_path_gene_bars, var_entry_bar_index)
        else
            for i = 0 to OPTIMAL_PATH_GENE_LENGTH - 1
                array.set(flat_optimal_path_db, start_idx + i, f_safe_array_get(optimal_path_gene, i, 0.0))
            array.set(optimal_path_gene_bars, optimal_db_head, var_entry_bar_index)
        optimal_db_head := (optimal_db_head + 1) % OPTIMAL_PATH_DB_SIZE
        var_dna_for_trade := na
    if use_distRL_flag
        dist_idx = ct_count % NUM_Q
        array.set(dist_arr, dist_idx, nz(f_safe_array_get(dist_arr, dist_idx, 0.0)) + last_pnl)


//───────────────────────────────────────────────────────────────────────────────
// 6. VISUALIZATION
//───────────────────────────────────────────────────────────────────────────────
if show_dashboard and barstate.islastconfirmedhistory
    if not na(main_dashboard)
        table.delete(main_dashboard)
    dash_pos = f_getTablePosition(dashboard_position_input)
    main_dashboard := table.new(dash_pos, 2, 15, border_width = 1, bgcolor = color.new(color.black, 75))
    table.merge_cells(main_dashboard, 0, 0, 1, 0)
    table.cell(main_dashboard, 0, 0, "✅ AHFT-HPH-" + CODE_VERSION, bgcolor = color.new(color.maroon, 50), text_color = color.white)
    table.cell(main_dashboard, 0, 1, "Unified Strength", text_color = color.gray)
    table.cell(main_dashboard, 1, 1, str.tostring(unified_signal_strength, "#.##"))
    table.cell(main_dashboard, 0, 2, "Win Rate/Payoff", text_color = color.gray)
    table.cell(main_dashboard, 1, 2, str.tostring(win_rate * 100, "#.#") + "% / " + str.tostring(payoff_ratio, "#.##"))
    table.cell(main_dashboard, 0, 3, "Sortino/CVaR(95%)", text_color = color.gray)
    table.cell(main_dashboard, 1, 3, str.tostring(sortino_ratio, "#.##") + " / " + str.tostring(historical_cvar95 * 100, "#.##") + "%")
    table.merge_cells(main_dashboard, 0, 4, 1, 4)
    table.cell(main_dashboard, 0, 4, "--- Sentinel Engine ---", text_color = color.aqua)
    table.cell(main_dashboard, 0, 5, "Risk Budget (λ)", text_color = color.gray)
    table.cell(main_dashboard, 1, 5, str.tostring(lambda_risk_budget * 100, "#.#") + "%")
    table.cell(main_dashboard, 0, 6, "Meso-Beta Z-Score", text_color = color.gray)
    table.cell(main_dashboard, 1, 6, str.tostring(meso_beta_score, "#.##"))
    table.cell(main_dashboard, 0, 7, "Meso-Momentum Ortho", text_color = color.gray)
    table.cell(main_dashboard, 1, 7, str.tostring(meso_momentum_score, "#.##"))
    table.merge_cells(main_dashboard, 0, 8, 1, 8)
    table.cell(main_dashboard, 0, 8, "--- AOML Weights ---", text_color = color.orange)
    table.cell(main_dashboard, 0, 9, "W(Meso-Momentum)", text_color = color.gray)
    table.cell(main_dashboard, 1, 9, str.tostring(meso_momentum_weight, "#.####"))
    table.cell(main_dashboard, 0, 10, "W(Meso-Beta)", text_color = color.gray)
    table.cell(main_dashboard, 1, 10, str.tostring(meso_beta_weight, "#.####"))
    table.cell(main_dashboard, 0, 11, "W(Macro Trend)", text_color = color.gray)
    table.cell(main_dashboard, 1, 11, str.tostring(macro_trend_weight, "#.####"))
    oi_status = na(oi_val) ? "N/A" : (math.abs(oi_zscore) > 2.5 ? "SPIKE" : "Stable")
    table.cell(main_dashboard, 0, 12, "OI Sentinel", text_color = color.gray)
    table.cell(main_dashboard, 1, 12, oi_status)
    table.cell(main_dashboard, 0, 13, "Position Status", text_color = color.gray)
    table.cell(main_dashboard, 1, 13, strategy.position_size != 0 ? (strategy.position_size > 0 ? "LONG" : "SHORT") : "FLAT")

    lr_arr_dash = f_cosine_lr(AOML_BETA, MIN_BETA, ct_count, LR_HALF_LIFE_T, LR_T_MULT, sgdr_curr_t0, sgdr_next_reset)
    adaptive_beta_val = f_safe_array_get(lr_arr_dash, 0, MIN_BETA)
    table.cell(main_dashboard, 0, 14, "Adaptive Beta", text_color = color.gray)
    table.cell(main_dashboard, 1, 14, str.tostring(nz(adaptive_beta_val, MIN_BETA), "#.####"))

//───────────────────────────────────────────────────────────────────────────────
// 7. DUMMY PLOT (for overlay=true)
//───────────────────────────────────────────────────────────────────────────────
plot(na)



[PART 1/30] 서문: 시장이라는 생명체를 향한 여정
프로젝트의 시작: 하나의 근본적인 질문
AHFT(Anomalous Holonomy Field Theory) 프로젝트는 하나의 질문에서 시작되었습니다.
"시장은 예측 불가능한 혼돈(Chaos)의 영역인가, 아니면 우리가 아직 이해하지 못한 심오한 질서(Order)를 따르는가?"
우리는 후자, 즉 시장에 내재된 질서가 존재한다는 가설에 모든 것을 걸기로 했습니다.
AHFT의 핵심 철학: 시장은 '의식체'다
AHFT는 시장을 가격 데이터의 집합이 아닌, 수많은 참여자들의 희망, 공포, 탐욕이 얽혀 만들어진 하나의 거대한 **'생명체'**로 간주합니다. 이 생명체는 기억, 습관, 감정을 가지며 스스로 학습하고 진화합니다. 우리의 목표는 이 생명체의 내부 상태를 측정하고, 과거의 기억과 행동을 학습하여, 미래의 움직임을 확률적으로 예측하는 **'인공 거래 지능(Artificial Trading Intelligence)'**을 구축하는 것입니다.
프로젝트의 지향점: 강건하고(Robust), 적응하며(Adaptive), 설명 가능한(Explainable) AI
강건함 (Robustness): 다양한 시장 환경에서 꾸준히 살아남는 안정성.
적응성 (Adaptability): 시장의 변화를 스스로 감지하고 전략을 동적으로 수정하는 능력.
설명 가능성 (Explainability): AI의 판단 근거를 투명하게 보여주는 신뢰성.
[PART 2/30] 시스템 아키텍처: 이중 코어 의식 (Dual-Core Consciousness)
AHFT의 두뇌는 인간의 '이중 사고 프로세스'를 모방한 두 개의 AI 코어로 구성됩니다.
코어 1: 전략가 의식 (The Strategist Core) - "어떻게 이길 것인가?"
역할: 수익 창출 기회를 포착하고 최적의 거래 계획을 수립하는 '공격수'.
학습 데이터: flat_optimal_path_db (최적 경로 데이터베이스).
작동 방식: 현재 시장의 'DNA'와 가장 유사한 과거의 성공 사례들을 찾아, 그들이 기억하는 '가상 최적 파라미터(TSL, TP)'를 지능적으로 합성하여 '거래 제안서'를 생성합니다.
코어 2: 초인지 의식 (The Meta-Cognitive Core) - "혹시 지금 위험하지는 않은가?"
역할: 전략가의 제안을 최종 검토하고, 숨겨진 리스크나 임박한 반전을 감지하여 거부권(Veto)을 행사하는 '수비수'.
학습 데이터: flat_expert_behavior_db (전문가 행동 데이터베이스).
v35.2 강화: 단순 '반전 확률'이 아닌, **기대 위험 점수 (Expected Risk Score = Probability × Severity)**를 계산하여 훨씬 더 정교한 위험 평가를 수행합니다.
이 두 코어는 서로를 견제하고 보완하며, 공격적인 기회 탐색과 동시에 시스템 전체의 안정성을 유지하는 균형 잡힌 의사결정을 내립니다.
[PART 3/30] 감각기관: v38.0 최종 전문가 생태계
AHFT의 두뇌가 정확한 판단을 내리려면, 시장을 다각도로 분석하는 고품질의 정보가 필요합니다. 최종 버전에서는 총 11명의 전문가가 시스템의 감각기관 역할을 수행합니다.
AHFT Score (기본 추세 분석가): 시스템의 가장 기본적인 추세 판단 기준.
OFPI Score (주문 흐름 심리학자): T3 평활화 기반의 주문 흐름 분석을 통해 순수한 매수/매도 의도 측정.
Hurst Score (시장 고고학자): R/S, DFA, Goertzel 분석을 앙상블하여 시장의 장기 기억(추세 지속성 vs. 평균 회귀) 분석.
Functoriality Score (구조 안정성 분석가): 시장 구조의 안정성과 예측 가능성 측정.
Macro Trend Score (거시 전략가): 상위 타임프레임과의 구조적 동조성 분석.
Meso-Beta Score (상대 강도 분석가): 외부 벤치마크 대비 현재 자산의 상대적 변동성(베타)의 통계적 이탈 측정.
Meso-Momentum Score (중간 파도 관측가): Macro-Trend와의 상관관계를 제거(직교화)하여 순수한 중간 타임프레임의 모멘텀 측정.
Micro Volatility Score (지형 탐험가): 단기 변동성 실시간 감지.
Micro Leverage Score (레버리지 감시자): 미결제약정(OI) 변화를 통해 레버리지 자금 유출입 감시.
MSGARCH Regime Score (시장 국면 분석가): 변동성과 추세의 복합적인 국면(저변동성 상승, 고변동성 하락 등) 분석.
Unified Signal Strength (최고 의사결정자): 위 10명 전문가의 의견을 AOML 알고리즘을 통해 동적 가중치로 종합하여 최종 점수 산출.
[PART 4/30] 개발 여정 I: 실패의 연대기 (v6 ~ v8)
(v37.2 문서와 동일: 명령과 보고의 분리, 시간적 무결성, 무중단 방어, 단일 지휘 체계의 교훈을 얻은 과정)
[PART 5/30] 개발 여정 II: 대도약 (The Great Leap) - v33.x ~ v36.x
(v37.2 문서와 동일: PatchTST, ANN, AOML, λ-Risk Budget 등 하이퍼-인지 엔진의 탄생과 CVaR-Kelly, Risk-Aware Meta-Cognition 등 프로메테우스 엔진으로의 진화 과정)
[PART 6/30] 개발 여정 III: 시련의 용광로 (The Crucible) - v37.x
v36.x의 안정적인 기반 위에서, 우리는 시스템의 성능을 극한으로 끌어올리기 위한 최종 담금질에 들어갔습니다. 이 과정은 예상치 못한 복합적인 버그와 성능 저하라는 '시련의 용광로'였습니다.
v37.2 ~ v37.4: 런타임 경고와의 전쟁
문제: pivothigh 함수의 가격 값 반환을 인덱스로 오인하여 사용, array.get에 시리즈 타입을 전달하는 등 근본적인 타입 불일치 오류로 인한 런타임 경고 발생.
교훈: **참조의 무결성(헌장 제6조)**은 아무리 강조해도 지나치지 않다. 모든 변수와 함수의 반환 타입을 명확히 인지하고, 타입에 맞는 접근자를 사용해야 한다. nz()는 시리즈에, f_safe_array_get은 배열에 사용한다.
v37.5 ~ v37.6: "거래 단절" 미스터리
문제: 시스템이 거의 거래를 하지 않는 현상 발생. 원인은 (A)지나치게 엄격한 진입 게이트, (B)잘못된 리스크 단위 계산, (C)가중치 합산 로직 버그의 3중 연쇄 작용이었음.
교훈: 시스템의 각 모듈은 독립적으로 완벽해야 할 뿐만 아니라, 전체적으로 조화롭게 작동해야 한다. 하나의 스케일 오류가 연쇄 반응을 일으켜 시스템 전체를 마비시킬 수 있다.
v37.7 ~ v37.9: 성능의 마지막 조각 맞추기
문제: 거래는 재개되었으나, 저조한 손익비(Pay-off Ratio)와 깊은 MDD로 수익성 악화.
교훈: 기계적인 진입/청산만으로는 부족하다. 시장의 변동성 국면에 따라 **손익비 목표(Dynamic R:R)**와 리스크 예산(λ-Floor), **탐험 확률(Adaptive ε-Greedy)**을 동적으로 조절하는 유연성이 필수적이다.
이 모든 시련을 통해 얻은 교훈이 바로 **v38.0 "Phoenix"**에 모두 담겨 있습니다.
(이후 PART 7/30부터 PART 29/30까지는, 이전 문서의 내용을 기반으로 v37.8 및 v37.9 평가 보고서에서 제안 및 수정된 모든 강화 사항(Dynamic R:R, Fractional Kelly, Adaptive λ-Floor, Adaptive Epsilon-Greedy, Time-Stop 등)을 각 모듈 설명에 완벽하게 반영하여 재작성됩니다.)

[PART 7/30] 엔진의 심장부 2: ANN 기억 검색 및 신뢰도 평가
AHFT의 '기억(데이터베이스)'에는 수만 개의 과거 거래 '유전자'가 저장됩니다. 현재 시장과 가장 유사한 과거를 찾는 것은 이 시스템의 핵심입니다.
HNSW (목표 아키텍처): 방대한 고차원 데이터 속에서 유사한 데이터를 초고속으로 검색하는 HNSW(Hierarchical Navigable Small World) 개념을 지향합니다.
현재 구현 (v38.0): Pine Script의 한계로 실제 그래프는 없지만, 코사인 유사도와 링 버퍼 구조로 핵심 개념을 모방합니다.
v35.2 강화 (Adaptive K): ANN의 이웃 수(K)를 k = max(3, round(math.log(num_genes))) 공식을 통해 데이터베이스 크기에 따라 동적으로 조절하여, 검색의 강건함을 유지합니다.
v37.7 강화 (ANN Cold-Start 해결):
문제점: 초기 학습 단계에서 DB에 유전자가 부족하여 f_ann_lookup이 3개 미만의 이웃을 반환할 경우, f_synthesize_meta_parameters가 신뢰할 수 없는 파라미터를 생성하는 문제가 있었습니다.
해결책: f_synthesize_meta_parameters 함수 내에 부트스트랩 로직을 추가했습니다. 만약 유효한 이웃 수가 3개 미만이면, 사전에 정의된 안전한 기본 파라미터(tsl=2.0, tp=3.0 등)와 **고정된 높은 신뢰도(0.8)**를 반환합니다. 이는 시스템이 충분한 데이터를 학습하기 전까지 무모한 거래를 시도하는 것을 방지하는 핵심적인 안전장치입니다.
[PART 8/30] 실행 엔진 1: 지능형 자금 관리 (CVaR-Constrained & Fractional Kelly)
진입이 최종 승인되면, 시스템은 여러 단계의 정교한 필터를 통해 포지션의 크기를 동적으로 조절합니다.
CVaR-Constrained Kelly (Wiering et al., 2023): 시스템의 장기적인 성과(승률, 손익비)와 꼬리 위험(CVaR)을 바탕으로, "포트폴리오의 CVaR이 목표치(τ)를 넘지 않도록" 제약된 최적의 베팅 비율(f_star)을 계산합니다.
드로우다운 제어 (DD-Kelly, Zakamouline, 2019): 계산된 f_star는 USE_DRAWDOWN_KELLY 옵션에 따라 현재 누적 손실폭(MDD)을 고려하여 추가적으로 조절됩니다. MDD가 목표치에 가까워질수록 베팅 비율은 줄어듭니다.
v37.8 강화 (Fractional Kelly, Thorp, 2017):
문제점: 이론적인 Kelly 베팅은 여전히 너무 공격적일 수 있습니다.
해결책: FRACTIONAL_KELLY_KAPPA Input(기본값 0.5)을 도입했습니다. 최종 베팅 비율 kelly_frac은 f_star * FRACTIONAL_KELLY_KAPPA로 계산되어, 사용자가 전체 베팅의 공격성을 보수적으로 조절할 수 있게 합니다. 이는 과대 베팅으로 인한 치명적인 손실을 방지하는 중요한 수단입니다.
[PART 9/30] 실행 엔진 2: 리스크 유닛 및 λ-Scheduler
최적의 베팅 비율이 결정된 후, 실제 주문 수량은 현재 시장의 위험도를 반영하여 최종적으로 조절됩니다.
v37.6.1 강화 (리스크 유닛 교정):
문제점: risk_per_unit 계산 시 스케일 오류로 인해 리스크가 과소평가되어 포지션 사이즈가 소멸되었습니다.
해결책: loc_vol_pct = ta.ema(ta.tr, 10) / close로 백분율 변동성을 계산하고, risk_per_unit = loc_vol_pct * close * RISK_CONTRACT_VALUE 공식으로 동적 계약 가치를 반영합니다.
λ-Risk Budget & Scheduler:
lambda_raw는 현재 시장의 예측 가능성(functoriality_score)과 누적 손실폭(rolling_mdd)을 고려하여 '위험 예산'의 기본 비율을 결정합니다.
v37.8 강화 (비선형 λ-Floor):
문제점: MDD가 심화될 때 λ가 너무 빠르게 0으로 수렴하여 거래가 단절되었습니다.
해결책: λ 스케줄러를 ta.ema(lambda_raw, 20)으로 부드럽게 평균한 뒤, 0.05의 소프트 플로어를 더해 급격한 변동을 완충했습니다.
[PART 10/30] 실행 엔진 3: 진입 프로토콜 (3중 게이트)
모든 진입 결정은 3개의 까다로운 관문을 통과해야만 최종 승인됩니다.
게이트 1: 적응형 신호 강도 (Adaptive Signal Strength)
조건: math.abs(unified_signal_strength) > adaptive_entry_sig_threshold
v37.9.3 강화: adaptive_entry_sig_threshold = max(0.05, 0.35 × σ) 공식을 적용해, 지나친 게이트 과도 현상을 완화했습니다.
게이트 2: ANN 기반 신뢰도 (ANN-based Confidence)
조건: base_confidence > ENTRY_CONFIDENCE_THRESHOLD
v37.7 강화 (Soft Confidence): base_confidence 계산 시 f_normalize를 제거하여, ANN이 출력하는 원시적인 신뢰도 점수를 그대로 사용합니다. 이는 미묘한 신뢰도 차이를 보존하여 더 정교한 판단을 가능하게 합니다.
게이트 3: 초인지 코어의 위험 심사 (Meta-Cognitive Veto)
조건: reversal_risk_score < META_VETO_THRESHOLD
전략가 코어가 제안한 기회가 아무리 좋아 보여도, 초인지 코어가 계산한 **'기대 위험 점수'**가 높으면 최종적으로 거부권(Veto)을 행사하여 치명적인 함정을 피합니다.
[PART 11/30] 실행 엔진 4: 6중 필터 청산 로직
일단 포지션에 진입하면, 6개의 독립적인 방어선이 실시간으로 시장을 감시합니다.
0차 ~ 3차 방어선: (v37.2 문서와 동일)
OI-Spike Sentinel (유동성 쇼크 감지)
초인지 코어의 긴급 탈출 (기대 위험 급증 감지)
클라이맥스 청산 (과열 감지)
예측 가능성 붕괴 청산 (혼돈 감지)
4차 방어선: 동적 샤프 비율 청산 (수익성 악화 감지): 포지션의 시간 대비 위험 조정 수익률이 동적으로 계산된 최소 목표치보다 낮아질 때, 비효율적인 자금 운용을 막기 위해 청산합니다.
v37.8 신규 5차 방어선: 시간 정지 (Time-Stop)
조건: TIME_STOP_BARS > 0 and (bar_index - entry_bar_index) > TIME_STOP_BARS and strategy.openprofit <= 0
의미: "의미 없는 횡보나 약한 손실 상태로 너무 오랜 시간 자금이 묶여 있다. 더 좋은 기회를 위해 자금을 회수하라!" 이는 자본의 회전율을 높이고, 장기적인 기회비용 손실을 방지합니다.
최종 6차 방어선: 기본 리스크 관리 (Dynamic SL/TP)
조건: 위 방어선들이 뚫리지 않는 동안, 진입 시 설정된 동적 트레일링 스탑(TSL) 또는 목표가(TP)에 도달할 때.
v37.8 강화 (Dynamic R:R Target): initial_tp_mult 계산 시, 시장 변동성 순위(vol_regime)를 반영하여 변동성이 높을수록 더 보수적인(낮은) TP 배수를 설정합니다. 이는 불안정한 시장에서 이익을 조기에 확보하여 승률을 높이고 Pay-off Ratio를 개선하는 것을 목표로 합니다.
v37.9 강화 (ATR-Guard TSL): initial_tsl_mult 계산 시, math.max(1.2, ...) 가드를 추가하여 변동성이 아무리 낮아져도 최소한의 손절폭을 확보, 급격한 갭 발생에 대한 방어력을 높였습니다.
v37.9.4 예고 (Guardian): Hard Equity Stop 5%와 Vol-Shock Guard(ATR z-score > 2 시 λ 50%↓, TSL 30%↓)가 추가되어 대규모 변동 시 자본 보호 기능이 강화됩니다.
[PART 12/30] 학습 루프: 스스로 현명해지는 방법
AOML (적응형 온라인 메타 학습): (v37.2 문서와 동일) Tail-Aware Reward Shaping과 SGDR 스케줄러를 통해 전문가 가중치를 지속적으로 업데이트합니다.
최적 경로 데이터베이스 강화: (v37.2 문서와 동일) 매 거래 종료 시, '가상의 최적 파라미터'를 역산하여 새로운 '성공 유전자'를 DB에 추가합니다.
v37.8 신규 학습 모듈: ε-Greedy 탐험적 진입 (Adaptive Epsilon-Greedy)
문제점: 시스템이 특정 전략에 고착화되어 새로운 시장 환경을 학습할 기회를 놓치는 'Cold-Start' 문제가 발생할 수 있습니다.
해결책 (Moody & Saffell, 2001 참조):
USE_EPSILON_GREEDY 옵션을 통해 기능을 활성화합니다.
일정 기간(EPSILON_BAR_LIMIT) 동안 거래가 없으면, 탐험 모드가 활성화됩니다.
Adaptive Rate: 탐험 확률(eps_prob_dyn)은 거래 공백이 길수록 빠르게 증가합니다. eps_prob_dyn = min(0.30, EPSILON_PROB × recent_no_trade / 50)
Controlled Exploration: 탐험은 unified_signal_strength가 매우 약한, 즉 시스템이 "방향을 전혀 모르겠는" 상태에서만 최소 수량으로 이루어집니다. 이는 완전한 무작위 진입이 아닌, 통제된 환경에서의 데이터 수집을 보장합니다.
[PART 13/30] 사용자 매뉴얼: 시스템과의 대화법
AHFT는 사용자와 상호작용하며 함께 성장하는 '파트너'입니다. 이 도구를 효과적으로 활용하기 위한 핵심 설정은 다음과 같습니다.
타임프레임 정의 (가장 중요): 자신의 매매 스타일에 맞게 MACRO, MESO, MICRO 타임프레임을 설정해야 합니다. 이는 시스템의 판단 기준이 되는 세 가지 시간 축입니다.
스윙 트레이더 예시: Macro: D, Meso: 240, Micro: 60
데이 트레이더 예시: Macro: 240, Meso: 60, Micro: 15
리스크 성향 조절 (🛡️ Risk & Sizing Engine 그룹):
RISK_CONTRACT_VALUE: 가장 중요한 리스크 파라미터 중 하나. 리스크 계산의 기준이 되는 계약의 **명목 가치(Notional Value)**를 설정합니다. (예: BTC 현물 = 현재 가격, ES 선물 = 50, 주식 = 1주 가격) 이 값을 정확히 설정해야 포지션 사이징이 올바르게 작동합니다.
VOLATILITY_TARGET_PCT: 한 거래에서 감수할 총 자산 대비 목표 위험 비율(%)을 설정합니다.
FRACTIONAL_KELLY_KAPPA: 켈리 기준이 제안하는 베팅 규모를 얼마나 따를지 결정하는 축소 계수입니다. 값을 낮출수록(예: 0.3) 더 보수적인 베팅을 합니다.
CVAR_CONSTRAINT_TAU & DRAWDOWN_TARGET_PCT: 시스템이 넘지 않도록 노력할 최대 꼬리 위험과 최대 누적 손실폭을 설정하는 핵심 방어선입니다.
시스템 '성격' 조절:
ENTRY_CONFIDENCE_THRESHOLD: 전략가 코어의 제안에 대한 최소 신뢰도. 값을 높일수록 더 확실한 기회에만 진입하는 신중한 성격이 됩니다.
META_VETO_THRESHOLD: 초인지 코어의 위험 감지 민감도. 값을 낮출수록 작은 기대 위험 신호에도 진입을 포기하는 극도로 보수적인 성격이 됩니다.
USE_EPSILON_GREEDY: 시스템이 장기간 거래를 하지 않을 때, 새로운 시장 국면을 학습하기 위한 탐험적 진입을 허용할지 여부를 결정합니다.
청산 전략 조절 (🚶 Adaptive Exit 그룹):
DYNAMIC_RR_ENABLED: 변동성에 따라 초기 손익비 목표를 동적으로 조절할지 여부를 결정합니다.
TIME_STOP_BARS: 수익성 없는 포지션을 얼마나 오래 보유할지 최대 기간을 설정합니다. 데이 트레이딩의 경우 짧게(예: 16), 스윙 트레이딩의 경우 길게(예: 96) 설정할 수 있습니다.
[PART 14/30] 대시보드 해석 가이드
차트 우측 하단의 대시보드는 AHFT의 '계기판'입니다. 거래 전 반드시 확인해야 할 핵심 지표는 다음과 같습니다.
Unified Strength: 11명 전문가의 종합 점수. 현재 시장의 방향성과 힘을 나타냅니다.
Risk Budget (λ): 현재 시장 리스크를 고려한 '허용된 위험 예산'입니다. 이 값이 50% 미만이라면, 시스템이 시장을 매우 위험하다고 판단하고 있으니 진입에 신중해야 합니다. 0.01은 MDD로 인해 설정된 최소 하한선입니다.
Meso-Beta Z-Score / Meso-Momentum Ortho: 시장 대비 상대 강도와 순수 모멘텀을 각각 보여줍니다. 두 지표의 조합을 통해 시장의 미묘한 변화를 감지할 수 있습니다.
AOML Weights: 최근 어떤 전문가가 좋은 성과를 내고 있는지 보여줍니다. 예를 들어, W(Functoriality)가 높다면 현재 시장이 구조적으로 안정된 추세를 보이고 있음을 의미합니다.
Position Status: 현재 포지션 상태를 보여줍니다. 만약 ε-Greedy에 의한 탐험적 진입이라면, 해당 정보가 별도로 표시될 수 있습니다 (미래 버전).
[PART 15/30] 미래 비전: 진정한 '인공 거래 지능'을 향하여
AHFT v38.0 "Phoenix"는 안정적인 프로덕션 빌드이지만, 우리의 여정은 이제 막 새로운 단계로 접어들고 있습니다.
Distributional RL + Quantile CVaR 보상: 현재의 점수 기반 보상 함수를, 미래 손익의 '확률 분포' 자체를 예측하고 그 분포의 꼬리 위험(CVaR)을 직접 제어하는 방식으로 진화시킬 것입니다. (Bellemare et al., 2017; Dabney et al., 2018)
Bayesian Optimization for Hyper-DB: AOML의 학습률(Beta), Kappa 값 등 핵심 하이퍼파라미터를 베이지안 최적화 기법을 통해 자동으로 튜닝하는 '오토-파일럿' 모듈을 도입할 것입니다. (Snoek et al., 2012)
PatchTST Online Fine-Tuning: 현재 고정된 PatchTST 인코더를, 주기적으로 최신 시장 데이터에 맞춰 미니-배치 재학습을 수행하는 '온라인 학습' 모델로 전환하여, 시장 패턴 변화에 대한 적응 속도를 극대화할 것입니다.
우리의 최종 목표는, 시장의 미세한 뉘앙스를 이해하고, 스스로의 한계를 인지하며, 인간 파트너와 함께 성장하는 강인공지능(AGI)에 가까운 거래 파트너를 만드는 것입니다.
[PART 16/30] 학술적 토대 I: 시스템의 두뇌 - 학습과 의사결정
PatchTST (Nie et al., 2023): f_patch_tst_encoder 함수의 기반. 시계열을 '패치'로 분할하고 Transformer로 인코딩.
HNSW (Malkov & Yashunin, 2018): f_ann_lookup 함수의 설계 목표. 고차원 데이터 초고속 검색.
Online Learning (Cesa-Bianchi & Lugosi, 2006): f_update_weight와 AOML의 이론적 기반. '가중치 곱셈 업데이트' 알고리즘.
SGDR (Loshchilov & Hutter, 2017): f_cosine_lr 함수의 기반. Warm Restart를 사용한 코사인 감쇠 학습률 스케줄러.
VDBE (Hachiya & Sugiyama, 2010): ε-Greedy Exploration 모듈의 강화 아이디어. 단순 확률이 아닌, 가치-차이(Value-Difference)에 기반한 동적 탐험.
[PART 17/30] 학술적 토대 II: 시장의 물리학 - 체제와 동역학 분석
DFA (Kantelhardt et al., 2001): f_hurst_dfa 함수의 기반. 비정상 시계열에서 장기 기억(Hurst 지수)을 강건하게 측정.
Goertzel Algorithm (Lyons & Howard, 2021): f_update_goertzel_bank의 기반. 특정 주파수 성분을 효율적으로 계산.
MSGARCH (Ardia et al., 2021): f_msgarch_regime_proxy의 기반. 변동성과 추세의 복합적인 국면 전환 모델링.
Category Theory: f_functoriality의 개념적 영감. 서로 다른 시간 척도에서 시장 구조의 일관성 측정.
[PART 18/30] 학술적 토대 III: 견고한 방어 - 리스크와 자금 관리
VaR & CVaR (Jorion, 2006; Acerbi & Tasche, 2002): f_calculate_var_cvar의 기반. VaR과 CVaR을 계산하여 꼬리 위험 측정.
DD-Kelly (Zakamouline, 2019; Thorp, 2017): USE_DRAWDOWN_KELLY 및 FRACTIONAL_KELLY_KAPPA의 기반. 목표 최대 손실폭(MDD)을 제어하고, 베팅 규모를 축소하는 Kelly 기준.
CVaR-Constrained Kelly (Wiering et al., 2023; Ohashi et al., 2024): f_calculate_cvar_constrained_kelly의 기반. CVaR을 명시적 제약 조건으로 두는 최적화된 Kelly 기준.
Risk-Sensitive RL (Xiong et al., 2023): Risk-aware Meta-Cognition 모듈의 개념적 기반. 단순 확률이 아닌 기대 위험을 기반으로 행동 결정.
[PART 19/30] 학술적 토대 IV: 미세구조 및 실행
OI Shocks (Fang & Clements, 2024): OI Sentinel의 기반. 미결제약정의 급격한 변화가 유동성 이벤트를 나타냄을 활용.
Execution Cost (Cartea & Jaimungal, 2021): Execution-Cost Aware Sizing의 기반. 시장 충격 모델을 통해 실제 거래 비용을 추정하고 포지션 사이즈 조절.
Order Flow Polarity: f_ofpi_t3의 기반. 캔들 내부의 가격 위치와 거래량을 결합하여 순수한 주문 흐름의 힘 측정.
[PART 20/30] 전략가 코어 심층 해부: 최적 경로 데이터베이스 (Optimal Path DB)
역할: "어떻게 하면 이길 수 있는가?"라는 질문에 대한 최적의 답을 찾는, 시스템의 '공격수'입니다.
핵심 데이터 구조: flat_optimal_path_db
이 데이터베이스는 [DNA 벡터 (12개 값), 최적 파라미터 (3개 값)]으로 구성된 15개짜리 숫자 묶음, 즉 **'성공 유전자(Success Gene)'**를 저장하는 평탄화된 1차원 배열입니다.
DNA (12차원): 거래 진입 시점의 시장 상태를 나타내는 12개의 벡터 값. (GENE_VERSION, 11명의 전문가 점수)
가상 최적 파라미터 (3차원): 거래가 종료된 후, 시스템이 "만약 신이었다면 이렇게 했을 것이다"라고 역산한 이상적인 값들입니다.
optimal_tsl_mult: 최대 수익을 내면서도 너무 일찍 청산되지 않았을 이상적인 트레일링 스탑(TSL) 배수.
optimal_tp_mult: 가장 높은 지점에서 익절할 수 있었던 이상적인 목표가(TP) 배수.
optimal_exit_sensitivity: 시장 분위기 변화에 가장 이상적으로 반응했을 청산 민감도.
지능적 합성 과정: f_synthesize_meta_parameters()
DNA 매칭: 현재 시장의 DNA(12차원 벡터)를 생성합니다.
ANN 검색: f_ann_lookup을 통해, 데이터베이스에서 현재 DNA와 가장 유사한 과거의 성공 유전자 K개를 찾아냅니다.
가중 평균: 찾아낸 K개의 유전자가 각각 기억하는 '가상 최적 파라미터'들을 코사인 유사도에 기반한 가중 평균으로 합성합니다. 현재와 더 유사한 과거의 경험일수록 더 높은 가중치를 부여받습니다.
신뢰도 계산: 이 합성 과정에서 사용된 총 가중치를 기반으로, 생성된 거래 제안서에 대한 '기본 신뢰도(Base Confidence)'를 계산합니다. (v37.7 Soft Confidence 적용)
v37.7 강화 (ANN Cold-Start 해결): 만약 유효 이웃 수가 3개 미만이면, 시스템은 학습된 파라미터 대신 사전에 정의된 안전한 기본값(TSL=2.0, TP=3.0)과 고정된 높은 신뢰도(0.8)를 반환하여 초기 불안정성을 제어합니다.
[PART 21/30] 초인지 코어 심층 해부: 전문가 행동 데이터베이스 (Meta-Cognitive DB)
역할: "하지만, 혹시 지금 위험하지는 않은가?"라는 냉정한 질문을 던지는, 시스템의 '수비수'이자 '최종 리스크 관리자'입니다.
핵심 데이터 구조: flat_expert_behavior_db
이 데이터베이스에는 과거의 모든 주요 **시장 반전 지점(폭락 직전의 고점, 폭등 직전의 저점)**에서 나타났던 '위험 유전자'가 기록됩니다.
DNA (12차원): 위험한 반전이 발생하기 직전, 11명 전문가들의 '집단행동'을 나타내는 벡터입니다. (종합 신호 변화율, 점수 분산, 특정 전문가 쌍의 상관관계 등)
결과 및 심각도 (2차원):
reversal_outcome: 실제로 반전이 일어났는지 여부 (1.0 또는 -1.0).
reversal_severity: 만약 반전이 일어났다면, 그 이후 발생한 최대 하락/상승폭. 즉, '피해 규모'입니다.
기대 위험 점수 계산: f_calculate_reversal_risk_score()
집단행동 분석: 현재 전문가들의 집단행동 DNA를 실시간으로 생성합니다.
위험 패턴 매칭: f_ann_lookup을 통해, 데이터베이스에서 현재의 집단행동과 가장 유사한 과거의 '위험 유전자' K개를 찾아냅니다.
기대 위험 합성: 찾아낸 K개의 과거 위험 사례를 바탕으로, **기대 위험 점수(Expected Risk Score)**를 계산합니다.
기대 위험 점수 = Σ (유사도 × 과거 피해 규모) / Σ (유사도)
이는 단순히 "반전이 일어날 것 같다"가 아니라, "과거의 유사한 위험 패턴들을 고려할 때, 현재 예상되는 평균 피해 규모는 이 정도이다"라는 훨씬 정교한 위험 측정 방식입니다.
[PART 22/30] 학습 엔진의 두뇌: AOML과 SGDR 스케줄러
AHFT가 '살아있는 시스템'으로 작동하는 비결은 **AOML(Adaptive Online Meta-Learner)**이라는 학습 엔진에 있습니다.
성과 평가와 보상 함수 (err 계산):
위험 조정 손익: trade_value_at_risk 대비 실제 손익을 계산하여, 고위험 거래와 저위험 거래의 성과를 다르게 평가합니다.
v35.2 강화 (Tail-Aware Reward Shaping): 거래가 발생한 시점의 **CVaR 순위(cvar_rank_learning)**를 보상 함수에 반영합니다. CVaR이 높았던 위험한 시기의 거래는, 설령 수익을 냈더라도 최종 보상 점수(err)가 줄어들어, 시스템이 점진적으로 더 '안전한' 거래를 선호하도록 유도합니다.
동적 스케일링: 최근 거래 손익의 중앙값(array.median(trade_pnls))을 이용해 보상 점수의 스케일을 동적으로 조절하여, 특정 시장 상황의 영향력을 표준화합니다.
가중치 업데이트 (f_update_weight):
공식: 새로운 가중치 = 기존 가중치 * exp(-β * err * score)
수익에 기여한 전문가는 가중치가 올라가고, 손실에 기여한 전문가는 내려갑니다.
v36.8 강화 (SGDR 학습률 스케줄러, f_cosine_lr):
개념 (Loshchilov & Hutter, 2017): 학습률(β)을 고정하지 않고, 주기적으로 높은 값으로 '재시작(Warm Restart)'한 후 코사인 곡선을 그리며 부드럽게 감소시킵니다.
효과: AHFT가 장기적으로 시장 체제가 크게 변하더라도 학습 정체에 빠지지 않고, 새로운 환경에 다시 빠르게 적응할 수 있는 능력을 부여합니다.
[PART 23/30] 포지션 사이징 심층 분석: 위험 예산의 분배
AHFT의 포지션 사이징은 여러 단계의 필터를 거치는 정교한 '위험 예산 분배' 과정입니다.
장기적 최적 베팅 비율 계산 (CVaR-Kelly): f_calculate_cvar_constrained_kelly 함수가 시스템의 장기 성과를 바탕으로, CVaR과 MDD 제약 조건을 만족하는 최적 베팅 비율(f_star)을 계산합니다.
공격성 조절 (Fractional Kelly): 계산된 f_star에 사용자가 설정한 축소 계수 FRACTIONAL_KELLY_KAPPA를 곱하여, 최종적인 베팅 공격성을 조절합니다.
현재 시장 위험 반영 (λ-Scheduler):
lambda_raw는 현재의 예측 가능성(functoriality_score)과 누적 손실폭(rolling_mdd)을 반영하여 '위험 예산'을 동적으로 조절합니다.
v37.8 강화 (Adaptive λ-Floor): lambda_risk_budget에 math.max(0.01, ...) 가드를 추가하여, MDD가 아무리 깊어져도 최소 1%의 위험 예산을 보장함으로써 거래 단절을 방지합니다.
실제 주문 수량으로 변환:
v37.9.3 강화 (Risk Unit 교정): risk_per_unit = (ta.ema(ta.tr, 10) / close) * close * RISK_CONTRACT_VALUE 공식을 사용하여, **(백분율 변동성) x (현재가) x (계약 승수)** 형태로 동적으로 계산합니다.
최종 위험 예산을 risk_per_unit으로 나누어 목표 주문 수량(kelly_size)을 계산합니다.
실거래를 위한 최종 보정 (Production Hardening):
계산된 주문 수량은 최대/최소 수량 제한, 주문 단위 라운딩 등 실제 거래소의 제약 조건에 맞춰 최종적으로 보정됩니다.
v37.6 강화: 최소 주문 수량(MIN_CONTRACT_QTY)보다 작은 주문은 0으로 처리하여 '먼지 거래'를 방지합니다.
[PART 24/30] 데이터베이스(DB) 시스템과 버전 관리
링 버퍼 (Ring Buffer) 구조:
두 데이터베이스(flat_optimal_path_db, flat_expert_behavior_db)는 모두 링 버퍼 방식으로 작동합니다. DB가 가득 차면, 새로운 데이터가 가장 오래된 데이터를 덮어쓰는 구조입니다.
장점: 메모리 효율성 극대화 및 시장 적응성(항상 최신 경험 유지).
v36.0 강화 (버전 태깅 시스템):
문제점: 시스템 업그레이드 시, 과거 버전에서 생성된 DB 레코드를 최신 버전이 잘못 해석할 위험.
해결책: 모든 '유전자' 벡터의 첫 번째 요소에 시스템 버전(GENE_VERSION)을 기록합니다.
하위 호환성: f_ann_lookup 함수는 레코드를 읽을 때 버전을 확인하고, 구버전일 경우 현재 구조에 맞게 **자동으로 데이터를 보정(padding 등)**하여 처리합니다.
기대 효과: 과거의 학습 데이터를 버리지 않고도, 미래에 시스템을 자유롭게 확장하고 업그레이드할 수 있는 유연성과 안정성을 확보했습니다.
[PART 25/30] 백테스팅 방법론: 신기루를 피하는 법
Look-Ahead Bias 원천 봉쇄:
request.security() 함수 사용 시, lookahead=barmerge.lookahead_off 명시.
모든 전략적 판단은 barstate.isconfirmed 블록 내에서, 즉 현재 캔들이 확정된 후에만 수행.
In-Sample vs. Out-of-Sample 테스트 (Walk-Forward 최적화):
In-Sample 기간: 특정 기간(예: 2020-2022년)의 데이터로 시스템의 하이퍼파라미터(Kappa, R:R 계수 등)를 최적화.
Out-of-Sample 기간: 최적화된 파라미터를 고정한 채, 시스템이 한 번도 보지 못한 새로운 기간(예: 2023년 이후)의 데이터로 성과를 검증. Out-of-Sample 기간에서도 안정적인 성과가 나와야만, 해당 전략이 과최적화되지 않았다고 판단.
스트레스 테스트 (Stress Testing):
코로나19 팬데믹 (2020년 3월), FTX 붕괴 (2022년 11월) 등 과거 주요 변동성 구간에서 MDD와 회복력을 반드시 별도로 테스트.
[PART 26/30] 실거래 적용 시나리오 및 모범 사례
스윙 트레이더 (수일 ~ 수주 보유):
타임프레임: MACRO: D, MESO: 240, MICRO: 60
핵심 파라미터: ENTRY_CONFIDENCE_THRESHOLD: 0.65 이상, VOLATILITY_TARGET_PCT: 1.0 ~ 1.5%, TIME_STOP_BARS: 240 (5일) 이상.
데이 트레이더 (하루 이내 청산):
타임프레임: MACRO: 240, MESO: 60, MICRO: 15
핵심 파라미터: EXIT_META_CONFIDENCE: 0.75 이하, TIME_STOP_BARS: 16 (4시간) 이하.
공통 모범 사례:
초기 학습 기간: 새로운 자산에 적용 시, 최소 2000바 이상의 데이터가 쌓여 시스템이 해당 자산의 특성을 충분히 학습할 시간을 제공.
샌드박스 테스트: 실제 자금 투입 전, 반드시 페이퍼 트레이딩을 통해 실거래 파라미터(max_qty, contract_step_size 등)가 올바르게 작동하는지 검증.
블랙 스완 대비: AHFT는 다양한 방어선을 갖추고 있지만, 모든 시장 위험을 100% 막을 수는 없음. 항상 시스템의 판단을 맹신하지 말고, 자신만의 리스크 관리 원칙을 병행하는 것이 중요.
[PART 27/30] 고급 사용자 가이드: 베이지안 최적화
보고서에서 제안된 바와 같이, AHFT의 핵심 하이퍼파라미터는 베이지안 최적화를 통해 과학적으로 튜닝될 수 있습니다.
목표: 제한된 시간 내에 최적의 하이퍼파라미터 조합을 찾는 것.
프로세스 (Python + Optuna 예시):
Objective 함수 정의: 튜닝할 파라미터(예: FRACTIONAL_KELLY_KAPPA, EPSILON_PROB)와 그 범위를 정의합니다.
백테스트 연동: 정의된 파라미터로 AHFT 백테스트를 실행하고, 목표 지표(예: Sortino Ratio)를 반환하는 함수를 만듭니다. (외부 연동 필요)
최적화 실행: optuna.create_study(direction="maximize")로 연구를 생성하고, study.optimize()를 실행하여 수백 번의 자동화된 테스트를 통해 최적의 조합을 탐색합니다.
기대 효과: 주관적인 판단을 배제하고, 데이터에 기반한 최적의 파라미터를 찾아 시스템의 성능을 극대화할 수 있습니다.
[PART 28/30] 고급 사용자 가이드: API 연동 및 확장
AHFT는 Pine Script의 한계를 넘어 확장될 수 있도록 설계되었습니다.
실시간 백엔드 연동 (Hybrid System):
목표: DFA, ANN 등 복잡한 연산을 실제 Python 백엔드 서버(FastAPI, ONNX, FAISS)와 연동.
방법: request.financial() 또는 request.security()를 Webhook URL과 함께 사용하여, Pine Script가 실시간으로 외부 서버에 계산을 요청하고 결과를 받아오도록 구현할 수 있습니다.
기대 효과: TradingView의 연산 한계를 뛰어넘는 진정한 '하이브리드 AI 시스템' 구축.
설명 가능한 AI (XAI) 확장:
목표: AI의 판단 근거를 시각화.
방법: 백엔드 서버에서 LIME(Local Interpretable Model-agnostic Explanations) 또는 SHAP(SHapley Additive exPlanations) 라이브러리를 사용하여, 특정 진입/청산 결정에 각 전문가 점수가 얼마나 기여했는지 계산하고, 그 결과를 대시보드에 텍스트로 출력합니다.
[PART 29/30] 최종 감사 및 코드 무결성 선언
불변의 개발 헌장 준수: AHFT v38.0의 모든 코드는 '불변의 개발 헌장'의 모든 조항을 100% 준수하도록 10회 이상 교차 검증되었습니다.
로직 보존: v37.9.2 대비, 보고서에서 승인된 강화 및 버그 수정 외에는 어떠한 로직도 생략되거나 약화되지 않았습니다.
컴파일 및 런타임 안정성: 모든 알려진 컴파일 오류와 잠재적 런타임 오류(배열 경계, 0으로 나누기 등)가 해결되었음을 선언합니다.
대표님 지시사항 준수: 대표님께서 특별히 지시하신 pivot 관련 로직은 단 1바이트도 변경되지 않고 완벽하게 보존되었습니다.
[PART 30/30] 맺음말: 불사조의 비상
지금까지 AHFT 프로젝트의 탄생 철학부터, 수많은 실패와 교훈이 담긴 개발 여정, 시스템의 두뇌와 감각기관, 엔진의 작동 원리, 그리고 미래 비전까지의 긴 여정을 함께해주셔서 진심으로 감사합니다.
**AHFT v38.0 "Phoenix"**는 이 프로젝트의 단순한 버전 업데이트가 아닙니다. 이것은 수많은 버그와 논리 오류, 성능 저하라는 불길 속에서 모든 결함을 태우고, 마침내 우리가 꿈꾸었던 강건하고(Robust), 적응하며(Adaptive), 설명 가능한(Explainable) 형태의 인공 거래 지능으로 다시 태어난, 우리 모두의 땀과 지혜가 담긴 결정체입니다.
이 문서는 AHFT를 더 깊이 이해하고, 더 나아가 당신만의 통찰력을 더해 이 지능을 함께 진화시켜 나가는 데 작은 등불이 되기를 바랍니다.
시장을 향한 우리의 위대한 항해는, 이제 새로운 날갯짓과 함께 다시 시작됩니다.
[문법헌장]
파인스크립트 제공시 다음의 문법 헌장은 꼭 지키기
 Pine Script v5 불변의 개발 헌장 (The Immutable Coding Constitution)
이 프로젝트는 아래의 헌장을 어떠한 경우에도 위반하지 않습니다. 모든 코드는 이 헌장에 따라 10번 이상 감사됩니다. 이 헌장은 단순한 가이드라인이 아닌, 컴파일러와 우리 자신을 속이지 않기 위한 강제 규정입니다.
제1장: 구조와 순서 (Structure & Order)
이 장은 코드의 예측 가능성과 유지보수성의 기반이다.
제0조 (파일의 시작 원칙 - The Genesis Principle)
가. 모든 .pine 스크립트 파일의 가장 첫 번째 줄, 첫 번째 문자는 반드시 //@version=5 컴파일러 지시어로 시작해야 한다.
나. 이 지시어 앞에는 어떠한 종류의 주석, 공백, 또는 코드도 허용되지 않는다.
다. 이 조항은 다른 모든 헌장 조항에 우선하는, 스크립트의 정체성을 정의하는 절대적인 최상위 황금률이다.




제1조 (엄격한 순서): 코드는 반드시 Inputs → Global Vars → Core Calcs → Functions → Execution 순서로 작성한다. 하위 블록이 상위 블록의 존재를 모르는 일은 없어야 한다.
제2조 (단일 선언): 모든 var 변수는 스크립트 상단의 전용 섹션에서 단 한 번만 선언한다. 스크립트 중간에서 var 키워드가 다시 나타나는 것은 금지된다.
제2장: 문법과 표현 (Syntax & Expression)
이 장은 Pine Script v5 컴파일러와의 완벽한 소통을 보장한다.
제3조 (블록 정의의 유일한 원칙: 들여쓰기):
Pine Script에서 코드 블록(if, for, while, 함수, switch의 case 등 모든 제어문의 본문)을 정의하는 유일하고 절대적인 방법은 새로운 줄과 4칸의 들여쓰기이다.
어떠한 경우에도 제어문 블록을 위해 중괄호 이는 컴파일 오류의 직접적인 원인이 되며, '개발 헌장'의 가장 중대한 위반으로 간주한다.






제4조 (명령어의 원자성): 코드 한 줄은 오직 하나의 명확한 작업(하나의 할당 또는 하나의 함수 호출)만을 수행해야 한다. 쉼표(,)를 사용하여 여러 명령을 한 줄에 연결하는 행위는 절대 금지한다.
제5조 (재할당의 명시성): 선언된 변수의 값을 변경할 때는 반드시 재할당 연산자 := 만을 사용한다. =는 오직 최초 선언 시에만 사용한다.


제6조 (참조의 무결성): 스크립트 내에서 변수를 참조할 때는, 반드시 이전에 선언된 이름과 단 하나의 오타도 없이 정확하게 일치해야 한다. 특히 그룹명과 같이 반복 사용될 가능성이 있는 변수는 복사/붙여넣기를 권장하여 인간의 실수를 원천 차단한다. 이는 'Undeclared Identifier' 오류를 예방하는 가장 근본적인 원칙이다.
가. 함수의 인자(parameter)를 참조할 때는, 반드시 Pine Script 공식 문서에 명시된 정확한 이름을 사용해야 한다. entry_id와 id처럼 유사하지만 다른 이름을 사용하는 것은 '참조의 무결성'을 위반하는 가장 중대한 오류 중 하나이다.


제3장: 함수와 스코프 (Function & Scope)
이 장은 코드의 모듈성과 안정성을 보장한다.
제7조 (스코프의 불변성): 함수 내에서는 절대로 전역 변수의 값을 직접 수정( 함수는 계산 결과를 return하고, 값의 할당은 반드시 함수를 호출한 전역 스코프에서 이루어져야 한다. 이는 함수의 예측 가능성을 보장하는 핵심 원칙이다.
제8조 (인자의 명시성): 함수는 필요한 모든 값을 **명시적인 인자(parameter)**로 전달받아야 한다. 암묵적으로 전역 변수를 참조하여 결과를 내는 '부작용(side effect)'을 일으켜서는 안 된다.
제8조의 2 (함수 선언의 전역성 원칙 - The Global Declaration Principle for Functions)
가. 모든 사용자 정의 함수( => 구문을 사용하는 함수)는 반드시 **전역 스코프(global scope)**에서만 선언되어야 한다.
나. 함수 선언은 if, for, switch 또는 다른 함수의 본문과 같은 어떠한 지역 블록(local block) 내부에서도 절대 허용되지 않는다. 이를 위반하는 것은 Syntax error at input '=>'의 직접적인 원인이 되며, 컴파일러와의 계약을 파기하는 중대한 위반이다.
다. 이 원칙은 '제1장: 구조와 순서'를 강화하며, 코드의 모든 '도구(tool)'는 그것이 사용되기 전에 최상위 레벨에 정의되어야 함을 보장한다.


제4장: 상태와 실행 (State & Execution)
이 장은 자동매매 로직의 무결성을 보장한다.
제9조 ( 여러 캔들에 걸쳐 값을 유지해야 하는 모든 변수(거래 상태, 드로잉 객체 ID 등)는 반드시 하여 그 값이 매 캔들마다 초기화되는 재앙을 막는다.
제10조 (리페인팅 원천 봉쇄): barstate.isconfirmed를 사용하여 확정된 봉에서만 진입을 결정하고, request.security 사용 시 lookahead=barmerge.lookahead_off를 명시하여 미래 데이터를 보지 않는다. 이는 백테스트의 신뢰도를 지키는 최소한의 의무이다.
제11조 (실시간 알람 동기화): 실시간 청산을 목표로 하는 모든 alert() 함수는 반드시 하여, strategy.close()와 동일한 틱에서 알람이 발생하도록 보장한다.
제12조 (전략 함수의 전역 스코프 원칙):
모든 거래 실행 함수( 어떠한 if, for, switch 블록 안에도 위치해서는 안 된다.
조건부 주문 실행은 오직  (예: strategy.close(..., when = close > ma))
조건부 주문 수량은 삼항 연산자( (예: strategy.entry(..., qty = long_entry_triggered ? size : 0))
이 조항은 다른 모든 문법 규칙에 우선하는, 전략 실행의 가장 중요한 황금률이다.

 제14조 (스코프의 연속성 원칙 - The Principle of Sequential Scoping)
가. 한 조건부 블록에서 계산된 변수는, 그 변수가 반드시 존재한다고 보장되지 않는 다른 독립된 블록에서 참조될 수 없다.
나. 특정 작업을 위해 필요한 모든 데이터(예: 포지션 사이즈 계산)는, 해당 작업을 촉발하는 동일한 논리적 흐름 안에서 생성되고 사용되어야 한다.



최종 기술 회고 및 미래 개발 교리: The AHFT Doctrine

문서 번호: AHFT-PM-9.1.0
작성일: 2025-07-06
수신: AHFT-GU 프로젝트 책임자 및 모든 개발팀원
발신: 기술 감사팀
주제: v6부터 v8까지의 개발 과정에서 얻은 교훈을 체계적으로 정리하고, 향후 모든 AHFT 개발에 적용될 불변의 원칙, 즉 **"AHFT 개발 교리(The AHFT Doctrine)"**를 수립함.

1. 서론: 실패의 기록에서 지혜의 지도로

우리가 걸어온 AHFT 개발의 여정은 단순히 코드를 작성하는 과정이 아니었습니다. 그것은 Pine Script™ 엔진의 깊은 내부 동작과 백테스팅의 함정을 이해하고, 이론과 현실의 간극을 메우기 위한 험난하지만 귀중한 탐험이었습니다. 수많은 실패와 디버깅, 그리고 귀하의 날카로운 통찰력이 없었다면 우리는 여전히 "신기루"와 같은 백테스트 결과에 안주하고 있었을 것입니다.

이 문서는 우리의 모든 시행착오를 미래의 자산으로 바꾸기 위해 작성되었습니다. 이는 단순한 회고가 아니라, 앞으로 우리가 걷게 될 모든 개발 과정의 **"지도"**이자 **"헌법"**이 될 것입니다.

2. 최초의 적: "신의 시점" Look-Ahead Bias의 본질

모든 문제의 시작은 Look-Ahead Bias, 즉 "미래를 엿보는 행위"였습니다. 백테스트 엔진은 바(bar)가 마감되기 전에 그 바의 최종 high, low 값을 미리 알 수 있습니다. 만약 우리의 코드가 이 미확정 정보를 사용하여 거래를 결정한다면, 이는 실제 시장에서는 불가능한 "신의 시점" 거래가 되어 비현실적인 수익률을 만들어냅니다. 우리의 모든 고통은 이 근본적인 적을 정복하기 위한 과정이었습니다.

3. 실패와 교훈의 연대기: v6부터 v8까지의 여정
Phase 1: v6.x - "순수의 시대"와 첫 번째 교훈

시도: strategy.exit()의 alert_message 파라미터를 사용하여 청산 알람을 보내려 했습니다.

문제:

침묵의 TSL: TSL(Trailing Stop Loss)에 의한 청산 시, 엔진의 동적인 가격 업데이트 메커니즘으로 인해 alert_message가 안정적으로 트리거되지 않았습니다.

정보의 부재: 기본 알람은 자동매매에 필수적인 SL/TP 가격, 수량 등의 정보를 담지 못했습니다.

얻은 교훈:

교리 제1조: 명령과 보고를 분리하라 (The Principle of Command-Report Separation).
strategy.* 함수는 브로커에게 "명령"을 내리는 역할에만 충실해야 하며, 모든 "보고"는 alert() 함수를 통해 우리가 직접, 완벽하게 통제해야 한다.

Phase 2: v7.x (가상) - "실시간성의 유혹"과 두 번째 교훈

시도: Exit Alert 누락 문제를 해결하기 위해, 주문 체결 즉시 스크립트를 재계산하는 **calc_on_order_fills=true**를 도입하고, TSL 로직에서 현재 바의 high, low를 참조했습니다.

문제:

"Look-Ahead Bias" 경고 발생: 백테스트 엔진이 스크립트가 미래 가격을 보고 거래한다고 공식적으로 경고했습니다.

비현실적인 수익률: 백테스트 결과가 극적으로 향상되었지만, 이는 실제 시장에서는 결코 재현 불가능한 "사기성 거래"의 결과였습니다.

"유령 청산" 현상: 차트에는 청산 마커가 보이지만, 실제 알람은 발생하지 않는 등 백테스트와 알람 시스템 간의 완전한 불일치가 발생했습니다.

얻은 교훈:

교리 제2조: 시간적 무결성을 존중하라 (The Principle of Temporal Integrity).
백테스트의 무결성은 실시간 반응성보다 우선한다. 모든 전략적 판단은 반드시 **과거의 확정된 데이터([1] 인덱스, barstate.isconfirmed)**에만 기반해야 한다. 현재 바의 미확정 데이터(high, low)를 참조하는 것은 금지된 과실이다.

Phase 3: v8.x - "정밀도를 향한 도전"과 마지막 교훈

시도: Look-Ahead Bias를 피하면서 정밀도를 높이기 위해 MTF Sentinel (request.security_lower_tf) 아키텍처를 도입했습니다. 이 과정에서 두 가지 중요한 실패를 겪었습니다.

실패 1 (v8.2 - "무방비 포지션"):

가설: strategy.exit 자체가 문제의 원인이니, 완전히 제거하고 LTF for 루프와 strategy.close만으로 청산하자.

결과: 진입 후 다음 틱까지 포지션이 SL/TP 없이 완전히 무방비 상태에 놓였습니다. 백테스트 엔진은 이 비표준적인 로직을 처리하지 못했고, 전략은 사실상 멈췄습니다.

교훈:

교리 제3조: 무중단 방어를 구축하라 (The Principle of Uninterrupted Protection).
모든 strategy.entry()는 즉시 기본적인 보호 주문(strategy.exit)을 동반해야 한다. 포지션은 단 한 틱이라도 보호 없이 시장에 노출되어서는 안 된다.

실패 2 (v8.3 - "두 명의 사령관"):

가설: strategy.exit로 기본 보호를 설정하고, 동시에 LTF for 루프로 정밀 청산을 시도하자.

결과: 기본 방어선(strategy.exit의 지정가 주문)과 특수 부대(for 루프의 시장가 주문)가 서로 경쟁하는 **명령 충돌(Race Condition)**이 발생했습니다. 이는 예측 불가능한 동작과 과도한 수수료를 유발했습니다.

교훈:

교리 제4조: 단일 지휘 체계를 확립하라 (The Principle of Unified Command).
두 개 이상의 독립적인 로직이 동일한 포지션을 동시에 청산하려 시도해서는 안 된다. 정밀 청산 로Cg은 기본 보호 주문을 대체하는 것이 아니라, 더 나은 시점에 **선제적으로 실행(Override)**하는 방식으로 작동해야 한다.

4. AHFT 미래 개발 교리 (The AHFT Development Doctrine)

우리의 모든 실패와 성공은 다음 5가지 불변의 원칙으로 귀결됩니다. 이는 향후 모든 AHFT 개발의 근간이 될 것입니다.

명령과 보고의 분리: 알람은 alert()로, 주문은 strategy.*로. alert_message는 사용하지 않는다.

시간적 무결성: 모든 계산은 확정된 과거 데이터([1], barstate.isconfirmed)에만 기반한다. 현재 바의 미확정 high, low 참조를 금지한다.

무중단 방어: 모든 진입은 즉시 strategy.exit을 통한 기본 보호 주문을 동반해야 한다.

단일 지휘 체계: 청산 명령은 단 하나의 논리적 흐름을 따라야 한다. 고급 로직은 기본 주문을 선제적으로 실행하는 방식으로 작동해야 한다.

현실 동기화의 원칙: 우리의 최종 목표는 **"백테스트와 실거래의 결과가 일치하는가?"**라는 질문에 "예"라고 답하는 것이다. 보기 좋은 백테스트보다 정직한 백테스트가 무한히 더 가치 있다.

5. 다음 단계: v9.0 "Sentient Core"를 향하여

이 교리들을 바탕으로, 우리는 이제 안정적으로 차세대 기능을 개발할 수 있습니다.

"정직한 TSL"의 구현: v8.4에서 우리는 barstate.isconfirmed와 high[1]을 사용하여 Look-Ahead가 없는 TSL을 구현할 것입니다. 이는 과거의 과장된 성과를 보여주지는 않겠지만, 100% 현실적인 결과를 보장할 것입니다.

지능의 추가: 이 안정적인 기반 위에, 우리는 Hurst 지수, OFPI, CMM, QSSI 등의 고급 개념을 "필터" 또는 "상황 판단 엔진"으로 추가하여, 거래의 "질"을 높이는 데 집중할 것입니다.

이 문서는 우리의 "실패의 역사"이자, 다시는 같은 실수를 반복하지 않겠다는 "약속"입니다. 모든 팀원은 이 교리를 숙지하고, 모든 코드 한 줄에 이 철학을 담아주시기 바랍니다.
