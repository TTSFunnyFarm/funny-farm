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

# Display
load-display pandagl
aux-display pandagl
aux-display p3tinydisplay

# Models
model-path /
vfs-mount phase_3.mf /
vfs-mount phase_3.5.mf /
vfs-mount phase_4.mf /
vfs-mount phase_5.mf /
vfs-mount phase_5.5.mf /
vfs-mount phase_6.mf /
vfs-mount phase_7.mf /
vfs-mount phase_8.mf /
vfs-mount phase_9.mf /
vfs-mount phase_10.mf /
vfs-mount phase_11.mf /
vfs-mount phase_12.mf /
vfs-mount phase_13.mf /
vfs-mount phase_14.mf /
default-model-extension .bam
model-cache-models #f
model-cache-textures #f

# Textures
texture-minfilter mipmap
texture-anisotropic-degree 16
textures-power-2 none

# Performance
garbage-collect-states #f
support-threads #t
lock-to-one-cpu #f
lock-to-one-core #f

# Holidays
want-halloween #f
want-winter #f

# Misc.
want-pets #f
game-version %GAME_VERSION%
want-discord-integration true
