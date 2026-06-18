import React, { useEffect, useState } from 'react';
import { Row, Col, message } from 'antd';
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, AreaChart, Area,
} from 'recharts';
import {
  ThunderboltOutlined,
  AlertOutlined,
  RiseOutlined,
  EyeOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { getRecentTransactions } from '../api/client';

const Monitoring: React.FC = () => {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [chartData, setChartData] = useState<any[]>([]);

  const fetchData = async () => {
    try {
      const res = await getRecentTransactions(100);
      const txs = res.data;
      setTransactions(txs);

      const byMinute: Record<string, any> = {};
      txs.forEach((tx: any) => {
        const d = new Date(tx.created_at);
        const key = `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
        if (!byMinute[key]) byMinute[key] = { time: key, total: 0, flagged: 0, avgScore: 0, scores: [] };
        byMinute[key].total++;
        if (tx.is_fraud_predicted) byMinute[key].flagged++;
        byMinute[key].scores.push(tx.fraud_score * 100);
      });

      const chart = Object.values(byMinute).map((d: any) => ({
        ...d,
        avgScore: d.scores.length > 0
          ? parseFloat((d.scores.reduce((a: number, b: number) => a + b, 0) / d.scores.length).toFixed(1))
          : 0,
        fraudRate: d.total > 0 ? parseFloat(((d.flagged / d.total) * 100).toFixed(1)) : 0,
      })).slice(-20);

      setChartData(chart);
    } catch (err) {
      message.error('Failed to fetch monitoring data');
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const total = transactions.length;
  const flagged = transactions.filter(t => t.is_fraud_predicted).length;
  const cleared = total - flagged;
  const fraudRate = total > 0 ? ((flagged / total) * 100).toFixed(1) : '0';
  const avgScore = total > 0
    ? (transactions.reduce((s: number, t: any) => s + t.fraud_score, 0) / total * 100).toFixed(1)
    : '0';
  const highRisk = transactions.filter(t => t.risk_level === 'HIGH' || t.risk_level === 'CRITICAL').length;

  const statCards = [
    { title: 'TOTAL SCORED', value: total, color: '#58a6ff', bg: '#0d1a2e', border: '#1a2744', icon: <ThunderboltOutlined /> },
    { title: 'FLAGGED', value: flagged, color: '#f85149', bg: '#1e0d0d', border: '#2e1a1a', icon: <AlertOutlined /> },
    { title: 'CLEARED', value: cleared, color: '#3fb950', bg: '#0d1e0d', border: '#1a2e1a', icon: <CheckCircleOutlined /> },
    { title: 'HIGH RISK', value: highRisk, color: '#d29922', bg: '#1e1a0d', border: '#2e221a', icon: <RiseOutlined /> },
    { title: 'FRAUD RATE', value: `${fraudRate}%`, color: '#f0883e', bg: '#1e150d', border: '#2e1f0d', icon: <EyeOutlined /> },
    { title: 'AVG SCORE', value: `${avgScore}%`, color: '#a371f7', bg: '#1a0d2e', border: '#2a1a44', icon: <BarChartIcon /> },
  ];

  function BarChartIcon() {
    return <span style={{ fontSize: '14px' }}>📊</span>;
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: '#0d1421',
          border: '1px solid #1a2744',
          borderRadius: '6px',
          padding: '10px 14px',
          fontSize: '12px'
        }}>
          <p style={{ color: '#8b949e', marginBottom: '6px' }}>Time: {label}</p>
          {payload.map((p: any, i: number) => (
            <p key={i} style={{ color: p.color, margin: '2px 0' }}>
              {p.name}: {p.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{
          color: '#e6edf3',
          fontSize: '22px',
          fontWeight: '700',
          margin: 0,
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <ThunderboltOutlined style={{ color: '#3fb950' }} />
          Live System Monitoring
        </h1>
        <p style={{ color: '#484f58', margin: '4px 0 0', fontSize: '13px' }}>
          Real-time metrics — auto-refreshes every 10 seconds
        </p>
      </div>

      {/* Stat Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(6, 1fr)',
        gap: '12px',
        marginBottom: '24px'
      }}>
        {statCards.map((stat, i) => (
          <div key={i} style={{
            background: stat.bg,
            border: `1px solid ${stat.border}`,
            borderRadius: '8px',
            padding: '14px 16px',
          }}>
            <div style={{ color: stat.color, fontSize: '18px', marginBottom: '8px', opacity: 0.8 }}>
              {stat.icon}
            </div>
            <div style={{ color: '#484f58', fontSize: '9px', letterSpacing: '1px', marginBottom: '4px' }}>
              {stat.title}
            </div>
            <div style={{ color: stat.color, fontSize: '22px', fontWeight: '700', lineHeight: 1 }}>
              {stat.value}
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>

        {/* Transaction Volume */}
        <div style={{
          background: '#0d1421',
          border: '1px solid #1a2744',
          borderRadius: '8px',
          overflow: 'hidden'
        }}>
          <div style={{
            padding: '12px 16px',
            borderBottom: '1px solid #1a2744',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span style={{ color: '#e6edf3', fontWeight: '600', fontSize: '13px' }}>
              Transaction Volume
            </span>
            <div style={{ display: 'flex', gap: '12px' }}>
              <span style={{ color: '#58a6ff', fontSize: '11px' }}>■ Total</span>
              <span style={{ color: '#f85149', fontSize: '11px' }}>■ Flagged</span>
            </div>
          </div>
          <div style={{ padding: '16px' }}>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="totalGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#58a6ff" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#58a6ff" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="flaggedGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f85149" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#f85149" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1a2744" />
                <XAxis dataKey="time" stroke="#484f58" tick={{ fontSize: 10, fill: '#484f58' }} />
                <YAxis stroke="#484f58" tick={{ fontSize: 10, fill: '#484f58' }} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="total" stroke="#58a6ff" strokeWidth={2} fill="url(#totalGrad)" name="Total" dot={false} />
                <Area type="monotone" dataKey="flagged" stroke="#f85149" strokeWidth={2} fill="url(#flaggedGrad)" name="Flagged" dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Avg Fraud Score */}
        <div style={{
          background: '#0d1421',
          border: '1px solid #1a2744',
          borderRadius: '8px',
          overflow: 'hidden'
        }}>
          <div style={{
            padding: '12px 16px',
            borderBottom: '1px solid #1a2744',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span style={{ color: '#e6edf3', fontWeight: '600', fontSize: '13px' }}>
              Avg Fraud Score Over Time
            </span>
            <span style={{ color: '#a371f7', fontSize: '11px' }}>■ Avg Score %</span>
          </div>
          <div style={{ padding: '16px' }}>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#a371f7" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#a371f7" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1a2744" />
                <XAxis dataKey="time" stroke="#484f58" tick={{ fontSize: 10, fill: '#484f58' }} />
                <YAxis stroke="#484f58" tick={{ fontSize: 10, fill: '#484f58' }} domain={[0, 100]} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="avgScore" stroke="#a371f7" strokeWidth={2} fill="url(#scoreGrad)" name="Avg Score %" dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Model Status */}
      <div style={{
        background: '#0d1421',
        border: '1px solid #1a2744',
        borderRadius: '8px',
        overflow: 'hidden',
        marginBottom: '16px'
      }}>
        <div style={{
          padding: '12px 16px',
          borderBottom: '1px solid #1a2744',
        }}>
          <span style={{ color: '#e6edf3', fontWeight: '600', fontSize: '13px' }}>
            🤖 Model Status
          </span>
        </div>
        <div style={{
          padding: '16px',
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '12px'
        }}>
          {[
            { name: 'XGBoost ONNX', status: 'ACTIVE', latency: '~2ms', color: '#3fb950', detail: 'IEEE-CIS Trained' },
            { name: 'Isolation Forest', status: 'ACTIVE', latency: '~1ms', color: '#3fb950', detail: 'Anomaly Detection' },
            { name: 'Meta Learner', status: 'ACTIVE', latency: '~1ms', color: '#3fb950', detail: 'Ensemble Combiner' },
            { name: 'GNN GraphSAGE', status: 'ACTIVE', latency: '~5ms', color: '#3fb950', detail: 'Neo4j Subgraph' },
          ].map((model, i) => (
            <div key={i} style={{
              background: '#0a1628',
              border: '1px solid #1a2744',
              borderRadius: '6px',
              padding: '12px 14px',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ color: '#e6edf3', fontSize: '12px', fontWeight: '600' }}>{model.name}</span>
                <span style={{
                  color: model.color,
                  fontSize: '9px',
                  fontWeight: '700',
                  background: '#0a1e0a',
                  padding: '1px 6px',
                  borderRadius: '4px',
                  border: `1px solid ${model.color}40`
                }}>
                  {model.status}
                </span>
              </div>
              <div style={{ color: '#484f58', fontSize: '10px' }}>{model.detail}</div>
              <div style={{ color: '#58a6ff', fontSize: '10px', marginTop: '4px' }}>
                Latency: {model.latency}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity Table */}
      <div style={{
        background: '#0d1421',
        border: '1px solid #1a2744',
        borderRadius: '8px',
        overflow: 'hidden'
      }}>
        <div style={{
          padding: '12px 16px',
          borderBottom: '1px solid #1a2744',
        }}>
          <span style={{ color: '#e6edf3', fontWeight: '600', fontSize: '13px' }}>
            Recent Activity
          </span>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#0a1628' }}>
                {['ACCOUNT', 'AMOUNT', 'SCORE', 'RISK', 'STATUS', 'TIME'].map(h => (
                  <th key={h} style={{
                    padding: '8px 16px',
                    color: '#484f58',
                    fontSize: '10px',
                    fontWeight: '700',
                    letterSpacing: '1px',
                    textAlign: 'left',
                    borderBottom: '1px solid #1a2744'
                  }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {transactions.slice(0, 15).map((tx: any, i: number) => {
                const score = (tx.fraud_score * 100).toFixed(1);
                const scoreColor = tx.fraud_score >= 0.7 ? '#f85149' : tx.fraud_score >= 0.4 ? '#d29922' : '#3fb950';
                return (
                  <tr key={i} style={{
                    borderBottom: '1px solid #1a2744',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={e => (e.currentTarget.style.background = '#1a2744')}
                  onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                  >
                    <td style={{ padding: '10px 16px', color: '#58a6ff', fontFamily: 'monospace', fontSize: '12px' }}>
                      {tx.account_id}
                    </td>
                    <td style={{ padding: '10px 16px', color: '#e6edf3', fontSize: '12px', fontWeight: '600' }}>
                      ₹{tx.amount?.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      <span style={{ color: scoreColor, fontWeight: '700', fontSize: '12px' }}>
                        {score}%
                      </span>
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      <span style={{
                        color: scoreColor,
                        fontSize: '10px',
                        fontWeight: '700',
                        background: `${scoreColor}20`,
                        padding: '2px 6px',
                        borderRadius: '3px',
                        border: `1px solid ${scoreColor}30`
                      }}>
                        {tx.risk_level}
                      </span>
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      {tx.is_fraud_predicted ? (
                        <span style={{ color: '#f85149', fontSize: '11px', fontWeight: '600' }}>
                          🚨 FLAGGED
                        </span>
                      ) : (
                        <span style={{ color: '#3fb950', fontSize: '11px', fontWeight: '600' }}>
                          ✅ CLEAR
                        </span>
                      )}
                    </td>
                    <td style={{ padding: '10px 16px', color: '#484f58', fontSize: '11px', fontFamily: 'monospace' }}>
                      {new Date(tx.created_at).toLocaleTimeString()}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Monitoring;