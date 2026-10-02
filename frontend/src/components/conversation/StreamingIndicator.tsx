'use client';

import React from 'react';

export const StreamingIndicator: React.FC = () => {
  return (
    <span className="inline-flex items-center ml-1 align-baseline select-none">
      <span className="w-2 h-4 bg-primary inline-block rounded-xs animate-pulse opacity-80" />
    </span>
  );
};
