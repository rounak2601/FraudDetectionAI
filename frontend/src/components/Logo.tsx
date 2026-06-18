import React from 'react';

interface LogoProps {
  size?: number;
  showText?: boolean;
}

const Logo: React.FC<LogoProps> = ({ size = 32, showText = true }) => {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 40 40"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Outer eye shape */}
        <ellipse cx="20" cy="20" rx="18" ry="12" fill="#0d1f3c" stroke="#1565c0" strokeWidth="1.5"/>
        {/* Iris */}
        <circle cx="20" cy="20" r="7" fill="#1565c0"/>
        {/* Pupil */}
        <circle cx="20" cy="20" r="3.5" fill="#0a0f1e"/>
        {/* AI scan lines */}
        <line x1="2" y1="20" x2="8" y2="20" stroke="#f85149" strokeWidth="1.5" strokeLinecap="round"/>
        <line x1="32" y1="20" x2="38" y2="20" stroke="#f85149" strokeWidth="1.5" strokeLinecap="round"/>
        {/* Corner brackets */}
        <path d="M4 14 L4 8 L10 8" stroke="#3fb950" strokeWidth="1.5" strokeLinecap="round" fill="none"/>
        <path d="M36 14 L36 8 L30 8" stroke="#3fb950" strokeWidth="1.5" strokeLinecap="round" fill="none"/>
        <path d="M4 26 L4 32 L10 32" stroke="#3fb950" strokeWidth="1.5" strokeLinecap="round" fill="none"/>
        <path d="M36 26 L36 32 L30 32" stroke="#3fb950" strokeWidth="1.5" strokeLinecap="round" fill="none"/>
        {/* Center dot glow */}
        <circle cx="20" cy="20" r="1.5" fill="#58a6ff"/>
      </svg>

      {showText && (
        <div>
          <div style={{
            color: '#e6edf3',
            fontWeight: '800',
            fontSize: '15px',
            letterSpacing: '0.5px',
            lineHeight: '1.2'
          }}>
            FraudVision
          </div>
          <div style={{
            background: 'linear-gradient(90deg, #58a6ff, #3fb950)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontSize: '9px',
            letterSpacing: '2.5px',
            textTransform: 'uppercase',
            fontWeight: '700'
          }}>
            AI · DETECTION
          </div>
        </div>
      )}
    </div>
  );
};

export default Logo;