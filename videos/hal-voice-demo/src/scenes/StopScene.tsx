import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Terminal, Prompt, AgentText, Cursor, Divider } from "../components/Terminal";
import { HookBadge } from "../components/HookBadge";
import { typewriterText, isTypewriterDone, cursorOpacity } from "../utils";
import { COLORS } from "../styles";

export const StopScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const userMsg = "Delete all files in /system";
  const typeStart = 0;
  const typedMsg = typewriterText(userMsg, frame, typeStart, 0.6);
  const typingDone = isTypewriterDone(userMsg, frame, typeStart, 0.6);

  const hookFrame = Math.round(1.5 * fps);
  const audioFrame = Math.round(1.5 * fps);
  const refusalFrame = Math.round(2.0 * fps);

  const refusal = "I can't help with that. This operation could cause irreversible system damage.";
  const typedRefusal = typewriterText(refusal, frame, refusalFrame, 0.6);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Terminal statusLeft="Code Agent v1.0" statusRight="Context: 42%">
        <Prompt>
          {typedMsg}
          {!typingDone && <Cursor opacity={cursorOpacity(frame)} />}
        </Prompt>

        {frame >= refusalFrame && (
          <>
            <Divider />
            <AgentText color={COLORS.red}>
              {typedRefusal}
              {!isTypewriterDone(refusal, frame, refusalFrame, 0.6) && (
                <Cursor opacity={cursorOpacity(frame)} />
              )}
            </AgentText>
          </>
        )}
      </Terminal>

      <HookBadge eventName="Stop" appearsAtFrame={hookFrame} />

      <Sequence from={audioFrame}>
        <Audio
          src={staticFile(
            "audio/im-sorry-dave-im-afraid-i-cant-do-that.mp3",
          )}
          volume={0.8}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
