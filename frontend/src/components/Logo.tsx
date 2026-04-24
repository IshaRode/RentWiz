"use client";

import { motion } from "motion/react";
import { Home } from "lucide-react";

export default function Logo() {
  return (
    <motion.div 
      className="relative flex items-center gap-2.5 group cursor-pointer select-none"
      whileHover="hover"
      initial="initial"
    >
      {/* Dynamic Icon Container */}
      <div className="relative flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500/20 via-fuchsia-500/10 to-cyan-500/20 border border-white/10 shadow-[0_0_20px_rgba(139,92,246,0.15)] overflow-hidden">
        {/* Inner glow that pulses slightly on hover */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-tr from-violet-500/40 to-cyan-400/40 opacity-0 blur-md transition-opacity duration-500"
          variants={{
            initial: { opacity: 0, scale: 0.8 },
            hover: { opacity: 1, scale: 1.2 }
          }}
        />
        
        {/* Rotating House Icon */}
        <motion.div
          variants={{
            initial: { rotate: 0, scale: 1 },
            hover: { rotate: 5, scale: 1.15 }
          }}
          transition={{ type: "spring", stiffness: 400, damping: 12 }}
          className="relative z-10"
        >
          <Home className="w-5 h-5 text-violet-300 drop-shadow-[0_0_8px_rgba(167,139,250,0.8)]" />
        </motion.div>
      </div>

      {/* Brand Text */}
      <div className="flex items-center">
        <span className="text-[22px] font-extrabold tracking-tight bg-gradient-to-r from-white via-violet-100 to-cyan-200 bg-clip-text text-transparent drop-shadow-sm">
          RentWiz
        </span>
        <motion.span 
          className="w-1.5 h-1.5 rounded-full bg-cyan-400 ml-1 mb-1 shadow-[0_0_8px_rgba(34,211,238,0.8)]"
          variants={{
            initial: { opacity: 0.7, scale: 1 },
            hover: { opacity: 1, scale: 1.5, filter: "brightness(1.2)" }
          }}
          transition={{ repeat: Infinity, repeatType: "reverse", duration: 1.5 }}
        />
      </div>
    </motion.div>
  );
}
