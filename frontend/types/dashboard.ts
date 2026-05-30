/**
 * OPay Pulse Trader Dashboard API Types
 * TypeScript interfaces for trader dashboard frontend
 */

// ============================================================
// Trader Profile
// ============================================================

export interface TraderProfile {
  trader_id: number;
  phone_number: string;
  credit_score: number;
  streak_count: number;
  joined_date: string;
  last_active: string | null;
}

// ============================================================
// Transaction
// ============================================================

export interface Transaction {
  id: number;
  type: "income" | "expense";
  amount: number;
  category: string;
  description?: string;
  logged_at: string;
}

export interface TraderTransactionsResponse {
  trader_id: number;
  data: Transaction[];
  total: number;
  limit: number;
  offset: number;
}

// ============================================================
// Trader Statistics
// ============================================================

export interface TraderStats {
  trader_id: number;
  period: string;
  total_transactions: number;
  income_transactions: number;
  expense_transactions: number;
  total_income: number;
  total_expense: number;
  net_balance: number;
  average_transaction: number;
}

// ============================================================
// Trader Ranking
// ============================================================

export interface RankedTrader {
  rank: number;
  trader_id: number;
  phone_number: string;
  credit_score: number;
  total_volume: number;
  transaction_count: number;
  streak_count: number;
}

export interface TraderRankingResponse {
  data: RankedTrader[];
  sort_by: "volume" | "credit_score" | "transactions";
  total_traders: number;
  returned: number;
}

// ============================================================
// Dashboard API Client
// ============================================================

export class DashboardAPI {
  private baseUrl: string;

  constructor(baseUrl: string = "/api") {
    this.baseUrl = baseUrl;
  }

  /**
   * Get trader profile information
   */
  async getTraderProfile(traderId: number): Promise<TraderProfile> {
    const response = await fetch(
      `${this.baseUrl}/dashboard/trader/${traderId}`
    );
    if (!response.ok) throw new Error("Failed to fetch trader profile");
    return response.json();
  }

  /**
   * Get trader's transactions
   */
  async getTraderTransactions(
    traderId: number,
    limit: number = 20,
    offset: number = 0,
    txType?: "income" | "expense"
  ): Promise<TraderTransactionsResponse> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });
    if (txType) params.append("tx_type", txType);

    const response = await fetch(
      `${this.baseUrl}/dashboard/trader/${traderId}/transactions?${params}`
    );
    if (!response.ok) throw new Error("Failed to fetch transactions");
    return response.json();
  }

  /**
   * Get trader statistics
   */
  async getTraderStats(
    traderId: number,
    period: "7d" | "30d" | "90d" | "1y" = "30d"
  ): Promise<TraderStats> {
    const response = await fetch(
      `${this.baseUrl}/dashboard/trader/${traderId}/stats?period=${period}`
    );
    if (!response.ok) throw new Error("Failed to fetch trader stats");
    return response.json();
  }

  /**
   * Get traders ranking
   */
  async getTradersRanking(
    limit: number = 10,
    sortBy: "volume" | "credit_score" | "transactions" = "volume"
  ): Promise<TraderRankingResponse> {
    const response = await fetch(
      `${this.baseUrl}/dashboard/traders/ranking?limit=${limit}&sort_by=${sortBy}`
    );
    if (!response.ok) throw new Error("Failed to fetch traders ranking");
    return response.json();
  }
}

