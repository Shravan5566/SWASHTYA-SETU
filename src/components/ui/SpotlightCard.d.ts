import React, { HTMLAttributes, ReactNode, CSSProperties } from 'react';

export interface SpotlightCardProps extends HTMLAttributes<HTMLDivElement> {
  children?: ReactNode;
  className?: string;
  style?: CSSProperties;
  spotlightColor?: string;
  intensity?: number;
  spotlightSize?: number;
  softness?: number;
  shape?: 'circle' | 'beam';
  borderGlow?: number;
  proximity?: number;
  smoothing?: number;
  ambient?: boolean;
  flare?: boolean;
  grain?: number;
  theme?: 'dark' | 'light';
  as?: any;
  href?: string;
}

declare const SpotlightCard: React.FC<SpotlightCardProps>;

export default SpotlightCard;
