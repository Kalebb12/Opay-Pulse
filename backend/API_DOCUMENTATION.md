# OPay Pulse Dashboard API Documentation

**Base URL:** `http://localhost:8000` (development) or your production domain

---

## Overview

The OPay Pulse Dashboard API provides comprehensive endpoints for displaying charts and metrics. All responses are JSON formatted and include proper HTTP status codes.

### Response Format

**Success (200 OK):**
```json
{
  "data": {...},
  "total": 100,
  ...
}
```

**Error (400/404/500):**
```json
{
  "detail": "Error message"
}
```

---

## Endpoints

### 1. Metrics Summary
**GET** `/api/metrics/summary`

Get overall KPI metrics for the dashboard.

**Query Parameters:** None

**Response:**
```json
{
  "total_traders": 150,
  "active_traders_today": 45,
  "total_transactions": 3200,
  "total_volume": 1250000.50,
  "average_transaction": 391.00,
  "average_credit_score": 720
}
```

**Use Case:** Display key metric cards at the top of the dashboard

---

### 2. Transaction Analytics
**GET** `/api/metrics/transactions`

Get transaction analytics for a specific period and category.

**Query Parameters:**
- `period` (string, optional): `7d`, `30d`, `90d`, `1y` (default: `30d`)
- `category` (string, optional): Filter by category name, or `all` for all categories

**Response:**
```json
{
  "total": 850,
  "income": 750000.00,
  "expense": 500000.00,
  "net": 250000.00,
  "success_rate": 98.5,
  "categories": {
    "sales": 500000.00,
    "stock": 350000.00,
    "transport": 150000.00
  }
}
```

**Use Case:** Display transaction summary statistics

---

### 3. Transaction Trend
**GET** `/api/analytics/transaction-trend`

Get transaction trends over time for line charts.

**Query Parameters:**
- `period` (string, optional): `7d`, `30d`, `90d`, `1y` (default: `7d`)
- `group_by` (string, optional): `daily`, `weekly`, `monthly` (default: `daily`)

**Response:**
```json
{
  "data": [
    {
      "date": "2026-05-24",
      "income": 50000,
      "expense": 30000,
      "net": 20000
    },
    {
      "date": "2026-05-25",
      "income": 65000,
      "expense": 25000,
      "net": 40000
    }
  ]
}
```

**Use Case:** Line/Area charts showing transaction trends

---

### 4. Category Distribution
**GET** `/api/analytics/category-distribution`

Get breakdown of transactions by category.

**Query Parameters:**
- `period` (string, optional): `7d`, `30d`, `90d`, `1y` (default: `30d`)

**Response:**
```json
{
  "data": [
    {
      "name": "Sales",
      "value": 500000,
      "percentage": 45.0
    },
    {
      "name": "Stock",
      "value": 350000,
      "percentage": 31.0
    },
    {
      "name": "Transport",
      "value": 200000,
      "percentage": 18.0
    },
    {
      "name": "Others",
      "value": 60000,
      "percentage": 6.0
    }
  ]
}
```

**Use Case:** Pie/Donut charts showing category breakdown

---

### 5. User Growth
**GET** `/api/metrics/user-growth`

Get user growth metrics over time.

**Query Parameters:**
- `period` (string, optional): `7d`, `30d`, `90d`, `1y` (default: `30d`)
- `group_by` (string, optional): `daily`, `weekly` (default: `daily`)

**Response:**
```json
{
  "data": [
    {
      "date": "2026-05-24",
      "new_traders": 5,
      "active_traders": 120,
      "cumulative": 1200
    },
    {
      "date": "2026-05-25",
      "new_traders": 8,
      "active_traders": 135,
      "cumulative": 1208
    }
  ]
}
```

**Use Case:** Line/Bar charts showing user growth trends

---

### 6. Top Traders
**GET** `/api/traders/top`

Get top performing traders.

**Query Parameters:**
- `limit` (integer, optional): 1-100 (default: 10)
- `sort_by` (string, optional): `volume`, `score`, `streak` (default: `volume`)
- `period` (string, optional): `7d`, `30d`, `90d`, `1y` (default: `30d`)

**Response:**
```json
{
  "data": [
    {
      "rank": 1,
      "trader_id": 42,
      "phone_number": "+234XXXXXXXXXX",
      "total_volume": 850000,
      "transaction_count": 125,
      "credit_score": 890,
      "streak_count": 45
    }
  ]
}
```

**Use Case:** Leaderboard table showing top performers

---

### 7. Credit Score Distribution
**GET** `/api/analytics/credit-score-distribution`

Get distribution of credit scores.

**Query Parameters:** None

**Response:**
```json
{
  "data": [
    {"range": "300-400", "count": 10},
    {"range": "400-500", "count": 25},
    {"range": "500-600", "count": 45},
    {"range": "600-700", "count": 38},
    {"range": "700-800", "count": 22},
    {"range": "800-900", "count": 8},
    {"range": "900+", "count": 2}
  ]
}
```

**Use Case:** Histogram chart showing score distribution

---

### 8. Income vs Expense
**GET** `/api/analytics/income-vs-expense`

Compare income and expense trends.

**Query Parameters:**
- `period` (string, optional): `7d`, `30d`, `90d`, `1y` (default: `7d`)

**Response:**
```json
{
  "data": [
    {
      "date": "2026-05-24",
      "income": 50000,
      "expense": 30000
    },
    {
      "date": "2026-05-25",
      "income": 65000,
      "expense": 25000
    }
  ]
}
```

**Use Case:** Stacked bar chart or dual-axis chart

---

### 9. Recent Transactions
**GET** `/api/transactions/recent`

Get recent transactions with pagination.

**Query Parameters:**
- `limit` (integer, optional): 1-100 (default: 20)
- `offset` (integer, optional): Pagination offset (default: 0)
- `sort_by` (string, optional): `date`, `amount` (default: `date`)
- `order` (string, optional): `asc`, `desc` (default: `desc`)

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "trader_id": 42,
      "trader_phone": "+234XXXXXXXXXX",
      "type": "income",
      "amount": 5000.00,
      "category": "sales",
      "description": "Sold items",
      "logged_at": "2026-05-26T14:30:00"
    }
  ],
  "total": 3200,
  "limit": 20,
  "offset": 0
}
```

**Use Case:** Data table showing recent transactions

---

### 10. Trader Performance
**GET** `/api/traders/{trader_id}/performance`

Get individual trader performance metrics.

**Path Parameters:**
- `trader_id` (integer): The trader's ID

**Query Parameters:**
- `period` (string, optional): `7d`, `30d`, `90d`, `1y` (default: `30d`)

**Response:**
```json
{
  "trader_id": 42,
  "phone_number": "+234XXXXXXXXXX",
  "total_transactions": 125,
  "total_volume": 850000,
  "average_transaction": 6800,
  "income_transactions": 80,
  "expense_transactions": 45,
  "income_total": 680000,
  "expense_total": 170000,
  "credit_score": 890,
  "streak_count": 45,
  "joined_date": "2025-01-15T10:30:00"
}
```

**Use Case:** Individual trader dashboard/profile page

---

### 11. Period Comparison
**GET** `/api/analytics/period-comparison`

Compare current period with previous period.

**Query Parameters:**
- `current_period` (string, optional): `7d`, `30d`, `90d`, `1y` (default: `7d`)

**Response:**
```json
{
  "current_period": {
    "transactions": 850,
    "volume": 1250000,
    "average_transaction": 1470.59
  },
  "previous_period": {
    "transactions": 920,
    "volume": 1100000,
    "average_transaction": 1195.65
  },
  "change": {
    "transactions": -7.6,
    "volume": 13.6,
    "average_transaction": 23.0
  }
}
```

**Use Case:** Show growth/decline indicators

---

### 12. Search Transactions
**GET** `/api/transactions/search`

Search and filter transactions with multiple criteria.

**Query Parameters:**
- `type` (string, optional): `income`, `expense` (filter by type)
- `category` (string, optional): Filter by category name
- `min_amount` (number, optional): Minimum transaction amount
- `max_amount` (number, optional): Maximum transaction amount
- `start_date` (string, optional): Start date in YYYY-MM-DD format
- `end_date` (string, optional): End date in YYYY-MM-DD format
- `trader_id` (integer, optional): Filter by trader ID
- `limit` (integer, optional): 1-100 (default: 20)
- `offset` (integer, optional): Pagination offset (default: 0)

**Example Request:**
```
GET /api/transactions/search?type=income&category=sales&min_amount=1000&max_amount=100000&start_date=2026-05-01&end_date=2026-05-31&limit=20&offset=0
```

**Response:**
Same as Recent Transactions endpoint

**Use Case:** Advanced search and filtering functionality

---

## Frontend Integration Examples

### Using React Query

```typescript
import { useQuery } from '@tanstack/react-query';
import { createDashboardApiClient } from '@/types/dashboard';

const apiClient = createDashboardApiClient('http://localhost:8000');

// In a React component:
function Dashboard() {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['metrics-summary'],
    queryFn: () => apiClient.getMetricsSummary(),
  });

  const { data: transactions } = useQuery({
    queryKey: ['recent-transactions'],
    queryFn: () => apiClient.getRecentTransactions(20, 0),
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <MetricsCards metrics={metrics} />
      <TransactionsTable data={transactions.data} />
    </div>
  );
}
```

### Using Fetch API

```typescript
async function getMetrics() {
  const response = await fetch('http://localhost:8000/api/metrics/summary');
  const data = await response.json();
  return data;
}
```

### Using Axios

```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
});

export async function getTransactionTrend(period = '7d') {
  const { data } = await apiClient.get('/api/analytics/transaction-trend', {
    params: { period },
  });
  return data;
}
```

---

## Error Handling

All errors follow a standard format:

```json
{
  "detail": "Error description"
}
```

**Common Status Codes:**
- `200` - Successful request
- `400` - Bad request (invalid parameters)
- `404` - Resource not found
- `500` - Server error

**Example:**
```typescript
try {
  const data = await apiClient.getMetricsSummary();
} catch (error) {
  if (error.response?.status === 404) {
    console.log('Resource not found');
  } else if (error.response?.status === 400) {
    console.log('Invalid parameters:', error.response.data.detail);
  }
}
```

---

## Rate Limiting

Currently, there is no rate limiting implemented. In production, consider adding rate limiting middleware.

---

## Performance Tips

1. **Use pagination** for large datasets (limit to 50 items)
2. **Cache responses** using React Query or similar library
3. **Filter data at API level** rather than in frontend
4. **Use specific date ranges** to reduce data volume
5. **Implement debouncing** for search filters

---

## Development

To test these endpoints locally:

```bash
# Start the backend
cd backend
python -m uvicorn src.main:app --reload

# Access API docs
http://localhost:8000/docs
```

---

## Support

For questions or issues, please refer to the main project README or contact the development team.
