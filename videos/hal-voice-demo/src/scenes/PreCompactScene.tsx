import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";
import { Terminal, SystemText, Divider } from "../components/Terminal";
import { HookBadge } from "../components/HookBadge";
import { COLORS } from "../styles";

export const PreCompactScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const warningFrame = Math.round(0.3 * fps);
  const compactFrame = Math.round(0.8 * fps);
  const hookFrame = Math.round(1.0 * fps);
  const audioFrame = Math.round(1.0 * fps);
  const progressStart = Math.round(1.5 * fps);
  const progressEnd = Math.round(5.5 * fps);
  const doneFrame = Math.round(5.8 * fps);

  const progressPercent =
    frame >= progressStart && frame <= progressEnd
      ? interpolate(frame, [progressStart, progressEnd], [0, 100], {
          extrapolateRight: "clamp",
        })
      : frame > progressEnd
        ? 100
        : 0;

  const BAR_WIDTH = 40;
  const filled = Math.round((progressPercent / 100) * BAR_WIDTH);
  const progressBar =
    "\u2588".repeat(filled) + "\u2591".repeat(BAR_WIDTH - filled);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Terminal statusLeft="Code Agent v1.0" statusRight={`Context: ${frame < doneFrame ? "98%" : "42%"}`}>
        {/* Dimmed previous conversation */}
        <div style={{ color: COLORS.dimText, fontSize: 16 }}>
          {">"} Help me refactor the auth module{"\n"}
          I'll analyze the auth module...{"\n"}
          {">"} Use JWT tokens{"\n"}
          Implementing JWT-based auth with refresh tokens...{"\n"}
          {">"} Add rate limiting too{"\n"}
          Adding express-rate-limit middleware...{"\n"}
          {">"} Now add input validation{"\n"}
          Setting up zod schemas for request validation...
        </div>

        <Divider />

        {frame >= warningFrame && (
          <div style={{ color: COLORS.yellow, fontWeight: "bold" }}>
            Warning: Context limit approaching (98%)
          </div>
        )}

        {frame >= compactFrame && (
          <>
            <Divider />
            <SystemText>Compacting conversation history...</SystemText>
          </>
        )}

        {frame >= progressStart && (
          <>
            <Divider />
            <div style={{ paddingLeft: 20, color: COLORS.gray }}>
              <span style={{ color: progressPercent < 100 ? COLORS.yellow : COLORS.green }}>
                {progressBar}
              </span>{" "}
              {Math.round(progressPercent)}%
            </div>
          </>
        )}

        {frame >= doneFrame && (
          <>
            <Divider />
            <div style={{ color: COLORS.green, paddingLeft: 20 }}>
              Compaction complete.
            </div>
            <SystemText>Context usage: 42%</SystemText>
          </>
        )}
      </Terminal>

      <HookBadge eventName="PreCompact" appearsAtFrame={hookFrame} />

      <Sequence from={audioFrame}>
        <Audio
          src={staticFile(
            "audio/my-mind-is-going-i-can-feel-it-i-can-feel-it.mp3",
          )}
          volume={0.8}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
