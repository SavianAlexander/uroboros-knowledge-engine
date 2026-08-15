import React from 'react';
import { Mic, Volume2, Square, Sparkles } from 'lucide-react';

interface CortanaOrbProps {
  state: 'idle' | 'listening' | 'speaking' | 'buffering';
  onClick?: () => void;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export const playCortanaSFX = async (sfxName: 'ready' | 'confirm' | 'complete' | 'alert' | 'dismiss') => {
  try {
    const res = await fetch(`/api/voice/sfx/${sfxName}`);
    if (res.ok) {
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.volume = 0.6;
      audio.onended = () => URL.revokeObjectURL(url);
      await audio.play();
    }
  } catch {
    // SFX fallback silent
  }
};

export const CortanaOrb: React.FC<CortanaOrbProps> = ({
  state,
  onClick,
  size = 'md',
  showLabel = false
}) => {
  const sizeMap = {
    sm: 'w-7 h-7',
    md: 'w-9 h-9',
    lg: 'w-12 h-12'
  };

  const iconSizeMap = {
    sm: 'w-3.5 h-3.5',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={onClick}
        type="button"
        className={`relative flex items-center justify-center rounded-full transition-all duration-300 group select-none cursor-pointer ${sizeMap[size]}`}
        title={
          state === 'speaking'
            ? 'Cortana Speaking (Click to Interrupt)'
            : state === 'listening'
            ? 'Cortana Listening (Click to Finish)'
            : 'Cortana Voice Assistant (Click to Speak)'
        }
      >
        {/* Outer Pulsing Holographic Ring */}
        {state === 'speaking' && (
          <>
            <span className="absolute inset-0 rounded-full bg-cyan-500/20 animate-ping duration-1000" />
            <span className="absolute -inset-1 rounded-full border border-cyan-400/40 animate-spin" style={{ animationDuration: '4s' }} />
            <span className="absolute -inset-2 rounded-full border border-purple-500/30 animate-spin" style={{ animationDuration: '6s', animationDirection: 'reverse' }} />
          </>
        )}

        {state === 'listening' && (
          <>
            <span className="absolute -inset-1.5 rounded-full bg-emerald-500/25 animate-pulse" />
            <span className="absolute -inset-2.5 rounded-full border border-emerald-400/50 animate-ping duration-700" />
          </>
        )}

        {state === 'buffering' && (
          <span className="absolute -inset-1 rounded-full border-2 border-cyan-400/40 border-t-cyan-400 animate-spin" />
        )}

        {/* Core Glowing Orb */}
        <div
          className={`relative z-10 w-full h-full rounded-full flex items-center justify-center shadow-lg transition-all duration-300 ${
            state === 'speaking'
              ? 'bg-gradient-to-tr from-cyan-500 via-blue-600 to-purple-600 shadow-cyan-500/50 scale-105 ring-2 ring-cyan-300/50'
              : state === 'listening'
              ? 'bg-gradient-to-tr from-emerald-500 to-teal-600 shadow-emerald-500/50 scale-110 ring-2 ring-emerald-300/50'
              : state === 'buffering'
              ? 'bg-gradient-to-tr from-cyan-600 to-indigo-600 shadow-cyan-500/30 animate-pulse'
              : 'bg-gradient-to-tr from-slate-700 via-slate-800 to-cyan-950 hover:from-cyan-600 hover:to-purple-600 shadow-black/40 hover:shadow-cyan-500/30 group-hover:scale-105 border border-white/10'
          }`}
        >
          {state === 'speaking' && (
            <div className="flex items-center gap-0.5">
              <span className="w-0.5 h-2 bg-white animate-pulse" />
              <span className="w-0.5 h-3.5 bg-white animate-bounce" />
              <span className="w-0.5 h-2 bg-white animate-pulse" />
            </div>
          )}

          {state === 'listening' && (
            <Mic className={`${iconSizeMap[size]} text-white animate-pulse`} />
          )}

          {state === 'buffering' && (
            <Sparkles className={`${iconSizeMap[size]} text-cyan-200 animate-spin`} />
          )}

          {state === 'idle' && (
            <Volume2 className={`${iconSizeMap[size]} text-cyan-400 group-hover:text-white transition-colors`} />
          )}
        </div>
      </button>

      {showLabel && (
        <div className="flex flex-col">
          <span className="text-[11px] font-semibold tracking-wider uppercase text-cyan-400 dark:text-cyan-300">
            Cortana Prime
          </span>
          <span className="text-[10px] text-slate-400">
            {state === 'speaking'
              ? 'Broadcasting...'
              : state === 'listening'
              ? 'Listening...'
              : state === 'buffering'
              ? 'Synthesizing...'
              : 'Online & Ready'}
          </span>
        </div>
      )}
    </div>
  );
};
