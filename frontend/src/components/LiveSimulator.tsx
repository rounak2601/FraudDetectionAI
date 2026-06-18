import React, { useState, useRef, useEffect } from 'react';
import { api } from '../api/client';

// Realistic transaction scenarios with varied risk levels
// Weight = how often this scenario appears (higher = more frequent)
const SCENARIOS = [
  // ── NORMAL / LOW risk (weight 3 each = frequent) ──────────
  {
    weight: 3, label: 'LOW',
    data: { account_id: 'ACC0101', amount: 450, merchant_category: 'GROCERY',
      country: 'IN', device_id: 'DEV001', ip_address: '192.168.1.1',
      card4: 'visa', card6: 'credit', P_emaildomain: 'gmail.com',
      R_emaildomain: 'gmail.com', addr1: 299, addr2: 87, dist1: 2,
      C1:1, C2:1, C3:0, C4:0, C5:0, C6:1, C7:0, C8:0, C9:1, C10:0,
      V1:1, V2:1, V3:1, V4:1, V5:1, V6:1, V7:1, V8:1, V9:1, V10:1 }
  },
  {
    weight: 3, label: 'LOW',
    data: { account_id: 'ACC0102', amount: 1200, merchant_category: 'RESTAURANT',
      country: 'IN', device_id: 'DEV002', ip_address: '192.168.1.2',
      card4: 'visa', card6: 'credit', P_emaildomain: 'yahoo.com',
      R_emaildomain: 'yahoo.com', addr1: 150, addr2: 87, dist1: 5,
      C1:1, C2:1, C3:0, C4:0, C5:0, C6:1, C7:0, C8:0, C9:1, C10:0,
      V1:1, V2:1, V3:1, V4:1, V5:1, V6:1, V7:1, V8:1, V9:1, V10:1 }
  },
  {
    weight: 3, label: 'LOW',
    data: { account_id: 'ACC0103', amount: 340, merchant_category: 'PHARMACY',
      country: 'US', device_id: 'DEV003', ip_address: '10.0.0.1',
      card4: 'mastercard', card6: 'credit', P_emaildomain: 'outlook.com',
      R_emaildomain: 'outlook.com', addr1: 200, addr2: 87, dist1: 1,
      C1:1, C2:1, C3:0, C4:0, C5:0, C6:1, C7:0, C8:0, C9:1, C10:0,
      V1:1, V2:1, V3:1, V4:1, V5:1, V6:1, V7:1, V8:1, V9:1, V10:1 }
  },
  {
    weight: 2, label: 'LOW',
    data: { account_id: 'ACC0104', amount: 850, merchant_category: 'FUEL',
      country: 'IN', device_id: 'DEV004', ip_address: '172.16.0.1',
      card4: 'visa', card6: 'debit', P_emaildomain: 'gmail.com',
      R_emaildomain: 'gmail.com', addr1: 320, addr2: 87, dist1: 3,
      C1:1, C2:2, C3:0, C4:0, C5:0, C6:1, C7:0, C8:0, C9:1, C10:0,
      V1:1, V2:1, V3:1, V4:1, V5:1, V6:1, V7:1, V8:1, V9:1, V10:1 }
  },
  {
    weight: 2, label: 'LOW',
    data: { account_id: 'ACC0105', amount: 2500, merchant_category: 'ONLINE',
      country: 'UK', device_id: 'DEV005', ip_address: '192.168.2.1',
      card4: 'discover', card6: 'credit', P_emaildomain: 'gmail.com',
      R_emaildomain: 'amazon.com', addr1: 180, addr2: 87, dist1: 10,
      C1:1, C2:1, C3:0, C4:0, C5:0, C6:1, C7:0, C8:0, C9:1, C10:0,
      V1:1, V2:1, V3:1, V4:1, V5:1, V6:1, V7:1, V8:1, V9:1, V10:1 }
  },
  // ── MEDIUM risk (weight 2 each) ────────────────────────────
  {
    weight: 2, label: 'MEDIUM',
    data: { account_id: 'ACC0301', amount: 15000, merchant_category: 'ONLINE',
      country: 'DE', device_id: 'DEV020', ip_address: '85.214.1.1',
      card4: 'visa', card6: 'debit', P_emaildomain: 'gmail.com',
      R_emaildomain: 'gmail.com', addr1: 350, addr2: 87, dist1: 80,
      C1:2, C2:3, C3:1, C4:0, C5:0, C6:1, C7:1, C8:0, C9:1, C10:0,
      V1:1, V2:0, V3:1, V4:0, V5:1, V6:0, V7:1, V8:0, V9:1, V10:0 }
  },
  {
    weight: 2, label: 'MEDIUM',
    data: { account_id: 'ACC0302', amount: 22000, merchant_category: 'TRAVEL',
      country: 'FR', device_id: 'DEV021', ip_address: '80.67.1.1',
      card4: 'mastercard', card6: 'debit', P_emaildomain: 'hotmail.com',
      R_emaildomain: 'hotmail.com', addr1: 280, addr2: 87, dist1: 120,
      C1:2, C2:3, C3:1, C4:0, C5:0, C6:1, C7:1, C8:0, C9:1, C10:0,
      V1:1, V2:0, V3:1, V4:0, V5:1, V6:0, V7:1, V8:0, V9:1, V10:0 }
  },
  // ── HIGH / CRITICAL risk (weight 1 each) ───────────────────
  // KEY: amount > 10000 triggers HIGH_AMOUNT rule (+0.1)
  //      amount > 10000 triggers VERY_HIGH_AMOUNT rule (+0.1)  <- need > 10k not > 5k
  //      P_emaildomain burner triggers BURNER_EMAIL (+0.1)
  //      R_emaildomain burner triggers BURNER_EMAIL (+0.1)
  //      addr1 = -999 triggers DEBIT_NO_ADDRESS (+0.1)
  //      Total rule boost: +0.5 on top of ML score
  //      So ML score 0.28 + 0.5 rules = 0.78 = CRITICAL
  {
    weight: 1, label: 'CRITICAL',
    data: { account_id: 'ACC0201', amount: 85000,
      merchant_category: 'ATM', country: 'NG',
      device_id: 'DEV010', ip_address: '41.58.1.1',
      card4: 'mastercard', card6: 'debit',
      P_emaildomain: 'mailinator.com', R_emaildomain: 'guerrillamail.com',
      addr1: -999, addr2: -999, dist1: 9999,
      C1:5, C2:8, C3:3, C4:2, C5:1, C6:0, C7:3, C8:12, C9:0, C10:2,
      V1:0, V2:0, V3:0, V4:0, V5:0, V6:0, V7:0, V8:0, V9:0, V10:0 }
  },
  {
    weight: 1, label: 'CRITICAL',
    data: { account_id: 'ACC0202', amount: 95000,
      merchant_category: 'ONLINE', country: 'CN',
      device_id: 'DEV011', ip_address: '58.22.1.1',
      card4: 'mastercard', card6: 'debit',
      P_emaildomain: 'guerrillamail.com', R_emaildomain: 'mailinator.com',
      addr1: -999, addr2: -999, dist1: 9999,
      C1:5, C2:8, C3:3, C4:2, C5:1, C6:0, C7:3, C8:12, C9:0, C10:2,
      V1:0, V2:0, V3:0, V4:0, V5:0, V6:0, V7:0, V8:0, V9:0, V10:0 }
  },
  {
    weight: 1, label: 'CRITICAL',
    data: { account_id: 'ACC0203', amount: 125000,
      merchant_category: 'ONLINE', country: 'NG',
      device_id: 'DEV012', ip_address: '196.216.1.1',
      card4: 'visa', card6: 'debit',
      P_emaildomain: 'throwam.com', R_emaildomain: 'mailinator.com',
      addr1: -999, addr2: -999, dist1: 9999,
      C1:5, C2:8, C3:3, C4:2, C5:1, C6:0, C7:3, C8:12, C9:0, C10:2,
      V1:0, V2:0, V3:0, V4:0, V5:0, V6:0, V7:0, V8:0, V9:0, V10:0 }
  },
];

// Build weighted pool
const POOL: any[] = [];
SCENARIOS.forEach(s => {
  for (let i = 0; i < s.weight; i++) POOL.push(s);
});

interface LiveSimulatorProps {
  onNewTransaction?: () => void;
}

const LiveSimulator: React.FC<LiveSimulatorProps> = ({ onNewTransaction }) => {
  const [count, setCount]     = useState(0);
  const [lastRisk, setLastRisk] = useState('');
  const [status, setStatus]   = useState<'ok' | 'error' | 'connecting'>('connecting');
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const sendTransaction = async () => {
    const scenario = POOL[Math.floor(Math.random() * POOL.length)];
    // Add ±15% random variation to amount so each transaction looks different
    const tx = {
      ...scenario.data,
      amount: Math.round(scenario.data.amount * (0.85 + Math.random() * 0.30)),
      // Vary account suffix slightly for realism
      account_id: scenario.data.account_id.slice(0, -1) +
                  Math.floor(Math.random() * 5),
    };

    try {
      await api.post('/api/transactions/score', tx);
      setCount(c => c + 1);
      setLastRisk(scenario.label);
      setStatus('ok');
      if (onNewTransaction) onNewTransaction();
    } catch {
      setStatus('error');
    }
  };

  useEffect(() => {
    // Start immediately, then every 5 seconds
    sendTransaction();
    intervalRef.current = setInterval(sendTransaction, 5000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  const dotColor = status === 'ok' ? '#3fb950'
                 : status === 'error' ? '#f85149' : '#d29922';
  const riskColor = lastRisk === 'CRITICAL' ? '#f85149'
                  : lastRisk === 'HIGH' ? '#f0883e'
                  : lastRisk === 'MEDIUM' ? '#d29922' : '#3fb950';

  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '12px',
      background: '#161b22', border: '1px solid #30363d',
      borderRadius: '8px', padding: '10px 16px', marginBottom: '20px',
      fontSize: '12px', flexWrap: 'wrap',
    }}>
      <span style={{ color: '#8b949e', fontWeight: 600 }}>⚡ Auto Feed</span>
      <span style={{
        width: 8, height: 8, borderRadius: '50%', background: dotColor,
        display: 'inline-block', boxShadow: `0 0 6px ${dotColor}`,
        animation: 'pulse 1.5s infinite'
      }}/>
      <span style={{ color: dotColor, fontWeight: 700 }}>
        {status === 'ok' ? 'LIVE' : status === 'error' ? 'ERROR' : 'CONNECTING'}
      </span>
      <span style={{ color: '#484f58' }}>·</span>
      <span style={{ color: '#8b949e' }}>{count} sent</span>
      {lastRisk && (
        <>
          <span style={{ color: '#484f58' }}>·</span>
          <span style={{ color: '#484f58', fontSize: '11px' }}>Last:</span>
          <span style={{
            color: riskColor, fontWeight: 700, fontSize: '11px',
            background: `${riskColor}20`, padding: '1px 8px',
            borderRadius: '4px', border: `1px solid ${riskColor}40`
          }}>{lastRisk}</span>
        </>
      )}
      <span style={{ color: '#484f58' }}>· Every 5s · Mix of LOW/MEDIUM/CRITICAL</span>
      <style>{`@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}`}</style>
    </div>
  );
};

export default LiveSimulator;