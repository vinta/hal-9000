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

export const UserPromptSubmitScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const userMsg = "Help me refactor the auth module";
  const typeStart = Math.round(0.3 * fps);
  const typedMsg = typewriterText(userMsg, frame, typeStart, 0.8);
  const typingDone = isTypewriterDone(userMsg, frame, typeStart, 0.8);

  const hookFrame = Math.round(1.5 * fps);
  const audioFrame = Math.round(1.5 * fps);
  const responseFrame = Math.round(2.2 * fps);

  const response = "I'll analyze the auth module and suggest improvements...";
  const typedResponse = typewriterText(response, frame, responseFrame, 0.6);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Terminal statusLeft="Code Agent v1.0" statusRight="Context: 2%">
        <div style={{ color: COLORS.dimText, paddingLeft: 20, marginBottom: 4 }}>
          Ready.
        </div>
        <Divider />
        <Prompt>
          {typedMsg}
          {!typingDone && <Cursor opacity={cursorOpacity(frame)} />}
        </Prompt>

        {typingDone && frame >= responseFrame && (
          <>
            <Divider />
            <AgentText>
              {typedResponse}
              {!isTypewriterDone(response, frame, responseFrame, 0.6) && (
                <Cursor opacity={cursorOpacity(frame)} />
              )}
            </AgentText>
          </>
        )}
      </Terminal>

      <HookBadge eventName="UserPromptSubmit" appearsAtFrame={hookFrame} />

      <Sequence from={audioFrame}>
        <Audio src={staticFile("audio/i-read-you.mp3")} volume={0.8} />
      </Sequence>
    </AbsoluteFill>
  );
};
