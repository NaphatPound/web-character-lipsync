"use client";

import { useEffect, useRef } from "react";

interface VideoPlayerProps {
  src: string;
}

export default function VideoPlayer({ src }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.load();
      videoRef.current.play().catch(() => {
        // Autoplay may be blocked by browser — user can press play manually
      });
    }
  }, [src]);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-violet-300 uppercase tracking-wider">
          Output
        </h2>
        <a
          href={src}
          download
          className="flex items-center gap-1.5 rounded-xl bg-violet-700/30 border border-violet-600/40 px-4 py-2 text-sm text-violet-300 hover:bg-violet-700/50 hover:text-white transition-all"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download MP4
        </a>
      </div>

      <div className="rounded-2xl overflow-hidden border border-violet-700/30 bg-black shadow-[0_0_40px_rgba(124,58,237,0.15)]">
        <video
          ref={videoRef}
          controls
          playsInline
          className="w-full max-h-[480px] object-contain"
        >
          <source src={src} type="video/mp4" />
          Your browser does not support video playback.
        </video>
      </div>
    </div>
  );
}
