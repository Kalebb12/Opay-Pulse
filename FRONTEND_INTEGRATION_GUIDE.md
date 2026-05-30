# Frontend Integration Guide

This guide explains how to integrate the OPay Pulse Dashboard API into your React frontend.

---

## Installation

### Step 1: Copy TypeScript Types

The TypeScript types are available in `frontend/types/dashboard.ts`. Copy this file to your React project:

```bash
cp frontend/types/dashboard.ts src/types/
```

### Step 2: Install Dependencies

```bash
npm install @tanstack/react-query axios
# or
yarn add @tanstack/react-query axios
```

### Step 3: Set Environment Variables

Create a `.env.local` file in your frontend root:

```env
VITE_API_BASE_URL=http://localhost:8000
# or for production
VITE_API_BASE_URL=https://your-api-domain.com
```

---

## Usage Examples

### 1. Basic API Client Setup

```typescript
// src/services/api.ts
import { createDashboardApiClient } from '@/types/dashboard';

const apiClient = createDashboardApiClient(
  process.env.VITE_API_BASE_URL || 'http://localhost:8000'
);

export default apiClient;
```

### 2. Using with React Query

```typescript
// src/hooks/useDashboard.ts
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/services/api';

export function useMetricsSummary() {
  return useQuery({
    queryKey: ['metrics-summary'],
    queryFn: () => apiClient.getMetricsSummary(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

export function useTransactionTrend(period = '7d') {
  return useQuery({
    queryKey: ['transaction-trend', period],
    queryFn: () => apiClient.getTransactionTrend(period),
  });
}

export function useTopTraders(limit = 10, sortBy = 'volume', period = '30d') {
  return useQuery({
    queryKey: ['top-traders', limit, sortBy, period],
    queryFn: () => apiClient.getTopTraders(limit, sortBy, period),
  });
}

export function useRecentTransactions(limit = 20, offset = 0) {
  return useQuery({
    queryKey: ['recent-transactions', limit, offset],
    queryFn: () => apiClient.getRecentTransactions(limit, offset),
  });
}
```

### 3. Dashboard Component with Charts

```typescript
// src/pages/Dashboard.tsx
import { useMetricsSummary, useTransactionTrend, useTopTraders } from '@/hooks/useDashboard';
import { MetricsCards } from '@/components/MetricsCards';
import { TransactionChart } from '@/components/TransactionChart';
import { TopTradersTable } from '@/components/TopTradersTable';

export function Dashboard() {
  const { data: metrics, isLoading: metricsLoading } = useMetricsSummary();
  const { data: trend, isLoading: trendLoading } = useTransactionTrend('7d');
  const { data: traders, isLoading: tradersLoading } = useTopTraders();

  if (metricsLoading || trendLoading || tradersLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      
      {/* Metrics Cards */}
      <MetricsCards metrics={metrics} />
      
      {/* Charts */}
      <div className="charts-grid">
        <TransactionChart data={trend.data} />
      </div>
      
      {/* Tables */}
      <TopTradersTable data={traders.data} />
    </div>
  );
}
```

### 4. Metrics Cards Component

```typescript
// src/components/MetricsCards.tsx
import { MetricsSummary } from '@/types/dashboard';

export function MetricsCards({ metrics }: { metrics?: MetricsSummary }) {
  if (!metrics) return null;

  return (
    <div className="metrics-grid">
      <MetricCard
        title="Total Traders"
        value={metrics.total_traders}
        icon="👥"
      />
      <MetricCard
        title="Active Today"
        value={metrics.active_traders_today}
        icon="🟢"
      />
      <MetricCard
        title="Total Transactions"
        value={metrics.total_transactions}
        icon="📊"
      />
      <MetricCard
        title="Total Volume"
        value={`₦${metrics.total_volume.toLocaleString()}`}
        icon="💰"
      />
      <MetricCard
        title="Avg Transaction"
        value={`₦${metrics.average_transaction.toLocaleString()}`}
        icon="📈"
      />
      <MetricCard
        title="Avg Credit Score"
        value={metrics.average_credit_score}
        icon="⭐"
      />
    </div>
  );
}

function MetricCard({ title, value, icon }: { title: string; value: any; icon: string }) {
  return (
    <div className="metric-card">
      <div className="icon">{icon}</div>
      <div className="content">
        <p className="title">{title}</p>
        <p className="value">{value}</p>
      </div>
    </div>
  );
}
```

### 5. Transaction Chart (using ApexCharts)

```typescript
// src/components/TransactionChart.tsx
import Chart from 'react-apexcharts';
import { DailyTransaction } from '@/types/dashboard';

export function TransactionChart({ data }: { data?: DailyTransaction[] }) {
  if (!data) return null;

  const options = {
    chart: {
      type: 'line',
      stacked: false,
    },
    xaxis: {
      categories: data.map((d) => d.date),
    },
    yaxis: {
      title: {
        text: 'Amount (₦)',
      },
    },
  };

  const series = [
    {
      name: 'Income',
      data: data.map((d) => d.income),
    },
    {
      name: 'Expense',
      data: data.map((d) => d.expense),
    },
    {
      name: 'Net',
      data: data.map((d) => d.net),
    },
  ];

  return (
    <div className="transaction-chart">
      <h3>Transaction Trend</h3>
      <Chart options={options} series={series} type="line" height={400} />
    </div>
  );
}
```

### 6. Category Distribution (Pie Chart)

```typescript
// src/components/CategoryChart.tsx
import Chart from 'react-apexcharts';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/services/api';

export function CategoryChart() {
  const { data, isLoading } = useQuery({
    queryKey: ['category-distribution'],
    queryFn: () => apiClient.getCategoryDistribution('30d'),
  });

  if (isLoading || !data) return null;

  const options = {
    labels: data.data.map((c) => c.name),
    legend: {
      position: 'bottom' as const,
    },
  };

  const series = data.data.map((c) => c.percentage);

  return (
    <div className="category-chart">
      <h3>Category Distribution</h3>
      <Chart
        options={options}
        series={series}
        type="donut"
        height={400}
      />
    </div>
  );
}
```

### 7. Top Traders Table

```typescript
// src/components/TopTradersTable.tsx
import { TopTrader } from '@/types/dashboard';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/services/api';

export function TopTradersTable() {
  const { data, isLoading } = useQuery({
    queryKey: ['top-traders'],
    queryFn: () => apiClient.getTopTraders(20, 'volume', '30d'),
  });

  if (isLoading || !data) return null;

  return (
    <div className="traders-table">
      <h3>Top Traders</h3>
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Phone</th>
            <th>Volume</th>
            <th>Transactions</th>
            <th>Score</th>
            <th>Streak</th>
          </tr>
        </thead>
        <tbody>
          {data.data.map((trader) => (
            <tr key={trader.trader_id}>
              <td>{trader.rank}</td>
              <td>{trader.phone_number}</td>
              <td>₦{trader.total_volume.toLocaleString()}</td>
              <td>{trader.transaction_count}</td>
              <td>{trader.credit_score}</td>
              <td>{trader.streak_count}🔥</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

### 8. Search & Filter Component

```typescript
// src/components/TransactionSearch.tsx
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/services/api';

export function TransactionSearch() {
  const [filters, setFilters] = useState({
    type: 'all' as any,
    category: '',
    minAmount: undefined as number | undefined,
    maxAmount: undefined as number | undefined,
  });

  const { data, isLoading } = useQuery({
    queryKey: ['search-transactions', filters],
    queryFn: () => apiClient.searchTransactions(filters),
  });

  const handleFilterChange = (key: string, value: any) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="transaction-search">
      <div className="filters">
        <select
          value={filters.type}
          onChange={(e) => handleFilterChange('type', e.target.value)}
        >
          <option value="all">All Types</option>
          <option value="income">Income</option>
          <option value="expense">Expense</option>
        </select>

        <input
          type="text"
          placeholder="Category"
          value={filters.category}
          onChange={(e) => handleFilterChange('category', e.target.value)}
        />

        <input
          type="number"
          placeholder="Min Amount"
          value={filters.minAmount || ''}
          onChange={(e) => handleFilterChange('minAmount', parseInt(e.target.value) || undefined)}
        />

        <input
          type="number"
          placeholder="Max Amount"
          value={filters.maxAmount || ''}
          onChange={(e) => handleFilterChange('maxAmount', parseInt(e.target.value) || undefined)}
        />
      </div>

      {isLoading ? <p>Loading...</p> : <TransactionTable data={data?.data} />}
    </div>
  );
}

function TransactionTable({ data }: { data?: any[] }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Type</th>
          <th>Amount</th>
          <th>Category</th>
          <th>Phone</th>
        </tr>
      </thead>
      <tbody>
        {data?.map((tx) => (
          <tr key={tx.id}>
            <td>{new Date(tx.logged_at).toLocaleDateString()}</td>
            <td>{tx.type}</td>
            <td>₦{tx.amount.toLocaleString()}</td>
            <td>{tx.category}</td>
            <td>{tx.trader_phone}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

### 9. Query Provider Setup

```typescript
// src/App.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Dashboard } from '@/pages/Dashboard';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  );
}
```

---

## Styling Example (Tailwind CSS)

```css
/* src/styles/dashboard.css */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.metric-card .icon {
  font-size: 2rem;
}

.metric-card .content {
  flex: 1;
}

.metric-card .title {
  color: #666;
  font-size: 0.875rem;
  margin: 0;
}

.metric-card .value {
  color: #333;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0.5rem 0 0;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.chart-container {
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

table {
  width: 100%;
  border-collapse: collapse;
}

table th {
  background: #f5f5f5;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #e0e0e0;
}

table td {
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

table tr:hover {
  background: #f9f9f9;
}
```

---

## Testing

```typescript
// src/__tests__/Dashboard.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Dashboard } from '@/pages/Dashboard';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('http://localhost:8000/api/metrics/summary', (req, res, ctx) => {
    return res(
      ctx.json({
        total_traders: 150,
        active_traders_today: 45,
        total_transactions: 3200,
        total_volume: 1250000.5,
        average_transaction: 391,
        average_credit_score: 720,
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('renders dashboard with metrics', async () => {
  const queryClient = new QueryClient();
  render(
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  );

  await waitFor(() => {
    expect(screen.getByText('150')).toBeInTheDocument();
  });
});
```

---

## Common Issues

### 1. CORS Errors

If you get CORS errors, make sure the backend includes proper CORS headers. The backend has CORS enabled for all origins in development, but you should restrict this in production.

### 2. API Base URL

Make sure your environment variable is correctly set:

```bash
echo $VITE_API_BASE_URL  # Should output the API URL
```

### 3. Stale Data

Use `refetchInterval` and `staleTime` options in React Query to control data freshness:

```typescript
useQuery({
  queryKey: ['metrics'],
  queryFn: () => apiClient.getMetricsSummary(),
  refetchInterval: 30000, // Refetch every 30 seconds
  staleTime: 10000, // Consider data stale after 10 seconds
});
```

---

## Next Steps

1. Create dashboard pages for each major chart/metric
2. Implement real-time updates using WebSockets
3. Add export functionality (CSV, PDF)
4. Implement caching strategy
5. Add role-based access control

---

For more information, see [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
