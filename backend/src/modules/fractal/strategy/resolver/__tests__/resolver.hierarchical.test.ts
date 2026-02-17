/**
 * BLOCK 58 — Hierarchical Resolver Tests
 * 
 * Key test cases:
 * - Conflict: 30d BUY vs 365d BEAR
 * - Agreement: all horizons bullish
 * - Blockers: HIGH_ENTROPY forces HOLD
 */

import { describe, it, expect, beforeEach } from 'vitest';
import {
  HierarchicalResolverService,
  type HierarchicalResolveInput,
} from '../resolver.hierarchical.service.js';
import type { HorizonKey } from '../../config/horizon.config.js';

describe('HierarchicalResolverService', () => {
  let resolver: HierarchicalResolverService;

  beforeEach(() => {
    resolver = new HierarchicalResolverService();
  });

  function createInput(overrides: Partial<Record<HorizonKey, any>> = {}): HierarchicalResolveInput {
    const baseHorizon = {
      expectedReturn: 0,
      confidence: 0.5,
      reliability: 0.75,
      phaseRisk: 0.1,
      blockers: [],
    };

    return {
      horizons: {
        '7d': { horizon: '7d', dir: 'HOLD', ...baseHorizon, ...overrides['7d'] },
        '14d': { horizon: '14d', dir: 'HOLD', ...baseHorizon, ...overrides['14d'] },
        '30d': { horizon: '30d', dir: 'HOLD', ...baseHorizon, ...overrides['30d'] },
        '90d': { horizon: '90d', dir: 'HOLD', ...baseHorizon, ...overrides['90d'] },
        '180d': { horizon: '180d', dir: 'HOLD', ...baseHorizon, ...overrides['180d'] },
        '365d': { horizon: '365d', dir: 'HOLD', ...baseHorizon, ...overrides['365d'] },
      },
      globalEntropy: 0.3,
      mcP95_DD: 0.35,
    };
  }

  describe('Conflict: 30d BUY vs 365d BEAR', () => {
    it('should resolve to COUNTER_TREND with reduced size', () => {
      const input = createInput({
        '7d': { dir: 'LONG', expectedReturn: 0.05, confidence: 0.4 },
        '14d': { dir: 'LONG', expectedReturn: 0.08, confidence: 0.45 },
        '30d': { dir: 'LONG', expectedReturn: 0.12, confidence: 0.5 },
        '180d': { dir: 'SHORT', expectedReturn: -0.15, confidence: 0.6 },
        '365d': { dir: 'SHORT', expectedReturn: -0.25, confidence: 0.7 },
      });

      const result = resolver.resolve(input);

      // Bias should be BEAR (dominated by 365d)
      expect(result.bias.dir).toBe('BEAR');
      expect(result.bias.dominantHorizon).toBe('365d');

      // Timing should be ENTER (short-term bullish)
      expect(result.timing.action).toBe('ENTER');
      expect(result.timing.score).toBeGreaterThan(0);

      // Final should be COUNTER_TREND with reduced size
      expect(result.final.mode).toBe('COUNTER_TREND');
      expect(result.final.action).toBe('BUY');
      expect(result.final.sizeMultiplier).toBeLessThan(0.3); // Heavily reduced
    });
  });

  describe('Agreement: All horizons bullish', () => {
    it('should resolve to TREND_FOLLOW with full size', () => {
      const input = createInput({
        '7d': { dir: 'LONG', expectedReturn: 0.03, confidence: 0.35 },
        '14d': { dir: 'LONG', expectedReturn: 0.06, confidence: 0.4 },
        '30d': { dir: 'LONG', expectedReturn: 0.10, confidence: 0.45 },
        '90d': { dir: 'LONG', expectedReturn: 0.15, confidence: 0.5 },
        '180d': { dir: 'LONG', expectedReturn: 0.20, confidence: 0.55 },
        '365d': { dir: 'LONG', expectedReturn: 0.30, confidence: 0.6 },
      });

      const result = resolver.resolve(input);

      // Bias should be BULL
      expect(result.bias.dir).toBe('BULL');
      
      // Timing should be ENTER
      expect(result.timing.action).toBe('ENTER');

      // Final should be TREND_FOLLOW
      expect(result.final.mode).toBe('TREND_FOLLOW');
      expect(result.final.action).toBe('BUY');
      expect(result.final.sizeMultiplier).toBeGreaterThan(0.1);
    });
  });

  describe('All horizons bearish', () => {
    it('should resolve to TREND_FOLLOW SELL', () => {
      const input = createInput({
        '7d': { dir: 'SHORT', expectedReturn: -0.03, confidence: 0.35 },
        '14d': { dir: 'SHORT', expectedReturn: -0.06, confidence: 0.4 },
        '30d': { dir: 'SHORT', expectedReturn: -0.10, confidence: 0.45 },
        '180d': { dir: 'SHORT', expectedReturn: -0.20, confidence: 0.55 },
        '365d': { dir: 'SHORT', expectedReturn: -0.30, confidence: 0.6 },
      });

      const result = resolver.resolve(input);

      expect(result.bias.dir).toBe('BEAR');
      expect(result.timing.action).toBe('EXIT');
      expect(result.final.mode).toBe('TREND_FOLLOW');
      expect(result.final.action).toBe('SELL');
    });
  });

  describe('Neutral bias with timing signal', () => {
    it('should allow small entry with reduced size', () => {
      const input = createInput({
        '7d': { dir: 'LONG', expectedReturn: 0.04, confidence: 0.4 },
        '14d': { dir: 'LONG', expectedReturn: 0.06, confidence: 0.45 },
        '30d': { dir: 'LONG', expectedReturn: 0.08, confidence: 0.5 },
        '180d': { dir: 'HOLD', expectedReturn: 0.01, confidence: 0.3 },
        '365d': { dir: 'HOLD', expectedReturn: -0.01, confidence: 0.25 },
      });

      const result = resolver.resolve(input);

      // Bias should be NEUTRAL (long-term mixed)
      expect(result.bias.dir).toBe('NEUTRAL');
      
      // Timing should allow entry
      expect(result.timing.action).toBe('ENTER');

      // Final action allowed but reduced
      expect(result.final.action).toBe('BUY');
      expect(result.final.sizeMultiplier).toBeLessThan(0.5); // Reduced for neutral bias
    });
  });

  describe('Blockers force HOLD', () => {
    it('should HOLD when LOW_CONFIDENCE blocker present', () => {
      const input = createInput({
        '7d': { dir: 'LONG', expectedReturn: 0.05, confidence: 0.4, blockers: ['LOW_CONFIDENCE'] },
        '14d': { dir: 'LONG', expectedReturn: 0.08, confidence: 0.45, blockers: ['LOW_CONFIDENCE'] },
        '30d': { dir: 'LONG', expectedReturn: 0.12, confidence: 0.5, blockers: ['LOW_CONFIDENCE'] },
        '365d': { dir: 'LONG', expectedReturn: 0.25, confidence: 0.7 },
      });

      const result = resolver.resolve(input);

      // Timing should be WAIT due to blockers
      expect(result.timing.action).toBe('WAIT');
      expect(result.timing.blockers).toContain('LOW_CONFIDENCE');

      // Final should be HOLD
      expect(result.final.mode).toBe('HOLD');
      expect(result.final.action).toBe('HOLD');
      expect(result.final.sizeMultiplier).toBe(0);
    });

    it('should HOLD when HIGH_ENTROPY blocker present', () => {
      const input = createInput({
        '30d': { dir: 'LONG', expectedReturn: 0.12, confidence: 0.5, blockers: ['HIGH_ENTROPY'] },
      });

      const result = resolver.resolve(input);

      expect(result.timing.action).toBe('WAIT');
      expect(result.final.action).toBe('HOLD');
    });

    it('should HOLD when HIGH_TAIL_RISK blocker present', () => {
      const input = createInput({
        '30d': { dir: 'LONG', expectedReturn: 0.12, confidence: 0.5, blockers: ['HIGH_TAIL_RISK'] },
      });
      input.mcP95_DD = 0.7; // High tail risk

      const result = resolver.resolve(input);

      expect(result.timing.action).toBe('WAIT');
      expect(result.final.action).toBe('HOLD');
    });
  });

  describe('Risk adjustments', () => {
    it('should apply entropy penalty to size', () => {
      const inputLowEntropy = createInput({
        '30d': { dir: 'LONG', expectedReturn: 0.10, confidence: 0.5 },
        '365d': { dir: 'LONG', expectedReturn: 0.25, confidence: 0.6 },
      });
      inputLowEntropy.globalEntropy = 0.2;

      const inputHighEntropy = { ...inputLowEntropy, globalEntropy: 0.9 };

      const resultLow = resolver.resolve(inputLowEntropy);
      const resultHigh = resolver.resolve(inputHighEntropy);

      // High entropy should have smaller size multiplier
      expect(resultHigh.final.sizeMultiplier).toBeLessThan(resultLow.final.sizeMultiplier);
    });

    it('should apply tail risk penalty', () => {
      const inputLowTail = createInput({
        '30d': { dir: 'LONG', expectedReturn: 0.10, confidence: 0.5 },
        '365d': { dir: 'LONG', expectedReturn: 0.25, confidence: 0.6 },
      });
      inputLowTail.mcP95_DD = 0.25;

      const inputHighTail = { ...inputLowTail, mcP95_DD: 0.7 };

      const resultLow = resolver.resolve(inputLowTail);
      const resultHigh = resolver.resolve(inputHighTail);

      // High tail risk should have smaller size
      expect(resultHigh.final.sizeMultiplier).toBeLessThan(resultLow.final.sizeMultiplier);
    });
  });

  describe('Bias calculation', () => {
    it('should weight 365d higher than 180d', () => {
      // 365d bearish, 180d bullish
      const input = createInput({
        '180d': { dir: 'LONG', expectedReturn: 0.15, confidence: 0.6 },
        '365d': { dir: 'SHORT', expectedReturn: -0.20, confidence: 0.6 },
      });

      const result = resolver.resolve(input);

      // 365d should dominate
      expect(result.bias.dir).toBe('BEAR');
      expect(result.bias.dominantHorizon).toBe('365d');
    });
  });

  describe('Timing calculation', () => {
    it('should weight 30d highest', () => {
      // 30d bullish, 7d/14d mixed
      const input = createInput({
        '7d': { dir: 'SHORT', expectedReturn: -0.02, confidence: 0.3 },
        '14d': { dir: 'HOLD', expectedReturn: 0.01, confidence: 0.35 },
        '30d': { dir: 'LONG', expectedReturn: 0.10, confidence: 0.5 },
        '365d': { dir: 'LONG', expectedReturn: 0.25, confidence: 0.6 },
      });

      const result = resolver.resolve(input);

      // 30d should dominate timing (weight 0.5)
      expect(result.timing.dominantHorizon).toBe('30d');
    });
  });
});
