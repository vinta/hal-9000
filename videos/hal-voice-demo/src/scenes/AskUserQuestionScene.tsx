import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  Terminal,
  AgentText,
  Cursor,
  Divider,
  BoxContent,
} from "../components/Terminal";
import { HookBadge } from "../components/HookBadge";
import { typewriterText, isTypewriterDone, cursorOpacity } from "../utils";
import { COLORS } from "../styles";

export const AskUserQuestionScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const intro = "I need to understand your preferences before proceeding.";
  const introStart = Math.round(0.3 * fps);
  const typedIntro = typewriterText(intro, frame, introStart, 0.8);

  const hookFrame = Math.round(1.0 * fps);
  const audioFrame = Math.round(1.0 * fps);
  const questionFrame = Math.round(1.8 * fps);
  const promptFrame = Math.round(3.5 * fps);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Terminal statusLeft="Code Agent v1.0" statusRight="Context: 8%">
        <div style={{ color: COLORS.dimText, paddingLeft: 20, marginBottom: 4 }}>
          {">"} Help me refactor the auth module
        </div>
        <div style={{ color: COLORS.dimText, paddingLeft: 20, marginBottom: 4 }}>
          I'll analyze the auth module and suggest improvements...
        </div>
        <Divider />

        <AgentText>
          {typedIntro}
          {!isTypewriterDone(intro, frame, introStart, 0.8) && (
            <Cursor opacity={cursorOpacity(frame)} />
          )}
        </AgentText>

        {frame >= questionFrame && (
          <>
            <Divider />
            <BoxContent title="Question" titleColor={COLORS.yellow}>
              <div>Which auth strategy do you prefer?</div>
              <Divider />
              <div style={{ color: COLORS.green }}> (a) JWT tokens</div>
              <div style={{ color: COLORS.text }}> (b) Session-based</div>
              <div style={{ color: COLORS.text }}> (c) OAuth 2.0</div>
            </BoxContent>
          </>
        )}

        {frame >= promptFrame && (
          <>
            <Divider />
            <div style={{ display: "flex", gap: 8 }}>
              <span style={{ color: COLORS.green, fontWeight: "bold" }}>{">"}</span>
              <Cursor opacity={cursorOpacity(frame)} />
            </div>
          </>
        )}
      </Terminal>

      <HookBadge
        eventName="PreToolUse: AskUserQuestion"
        appearsAtFrame={hookFrame}
      />

      <Sequence from={audioFrame}>
        <Audio
          src={staticFile(
            "audio/do-you-mind-if-i-ask-you-a-personal-question.mp3",
          )}
          volume={0.8}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
