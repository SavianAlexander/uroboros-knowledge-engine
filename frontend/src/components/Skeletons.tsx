import React from 'react';
import { glassCardClasses } from '../lib/utils';

export function StatCardSkeleton() {
  return (
    <div className={`${glassCardClasses} p-5 space-y-3`}>
      <div className="flex items-center justify-between">
        <div className="w-24 h-3.5 rounded-md animate-shimmer" />
        <div className="w-8 h-8 rounded-xl animate-shimmer" />
      </div>
      <div className="w-20 h-7 rounded-lg animate-shimmer" />
      <div className="w-32 h-2.5 rounded-md animate-shimmer" />
    </div>
  );
}

export function SearchResultSkeleton() {
  return (
    <div className={`${glassCardClasses} p-5 space-y-3.5`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl animate-shimmer flex-shrink-0" />
          <div className="space-y-2">
            <div className="w-48 h-4 rounded-md animate-shimmer" />
            <div className="w-32 h-2.5 rounded-md animate-shimmer" />
          </div>
        </div>
        <div className="w-14 h-6 rounded-full animate-shimmer" />
      </div>
      <div className="space-y-2 pt-1">
        <div className="w-full h-3 rounded-md animate-shimmer" />
        <div className="w-5/6 h-3 rounded-md animate-shimmer" />
      </div>
      <div className="flex items-center gap-2 pt-1">
        <div className="w-28 h-4 rounded-md animate-shimmer" />
        <div className="w-20 h-4 rounded-md animate-shimmer" />
      </div>
    </div>
  );
}

export function FileTreeSkeleton() {
  return (
    <div className="p-3 space-y-2.5">
      {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
        <div key={i} className="flex items-center gap-2 px-2 py-1.5 rounded-lg">
          <div className="w-4 h-4 rounded animate-shimmer flex-shrink-0" />
          <div
            className="h-3 rounded-md animate-shimmer"
            style={{ width: `${Math.max(40, (i * 37) % 85 + 30)}%` }}
          />
        </div>
      ))}
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className={`${glassCardClasses} p-6 space-y-4`}>
      <div className="flex items-center justify-between">
        <div className="w-36 h-4 rounded-md animate-shimmer" />
        <div className="w-20 h-5 rounded-md animate-shimmer" />
      </div>
      <div className="w-full h-48 rounded-xl animate-shimmer" />
    </div>
  );
}
