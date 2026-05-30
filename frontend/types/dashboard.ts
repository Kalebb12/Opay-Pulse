/**
 * OPay Pulse Dashboard API Types
 * Auto-generated TypeScript types for frontend integration
 */

// ============================================================
// Metric Cards & Summary
// ============================================================

export interface MetricsSummary {
  total_traders: number;
  active_traders_today: number;
  total_transactions: number;
  total_volume: number;
  average_transaction: number;
  average_credit_score: number;
}

// ============================================================
// Transaction Analytics
// ============================================================

export interface TransactionAnalytics {
  total: number;
  income: number;
  expense: number;
  net: number;
  success_rate: number;
  categories: Record<string, number>;
}

// ============================================================
// Transaction Trend
// ============================================================

export interface DailyTransaction {
  date: string;
  income: number;
  expense: number;
  net: number;
}

export interface TransactionTrendResponse {
  data: DailyTransaction[];
}

// ============================================================
// Category Distribution
// ============================================================

export interface CategoryData {
  name: string;
  value: number;
  percentage: number;
}

export interface CategoryDistributionResponse {
  data: CategoryData[];
}

// ============================================================
// User Growth
// ============================================================

export interface DailyGrowth {
  date: string;
  new_traders: number;
  active_traders: number;
  cumulative: number;
}

export interface UserGrowthResponse {
  data: DailyGrowth[];
}

// ============================================================
// Top Traders
// ============================================================

export interface TopTrader {
  rank: number;
  trader_id: number;
  phone_number: string;
  total_volume: number;
  transaction_count: number;
  credit_score: number;
  streak_count: number;
}

export interface TopTradersResponse {
  data: TopTrader[];
}

// ============================================================
// Credit Score Distribution
// ============================================================

export interface CreditScoreBucket {
  range: string;
  count: number;
}

export interface CreditScoreDistributionResponse {
  data: CreditScoreBucket[];
}

// ============================================================
// Income vs Expense
// ============================================================

export interface IncomeExpenseData {
  date: string;
  income: number;
  expense: number;
}

export interface IncomeVsExpenseResponse {
  data: IncomeExpenseData[];
}

// ============================================================
// Transactions
// ============================================================

export interface TransactionData {
  id: number;
  trader_id: number;
  trader_phone: string;
  type: "income" | "expense";
  amount: number;
  category: string;
  description?: string;
  logged_at: string;
}

export interface TransactionsResponse {
  data: TransactionData[];
  total: number;
  limit: number;
  offset: number;
}

// ============================================================
// Trader Performance
// ============================================================

export interface TraderPerformance {
  trader_id: number;
  phone_number: string;
  total_transactions: number;
  total_volume: number;
  average_transaction: number;
  income_transactions: number;
  expense_transactions: number;
  income_total: number;
  expense_total: number;
  credit_score: number;
  streak_count: number;
  joined_date: string;
}

// ============================================================
// Period Comparison
// ============================================================

export interface PeriodStats {
  transactions: number;
  volume: number;
  average_transaction: number;
}

export interface PeriodChange {
  transactions: number;
  volume: number;
  average_transaction: number;
}

export interface PeriodComparisonResponse {
  current_period: PeriodStats;
  previous_period: PeriodStats;
  change: PeriodChange;
}

// ============================================================
// Query Parameters
// ============================================================

export type Period = "7d" | "30d" | "90d" | "1y";
export type SortBy = "volume" | "score" | "streak" | "date" | "amount";
export type Order = "asc" | "desc";
export type GroupBy = "daily" | "weekly" | "monthly";
export type TransactionType = "income" | "expense" | "all";

// ============================================================
// API Client Configuration
// ============================================================

export interface ApiConfig {
  baseUrl: string;
  timeout?: number;
  headers?: Record<string, string>;
}

// ============================================================
// API Client Class
// ============================================================

export class DashboardApiClient {
  private baseUrl: string;

  constructor(config: ApiConfig) {
    this.baseUrl = config.baseUrl;
  }

  /**
   * Get overall KPI metrics
   */
  async getMetricsSummary(): Promise<MetricsSummary> {
    return this.get<MetricsSummary>("/api/metrics/summary");
  }

  /**
   * Get transaction analytics for a period
   */
  async getTransactionMetrics(
    period: Period = "30d",
    category?: string
  ): Promise<TransactionAnalytics> {
    const params = new URLSearchParams();
    params.append("period", period);
    if (category) params.append("category", category);
    return this.get<TransactionAnalytics>("/api/metrics/transactions", params);
  }

  /**
   * Get transaction trends over time
   */
  async getTransactionTrend(
    period: Period = "7d",
    groupBy: GroupBy = "daily"
  ): Promise<TransactionTrendResponse> {
    const params = new URLSearchParams();
    params.append("period", period);
    params.append("group_by", groupBy);
    return this.get<TransactionTrendResponse>(
      "/api/analytics/transaction-trend",
      params
    );
  }

  /**
   * Get category distribution
   */
  async getCategoryDistribution(
    period: Period = "30d"
  ): Promise<CategoryDistributionResponse> {
    const params = new URLSearchParams();
    params.append("period", period);
    return this.get<CategoryDistributionResponse>(
      "/api/analytics/category-distribution",
      params
    );
  }

  /**
   * Get user growth metrics
   */
  async getUserGrowth(
    period: Period = "30d",
    groupBy: GroupBy = "daily"
  ): Promise<UserGrowthResponse> {
    const params = new URLSearchParams();
    params.append("period", period);
    params.append("group_by", groupBy);
    return this.get<UserGrowthResponse>("/api/metrics/user-growth", params);
  }

  /**
   * Get top traders
   */
  async getTopTraders(
    limit: number = 10,
    sortBy: SortBy = "volume",
    period: Period = "30d"
  ): Promise<TopTradersResponse> {
    const params = new URLSearchParams();
    params.append("limit", limit.toString());
    params.append("sort_by", sortBy);
    params.append("period", period);
    return this.get<TopTradersResponse>("/api/traders/top", params);
  }

  /**
   * Get credit score distribution
   */
  async getCreditScoreDistribution(): Promise<CreditScoreDistributionResponse> {
    return this.get<CreditScoreDistributionResponse>(
      "/api/analytics/credit-score-distribution"
    );
  }

  /**
   * Get income vs expense comparison
   */
  async getIncomeVsExpense(
    period: Period = "7d"
  ): Promise<IncomeVsExpenseResponse> {
    const params = new URLSearchParams();
    params.append("period", period);
    return this.get<IncomeVsExpenseResponse>(
      "/api/analytics/income-vs-expense",
      params
    );
  }

  /**
   * Get recent transactions
   */
  async getRecentTransactions(
    limit: number = 20,
    offset: number = 0,
    sortBy: SortBy = "date",
    order: Order = "desc"
  ): Promise<TransactionsResponse> {
    const params = new URLSearchParams();
    params.append("limit", limit.toString());
    params.append("offset", offset.toString());
    params.append("sort_by", sortBy);
    params.append("order", order);
    return this.get<TransactionsResponse>("/api/transactions/recent", params);
  }

  /**
   * Get trader performance metrics
   */
  async getTraderPerformance(
    traderId: number,
    period: Period = "30d"
  ): Promise<TraderPerformance> {
    const params = new URLSearchParams();
    params.append("period", period);
    return this.get<TraderPerformance>(
      `/api/traders/${traderId}/performance`,
      params
    );
  }

  /**
   * Get period comparison
   */
  async getPeriodComparison(
    currentPeriod: Period = "7d"
  ): Promise<PeriodComparisonResponse> {
    const params = new URLSearchParams();
    params.append("current_period", currentPeriod);
    return this.get<PeriodComparisonResponse>(
      "/api/analytics/period-comparison",
      params
    );
  }

  /**
   * Search and filter transactions
   */
  async searchTransactions(
    filters: {
      type?: TransactionType;
      category?: string;
      minAmount?: number;
      maxAmount?: number;
      startDate?: string;
      endDate?: string;
      traderId?: number;
      limit?: number;
      offset?: number;
    }
  ): Promise<TransactionsResponse> {
    const params = new URLSearchParams();
    if (filters.type) params.append("tx_type", filters.type);
    if (filters.category) params.append("category", filters.category);
    if (filters.minAmount) params.append("min_amount", filters.minAmount.toString());
    if (filters.maxAmount) params.append("max_amount", filters.maxAmount.toString());
    if (filters.startDate) params.append("start_date", filters.startDate);
    if (filters.endDate) params.append("end_date", filters.endDate);
    if (filters.traderId) params.append("trader_id", filters.traderId.toString());
    params.append("limit", (filters.limit || 20).toString());
    params.append("offset", (filters.offset || 0).toString());
    return this.get<TransactionsResponse>("/api/transactions/search", params);
  }

  /**
   * Generic GET request helper
   */
  private async get<T>(
    endpoint: string,
    params?: URLSearchParams
  ): Promise<T> {
    const url = new URL(endpoint, this.baseUrl);
    if (params) {
      url.search = params.toString();
    }

    const response = await fetch(url.toString(), {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(
        `API Error: ${response.status} ${response.statusText}`
      );
    }

    return response.json() as Promise<T>;
  }
}

/**
 * Factory function to create API client
 */
export function createDashboardApiClient(baseUrl: string): DashboardApiClient {
  return new DashboardApiClient({ baseUrl });
}

// ============================================================
// React Hooks (Optional - for convenience)
// ============================================================

/**
 * Example usage with React Query:
 * 
 * import { useQuery } from '@tanstack/react-query';
 * 
 * export function useMetricsSummary(apiClient: DashboardApiClient) {
 *   return useQuery({
 *     queryKey: ['metrics-summary'],
 *     queryFn: () => apiClient.getMetricsSummary(),
 *   });
 * }
 */
