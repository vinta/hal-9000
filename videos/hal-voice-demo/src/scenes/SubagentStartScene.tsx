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
import { Terminal, AgentText, Divider, SystemText } from "../components/Terminal";
import { HookBadge } from "../components/HookBadge";
import { typewriterText, isTypewriterDone } from "../utils";
import { COLORS } from "../styles";

const SPINNER_CHARS = ["\u2839", "\u2838", "\u2834", "\u2826", "\u2807", "\u280F", "\u2819", "\u2839"];

export const SubagentStartScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const intro = "Let me research the best approach for this codebase.";
  const introStart = 0;
  const typedIntro = typewriterText(intro, frame, introStart, 0.8);
  const introDone = isTypewriterDone(intro, frame, introStart, 0.8);

  const launchFrame = Math.round(0.8 * fps);
  const hookFrame = Math.round(1.0 * fps);
  const audioFrame = Math.round(1.0 * fps);
  const resultFrame = Math.round(4.2 * fps);

  const spinnerIdx = Math.floor(frame / 3) % SPINNER_CHARS.length;
  const showSpinner = frame >= launchFrame && frame < resultFrame;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Terminal statusLeft="Code Agent v1.0" statusRight="Context: 15%">
        <AgentText>
          {typedIntro}
        </AgentText>

        {introDone && frame >= launchFrame && (
          <>
            <Divider />
            <SystemText>Launching research agent...</SystemText>
          </>
        )}

        {showSpinner && (
          <>
            <Divider />
            <div style={{ paddingLeft: 20, color: COLORS.yellow }}>
              {SPINNER_CHARS[spinnerIdx]} Agent working...
            </div>
          </>
        )}

        {frame >= resultFrame && (
          <>
            <Divider />
            <div style={{ color: COLORS.green, paddingLeft: 20 }}>
              Agent complete.
            </div>
            <AgentText>
              Found 3 relevant patterns in the codebase.
            </AgentText>
          </>
        )}
      </Terminal>

      <HookBadge eventName="SubagentStart" appearsAtFrame={hookFrame} />

      <Sequence from={audioFrame}>
        <Audio
          src={staticFile("audio/just-a-moment-just-a-moment.mp3")}
          volume={0.8}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
