import type { CSSProperties, ComponentType } from 'react';

export interface MetallicPaintProps {
  imageSrc?: string;
  text?: string;
  fontFamily?: string;
  fontWeight?: number;
  color?: string;
  backgroundColor?: string;
  density?: number;
  softness?: number;
  dispersion?: number;
  distortion?: number;
  edgeBend?: number;
  angle?: number;
  speed?: number;
  scale?: number;
  rotation?: number;
  mouseTilt?: number;
  lightMode?: boolean;
  intro?: boolean;
  paused?: boolean;
  dpr?: number;
  className?: string;
  style?: CSSProperties;
}

declare const MetallicPaint: ComponentType<MetallicPaintProps>;
export default MetallicPaint;
