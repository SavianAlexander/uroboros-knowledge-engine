import React, { useEffect, useRef } from 'react';

interface AudioVisualizerProps {
  isPlaying: boolean;
  audioRef?: React.RefObject<HTMLAudioElement | null>;
  colorTheme?: 'purple' | 'emerald' | 'amber' | 'cyan';
  barCount?: number;
  height?: number;
}

export const AudioVisualizer: React.FC<AudioVisualizerProps> = ({
  isPlaying,
  audioRef,
  colorTheme = 'purple',
  barCount = 32,
  height = 36,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceNodeRef = useRef<MediaElementAudioSourceNode | null>(null);

  useEffect(() => {
    if (!isPlaying) {
      if (animFrameRef.current) {
        cancelAnimationFrame(animFrameRef.current);
        animFrameRef.current = null;
      }
      // Draw flat/idle wave
      drawIdle();
      return;
    }

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let phase = 0;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const width = canvas.width;
      const h = canvas.height;
      const barWidth = width / barCount;

      phase += 0.08;

      for (let i = 0; i < barCount; i++) {
        // Multi-frequency harmonic waveform simulation (when audio element is streaming/cross-origin protected)
        const sin1 = Math.sin(phase + (i * 0.35));
        const sin2 = Math.cos(phase * 1.5 + (i * 0.2));
        const sin3 = Math.sin(phase * 0.6 - (i * 0.15));
        
        let magnitude = (Math.abs(sin1 * 0.5 + sin2 * 0.3 + sin3 * 0.2));
        magnitude = Math.min(1.0, Math.max(0.12, magnitude));

        const barH = magnitude * (h * 0.85);
        const x = i * barWidth + (barWidth * 0.15);
        const y = (h - barH) / 2;

        // Gradient styling
        const grad = ctx.createLinearGradient(0, y, 0, y + barH);
        if (colorTheme === 'purple') {
          grad.addColorStop(0, '#c084fc');
          grad.addColorStop(0.5, '#a855f7');
          grad.addColorStop(1, '#6366f1');
        } else if (colorTheme === 'emerald') {
          grad.addColorStop(0, '#34d399');
          grad.addColorStop(0.5, '#10b981');
          grad.addColorStop(1, '#059669');
        } else if (colorTheme === 'amber') {
          grad.addColorStop(0, '#fcd34d');
          grad.addColorStop(0.5, '#f59e0b');
          grad.addColorStop(1, '#d97706');
        } else {
          grad.addColorStop(0, '#67e8f9');
          grad.addColorStop(0.5, '#06b6d4');
          grad.addColorStop(1, '#0284c7');
        }

        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.roundRect(x, y, barWidth * 0.7, barH, 2);
        ctx.fill();
      }

      animFrameRef.current = requestAnimationFrame(render);
    };

    render();

    return () => {
      if (animFrameRef.current) {
        cancelAnimationFrame(animFrameRef.current);
      }
    };
  }, [isPlaying, colorTheme, barCount]);

  const drawIdle = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const width = canvas.width;
    const h = canvas.height;
    const barWidth = width / barCount;

    ctx.fillStyle = 'rgba(148, 163, 184, 0.2)';
    for (let i = 0; i < barCount; i++) {
      const barH = 3;
      const x = i * barWidth + (barWidth * 0.15);
      const y = (h - barH) / 2;
      ctx.beginPath();
      ctx.roundRect(x, y, barWidth * 0.7, barH, 1.5);
      ctx.fill();
    }
  };

  useEffect(() => {
    drawIdle();
  }, []);

  return (
    <div className="flex items-center justify-center">
      <canvas
        ref={canvasRef}
        width={180}
        height={height}
        className="w-full max-w-[200px] h-8 transition-opacity duration-300"
      />
    </div>
  );
};
