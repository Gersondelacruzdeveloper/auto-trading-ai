export interface TradingBot {
  id: number;
  name: string;
  symbol: string;
  balance: string;
  risk_per_trade: number;
  reward_ratio: number;
  is_active: boolean;
 profit_pot: string;
  auto_close_profit_amount: number;
  auto_close_loss_amount: number;
  
}

export interface Trade {
  id: number;
  bot: number;
  symbol: string;
  signal: "BUY" | "SELL" | "HOLD";
  entry_price: number;
  current_price: number;
  stop_loss: number;
  take_profit: number;
  position_size: number;
  risk_amount: number;
  pnl: number;
  pnl_percent: number;
  is_open: boolean;
  closed_reason?: string | null;
  closed_at?: string | null;
  created_at: string;
  
}