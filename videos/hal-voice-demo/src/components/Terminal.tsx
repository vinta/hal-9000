import React from "react";
import { loadFont } from "@remotion/google-fonts/SpaceMono";
import { COLORS } from "../styles";

const { fontFamily } = loadFont();

export const Terminal: React.FC<{
  title?: string;
  statusLeft?: string;
  statusRight?: string;
  opacity?: number;
  children: React.ReactNode;
}> = ({
  title = "code-agent",
  statusLeft,
  statusRight,
  opacity = 1,
  children,
}) => {
  return (
    <div
      style={{
        width: 1760,
        height: 920,
        backgroundColor: COLORS.termBg,
        borderRadius: 12,
        border: `1px solid ${COLORS.border}`,
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        fontFamily,
        opacity,
      }}
    >
      <div
        style={{
          height: 48,
          backgroundColor: COLORS.chrome,
          display: "flex",
          alignItems: "center",
          padding: "0 16px",
          gap: 8,
          borderBottom: `1px solid ${COLORS.border}`,
        }}
      >
        <div
          style={{
            width: 12,
            height: 12,
            borderRadius: 6,
            backgroundColor: "#ff5f57",
          }}
        />
        <div
          style={{
            width: 12,
            height: 12,
            borderRadius: 6,
            backgroundColor: COLORS.yellow,
          }}
        />
        <div
          style={{
            width: 12,
            height: 12,
            borderRadius: 6,
            backgroundColor: COLORS.green,
          }}
        />
        <div
          style={{
            flex: 1,
            textAlign: "center",
            color: COLORS.gray,
            fontSize: 14,
          }}
        >
          {title}
        </div>
        <div style={{ width: 52 }} />
      </div>

      <div
        style={{
          flex: 1,
          padding: 24,
          color: COLORS.text,
          fontSize: 18,
          lineHeight: "30px",
          overflow: "hidden",
          whiteSpace: "pre-wrap",
        }}
      >
        {children}
      </div>

      {(statusLeft || statusRight) && (
        <div
          style={{
            height: 32,
            backgroundColor: COLORS.chrome,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 16px",
            borderTop: `1px solid ${COLORS.border}`,
            color: COLORS.gray,
            fontSize: 12,
          }}
        >
          <span>{statusLeft}</span>
          <span>{statusRight}</span>
        </div>
      )}
    </div>
  );
};

export const Prompt: React.FC<{ children?: React.ReactNode }> = ({
  children,
}) => (
  <div style={{ display: "flex", gap: 8 }}>
    <span style={{ color: COLORS.green, fontWeight: "bold" }}>{">"}</span>
    <span style={{ color: COLORS.text }}>{children}</span>
  </div>
);

export const AgentText: React.FC<{
  children: React.ReactNode;
  color?: string;
}> = ({ children, color = COLORS.text }) => (
  <div style={{ color, paddingLeft: 20 }}>{children}</div>
);

export const SystemText: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => (
  <div style={{ color: COLORS.gray, fontStyle: "italic" }}>{children}</div>
);

export const ErrorText: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => (
  <div style={{ color: COLORS.error, paddingLeft: 20 }}>{children}</div>
);

export const Cursor: React.FC<{ opacity: number }> = ({ opacity }) => (
  <span
    style={{
      color: COLORS.red,
      opacity,
      fontWeight: "bold",
    }}
  >
    |
  </span>
);

export const Divider: React.FC = () => (
  <div style={{ height: 12 }} />
);

export const BoxContent: React.FC<{
  title: string;
  titleColor?: string;
  children: React.ReactNode;
}> = ({ title, titleColor = COLORS.yellow, children }) => (
  <div
    style={{
      border: `1px solid ${titleColor}`,
      borderRadius: 6,
      padding: "12px 16px",
      margin: "8px 0 8px 20px",
    }}
  >
    <div
      style={{
        color: titleColor,
        fontSize: 14,
        fontWeight: "bold",
        marginBottom: 8,
      }}
    >
      {title}
    </div>
    <div style={{ color: COLORS.text, fontSize: 16 }}>{children}</div>
  </div>
);
