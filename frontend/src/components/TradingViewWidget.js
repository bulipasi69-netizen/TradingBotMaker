import React, { useEffect, useRef } from 'react';

const TradingViewWidget = ({
  symbol = 'NASDAQ:AAPL',
  interval = 'D',
  timezone = 'Etc/UTC',
  theme = 'dark',
  style = '1',
  locale = 'en',
  autosize = true,
  allowSymbolChange = true,
}) => {
  const containerRef = useRef(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Clear any previous widget
    container.innerHTML = '';

    // Create and configure the TradingView script
    const script = document.createElement('script');
    script.src =
      'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
    script.async = true;
    script.innerHTML = JSON.stringify({
      autosize,
      symbol,
      interval,
      timezone,
      theme,
      style,
      locale,
      allow_symbol_change: allowSymbolChange,
      support_host: 'https://www.tradingview.com',
    });

    // Append the script into our container
    container.appendChild(script);

    // Cleanup on unmount: clears the same container element
    return () => {
      container.innerHTML = '';
    };
  }, [
    symbol,
    interval,
    timezone,
    theme,
    style,
    locale,
    autosize,
    allowSymbolChange,
  ]);

  return (
    <div
      className="tradingview-widget-container"
      style={{ height: '100%', width: '100%' }}
    >
      <div
        ref={containerRef}
        className="tradingview-widget-container__widget"
        style={{ height: 'calc(100% - 32px)', width: '100%' }}
      />
      <div className="tradingview-widget-copyright">
        <a
          href="https://www.tradingview.com/"
          rel="noopener nofollow"
          target="_blank"
        >
          <span className="blue-text">Track all markets on TradingView</span>
        </a>
      </div>
    </div>
  );
};

export default TradingViewWidget;
