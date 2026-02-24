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

export const PermissionRequestScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const intro = "I need to install a dependency to proceed.";
  const introStart = Math.round(0.0 * fps);
  const typedIntro = typewriterText(intro, frame, introStart, 0.8);

  const boxFrame = Math.round(0.8 * fps);
  const hookFrame = Math.round(1.0 * fps);
  const audioFrame = Math.round(1.0 * fps);
  const userAnswerFrame = Math.round(4.0 * fps);
  const installFrame = Math.round(4.5 * fps);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Terminal statusLeft="Code Agent v1.0" statusRight="Context: 12%">
        <AgentText>
          {typedIntro}
          {!isTypewriterDone(intro, frame, introStart, 0.8) && (
            <Cursor opacity={cursorOpacity(frame)} />
          )}
        </AgentText>

        {frame >= boxFrame && (
          <>
            <Divider />
            <BoxContent title="Permission Required" titleColor={COLORS.yellow}>
              <div>
                Run:{" "}
                <span style={{ color: COLORS.green }}>
                  npm install jsonwebtoken
                </span>
              </div>
              <Divider />
              <div>
                Allow? (
                <span style={{ color: COLORS.green, fontWeight: "bold" }}>
                  y
                </span>
                /n)
              </div>
            </BoxContent>
          </>
        )}

        {frame >= userAnswerFrame && (
          <>
            <Divider />
            <div style={{ color: COLORS.green, paddingLeft: 20, fontWeight: "bold" }}>
              y
            </div>
          </>
        )}

        {frame >= installFrame && (
          <>
            <AgentText color={COLORS.gray}>Installing...</AgentText>
          </>
        )}

        {frame >= installFrame + Math.round(0.5 * fps) && (
          <div style={{ color: COLORS.green, paddingLeft: 20 }}>
            Installed jsonwebtoken@9.0.2
          </div>
        )}
      </Terminal>

      <HookBadge eventName="PermissionRequest" appearsAtFrame={hookFrame} />

      <Sequence from={audioFrame}>
        <Audio
          src={staticFile(
            "audio/well-forgive-me-for-being-so-inquisitive.mp3",
          )}
          volume={0.8}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
