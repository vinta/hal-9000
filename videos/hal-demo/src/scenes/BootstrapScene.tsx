import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/SpaceMono";

const { fontFamily } = loadFont();

const BOOTSTRAP_COMMAND =
  "curl -L https://raw.githubusercontent.com/vinta/hal-9000/master/bin/open-the-pod-bay-doors | bash";

const CHAR_FRAMES = 1.5;

export const BootstrapScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Title animation
  const titleProgress = spring({
    frame,
    fps,
    config: { damping: 200 },
  });

  // Typewriter effect for command
  const commandStartFrame = 0.8 * fps;
  const typedChars = Math.min(
    BOOTSTRAP_COMMAND.length,
    Math.floor((frame - commandStartFrame) / CHAR_FRAMES)
  );
  const typedText =
    frame > commandStartFrame ? BOOTSTRAP_COMMAND.slice(0, typedChars) : "";

  // Cursor blink
  const cursorOpacity = interpolate(
    (frame * 0.15) % 1,
    [0, 0.5, 1],
    [1, 0, 1]
  );

  // Terminal window animation
  const terminalProgress = spring({
    frame: frame - 0.3 * fps,
    fps,
    config: { damping: 200 },
  });

  const terminalScale = interpolate(terminalProgress, [0, 1], [0.9, 1]);
  const terminalOpacity = interpolate(terminalProgress, [0, 1], [0, 1]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0a0a",
        justifyContent: "center",
        alignItems: "center",
        padding: 60,
      }}
    >
      {/* Section title */}
      <div
        style={{
          position: "absolute",
          top: 80,
          fontFamily,
          fontSize: 36,
          color: "#ff3333",
          opacity: interpolate(titleProgress, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(titleProgress, [0, 1], [-20, 0])}px)`,
        }}
      >
        One-liner Bootstrap
      </div>

      {/* Terminal window */}
      <div
        style={{
          width: "90%",
          maxWidth: 1100,
          backgroundColor: "#1a1a1a",
          borderRadius: 12,
          overflow: "hidden",
          boxShadow: "0 20px 60px rgba(0, 0, 0, 0.5)",
          opacity: terminalOpacity,
          transform: `scale(${terminalScale})`,
        }}
      >
        {/* Terminal header */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            padding: "12px 16px",
            backgroundColor: "#2a2a2a",
            gap: 8,
          }}
        >
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              backgroundColor: "#ff5f57",
            }}
          />
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              backgroundColor: "#febc2e",
            }}
          />
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              backgroundColor: "#28c840",
            }}
          />
          <span
            style={{
              marginLeft: 12,
              fontFamily,
              fontSize: 14,
              color: "#666",
            }}
          >
            Terminal
          </span>
        </div>

        {/* Terminal content */}
        <div
          style={{
            padding: 24,
            fontFamily,
            fontSize: 18,
            lineHeight: 1.6,
          }}
        >
          <div style={{ color: "#888" }}>
            <span style={{ color: "#28c840" }}>$</span>{" "}
            <span style={{ color: "#ffffff" }}>{typedText}</span>
            <span
              style={{
                color: "#ff3333",
                opacity: cursorOpacity,
              }}
            >
              |
            </span>
          </div>
        </div>
      </div>

      {/* Subtitle */}
      <div
        style={{
          position: "absolute",
          bottom: 100,
          fontFamily,
          fontSize: 20,
          color: "#666",
          textAlign: "center",
        }}
      >
        Installs Homebrew, Ansible, and configures your entire dev environment
      </div>
    </AbsoluteFill>
  );
};
