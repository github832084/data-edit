import { Config } from '@remotion/cli/config';
// Use a locally installed Chromium if REMOTION_CHROME points at one (e.g. /opt/pw-browsers/...); else Remotion downloads its own.
if (process.env.REMOTION_CHROME) Config.setBrowserExecutable(process.env.REMOTION_CHROME);
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(92);
