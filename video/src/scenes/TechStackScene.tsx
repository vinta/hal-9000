import { loadFont } from "@remotion/google-fonts/SpaceMono";
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const { fontFamily } = loadFont();

type TechItem = {
  name: string;
  icon: string;
  color: string;
};

const TECH_STACK: TechItem[] = [
  { name: "Python", icon: "icons/python.svg", color: "#3776ab" },
  { name: "Node.js", icon: "icons/nodejs.svg", color: "#5fa04e" },
  { name: "Docker", icon: "icons/docker.svg", color: "#2496ed" },
  { name: "Kubernetes", icon: "icons/kubernetes.svg", color: "#326ce5" },
  { name: "Amazon Web Services", icon: "icons/aws.svg", color: "#ff9900" },
  { name: "Google Cloud", icon: "icons/gcp.svg", color: "#4285f4" },
  { name: "Bun", icon: "icons/bun.svg", color: "#fbf0df" },
  { name: "Claude Code", icon: "icons/claude.svg", color: "#d4a27f" },
];

const TechCard: React.FC<{
  item: TechItem;
  index: number;
}> = ({ item, index }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const row = Math.floor(index / 4);
  const col = index % 4;
  const delay = (row * 0.15 + col * 0.1) * fps;

  const progress = spring({
    frame: frame - delay,
    fps,
    config: { damping: 15, stiffness: 200 },
  });

  const scale = interpolate(progress, [0, 1], [0, 1]);
  const opacity = interpolate(progress, [0, 0.5], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 12,
        opacity,
        transform: `scale(${scale})`,
      }}
    >
      <div
        style={{
          width: 100,
          height: 100,
          borderRadius: 20,
          backgroundColor: "#ffffff",
          border: `2px solid ${item.color}`,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          boxShadow: `0 4px 20px ${item.color}33`,
          padding: 20,
        }}
      >
        <Img
          src={staticFile(item.icon)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "contain",
          }}
        />
      </div>
      <span
        style={{
          fontFamily,
          fontSize: 16,
          color: "#ffffff",
        }}
      >
        {item.name}
      </span>
    </div>
  );
};

export const TechStackScene: React.FC = () => {
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
        justifyContent: "center",
        alignItems: "center",
        padding: 80,
      }}
    >
      {/* Section title */}
      <div
        style={{
          position: "absolute",
          top: 80,
          fontFamily,
          fontSize: 36,
          color: "#ff3333",
          opacity: interpolate(titleProgress, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(titleProgress, [0, 1], [-20, 0])}px)`,
        }}
      >
        Complete Dev Stack
      </div>

      {/* Tech grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 48,
          marginTop: 40,
        }}
      >
        {TECH_STACK.map((item, index) => (
          <TechCard key={item.name} item={item} index={index} />
        ))}
      </div>

      {/* Subtitle */}
      <div
        style={{
          position: "absolute",
          bottom: 80,
          fontFamily,
          fontSize: 20,
          color: "#666",
        }}
      >
        All configured with a single command
      </div>
    </AbsoluteFill>
  );
};
