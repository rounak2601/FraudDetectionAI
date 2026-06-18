import React, { useEffect, useState } from 'react';
import { Table, Tag, Button, Card, Statistic, Row, Col, message, Badge } from 'antd';
import { useNavigate } from 'react-router-dom';
import {
  AlertOutlined,
  CheckCircleOutlined,
  EyeOutlined,
  ThunderboltOutlined,
  RiseOutlined,
} from '@ant-design/icons';
import { getRecentTransactions, createCase } from '../api/client';
import LiveSimulator from '../components/LiveSimulator';

interface Transaction {
  transaction_id: string;
  account_id: string;
  amount: number;
  fraud_score: number;
  risk_level: string;
  is_fraud_predicted: boolean;
  created_at: string;
}

const Dashboard: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [newTxCount, setNewTxCount] = useState(0);
  const navigate = useNavigate();

  const fetchTransactions = async () => {
    try {
      const res = await getRecentTransactions(50);
      setTransactions(res.data);
      setNewTxCount(c => c + 1);
    } catch (err) {
      message.error('Failed to load transactions. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
    const interval = setInterval(fetchTransactions, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleInvestigate = async (txId: string) => {
    try {
      await createCase(txId);
    } catch (err) {}
    navigate(`/investigation/${txId}`);
  };

  const total = transactions.length;
  const flagged = transactions.filter(t => t.is_fraud_predicted).length;
  const highRisk = transactions.filter(t => t.risk_level === 'HIGH' || t.risk_level === 'CRITICAL').length;
  const avgScore = total > 0
    ? (transactions.reduce((s, t) => s + t.fraud_score, 0) / total * 100).toFixed(1)
    : '0';

  const columns = [
    {
      title: 'TRANSACTION ID',
      dataIndex: 'transaction_id',
      key: 'transaction_id',
      render: (id: string) => (
        <span style={{ color: '#58a6ff', fontFamily: 'monospace', fontSize: '12px' }}>
          {id.substring(0, 18)}...
        </span>
      ),
    },
    {
      title: 'ACCOUNT',
      dataIndex: 'account_id',
      key: 'account_id',
      render: (id: string) => (
        <span style={{ color: '#e6edf3', fontFamily: 'monospace', fontSize: '12px' }}>{id}</span>
      ),
    },
    {
      title: 'AMOUNT',
      dataIndex: 'amount',
      key: 'amount',
      render: (amt: number) => (
        <span style={{ color: '#e6edf3', fontWeight: '600' }}>
          ₹{amt?.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
        </span>
      ),
      sorter: (a: Transaction, b: Transaction) => a.amount - b.amount,
    },
    {
      title: 'FRAUD SCORE',
      dataIndex: 'fraud_score',
      key: 'fraud_score',
      render: (score: number) => {
        const pct = (score * 100).toFixed(1);
        const color = score >= 0.7 ? '#f85149' : score >= 0.4 ? '#d29922' : '#3fb950';
        const bg = score >= 0.7 ? '#2e1a1a' : score >= 0.4 ? '#2e221a' : '#1a2e1a';
        return (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <div style={{
              width: '60px',
              height: '6px',
              background: '#1a2744',
              borderRadius: '3px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${pct}%`,
                height: '100%',
                background: color,
                borderRadius: '3px',
                transition: 'width 0.3s ease'
              }} />
            </div>
            <span style={{
              color,
              fontWeight: '700',
              fontSize: '13px',
              background: bg,
              padding: '2px 6px',
              borderRadius: '4px',
              border: `1px solid ${color}40`
            }}>
              {pct}%
            </span>
          </div>
        );
      },
      sorter: (a: Transaction, b: Transaction) => a.fraud_score - b.fraud_score,
      defaultSortOrder: 'descend' as const,
    },
    {
      title: 'RISK',
      dataIndex: 'risk_level',
      key: 'risk_level',
      render: (level: string) => {
        const configs: Record<string, { color: string; bg: string; border: string }> = {
          CRITICAL: { color: '#f85149', bg: '#2e1a1a', border: '#f85149' },
          HIGH:     { color: '#f85149', bg: '#2e1a1a', border: '#f85149' },
          MEDIUM:   { color: '#d29922', bg: '#2e221a', border: '#d29922' },
          LOW:      { color: '#3fb950', bg: '#1a2e1a', border: '#3fb950' },
        };
        const c = configs[level] || configs.LOW;
        return (
          <span style={{
            color: c.color,
            background: c.bg,
            border: `1px solid ${c.border}40`,
            padding: '2px 8px',
            borderRadius: '4px',
            fontSize: '11px',
            fontWeight: '700',
            letterSpacing: '0.5px'
          }}>
            {level}
          </span>
        );
      },
    },
    {
      title: 'STATUS',
      dataIndex: 'is_fraud_predicted',
      key: 'is_fraud_predicted',
      render: (flagged: boolean) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {flagged ? (
            <>
              <AlertOutlined style={{ color: '#f85149', fontSize: '12px' }} />
              <span style={{ color: '#f85149', fontSize: '12px', fontWeight: '600' }}>FLAGGED</span>
            </>
          ) : (
            <>
              <CheckCircleOutlined style={{ color: '#3fb950', fontSize: '12px' }} />
              <span style={{ color: '#3fb950', fontSize: '12px', fontWeight: '600' }}>CLEAR</span>
            </>
          )}
        </div>
      ),
    },
    {
      title: 'TIME',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (t: string) => (
        <span style={{ color: '#484f58', fontSize: '11px', fontFamily: 'monospace' }}>
          {new Date(t).toLocaleTimeString()}
        </span>
      ),
    },
    {
      title: 'ACTION',
      key: 'action',
      render: (_: any, record: Transaction) => (
        <Button
          size="small"
          icon={<EyeOutlined />}
          onClick={() => handleInvestigate(record.transaction_id)}
          style={{
            background: record.is_fraud_predicted ? '#2e1a1a' : '#1a2744',
            border: `1px solid ${record.is_fraud_predicted ? '#f85149' : '#58a6ff'}`,
            color: record.is_fraud_predicted ? '#f85149' : '#58a6ff',
            borderRadius: '4px',
            fontSize: '11px',
          }}
        >
          Investigate
        </Button>
      ),
    },
  ];

  return (
    <div>
      {/* Page Header */}
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
          <EyeOutlined style={{ color: '#58a6ff' }} />
          Investigation Queue
        </h1>
        <p style={{ color: '#484f58', margin: '4px 0 0', fontSize: '13px' }}>
          Real-time transaction monitoring powered by XGBoost + GNN ensemble with SHAP explainability
        </p>
      </div>

      {/* Live Simulator */}
      <LiveSimulator onNewTransaction={fetchTransactions} />

      {/* Pipeline Flow */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0',
        marginBottom: '24px',
        background: '#0d1421',
        border: '1px solid #1a2744',
        borderRadius: '8px',
        padding: '12px 20px',
        overflowX: 'auto',
      }}>
        {[
          { label: 'Transaction In', icon: '💳', color: '#58a6ff', desc: 'Kafka Topic' },
          { label: 'Feature Engineering', icon: '⚙️', color: '#d29922', desc: 'Redis Velocity' },
          { label: 'Graph Analysis', icon: '🕸️', color: '#a371f7', desc: 'Neo4j GNN' },
          { label: 'ML Ensemble', icon: '🤖', color: '#3fb950', desc: 'XGBoost + IF' },
          { label: 'SHAP Explain', icon: '📊', color: '#f0883e', desc: 'Explainability' },
          { label: 'Decision', icon: '⚖️', color: '#f85149', desc: 'Approve / Block' },
        ].map((step, i, arr) => (
          <React.Fragment key={i}>
            <div style={{ textAlign: 'center', minWidth: '90px' }}>
              <div style={{
                fontSize: '18px',
                marginBottom: '4px',
                filter: 'drop-shadow(0 0 4px ' + step.color + ')'
              }}>
                {step.icon}
              </div>
              <div style={{ color: step.color, fontSize: '10px', fontWeight: '700', letterSpacing: '0.3px' }}>
                {step.label}
              </div>
              <div style={{ color: '#484f58', fontSize: '9px', marginTop: '2px' }}>
                {step.desc}
              </div>
            </div>
            {i < arr.length - 1 && (
              <div style={{
                flex: 1,
                height: '1px',
                background: 'linear-gradient(90deg, #1a2744, #58a6ff40, #1a2744)',
                minWidth: '20px',
                position: 'relative',
              }}>
                <div style={{
                  position: 'absolute',
                  right: '-4px',
                  top: '-4px',
                  color: '#58a6ff',
                  fontSize: '10px'
                }}>›</div>
              </div>
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Stats */}
      <Row gutter={16} style={{ marginBottom: '20px' }}>
        {[
          {
            title: 'Total Scored',
            value: total,
            color: '#58a6ff',
            bg: '#0d1a2e',
            border: '#1a2744',
            icon: <ThunderboltOutlined />,
          },
          {
            title: 'Flagged',
            value: flagged,
            color: '#f85149',
            bg: '#1e0d0d',
            border: '#2e1a1a',
            icon: <AlertOutlined />,
          },
          {
            title: 'High Risk',
            value: highRisk,
            color: '#d29922',
            bg: '#1e1a0d',
            border: '#2e221a',
            icon: <RiseOutlined />,
          },
          {
            title: 'Avg Fraud Score',
            value: `${avgScore}%`,
            color: '#3fb950',
            bg: '#0d1e0d',
            border: '#1a2e1a',
            icon: <EyeOutlined />,
          },
        ].map((stat, i) => (
          <Col span={6} key={i}>
            <div style={{
              background: stat.bg,
              border: `1px solid ${stat.border}`,
              borderRadius: '8px',
              padding: '16px 20px',
              display: 'flex',
              alignItems: 'center',
              gap: '16px'
            }}>
              <div style={{
                fontSize: '22px',
                color: stat.color,
                opacity: 0.8
              }}>
                {stat.icon}
              </div>
              <div>
                <div style={{ color: '#484f58', fontSize: '11px', marginBottom: '4px', letterSpacing: '0.5px' }}>
                  {stat.title.toUpperCase()}
                </div>
                <div style={{ color: stat.color, fontSize: '24px', fontWeight: '700', lineHeight: 1 }}>
                  {stat.value}
                </div>
              </div>
            </div>
          </Col>
        ))}
      </Row>

      {/* Transaction Table */}
      <div style={{
        background: '#0d1421',
        border: '1px solid #1a2744',
        borderRadius: '8px',
        overflow: 'hidden'
      }}>
        <div style={{
          padding: '14px 20px',
          borderBottom: '1px solid #1a2744',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ color: '#e6edf3', fontWeight: '600', fontSize: '14px' }}>
              Recent Transactions
            </span>
            <Badge
              count={flagged}
              style={{ background: '#f85149', fontSize: '10px' }}
            />
          </div>
          <Button
            size="small"
            onClick={fetchTransactions}
            style={{
              background: '#1a2744',
              border: '1px solid #30363d',
              color: '#8b949e',
              fontSize: '11px'
            }}
          >
            🔄 Refresh
          </Button>
        </div>
        <Table
          columns={columns}
          dataSource={transactions}
          rowKey="transaction_id"
          loading={loading}
          pagination={{ pageSize: 15, size: 'small' }}
          size="small"
          style={{ background: '#0d1421' }}
        />
      </div>
    </div>
  );
};

export default Dashboard;