import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Terminal, Prompt, SystemText, Cursor, Divider } from "../components/Terminal";
import { HookBadge } from "../components/HookBadge";
import { typewriterText, isTypewriterDone, cursorOpacity } from "../utils";
import { COLORS } from "../styles";

export const SessionStartScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const commandStart = Math.round(0.5 * fps);
  const command = "code-agent";
  const commandText = typewriterText(command, frame, commandStart, 0.5);
  const commandDone = isTypewriterDone(command, frame, commandStart, 0.5);

  const bootFrame = Math.round(1.8 * fps);
  const hookFrame = Math.round(2.0 * fps);
  const audioFrame = Math.round(2.0 * fps);
  const pluginsFrame = Math.round(4.5 * fps);
  const readyFrame = Math.round(6.2 * fps);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Terminal statusLeft="Code Agent v1.0" statusRight="Ready">
        <div style={{ display: "flex", gap: 8 }}>
          <span style={{ color: COLORS.green }}>$</span>
          <span>{commandText}</span>
          {!commandDone && <Cursor opacity={cursorOpacity(frame)} />}
        </div>

        {commandDone && <Divider />}

        {frame >= bootFrame && (
          <>
            <SystemText>Code Agent v1.0</SystemText>
            <SystemText>Initializing...</SystemText>
          </>
        )}

        {frame >= bootFrame + Math.round(0.3 * fps) && (
          <SystemText>Loading configuration...</SystemText>
        )}

        {frame >= bootFrame + Math.round(0.5 * fps) && (
          <SystemText>Loading plugins...</SystemText>
        )}

        {frame >= pluginsFrame && (
          <>
            <Divider />
            <div style={{ color: COLORS.green, paddingLeft: 20 }}>
              3 plugins loaded
            </div>
          </>
        )}

        {frame >= pluginsFrame + Math.round(0.3 * fps) && (
          <div style={{ color: COLORS.green, paddingLeft: 20 }}>
            hal-voice active
          </div>
        )}

        {frame >= readyFrame && (
          <>
            <Divider />
            <div style={{ color: COLORS.text, fontWeight: "bold" }}>
              Ready.
            </div>
            <Divider />
            <Prompt>
              <Cursor opacity={cursorOpacity(frame)} />
            </Prompt>
          </>
        )}
      </Terminal>

      <HookBadge eventName="SessionStart" appearsAtFrame={hookFrame} />

      <Sequence from={audioFrame}>
        <Audio src={staticFile("audio/good-evening-dave-everythings-running-smoothly.mp3")} volume={0.8} />
      </Sequence>
    </AbsoluteFill>
  );
};
