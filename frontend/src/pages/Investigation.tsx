import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, message, Input } from 'antd';
import {
  ArrowLeftOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  RobotOutlined,
  BarChartOutlined,
  SafetyOutlined,
} from '@ant-design/icons';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer,
} from 'recharts';
import { getTransaction, approveCase, blockCase, createCase } from '../api/client';
import { api } from '../api/client';

const { TextArea } = Input;

const Investigation: React.FC = () => {
  const { transactionId } = useParams<{ transactionId: string }>();
  const navigate = useNavigate();
  const [tx, setTx] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [notes, setNotes] = useState('');
  const [caseId, setCaseId] = useState('');
  const [decided, setDecided] = useState(false);

  // ── Single useEffect: load + retry + on-demand LLM trigger + polling ──
  useEffect(() => {
    let pollInterval: NodeJS.Timeout | null = null;
    let pollCount = 0;

    const load = async (retries = 3) => {
      try {
        const res = await getTransaction(transactionId!);
        setTx(res.data);

        // Create case — ignore if already exists
        try {
          const caseRes = await createCase(transactionId!);
          setCaseId(caseRes.data.case_id);
        } catch {}

        // Trigger on-demand LLM if no explanation yet
        const txData = res.data;
        const needsLLM =
          !txData.llm_explanation ||
          txData.llm_explanation === 'Generating explanation...' ||
          txData.llm_explanation.length < 20;
        if (needsLLM) {
          api.post(`/api/transactions/${transactionId}/explain`).catch(() => {});
        }

        // Poll every 4 seconds for SHAP + LLM updates (max 2 minutes)
        pollInterval = setInterval(async () => {
          pollCount++;
          if (pollCount > 30) {
            if (pollInterval) clearInterval(pollInterval);
            return;
          }
          try {
            const updated = await getTransaction(transactionId!);
            const d = updated.data;
            const hasShap =
              d.shap_values && Object.keys(d.shap_values).length > 0;
            const hasLlm =
              d.llm_explanation &&
              d.llm_explanation !== 'Generating explanation...' &&
              d.llm_explanation.length > 30;

            if (hasShap || hasLlm) {
              setTx(d);
              // Stop polling once both are ready
              if (hasShap && hasLlm && pollInterval) {
                clearInterval(pollInterval);
              }
            }
          } catch {}
        }, 4000);

      } catch (err) {
        // Retry up to 3 times with 1.5s gap (handles timing race on fresh transactions)
        if (retries > 0) {
          setTimeout(() => load(retries - 1), 1500);
        } else {
          message.error('Failed to load transaction');
          setLoading(false);
        }
        return;
      }
      setLoading(false);
    };

    load();

    // Cleanup on unmount
    return () => {
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [transactionId]);

  const handleApprove = async () => {
    try {
      await approveCase(caseId, notes);
      message.success('✅ Transaction approved — marked as legitimate');
      setDecided(true);
      setTimeout(() => navigate('/'), 1500);
    } catch {
      message.error('Failed to approve');
    }
  };

  const handleBlock = async () => {
    try {
      await blockCase(caseId, notes);
      message.success('🚫 Transaction blocked — confirmed fraud');
      setDecided(true);
      setTimeout(() => navigate('/'), 1500);
    } catch {
      message.error('Failed to block');
    }
  };

  if (loading)
    return (
      <div style={{ color: '#58a6ff', padding: '60px', textAlign: 'center', fontSize: '14px' }}>
        <div style={{ fontSize: '32px', marginBottom: '16px' }}>👁️</div>
        Analyzing transaction...
      </div>
    );

  if (!tx)
    return (
      <div style={{ color: '#f85149', padding: '40px', textAlign: 'center' }}>
        Transaction not found
      </div>
    );

  const shapData = Object.entries(tx.shap_values || {})
    .map(([name, value]: [string, any]) => ({
      name: name.length > 12 ? name.substring(0, 12) + '..' : name,
      value: parseFloat(parseFloat(value).toFixed(4)),
    }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    .slice(0, 10);

  const fraudPct = (tx.fraud_score * 100).toFixed(1);
  const scoreNum = parseFloat(fraudPct);
  const riskColor =
    scoreNum >= 70 ? '#f85149' : scoreNum >= 40 ? '#d29922' : '#3fb950';
  const riskBg =
    scoreNum >= 70 ? '#2e1a1a' : scoreNum >= 40 ? '#2e221a' : '#1a2e1a';

  const gaugeSegments = [
    { label: 'LOW',      color: '#3fb950', active: scoreNum < 30 },
    { label: 'MEDIUM',   color: '#d29922', active: scoreNum >= 30 && scoreNum < 50 },
    { label: 'HIGH',     color: '#f0883e', active: scoreNum >= 50 && scoreNum < 75 },
    { label: 'CRITICAL', color: '#f85149', active: scoreNum >= 75 },
  ];

  const llmText =
    tx.llm_explanation && tx.llm_explanation.length > 20
      ? tx.llm_explanation
      : null;

  return (
    <div>
      {/* ── Header ── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/')}
          style={{ background: '#1a2744', border: '1px solid #30363d', color: '#8b949e' }}
        >
          Back
        </Button>
        <div>
          <h1 style={{ color: '#e6edf3', fontSize: '18px', fontWeight: '700', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertOutlined style={{ color: riskColor }} />
            Case Investigation
          </h1>
          <p style={{ color: '#484f58', margin: '2px 0 0', fontSize: '12px', fontFamily: 'monospace' }}>
            TXN: {transactionId}
          </p>
        </div>
        <div style={{ marginLeft: 'auto' }}>
          <div style={{ background: riskBg, border: `1px solid ${riskColor}`, borderRadius: '8px', padding: '8px 20px', textAlign: 'center' }}>
            <div style={{ color: riskColor, fontSize: '28px', fontWeight: '800', lineHeight: 1 }}>
              {fraudPct}%
            </div>
            <div style={{ color: riskColor, fontSize: '10px', fontWeight: '700', letterSpacing: '1px' }}>
              FRAUD SCORE
            </div>
          </div>
        </div>
      </div>

      {/* ── Risk Meter ── */}
      <div style={{ background: '#0d1421', border: '1px solid #1a2744', borderRadius: '8px', padding: '16px 20px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span style={{ color: '#8b949e', fontSize: '12px', fontWeight: '600', minWidth: '80px' }}>
          RISK METER
        </span>
        <div style={{ flex: 1, display: 'flex', gap: '4px' }}>
          {gaugeSegments.map((seg, i) => (
            <div key={i} style={{ flex: 1 }}>
              <div style={{
                height: '8px',
                background: seg.active ? seg.color : `${seg.color}30`,
                borderRadius: i === 0 ? '4px 0 0 4px' : i === gaugeSegments.length - 1 ? '0 4px 4px 0' : '0',
                boxShadow: seg.active ? `0 0 8px ${seg.color}` : 'none',
                transition: 'all 0.3s ease',
              }} />
              <div style={{ color: seg.active ? seg.color : '#484f58', fontSize: '9px', marginTop: '4px', fontWeight: seg.active ? '700' : '400', textAlign: 'center' }}>
                {seg.label}
              </div>
            </div>
          ))}
        </div>
        <div style={{ background: riskBg, border: `1px solid ${riskColor}40`, borderRadius: '4px', padding: '4px 10px', color: riskColor, fontSize: '12px', fontWeight: '700', minWidth: '80px', textAlign: 'center' }}>
          {tx.risk_level}
        </div>
      </div>

      {/* ── Main Grid: Details + AI Explanation ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>

        {/* Transaction Details */}
        <div style={{ background: '#0d1421', border: '1px solid #1a2744', borderRadius: '8px', overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid #1a2744', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <SafetyOutlined style={{ color: '#58a6ff' }} />
            <span style={{ color: '#e6edf3', fontWeight: '600', fontSize: '13px' }}>Transaction Details</span>
          </div>
          <div style={{ padding: '16px' }}>
            {[
              { label: 'Account ID',       value: tx.account_id,                                           color: '#58a6ff' },
              { label: 'Amount',           value: `₹${tx.amount?.toLocaleString('en-IN')}`,                color: '#e6edf3', bold: true },
              { label: 'Country',          value: tx.country || 'N/A',                                     color: '#e6edf3' },
              { label: 'XGBoost Score',    value: `${((tx.xgboost_score || 0) * 100).toFixed(1)}%`,        color: '#d29922' },
              { label: 'Isolation Score',  value: `${((tx.isolation_score || 0) * 100).toFixed(1)}%`,      color: '#a371f7' },
              { label: 'Scored At',        value: new Date(tx.created_at).toLocaleString(),                color: '#484f58' },
            ].map((row, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: i < 5 ? '1px solid #1a2744' : 'none' }}>
                <span style={{ color: '#484f58', fontSize: '12px' }}>{row.label}</span>
                <span style={{ color: row.color, fontSize: '12px', fontWeight: row.bold ? '700' : '500', fontFamily: 'monospace' }}>
                  {row.value}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* AI Explanation */}
        <div style={{ background: '#0d1421', border: '1px solid #1a2744', borderRadius: '8px', overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid #1a2744', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <RobotOutlined style={{ color: '#a371f7' }} />
            <span style={{ color: '#e6edf3', fontWeight: '600', fontSize: '13px' }}>AI Explanation</span>
            <span style={{ background: '#1a0d2e', border: '1px solid #a371f7', color: '#a371f7', fontSize: '9px', padding: '1px 6px', borderRadius: '4px', marginLeft: 'auto', fontWeight: '700' }}>
              LLM · LLAMA3
            </span>
          </div>
          <div style={{ padding: '16px' }}>
            {llmText ? (
              <p style={{ color: '#c9d1d9', lineHeight: '1.7', fontSize: '13px', marginBottom: '16px', fontStyle: 'italic' }}>
                "{llmText}"
              </p>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px', padding: '12px', background: '#0a1628', borderRadius: '6px', border: '1px solid #1a2744' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#a371f7', animation: 'pulse 1.5s infinite' }} />
                <span style={{ color: '#8b949e', fontSize: '12px' }}>
                  Generating AI explanation... (updates automatically)
                </span>
                <style>{`@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}`}</style>
              </div>
            )}

            {tx.triggered_rules?.length > 0 && (
              <div>
                <div style={{ color: '#484f58', fontSize: '10px', fontWeight: '700', letterSpacing: '1px', marginBottom: '8px' }}>
                  TRIGGERED RULES
                </div>
                {tx.triggered_rules.map((rule: string, i: number) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', marginBottom: '6px' }}>
                    <span style={{ color: '#f85149', fontSize: '10px', marginTop: '2px' }}>⚠</span>
                    <span style={{ color: '#d29922', fontSize: '11px', background: '#2e221a', padding: '3px 8px', borderRadius: '4px', border: '1px solid #d2992230' }}>
                      {rule}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── SHAP Chart ── */}
      <div style={{ background: '#0d1421', border: '1px solid #1a2744', borderRadius: '8px', overflow: 'hidden', marginBottom: '16px' }}>
        <div style={{ padding: '12px 16px', borderBottom: '1px solid #1a2744', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChartOutlined style={{ color: '#f0883e' }} />
            <span style={{ color: '#e6edf3', fontWeight: '600', fontSize: '13px' }}>SHAP Feature Importance</span>
          </div>
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            <span style={{ color: '#484f58', fontSize: '10px' }}>
              Each bar shows how much a feature pushed the fraud score up (red) or down (green)
            </span>
            <span style={{ color: '#f85149', fontSize: '11px' }}>■ Increases fraud</span>
            <span style={{ color: '#3fb950', fontSize: '11px' }}>■ Decreases fraud</span>
          </div>
        </div>
        <div style={{ padding: '16px' }}>
          {shapData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={shapData} layout="vertical" margin={{ left: 10, right: 20 }}>
                <XAxis type="number" stroke="#484f58" tick={{ fontSize: 10, fill: '#484f58' }} axisLine={{ stroke: '#1a2744' }} />
                <YAxis type="category" dataKey="name" stroke="#484f58" width={110} tick={{ fontSize: 10, fill: '#8b949e' }} axisLine={{ stroke: '#1a2744' }} />
                <Tooltip
                  contentStyle={{ background: '#0d1421', border: '1px solid #1a2744', color: '#e6edf3', borderRadius: '6px', fontSize: '12px' }}
                  labelStyle={{ color: '#e6edf3' }}
                  itemStyle={{ color: '#e6edf3' }}
                  formatter={(value: any) => [`${parseFloat(value).toFixed(4)}`, 'SHAP Value']}
                />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {shapData.map((entry, i) => (
                    <Cell key={i} fill={entry.value > 0 ? '#f85149' : '#3fb950'} opacity={0.85} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#484f58' }}>
              <BarChartOutlined style={{ fontSize: '32px', marginBottom: '8px', display: 'block' }} />
              <div>Loading SHAP analysis...</div>
              <div style={{ fontSize: '11px', marginTop: '6px', color: '#30363d' }}>
                Updates automatically within a few seconds
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── Analyst Decision ── */}
      {!decided ? (
        <div style={{ background: '#0d1421', border: '1px solid #1a2744', borderRadius: '8px', overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid #1a2744', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ color: '#e6edf3', fontWeight: '600', fontSize: '13px' }}>⚖️ Analyst Decision</span>
            <span style={{ color: '#484f58', fontSize: '11px', marginLeft: 'auto' }}>Case ID: {caseId}</span>
          </div>
          <div style={{ padding: '16px' }}>
            <TextArea
              rows={3}
              placeholder="Add investigation notes (optional) — e.g. 'Confirmed fraud ring based on device fingerprint overlap'"
              value={notes}
              onChange={e => setNotes(e.target.value)}
              style={{ marginBottom: '16px', background: '#0a0f1e', color: '#e6edf3', borderColor: '#1a2744', borderRadius: '6px', fontSize: '12px' }}
            />
            <div style={{ display: 'flex', gap: '12px' }}>
              <Button
                onClick={handleApprove}
                icon={<CheckCircleOutlined />}
                style={{ flex: 1, height: '44px', background: '#0a1e0a', border: '1px solid #3fb950', color: '#3fb950', fontWeight: '700', fontSize: '13px', borderRadius: '6px' }}
              >
                ✅ Approve — Legitimate Transaction
              </Button>
              <Button
                onClick={handleBlock}
                icon={<AlertOutlined />}
                style={{ flex: 1, height: '44px', background: '#1e0a0a', border: '1px solid #f85149', color: '#f85149', fontWeight: '700', fontSize: '13px', borderRadius: '6px' }}
              >
                🚫 Block — Confirmed Fraud
              </Button>
            </div>
          </div>
        </div>
      ) : (
        <div style={{ background: '#0a1e0a', border: '1px solid #3fb950', borderRadius: '8px', padding: '24px', textAlign: 'center' }}>
          <CheckCircleOutlined style={{ color: '#3fb950', fontSize: '32px', marginBottom: '8px', display: 'block' }} />
          <span style={{ color: '#3fb950', fontSize: '16px', fontWeight: '700' }}>
            Decision recorded. Returning to queue...
          </span>
        </div>
      )}
    </div>
  );
};

export default Investigation;
