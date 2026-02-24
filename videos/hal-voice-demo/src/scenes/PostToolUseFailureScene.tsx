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
  ErrorText,
  Cursor,
  Divider,
} from "../components/Terminal";
import { HookBadge } from "../components/HookBadge";
import { typewriterText, isTypewriterDone, cursorOpacity } from "../utils";
import { COLORS } from "../styles";

export const PostToolUseFailureScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const intro = "Running test suite...";
  const introStart = 0;
  const typedIntro = typewriterText(intro, frame, introStart, 0.8);

  const cmdFrame = Math.round(0.5 * fps);
  const failFrame = Math.round(0.8 * fps);
  const hookFrame = Math.round(1.0 * fps);
  const audioFrame = Math.round(1.0 * fps);
  const fixFrame = Math.round(2.5 * fps);

  const fixMsg = "Let me fix those failing tests...";
  const typedFix = typewriterText(fixMsg, frame, fixFrame, 0.6);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Terminal statusLeft="Code Agent v1.0" statusRight="Context: 24%">
        <AgentText>{typedIntro}</AgentText>

        {frame >= cmdFrame && (
          <>
            <Divider />
            <div style={{ paddingLeft: 20 }}>
              <span style={{ color: COLORS.green }}>$</span>{" "}
              <span style={{ color: COLORS.gray }}>npm test</span>
            </div>
          </>
        )}

        {frame >= failFrame && (
          <>
            <Divider />
            <ErrorText>FAIL src/auth.test.ts</ErrorText>
            <ErrorText>  x should validate token</ErrorText>
            <ErrorText>  x should handle expiry</ErrorText>
            <Divider />
            <ErrorText>2 tests failed</ErrorText>
          </>
        )}

        {frame >= fixFrame && (
          <>
            <Divider />
            <AgentText>
              {typedFix}
              {!isTypewriterDone(fixMsg, frame, fixFrame, 0.6) && (
                <Cursor opacity={cursorOpacity(frame)} />
              )}
            </AgentText>
          </>
        )}
      </Terminal>

      <HookBadge eventName="PostToolUseFailure" appearsAtFrame={hookFrame} />

      <Sequence from={audioFrame}>
        <Audio src={staticFile("audio/human-error.mp3")} volume={0.8} />
      </Sequence>
    </AbsoluteFill>
  );
};
