import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Logo from '../components/Logo';

const DEMO_TRANSACTIONS = [
  { id: '#TXN-9876', status: 'Declined', color: '#f85149', bg: '#2e1a1a', score: 89, rule: 'Blacklisted IP Address' },
  { id: '#TXN-8762', status: 'Under Review', color: '#d29922', bg: '#2e221a', score: 62, rule: 'High Velocity - 12 txns/min' },
  { id: '#TXN-7543', status: 'Approved', color: '#3fb950', bg: '#1a2e1a', score: 12, rule: null },
  { id: '#TXN-6821', status: 'Processing...', color: '#58a6ff', bg: '#1a2744', score: 45, rule: 'Burner Email Detected' },
  { id: '#TXN-5190', status: 'Declined', color: '#f85149', bg: '#2e1a1a', score: 91, rule: 'Known Fraud Ring' },
];

const FEATURES = [
  { icon: 'A', title: 'Real-Time Scoring', desc: 'Sub-50ms fraud decisions via Kafka streaming and Redis sliding-window velocity features.' },
  { icon: 'B', title: 'Graph Neural Networks', desc: 'GraphSAGE model traverses Neo4j relationship graphs to surface coordinated fraud rings invisible to tabular models.' },
  { icon: 'C', title: 'SHAP Explainability', desc: 'Every high-risk decision includes per-feature SHAP attribution showing exactly why it was flagged.' },
  { icon: 'D', title: 'LLM Narratives', desc: 'Local Mistral-7B via Ollama converts SHAP values into plain-English analyst explanations.' },
  { icon: 'E', title: 'Case Management', desc: 'Full investigation workflow - open, investigate, approve or block, with analyst notes captured per case.' },
  { icon: 'F', title: 'Tamper-Evident Audit Log', desc: 'SHA-256 hash-chained audit trail for every decision, ready for compliance review.' },
];

const PIPELINE = [
  { label: 'Transaction In', icon: '1', color: '#58a6ff', desc: 'Kafka Topic - raw_transactions' },
  { label: 'Feature Engineering', icon: '2', color: '#d29922', desc: 'Redis Sorted Sets - velocity windows' },
  { label: 'Graph Analysis', icon: '3', color: '#a371f7', desc: 'Neo4j 2-hop subgraph - GNN scoring' },
  { label: 'ML Ensemble', icon: '4', color: '#3fb950', desc: 'XGBoost (ONNX) + Isolation Forest' },
  { label: 'SHAP + LLM', icon: '5', color: '#f0883e', desc: 'TreeExplainer + Mistral-7B narrative' },
  { label: 'Analyst Decision', icon: '6', color: '#f85149', desc: 'Approve / Block + audit log' },
];

const PERFORMANCE = [
  { label: 'Designed Throughput', value: '10,000+', unit: 'TPS', color: '#58a6ff', desc: 'Kafka partitioned across topics' },
  { label: 'P99 Target Latency', value: '<50', unit: 'ms', color: '#3fb950', desc: 'End-to-end scoring decision' },
  { label: 'XGBoost Inference', value: '~2', unit: 'ms', color: '#d29922', desc: 'ONNX Runtime on CPU' },
  { label: 'Redis Feature Lookup', value: '<1', unit: 'ms', color: '#a371f7', desc: 'Sliding window counts' },
  { label: 'Model AUC-ROC', value: '94.2', unit: '%', color: '#f0883e', desc: 'IEEE-CIS fraud dataset' },
  { label: 'Neo4j Subgraph Query', value: '<10', unit: 'ms', color: '#f85149', desc: '2-hop neighborhood' },
];

const Landing: React.FC = () => {
  const navigate = useNavigate();
  const [activeIdx, setActiveIdx] = useState(0);
  const [score, setScore] = useState(0);
  const [targetScore, setTargetScore] = useState(89);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveIdx(i => (i + 1) % DEMO_TRANSACTIONS.length);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const tx = DEMO_TRANSACTIONS[activeIdx];
    setTargetScore(tx.score);
  }, [activeIdx]);

  useEffect(() => {
    const step = targetScore > score ? 3 : -3;
    if (Math.abs(score - targetScore) < 3) {
      setScore(targetScore);
      return;
    }
    const t = setTimeout(() => setScore(s => s + step), 16);
    return () => clearTimeout(t);
  }, [score, targetScore]);

  const activeTx = DEMO_TRANSACTIONS[activeIdx];
  const scoreColor = score >= 70 ? '#f85149' : score >= 40 ? '#d29922' : '#3fb950';

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #050a14 0%, #0a0f1e 40%, #0d1421 100%)',
      color: '#e6edf3',
      fontFamily: "'Inter', -apple-system, sans-serif",
    }}>

      <nav style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '16px 60px',
        borderBottom: '1px solid #1a2744',
        background: 'rgba(13,20,33,0.8)',
        backdropFilter: 'blur(10px)',

        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        <Logo size={32} showText={true} />

        <div style={{ display: 'flex', gap: '32px' }}>
          {[
            { label: 'Features', href: '#features' },
            { label: 'Architecture', href: '#architecture' },
            { label: 'Performance', href: '#performance' },
            { label: 'Docs', href: '#docs' },
          ].map(item => (
            <a key={item.label} href={item.href} style={{
              color: '#8b949e',
              fontSize: '14px',
              textDecoration: 'none',
              transition: 'color 0.2s'
            }}
            onMouseEnter={e => (e.currentTarget.style.color = '#e6edf3')}
            onMouseLeave={e => (e.currentTarget.style.color = '#8b949e')}
            >
              {item.label}
            </a>
          ))}
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: '#0a1e0a',
            border: '1px solid #3fb950',
            borderRadius: '20px',
            padding: '4px 12px',
            fontSize: '11px',
            color: '#3fb950',
            fontWeight: '700',
          }}>
            <div style={{
              width: '6px', height: '6px', borderRadius: '50%',
              background: '#3fb950',
              animation: 'glow 2s infinite'
            }} />
            LIVE DEMO
          </div>
          <button
            onClick={() => navigate('/dashboard')}
            style={{
              background: 'linear-gradient(135deg, #1565c0, #1976d2)',
              border: 'none',
              borderRadius: '8px',
              color: '#fff',
              padding: '8px 20px',
              fontSize: '13px',
              fontWeight: '700',
              cursor: 'pointer',
              boxShadow: '0 4px 15px rgba(21,101,192,0.4)',
            }}
          >
            Launch Dashboard
          </button>
        </div>
      </nav>

      <div id="home" style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '60px',
        padding: '80px 60px',
        maxWidth: '1300px',
        margin: '0 auto',
        alignItems: 'center',
      }}>
        <div>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            background: '#1a2744',
            border: '1px solid #58a6ff40',
            borderRadius: '20px',
            padding: '4px 14px',
            fontSize: '11px',
            color: '#58a6ff',
            fontWeight: '700',
            marginBottom: '24px',
            letterSpacing: '1px',
          }}>
            v2.1 - IEEE-CIS Trained - GNN + XGBoost Ensemble
          </div>

          <h1 style={{
            fontSize: '52px',
            fontWeight: '800',
            lineHeight: '1.1',
            marginBottom: '16px',
            letterSpacing: '-1px',
          }}>
            <span style={{ color: '#e6edf3' }}>AI-Powered</span>
            <br />
            <span style={{
              background: 'linear-gradient(135deg, #58a6ff, #3fb950)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}>
              Fraud Detection
            </span>
            <br />
            <span style={{ color: '#e6edf3' }}>& Explainability</span>
          </h1>

          <p style={{
            color: '#8b949e',
            fontSize: '17px',
            lineHeight: '1.7',
            marginBottom: '16px',
            maxWidth: '480px',
          }}>
            Catch More Fraud. Close Investigations Faster.
          </p>
          <p style={{
            color: '#484f58',
            fontSize: '14px',
            lineHeight: '1.7',
            marginBottom: '36px',
            maxWidth: '480px',
          }}>
            Real-time transaction scoring with XGBoost plus Graph Neural Networks,
            SHAP explainability, and LLM-powered analyst narratives.
            Processes 10,000+ transactions per second with sub-50ms latency.
          </p>

          <div style={{ display: 'flex', gap: '12px', marginBottom: '48px' }}>
            <button
              onClick={() => navigate('/dashboard')}
              style={{
                background: 'linear-gradient(135deg, #1565c0, #1976d2)',
                border: 'none',
                borderRadius: '8px',
                color: '#fff',
                padding: '14px 28px',
                fontSize: '14px',
                fontWeight: '700',
                cursor: 'pointer',
                boxShadow: '0 4px 20px rgba(21,101,192,0.4)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              Launch Dashboard
            </button>
            <button
              onClick={() => navigate('/monitoring')}
              style={{
                background: 'transparent',
                border: '1px solid #1a2744',
                borderRadius: '8px',
                color: '#8b949e',
                padding: '14px 28px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
              }}
            >
              Live Monitoring
            </button>
          </div>

          <div style={{ display: 'flex', gap: '32px' }}>
            {[
              { value: '10K+', label: 'TPS Throughput', color: '#58a6ff' },
              { value: '<50ms', label: 'P99 Latency', color: '#3fb950' },
              { value: '94.2%', label: 'AUC-ROC Score', color: '#d29922' },
              { value: '3', label: 'ML Models', color: '#a371f7' },
            ].map((s, i) => (
              <div key={i}>
                <div style={{ color: s.color, fontSize: '22px', fontWeight: '800' }}>{s.value}</div>
                <div style={{ color: '#484f58', fontSize: '11px', marginTop: '2px' }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ position: 'relative' }}>
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '300px',
            height: '300px',
            background: 'radial-gradient(circle, #1565c020 0%, transparent 70%)',
            borderRadius: '50%',
            pointerEvents: 'none',
          }} />

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>

            <div style={{
              background: '#0d1421',
              border: '1px solid #1a2744',
              borderRadius: '10px',
              overflow: 'hidden',
              gridColumn: '1',
            }}>
              <div style={{
                padding: '10px 14px',
                borderBottom: '1px solid #1a2744',
                fontSize: '11px',
                color: '#484f58',
                fontWeight: '700',
                letterSpacing: '1px'
              }}>
                LIVE TRANSACTIONS
              </div>
              {DEMO_TRANSACTIONS.map((tx, i) => (
                <div key={i} style={{
                  padding: '10px 14px',
                  borderBottom: '1px solid #1a2744',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  opacity: i === activeIdx ? 1 : 0.4,
                  transition: 'opacity 0.4s ease',
                  background: i === activeIdx ? '#1a2744' : 'transparent',
                }}>
                  <div style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    background: tx.bg,
                    border: '1px solid ' + tx.color,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '11px',
                    color: tx.color,
                    fontWeight: '700',
                    flexShrink: 0,
                  }}>
                    {tx.score > 70 ? '!' : tx.score > 40 ? '?' : 'OK'}
                  </div>
                  <div>
                    <div style={{ color: '#e6edf3', fontSize: '12px', fontWeight: '600' }}>{tx.id}</div>
                    <div style={{ color: tx.color, fontSize: '10px' }}>{tx.status}</div>
                  </div>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>

              <div style={{
                background: '#0d1421',
                border: '1px solid #1a2744',
                borderRadius: '10px',
                overflow: 'hidden',
              }}>
                <div style={{
                  padding: '8px 14px',
                  borderBottom: '1px solid #1a2744',
                  fontSize: '11px',
                  color: '#484f58',
                  fontWeight: '700',
                  letterSpacing: '1px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}>
                  RULES AND CHECKS
                  <span style={{
                    width: '6px', height: '6px', borderRadius: '50%',
                    background: '#3fb950',
                    display: 'inline-block',
                    boxShadow: '0 0 6px #3fb950',
                  }} />
                </div>
                <div style={{ padding: '10px 14px', minHeight: '50px' }}>
                  {activeTx.rule ? (
                    <div style={{
                      background: activeTx.bg,
                      border: '1px solid ' + activeTx.color + '40',
                      borderRadius: '6px',
                      padding: '6px 10px',
                      fontSize: '11px',
                      color: activeTx.color,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      animation: 'slideIn 0.3s ease',
                    }}>
                      {activeTx.rule}
                    </div>
                  ) : (
                    <div style={{ color: '#3fb950', fontSize: '11px' }}>
                      No rules triggered
                    </div>
                  )}
                </div>
              </div>

              <div style={{
                background: '#0d1421',
                border: '1px solid #1a2744',
                borderRadius: '10px',
                overflow: 'hidden',
              }}>
                <div style={{
                  padding: '8px 14px',
                  borderBottom: '1px solid #1a2744',
                  fontSize: '11px',
                  color: '#484f58',
                  fontWeight: '700',
                  letterSpacing: '1px'
                }}>
                  FRAUD SCORE
                </div>
                <div style={{ padding: '14px', textAlign: 'center' }}>
                  <div style={{
                    fontSize: '42px',
                    fontWeight: '800',
                    color: scoreColor,
                    lineHeight: 1,
                    transition: 'color 0.3s ease',
                  }}>
                    {score}
                  </div>
                  <div style={{ color: '#484f58', fontSize: '11px', marginBottom: '12px' }}>/100</div>

                  <div style={{
                    height: '6px',
                    background: '#1a2744',
                    borderRadius: '3px',
                    overflow: 'hidden',
                    marginBottom: '12px',
                  }}>
                    <div style={{
                      width: score + '%',
                      height: '100%',
                      background: 'linear-gradient(90deg, #3fb950, ' + scoreColor + ')',
                      borderRadius: '3px',
                      transition: 'width 0.1s ease',
                    }} />
                  </div>

                  <div style={{ display: 'flex', gap: '6px', justifyContent: 'center' }}>
                    {[
                      { label: 'Approve', color: '#3fb950', active: score < 40 },
                      { label: 'Review', color: '#d29922', active: score >= 40 && score < 70 },
                      { label: 'Decline', color: '#f85149', active: score >= 70 },
                    ].map((btn, i) => (
                      <div key={i} style={{
                        padding: '4px 10px',
                        borderRadius: '4px',
                        fontSize: '10px',
                        fontWeight: '700',
                        color: btn.active ? btn.color : '#484f58',
                        background: btn.active ? btn.color + '20' : '#1a2744',
                        border: '1px solid ' + (btn.active ? btn.color + '60' : '#1a2744'),
                        transition: 'all 0.3s ease',
                      }}>
                        {btn.label}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div id="features" style={{
        padding: '80px 60px',
        borderTop: '1px solid #1a2744',
        maxWidth: '1300px',
        margin: '0 auto',
      }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            background: '#1a2744',
            border: '1px solid #58a6ff40',
            borderRadius: '20px',
            padding: '4px 14px',
            fontSize: '11px',
            color: '#58a6ff',
            fontWeight: '700',
            marginBottom: '16px',
            letterSpacing: '1px',
          }}>
            CORE CAPABILITIES
          </div>
          <h2 style={{ fontSize: '32px', fontWeight: '800', margin: 0 }}>
            Everything an analyst needs, in one place
          </h2>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '20px',
        }}>
          {FEATURES.map((f, i) => (
            <div key={i} style={{
              background: '#0d1421',
              border: '1px solid #1a2744',
              borderRadius: '10px',
              padding: '24px',
            }}>
              <div style={{ color: '#58a6ff', fontSize: '12px', fontWeight: '800', marginBottom: '12px' }}>{f.icon}</div>
              <div style={{ color: '#e6edf3', fontSize: '15px', fontWeight: '700', marginBottom: '8px' }}>
                {f.title}
              </div>
              <div style={{ color: '#8b949e', fontSize: '13px', lineHeight: '1.6' }}>
                {f.desc}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div id="architecture" style={{
        padding: '80px 60px',
        borderTop: '1px solid #1a2744',
        maxWidth: '1300px',
        margin: '0 auto',
      }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            background: '#1a2744',
            border: '1px solid #3fb95040',
            borderRadius: '20px',
            padding: '4px 14px',
            fontSize: '11px',
            color: '#3fb950',
            fontWeight: '700',
            marginBottom: '16px',
            letterSpacing: '1px',
          }}>
            SYSTEM ARCHITECTURE
          </div>
          <h2 style={{ fontSize: '32px', fontWeight: '800', margin: 0 }}>
            From transaction to decision in six stages
          </h2>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: '0',
          marginBottom: '40px',
          background: '#0d1421',
          border: '1px solid #1a2744',
          borderRadius: '10px',
          padding: '24px 20px',
          overflowX: 'auto',
        }}>
          {PIPELINE.map((step, i, arr) => (
            <React.Fragment key={i}>
              <div style={{ textAlign: 'center', minWidth: '150px' }}>
                <div style={{
                  color: step.color,
                  fontSize: '12px',
                  fontWeight: '800',
                  marginBottom: '8px',
                }}>
                  STEP {step.icon}
                </div>
                <div style={{ color: step.color, fontSize: '12px', fontWeight: '700', marginBottom: '4px' }}>
                  {step.label}
                </div>
                <div style={{ color: '#484f58', fontSize: '10px', lineHeight: '1.5' }}>
                  {step.desc}
                </div>
              </div>
              {i < arr.length - 1 && (
                <div style={{
                  flex: 1,
                  height: '1px',
                  background: 'linear-gradient(90deg, #1a2744, #58a6ff40, #1a2744)',
                  minWidth: '20px',
                  marginTop: '16px',
                }} />
              )}
            </React.Fragment>
          ))}
        </div>

        <p style={{ color: '#484f58', fontSize: '12px', marginBottom: '20px', letterSpacing: '1px', textAlign: 'center' }}>
          BUILT WITH ENTERPRISE-GRADE OPEN SOURCE TECHNOLOGY
        </p>
        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
          {[
            { name: 'Apache Kafka', desc: 'Streaming' },
            { name: 'Redis', desc: 'Feature Store' },
            { name: 'Neo4j', desc: 'Graph DB' },
            { name: 'XGBoost', desc: 'ML Model' },
            { name: 'PyTorch GNN', desc: 'Graph Neural Net' },
            { name: 'SHAP', desc: 'Explainability' },
            { name: 'FastAPI', desc: 'Backend' },
            { name: 'Ollama LLM', desc: 'AI Narratives' },
          ].map((tech, i) => (
            <div key={i} style={{
              background: '#0d1421',
              border: '1px solid #1a2744',
              borderRadius: '8px',
              padding: '10px 16px',
              minWidth: '110px',
              textAlign: 'center',
            }}>
              <div style={{ color: '#e6edf3', fontSize: '12px', fontWeight: '700' }}>{tech.name}</div>
              <div style={{ color: '#484f58', fontSize: '10px', marginTop: '2px' }}>{tech.desc}</div>
            </div>
          ))}
        </div>
      </div>

      <div id="performance" style={{
        padding: '80px 60px',
        borderTop: '1px solid #1a2744',
        maxWidth: '1300px',
        margin: '0 auto',
      }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            background: '#1a2744',
            border: '1px solid #d2992240',
            borderRadius: '20px',
            padding: '4px 14px',
            fontSize: '11px',
            color: '#d29922',
            fontWeight: '700',
            marginBottom: '16px',
            letterSpacing: '1px',
          }}>
            BENCHMARKS
          </div>
          <h2 style={{ fontSize: '32px', fontWeight: '800', margin: 0 }}>
            Built for production-scale workloads
          </h2>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '20px',
        }}>
          {PERFORMANCE.map((p, i) => (
            <div key={i} style={{
              background: '#0d1421',
              border: '1px solid #1a2744',
              borderRadius: '10px',
              padding: '24px',
            }}>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginBottom: '8px' }}>
                <span style={{ color: p.color, fontSize: '32px', fontWeight: '800' }}>{p.value}</span>
                <span style={{ color: p.color, fontSize: '14px', fontWeight: '700' }}>{p.unit}</span>
              </div>
              <div style={{ color: '#e6edf3', fontSize: '13px', fontWeight: '600', marginBottom: '4px' }}>
                {p.label}
              </div>
              <div style={{ color: '#484f58', fontSize: '11px' }}>
                {p.desc}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div id="docs" style={{
        padding: '80px 60px',
        borderTop: '1px solid #1a2744',
        maxWidth: '1300px',
        margin: '0 auto',
        marginBottom: '40px',
      }}>
        <div style={{
          background: '#0d1421',
          border: '1px solid #1a2744',
          borderRadius: '12px',
          padding: '40px',
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '40px',
          alignItems: 'center',
        }}>
          <div>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              background: '#1a2744',
              border: '1px solid #a371f740',
              borderRadius: '20px',
              padding: '4px 14px',
              fontSize: '11px',
              color: '#a371f7',
              fontWeight: '700',
              marginBottom: '16px',
              letterSpacing: '1px',
            }}>
              OPEN SOURCE
            </div>
            <h2 style={{ fontSize: '26px', fontWeight: '800', margin: '0 0 12px' }}>
              Run it yourself
            </h2>
            <p style={{ color: '#8b949e', fontSize: '13px', lineHeight: '1.7', marginBottom: '20px' }}>
              The entire stack runs locally with Docker Compose, including Kafka, Redis, Neo4j,
              Postgres, and Grafana, all free and open source. No cloud account required.
            </p>
            <button
              onClick={() => window.open('https://github.com/rounak2601/FraudDetectionAI', '_blank')}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                background: 'linear-gradient(135deg, #1565c0, #1976d2)',
                border: 'none',
                borderRadius: '8px',
                color: '#fff',
                padding: '12px 24px',
                fontSize: '13px',
                fontWeight: '700',
                cursor: 'pointer',
                boxShadow: '0 4px 15px rgba(21,101,192,0.4)',
              }}
            >
              View on GitHub
            </button>
          </div>
          <div style={{
            background: '#0a0f1e',
            border: '1px solid #1a2744',
            borderRadius: '8px',
            padding: '20px',
            fontFamily: 'monospace',
            fontSize: '12px',
            color: '#8b949e',
            lineHeight: '1.8',
          }}>
            <div style={{ color: '#484f58' }}>## Clone and start infrastructure</div>
            <div style={{ color: '#3fb950' }}>git clone github.com/rounak2601/FraudDetectionAI</div>
            <div style={{ color: '#3fb950' }}>docker-compose up -d</div>
            <br/>
            <div style={{ color: '#484f58' }}>## Start the API</div>
            <div style={{ color: '#58a6ff' }}>uvicorn backend.main:app --port 8000</div>
            <br/>
            <div style={{ color: '#484f58' }}>## Start the dashboard</div>
            <div style={{ color: '#d29922' }}>cd frontend</div>
            <div style={{ color: '#d29922' }}>npm start</div>
          </div>
        </div>
      </div>

      <div style={{
        padding: '24px 60px',
        borderTop: '1px solid #1a2744',
        textAlign: 'center',
        color: '#484f58',
        fontSize: '12px',
      }}>
        FraudVision AI - Built with XGBoost, GNN, Kafka, Neo4j and FastAPI - Open Source
      </div>

      <style>{`
        @keyframes glow {
          0%, 100% { box-shadow: 0 0 4px #3fb950; }
          50% { box-shadow: 0 0 10px #3fb950; }
        }
        @keyframes slideIn {
          from { opacity: 0; transform: translateX(-8px); }
          to { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </div>
  );
};

export default Landing;
