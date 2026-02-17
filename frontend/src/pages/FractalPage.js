/**
 * FRACTAL RESEARCH TERMINAL v4
 * Institutional-grade pattern analysis interface
 * 
 * Features:
 * - Price Chart with Aftermath-Driven Forecast
 * - Fractal Overlay with Distribution Fan (P10-P90)
 */

import React, { useState } from 'react';
import { FractalMainChart } from '../components/fractal/chart/FractalMainChart';
import { FractalOverlaySection } from '../components/fractal/sections/FractalOverlaySection';
import { StrategyPanel } from '../components/fractal/sections/StrategyPanel';
import ForwardPerformancePanel from '../components/fractal/ForwardPerformancePanel';

// ═══════════════════════════════════════════════════════════════
// CHART MODE SWITCHER
// ═══════════════════════════════════════════════════════════════

const ChartModeSwitcher = ({ mode, onModeChange }) => {
  const modes = [
    { id: 'price', label: 'Price Chart', icon: '📈' },
    { id: 'fractal', label: 'Fractal Overlay', icon: '📐' },
  ];
  
  return (
    <div className="flex gap-1 p-1 bg-slate-100 rounded-lg" data-testid="chart-mode-switcher">
      {modes.map(m => (
        <button
          key={m.id}
          onClick={() => onModeChange(m.id)}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
            mode === m.id
              ? 'bg-white text-slate-900 shadow-sm'
              : 'text-slate-600 hover:text-slate-800 hover:bg-slate-50'
          }`}
          data-testid={`mode-${m.id}`}
        >
          <span>{m.icon}</span>
          {m.label}
        </button>
      ))}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════
// MAIN TERMINAL PAGE
// ═══════════════════════════════════════════════════════════════

const FractalTerminal = () => {
  const [chartMode, setChartMode] = useState('price');
  const symbol = 'BTC';

  return (
    <div className="min-h-screen bg-slate-50" data-testid="fractal-terminal">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-xl font-bold text-slate-900">Fractal Research Terminal</h1>
              <span className="px-2 py-1 bg-slate-100 rounded text-xs font-medium text-slate-600">
                {symbol}
              </span>
            </div>
            <div className="text-xs text-slate-400">
              v4 · Institutional Grade
            </div>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-6">
        {/* Chart Section */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-slate-800">Research Canvas</h2>
            <ChartModeSwitcher mode={chartMode} onModeChange={setChartMode} />
          </div>
          
          {/* Chart Render based on mode */}
          <div className="min-h-[450px]">
            {chartMode === 'price' && (
              <FractalMainChart symbol={symbol} width={1100} height={420} />
            )}
            
            {chartMode === 'fractal' && (
              <FractalOverlaySection symbol={symbol} />
            )}
          </div>
          
          {/* Strategy Engine Panel */}
          <StrategyPanel symbol={symbol} />
          
          {/* Forward Performance Panel (BLOCK 56.5) */}
          <ForwardPerformancePanel />
        </div>
      </main>
      
      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white mt-8">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Fractal Research Terminal v4 · API v2.1</span>
            <span>Aftermath-Driven Forecast · Distribution Fan (P10-P90)</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default FractalTerminal;
