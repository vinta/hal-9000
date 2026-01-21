import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/SpaceMono";

const { fontFamily } = loadFont();

type Command = {
  cmd: string;
  description: string;
  delay: number;
};

const COMMANDS: Command[] = [
  {
    cmd: "hal update --tags python,node",
    description: "Install specific development stacks",
    delay: 0,
  },
  {
    cmd: "hal link ~/.zshrc",
    description: "Symlink dotfiles to version control",
    delay: 1.5,
  },
  {
    cmd: "hal sync",
    description: "Force-sync all tracked configurations",
    delay: 3,
  },
];

const CommandBlock: React.FC<{
  command: Command;
  index: number;
}> = ({ command, index }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const delayFrames = command.delay * fps;

  const progress = spring({
    frame: frame - delayFrames,
    fps,
    config: { damping: 200 },
  });

  const opacity = interpolate(progress, [0, 1], [0, 1]);
  const translateX = interpolate(progress, [0, 1], [-40, 0]);

  return (
    <div
      style={{
        opacity,
        transform: `translateX(${translateX}px)`,
        marginBottom: 32,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 16,
          marginBottom: 8,
        }}
      >
        <span style={{ color: "#28c840", fontSize: 20 }}>$</span>
        <span
          style={{
            fontFamily,
            fontSize: 24,
            color: "#ffffff",
            backgroundColor: "#1a1a1a",
            padding: "8px 16px",
            borderRadius: 6,
            border: "1px solid #333",
          }}
        >
          {command.cmd}
        </span>
      </div>
      <div
        style={{
          fontFamily,
          fontSize: 16,
          color: "#888",
          marginLeft: 36,
        }}
      >
        {command.description}
      </div>
    </div>
  );
};

export const CommandsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleProgress = spring({
    frame,
    fps,
    config: { damping: 200 },
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0a0a",
        padding: 80,
      }}
    >
      {/* Section title */}
      <div
        style={{
          fontFamily,
          fontSize: 36,
          color: "#ff3333",
          marginBottom: 60,
          opacity: interpolate(titleProgress, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(titleProgress, [0, 1], [-20, 0])}px)`,
        }}
      >
        Powerful CLI Commands
      </div>

      {/* Commands list */}
      <div style={{ marginTop: 20 }}>
        {COMMANDS.map((command, index) => (
          <CommandBlock key={command.cmd} command={command} index={index} />
        ))}
      </div>
    </AbsoluteFill>
  );
};
