"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";

/**
 * A proper, clean SVG House icon for the logo animation.
 * We use a custom SVG instead of an emoji to ensure a premium look.
 */
const HouseIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg
    {...props}
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2.5"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M3 10l9-7 9 7" />
    <path d="M4 10v10a2 2 0 002 2h12a2 2 0 002-2V10" />
    <path d="M9 22V12h6v10" />
  </svg>
);

export default function Logo() {
  // State to manage which part of the animation is active.
  // We use a simple boolean: false = show icon, true = show text.
  const [showText, setShowText] = useState(false);

  useEffect(() => {
    // 1. House icon displays first.
    // 2. After 1.2 seconds, trigger the transition to text.
    const timer = setTimeout(() => {
      setShowText(true);
    }, 1200);

    // Cleanup timer if the component unmounts
    return () => clearTimeout(timer);
  }, []);

  return (
    // The container reserves enough width and height for both states
    // so the layout doesn't jump during the transition.
    <div className="relative flex items-center w-[90px] h-[32px]">
      {/* 
        AnimatePresence handles exit animations. By NOT using mode="wait", 
        the house exit and text enter happen simultaneously for a seamless blend.
      */}
      <AnimatePresence>
        {!showText ? (
          <motion.div
            key="icon"
            // Enter animation: fade in, scale up slightly
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            // Exit animation: scale down, fade out, slight rotation for polish
            exit={{ opacity: 0, scale: 0.5, rotate: 10 }}
            transition={{ duration: 0.5, ease: "easeInOut" }}
            className="absolute left-0 text-blue-600"
          >
            <HouseIcon className="w-8 h-8" />
          </motion.div>
        ) : (
          <motion.div
            key="text"
            // Enter animation: start lower (y: 20) and invisible
            initial={{ opacity: 0, y: 20 }}
            // Final state: move up to original position and fully visible
            animate={{ opacity: 1, y: 0 }}
            // Smooth easeOut gives a natural, premium feel. 
            // Slight delay ensures the house has started shrinking before text appears.
            transition={{ duration: 0.6, ease: "easeOut", delay: 0.1 }}
            className="absolute left-0"
          >
            <span 
              className="text-2xl font-bold text-[#2563eb] tracking-tight"
              style={{ textShadow: "0 2px 10px rgba(37, 99, 235, 0.4)" }}
            >
              RentWiz
            </span>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
