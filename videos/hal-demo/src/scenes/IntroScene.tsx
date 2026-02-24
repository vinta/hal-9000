import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/SpaceMono";

const { fontFamily } = loadFont();

export const IntroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // HAL eye fade in (start visible for thumbnail)
  const eyeOpacity = interpolate(frame, [0, 0.5 * fps], [0.8, 1], {
    extrapolateRight: "clamp",
  });

  // HAL eye glow pulse
  const glowIntensity = interpolate(
    Math.sin(frame * 0.1),
    [-1, 1],
    [0.3, 0.6]
  );

  // Title animation
  const titleProgress = spring({
    frame: frame - 1.5 * fps,
    fps,
    config: { damping: 200 },
  });

  const titleOpacity = interpolate(titleProgress, [0, 1], [0, 1]);
  const titleY = interpolate(titleProgress, [0, 1], [30, 0]);

  // Tagline animation
  const taglineProgress = spring({
    frame: frame - 2.2 * fps,
    fps,
    config: { damping: 200 },
  });

  const taglineOpacity = interpolate(taglineProgress, [0, 1], [0, 1]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0a0a",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {/* Red glow behind HAL eye */}
      <div
        style={{
          position: "absolute",
          width: 400,
          height: 400,
          borderRadius: "50%",
          background: `radial-gradient(circle, rgba(255, 0, 0, ${glowIntensity}) 0%, transparent 70%)`,
          opacity: eyeOpacity,
        }}
      />

      {/* HAL 9000 eye */}
      <Img
        src={staticFile("hal-9000.jpg")}
        style={{
          width: 280,
          height: 280,
          borderRadius: "50%",
          objectFit: "cover",
          opacity: eyeOpacity,
          boxShadow: `0 0 60px rgba(255, 0, 0, ${glowIntensity})`,
        }}
      />

      {/* Title */}
      <div
        style={{
          position: "absolute",
          bottom: 180,
          fontFamily,
          fontSize: 72,
          fontWeight: 700,
          color: "#ffffff",
          letterSpacing: "0.1em",
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
        }}
      >
        HAL 9000
      </div>

      {/* Tagline */}
      <div
        style={{
          position: "absolute",
          bottom: 120,
          fontFamily,
          fontSize: 24,
          color: "#888888",
          opacity: taglineOpacity,
          textAlign: "center",
          maxWidth: 800,
        }}
      >
        Opinionated macOS development environment automation
      </div>
    </AbsoluteFill>
  );
};
