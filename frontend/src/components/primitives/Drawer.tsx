'use client';

import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { IconButton } from './IconButton';

export interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  side?: 'left' | 'right';
  className?: string;
}

export const Drawer: React.FC<DrawerProps> = ({
  isOpen,
  onClose,
  title,
  children,
  side = 'left',
  className = '',
}) => {
  // Close on ESC key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Lock body scroll when open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const slideVariants = {
    closed: {
      x: side === 'left' ? '-100%' : '100%',
      opacity: 0.5,
      transition: { type: 'spring' as const, damping: 30, stiffness: 300 },
    },
    open: {
      x: 0,
      opacity: 1,
      transition: { type: 'spring' as const, damping: 30, stiffness: 300 },
    },
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex" role="dialog" aria-modal="true">
          {/* Backdrop overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-xs"
            onClick={onClose}
          />

          {/* Sliding sheet */}
          <motion.aside
            variants={slideVariants}
            initial="closed"
            animate="open"
            exit="closed"
            className={`relative z-10 flex flex-col h-full bg-surface-container-low border-r border-outline-variant shadow-2xl ${
              side === 'right' ? 'ml-auto border-l border-r-0' : ''
            } ${className || 'w-72 sm:w-80 max-w-[85vw]'}`}
          >
            {title && (
              <div className="flex items-center justify-between px-4 py-3.5 border-b border-outline-variant/60">
                <span className="font-semibold text-sm text-on-surface">{title}</span>
                <IconButton label="Close drawer" size="sm" onClick={onClose}>
                  <X className="w-4 h-4" />
                </IconButton>
              </div>
            )}
            <div className="flex-1 overflow-y-auto overflow-x-hidden min-h-0">
              {children}
            </div>
          </motion.aside>
        </div>
      )}
    </AnimatePresence>
  );
};
