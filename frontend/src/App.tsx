import React from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  MonitorOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import Dashboard from './pages/Dashboard';
import Investigation from './pages/Investigation';
import Monitoring from './pages/Monitoring';
import Landing from './pages/Landing';
import Logo from './components/Logo';

const { Sider, Content, Header } = Layout;

const App: React.FC = () => {
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined style={{ color: '#58a6ff' }} />,
      label: <Link to="/" style={{ color: 'inherit' }}>Home</Link>,
    },
    {
      key: '/dashboard',
      icon: <EyeOutlined style={{ color: '#58a6ff' }} />,
      label: <Link to="/dashboard" style={{ color: 'inherit' }}>Investigation Queue</Link>,
    },
    {
      key: '/monitoring',
      icon: <MonitorOutlined style={{ color: '#3fb950' }} />,
      label: <Link to="/monitoring" style={{ color: 'inherit' }}>Live Monitoring</Link>,
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh', background: '#0a0f1e' }}>
      <Sider
        width={220}
        style={{
          background: '#0d1421',
          borderRight: '1px solid #1a2744',
          position: 'fixed',
          height: '100vh',
          left: 0,
          top: 0,
          zIndex: 100,
        }}
      >
        {/* Logo */}
        <div style={{
          padding: '20px 16px',
          borderBottom: '1px solid #1a2744',
          marginBottom: '8px'
        }}>
          <Logo size={28} showText={true} />
        </div>

        {/* System Status */}
        <div style={{
          margin: '0 12px 16px',
          padding: '8px 12px',
          background: '#0a1628',
          borderRadius: '6px',
          border: '1px solid #1a2744',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <div style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            background: '#3fb950',
            boxShadow: '0 0 6px #3fb950',
            animation: 'glow 2s infinite'
          }} />
          <span style={{ color: '#3fb950', fontSize: '11px', fontWeight: '600' }}>
            SYSTEM ONLINE
          </span>
        </div>

        <Menu
          mode="inline"
          selectedKeys={[location.pathname.startsWith('/investigation') ? '/' : location.pathname]}
          style={{
            background: '#0d1421',
            border: 'none',
            color: '#8b949e'
          }}
          items={menuItems}
        />

        {/* Bottom info */}
        <div style={{
          position: 'absolute',
          bottom: '16px',
          left: '12px',
          right: '12px',
          padding: '10px 12px',
          background: '#0a1628',
          borderRadius: '6px',
          border: '1px solid #1a2744',
        }}>
          <div style={{ color: '#8b949e', fontSize: '10px', marginBottom: '4px' }}>
            MODEL VERSION
          </div>
          <div style={{ color: '#58a6ff', fontSize: '11px', fontWeight: '600' }}>
            XGBoost + GNN v2.1
          </div>
          <div style={{ color: '#8b949e', fontSize: '10px', marginTop: '4px' }}>
            Trained on IEEE-CIS Dataset
          </div>
        </div>
      </Sider>

      <Layout style={{ marginLeft: 220, background: '#0a0f1e' }}>
        <Header style={{
          background: '#0d1421',
          borderBottom: '1px solid #1a2744',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 99,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <EyeOutlined style={{ color: '#58a6ff' }} />
            <span style={{ color: '#8b949e', fontSize: '13px' }}>
              Real-Time Financial Fraud Detection & Explainable AI
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span style={{ color: '#8b949e', fontSize: '12px' }}>
              Latency: <span style={{ color: '#3fb950' }}>~50ms</span>
            </span>
            <span style={{ color: '#8b949e', fontSize: '12px' }}>
              Models: <span style={{ color: '#58a6ff' }}>3 Active</span>
            </span>
            <div style={{
              color: '#3fb950',
              fontSize: '11px',
              background: '#0a1e0a',
              padding: '4px 12px',
              borderRadius: '12px',
              border: '1px solid #3fb950',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span style={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                background: '#3fb950',
                display: 'inline-block',
              }}/>
              LIVE
            </div>
          </div>
        </Header>

        <Content style={{ padding: '24px', background: '#0a0f1e', minHeight: 'calc(100vh - 64px)' }}>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/investigation/:transactionId" element={<Investigation />} />
            <Route path="/monitoring" element={<Monitoring />} />
          </Routes>
        </Content>
      </Layout>

      <style>{`
        @keyframes glow {
          0%, 100% { opacity: 1; box-shadow: 0 0 6px #3fb950; }
          50% { opacity: 0.6; box-shadow: 0 0 12px #3fb950; }
        }
        .ant-menu-item-selected {
          background: #1a2744 !important;
          border-right: 2px solid #58a6ff !important;
        }
        .ant-menu-item-selected a {
          color: #58a6ff !important;
        }
        .ant-menu-item:hover {
          background: #1a2744 !important;
        }
      `}</style>
    </Layout>
  );
};

export default App;