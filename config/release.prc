# Window options
window-title Toontown's Funny Farm
win-origin 8 31
win-size 1280 720

# Notify
notify-level warning
default-directnotify-level info
notify-timestamp #t
notify-integrate #f

# Audio
audio-library-name p3openal_audio

# Shaders/OpenGL
gl-version 3 2

# Display
load-display pandagl

# Models
model-path resources
vfs-mount resources/phase_3.mf resources
vfs-mount resources/phase_3.5.mf resources
vfs-mount resources/phase_4.mf resources
vfs-mount resources/phase_5.mf resources
vfs-mount resources/phase_5.5.mf resources
vfs-mount resources/phase_6.mf resources
vfs-mount resources/phase_7.mf resources
vfs-mount resources/phase_8.mf resources
vfs-mount resources/phase_9.mf resources
vfs-mount resources/phase_10.mf resources
vfs-mount resources/phase_11.mf resources
vfs-mount resources/phase_12.mf resources
vfs-mount resources/phase_13.mf resources
vfs-mount resources/phase_14.mf resources
default-model-extension .bam
model-cache-models #f
model-cache-textures #f

# Textures
texture-minfilter mipmap
texture-anisotropic-degree 16
textures-power-2 none

# Performance
gc-save-all 0

# Holidays
want-halloween #f
want-winter #f

# Misc.
want-pets #f
game-version %GAME_VERSION%
want-discord-integration true
