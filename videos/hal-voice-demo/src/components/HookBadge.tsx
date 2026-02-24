import React from "react";
import { Img, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { loadFont } from "@remotion/google-fonts/SpaceMono";
import { staticFile } from "remotion";
import { COLORS } from "../styles";

const { fontFamily } = loadFont();

export const HookBadge: React.FC<{
  eventName: string;
  appearsAtFrame: number;
}> = ({ eventName, appearsAtFrame }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (frame < appearsAtFrame) return null;

  const localFrame = frame - appearsAtFrame;

  const progress = spring({
    frame: localFrame,
    fps,
    config: { damping: 20, stiffness: 200 },
  });

  const translateX = interpolate(progress, [0, 1], [400, 0]);
  const opacity = interpolate(progress, [0, 1], [0, 1]);

  const pulseOpacity = interpolate(
    Math.sin(localFrame * 0.15),
    [-1, 1],
    [0.4, 1],
  );

  return (
    <div
      style={{
        position: "absolute",
        top: 100,
        right: 40,
        transform: `translateX(${translateX}px)`,
        opacity,
        display: "flex",
        alignItems: "center",
        gap: 16,
        backgroundColor: "rgba(10, 10, 10, 0.95)",
        border: `2px solid ${COLORS.red}`,
        borderRadius: 12,
        padding: "16px 24px",
        fontFamily,
      }}
    >
      <Img
        src={staticFile("hal-9000.jpg")}
        style={{
          width: 48,
          height: 48,
          borderRadius: 24,
          opacity: pulseOpacity,
          boxShadow: `0 0 ${20 * pulseOpacity}px ${COLORS.red}`,
        }}
      />
      <div>
        <div
          style={{
            color: COLORS.gray,
            fontSize: 12,
            letterSpacing: 2,
            textTransform: "uppercase",
            marginBottom: 4,
          }}
        >
          Hook Event
        </div>
        <div
          style={{
            color: COLORS.red,
            fontSize: 20,
            fontWeight: "bold",
            letterSpacing: 1,
          }}
        >
          {eventName}
        </div>
      </div>
    </div>
  );
};
