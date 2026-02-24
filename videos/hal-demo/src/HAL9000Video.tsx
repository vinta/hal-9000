import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { useVideoConfig } from "remotion";

import { IntroScene } from "./scenes/IntroScene";
import { BootstrapScene } from "./scenes/BootstrapScene";
import { CommandsScene } from "./scenes/CommandsScene";
import { TechStackScene } from "./scenes/TechStackScene";
import { OutroScene } from "./scenes/OutroScene";

export const HAL9000Video: React.FC = () => {
  const { fps } = useVideoConfig();

  const transitionDuration = Math.round(0.5 * fps);

  return (
    <TransitionSeries>
      {/* Intro - HAL eye and title */}
      <TransitionSeries.Sequence durationInFrames={4 * fps}>
        <IntroScene />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* Bootstrap command */}
      <TransitionSeries.Sequence durationInFrames={5 * fps}>
        <BootstrapScene />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={slide({ direction: "from-right" })}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* CLI Commands */}
      <TransitionSeries.Sequence durationInFrames={5 * fps}>
        <CommandsScene />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={slide({ direction: "from-right" })}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* Tech Stack */}
      <TransitionSeries.Sequence durationInFrames={4 * fps}>
        <TechStackScene />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* Outro with audio */}
      <TransitionSeries.Sequence durationInFrames={7 * fps}>
        <OutroScene />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
