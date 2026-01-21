import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/SpaceMono";

const { fontFamily } = loadFont();

export const OutroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // HAL eye animation
  const eyeProgress = spring({
    frame,
    fps,
    config: { damping: 200 },
  });

  const eyeScale = interpolate(eyeProgress, [0, 1], [0.8, 1]);
  const eyeOpacity = interpolate(eyeProgress, [0, 1], [0, 1]);

  // Glow pulse
  const glowIntensity = interpolate(
    Math.sin(frame * 0.08),
    [-1, 1],
    [0.4, 0.8]
  );

  // Command animation (shows first)
  const commandProgress = spring({
    frame: frame - 0.5 * fps,
    fps,
    config: { damping: 200 },
  });

  // Quote animation (HAL's reply, after audio)
  const quoteProgress = spring({
    frame: frame - 1.5 * fps,
    fps,
    config: { damping: 200 },
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0a0a",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {/* Audio (plays after command appears) */}
      <Sequence from={1 * fps}>
        <Audio src={staticFile("hal-quote.mp3")} volume={0.8} />
      </Sequence>

      {/* Red glow */}
      <div
        style={{
          position: "absolute",
          width: 500,
          height: 500,
          borderRadius: "50%",
          background: `radial-gradient(circle, rgba(255, 0, 0, ${glowIntensity}) 0%, transparent 70%)`,
          opacity: eyeOpacity,
        }}
      />

      {/* HAL eye */}
      <Img
        src={staticFile("hal-9000.jpg")}
        style={{
          width: 200,
          height: 200,
          borderRadius: "50%",
          objectFit: "cover",
          opacity: eyeOpacity,
          transform: `scale(${eyeScale})`,
          boxShadow: `0 0 80px rgba(255, 0, 0, ${glowIntensity})`,
        }}
      />

      {/* Quote */}
      <div
        style={{
          position: "absolute",
          top: 120,
          fontFamily,
          fontSize: 28,
          color: "#ff3333",
          fontStyle: "italic",
          opacity: interpolate(quoteProgress, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(quoteProgress, [0, 1], [20, 0])}px)`,
          textAlign: "center",
        }}
      >
        "I'm sorry, Dave. I'm afraid I can't do that."
      </div>

      {/* Command */}
      <div
        style={{
          position: "absolute",
          bottom: 120,
          fontFamily,
          fontSize: 32,
          color: "#ffffff",
          opacity: interpolate(commandProgress, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(commandProgress, [0, 1], [20, 0])}px)`,
        }}
      >
        <span style={{ color: "#888" }}>$</span>{" "}
        <span style={{ color: "#28c840" }}>hal open-the-pod-bay-doors</span>
      </div>

      {/* Tagline */}
      <div
        style={{
          position: "absolute",
          bottom: 60,
          fontFamily,
          fontSize: 18,
          color: "#666",
          opacity: interpolate(commandProgress, [0, 1], [0, 1]),
        }}
      >
        This dev environment is too important for me to allow you to jeopardize it.
      </div>
    </AbsoluteFill>
  );
};
