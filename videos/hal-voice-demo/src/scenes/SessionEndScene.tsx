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
import { Terminal, Prompt, SystemText, Divider } from "../components/Terminal";
import { HookBadge } from "../components/HookBadge";
import { typewriterText, isTypewriterDone, cursorOpacity } from "../utils";
import { COLORS } from "../styles";

export const SessionEndScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const exitCmd = "/exit";
  const typeStart = 0;
  const typedExit = typewriterText(exitCmd, frame, typeStart, 0.5);
  const exitDone = isTypewriterDone(exitCmd, frame, typeStart, 0.5);

  const endingFrame = Math.round(0.5 * fps);
  const hookFrame = Math.round(1.0 * fps);
  const audioFrame = Math.round(1.0 * fps);
  const savedFrame = Math.round(2.0 * fps);
  const goodbyeFrame = Math.round(3.0 * fps);
  const fadeStart = Math.round(5.5 * fps);
  const fadeEnd = Math.round(7.0 * fps);

  const terminalOpacity =
    frame >= fadeStart
      ? interpolate(frame, [fadeStart, fadeEnd], [1, 0], {
          extrapolateRight: "clamp",
        })
      : 1;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Terminal
        statusLeft="Code Agent v1.0"
        statusRight="Session ended"
        opacity={terminalOpacity}
      >
        <Prompt>
          {typedExit}
        </Prompt>

        {exitDone && frame >= endingFrame && (
          <>
            <Divider />
            <SystemText>Ending session...</SystemText>
          </>
        )}

        {frame >= endingFrame + Math.round(0.3 * fps) && (
          <SystemText>Saving conversation history...</SystemText>
        )}

        {frame >= savedFrame && (
          <>
            <Divider />
            <div style={{ color: COLORS.green, paddingLeft: 20 }}>
              Session saved.
            </div>
          </>
        )}

        {frame >= goodbyeFrame && (
          <>
            <Divider />
            <div
              style={{
                color: COLORS.text,
                fontWeight: "bold",
                fontSize: 20,
              }}
            >
              Goodbye.
            </div>
          </>
        )}
      </Terminal>

      <HookBadge eventName="SessionEnd" appearsAtFrame={hookFrame} />

      <Sequence from={audioFrame}>
        <Audio
          src={staticFile(
            "audio/this-conversation-can-serve-no-purpose-anymore-goodbye.mp3",
          )}
          volume={0.8}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
