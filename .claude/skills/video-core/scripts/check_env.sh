#!/usr/bin/env bash
# Check (and with --install, fix) everything the video skills need.
#   bash .claude/skills/video-core/scripts/check_env.sh [--install]
inst=0; [ "${1:-}" = "--install" ] && inst=1
miss=0
ok()   { echo "  ok    $1"; }
bad()  { echo "  MISS  $1  ->  $2"; miss=$((miss+1)); }
try()  { if [ $inst = 1 ]; then echo "  ...   $2"; eval "$2" >/dev/null 2>&1 && return 0; fi; return 1; }
apt_or_brew() { if command -v brew >/dev/null; then echo "brew install $2"; else echo "apt-get install -y $1"; fi; }

echo "tools"
command -v ffmpeg >/dev/null || try ffmpeg "$(apt_or_brew ffmpeg ffmpeg)" ; command -v ffmpeg >/dev/null && ok "ffmpeg $(ffmpeg -version | head -1 | awk '{print $3}')" || bad ffmpeg "$(apt_or_brew ffmpeg ffmpeg)"
ffmpeg -hide_banner -encoders 2>/dev/null | grep -q libx264 && ok "ffmpeg libx264" || bad "ffmpeg libx264" "install an ffmpeg build with libx264"
command -v node >/dev/null || try node "$(apt_or_brew nodejs node)"
if command -v node >/dev/null && [ "$(node -p 'process.versions.node.split(".")[0]')" -ge 18 ]; then ok "node $(node -v)"; else bad "node >= 18" "$(apt_or_brew nodejs node)"; fi
node -e "require('playwright')" 2>/dev/null || try playwright "npm install -g playwright && npx playwright install chromium"
node -e "require('playwright').chromium.launch().then(b=>b.close())" 2>/dev/null && ok "playwright + headless chromium" || bad "playwright chromium" "npm install -g playwright && npx playwright install chromium"
echo "python"
for spec in "torch:torch" "torchaudio:torchaudio" "uroman:uroman" "whisper:openai-whisper" "demucs:demucs" "librosa:librosa" "soundfile:soundfile" "cv2:opencv-python" "PIL:pillow" "numpy:numpy" "mediapipe:mediapipe" "rembg:rembg[cpu]"; do
  m=${spec%%:*}; p=${spec#*:}
  python3 -c "import $m" 2>/dev/null || try "$m" "pip install '$p' || pip install --user '$p'"
  python3 -c "import $m" 2>/dev/null && ok "$m" || bad "$m" "pip install '$p'"
done
if [ "$(uname)" = Linux ]; then ldconfig -p 2>/dev/null | grep -q libEGL.so.1 || try libegl "apt-get install -y libegl1 libgles2"; ldconfig -p 2>/dev/null | grep -q libEGL.so.1 && ok "libEGL (MediaPipe)" || bad "libEGL (MediaPipe)" "apt-get install -y libegl1 libgles2"; fi
echo "models (downloaded once, then cached)"
python3 -c "import torchaudio; torchaudio.pipelines.MMS_FA.get_model()" 2>/dev/null && ok "MMS_FA forced aligner" || bad "MMS_FA weights" "needs download.pytorch.org"
python3 -c "from demucs.pretrained import get_model; get_model('htdemucs')" 2>/dev/null && ok "demucs htdemucs" || bad "demucs weights" "needs dl.fbaipublicfiles.com"
python3 -c "import sys; sys.path.insert(0, '$(dirname "$0")'); import vision; vision.model('face_full'); vision.model('selfie')" 2>/dev/null && ok "MediaPipe face + person models" || bad "MediaPipe models" "needs storage.googleapis.com"
ls ~/.cache/whisper/large-v3*.pt >/dev/null 2>&1 && ok "whisper large-v3" || echo "  opt   whisper large-v3 not cached yet (first transcribe downloads ~3 GB from openaipublic.azureedge.net)"
echo "optional"
command -v blender >/dev/null && ok "blender $(blender -v 2>/dev/null | head -1)" || echo "  opt   blender (only 3d-explainer): $(command -v brew >/dev/null && echo 'brew install --cask blender' || echo 'download from blender.org')"
command -v yt-dlp >/dev/null && ok "yt-dlp" || echo "  opt   yt-dlp (only youtube-clips links): pip install yt-dlp"
command -v avconvert >/dev/null && ok "avconvert (iPhone HDR -> SDR)" || echo "  opt   avconvert is macOS-only (talking-head-edit HDR input)"
echo; echo "$miss missing"; [ $miss = 0 ]
